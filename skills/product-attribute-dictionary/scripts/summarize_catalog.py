"""
Product Catalog Summarizer
Reads a product catalog CSV and produces a compact JSON summary
for the product attribute dictionary skill.

Designed to reduce a large CSV into a small, structured overview
that an LLM can read efficiently. The LLM does the interpretive
work; this script gives it clean, complete, deduplicated data.

Usage:
    python summarize_catalog.py <path_to_csv> [--output <path_to_json>]

Output:
    JSON summary with column headers, platform detection, product
    types, distinct values per column, variant dimensions, and
    sample rows for pattern recognition.
"""

import csv
import json
import sys
import os
from collections import Counter, defaultdict
from argparse import ArgumentParser


# -- Platform detection --

def detect_platform(headers):
    header_set = set(h.lower().strip() for h in headers)
    signals = {
        "shopify": {"handle", "variant sku", "variant price", "variant grams", "variant inventory qty"},
        "bigcommerce": {"product id", "product name", "brand name", "product type", "product code/sku"},
        "woocommerce": {"post_title", "regular_price", "sale_price", "post_status", "sku"},
    }
    scores = {p: len(s & header_set) for p, s in signals.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] >= 2 else "unknown"


def detect_type_column(headers, platform):
    candidates = {
        "shopify": ["type", "product type"],
        "bigcommerce": ["product type", "type", "category"],
        "woocommerce": ["product_type", "type", "tax:product_type"],
        "unknown": ["type", "product type", "product_type", "category"],
    }
    header_lower_map = {h.lower().strip(): h for h in headers}
    for candidate in candidates.get(platform, candidates["unknown"]):
        if candidate in header_lower_map:
            return header_lower_map[candidate]
    return None


# -- Shopify field propagation --

SHOPIFY_PRODUCT_FIELDS = {
    "title", "body (html)", "vendor", "type", "tags", "published",
    "product category", "image src", "image position", "image alt text",
    "seo title", "seo description", "collection", "template suffix",
    "custom product type", "status",
}


def propagate_shopify_fields(rows, headers):
    handle_col = None
    for h in headers:
        if h.lower().strip() == "handle":
            handle_col = h
            break
    if not handle_col:
        return rows

    product_fields = [h for h in headers if h.lower().strip() in SHOPIFY_PRODUCT_FIELDS]
    if not product_fields:
        return rows

    propagated = []
    current = {}
    for row in rows:
        handle = row.get(handle_col, "").strip()
        if handle:
            title = row.get("Title", "").strip() if "Title" in row else ""
            if title or not current.get("_handle"):
                current = {"_handle": handle}
                for field in product_fields:
                    val = row.get(field, "").strip()
                    if val:
                        current[field] = val

        new_row = dict(row)
        if handle == current.get("_handle", ""):
            for field in product_fields:
                if not new_row.get(field, "").strip() and field in current:
                    new_row[field] = current[field]
        propagated.append(new_row)
    return propagated


# -- Core summarization --

# Columns where listing distinct values is not useful
SKIP_DISTINCT = {
    "body (html)", "image src", "image alt text", "seo title",
    "seo description", "variant barcode", "handle", "variant image",
    "variant inventory qty", "variant grams", "cost per item",
}


def truncate(val, maxlen=120):
    """Truncate a string value for display."""
    if len(val) <= maxlen:
        return val
    return val[:maxlen] + "..."


def distinct_values(rows, column, limit=30):
    """Return top distinct values for a column, sorted by frequency."""
    if column.lower().strip() in SKIP_DISTINCT:
        non_empty = sum(1 for row in rows if row.get(column, "").strip())
        return {"skipped": True, "non_empty_rows": non_empty, "total_rows": len(rows)}

    counter = Counter()
    for row in rows:
        val = row.get(column, "").strip()
        if val:
            counter[val] += 1
    top = counter.most_common(limit)
    total_distinct = len(counter)
    result = [truncate(v) for v, _ in top]
    if total_distinct > limit:
        result.append(f"... and {total_distinct - limit} more")
    return result


def sample_rows(rows, headers, n=3):
    """Return a sample of rows, keeping only pattern-relevant columns."""
    # Only include columns useful for convention/pattern detection.
    keep_lower = {
        "handle", "title", "body (html)", "vendor", "type", "tags",
        "product category", "status",
        "option1 name", "option1 value", "option2 name", "option2 value",
        "option3 name", "option3 value",
        "variant sku", "variant price", "variant compare at price",
        "image src",
    }

    sample = rows[:n] if len(rows) <= n else [
        rows[0],
        rows[len(rows) // 2],
        rows[-1],
    ]
    cleaned = []
    for row in sample:
        cleaned.append({
            k: truncate(v, 150)
            for k, v in row.items()
            if v.strip() and k.lower().strip() in keep_lower
        })
    return cleaned


def detect_shopify_options(rows, headers):
    """Read Shopify Option Name columns to get variant dimension labels."""
    name_cols = sorted(h for h in headers if h.lower().strip().startswith("option") and "name" in h.lower())
    value_cols = sorted(h for h in headers if h.lower().strip().startswith("option") and "value" in h.lower())

    dimensions = {}
    for name_col, value_col in zip(name_cols, value_cols):
        labels = set()
        for row in rows:
            label = row.get(name_col, "").strip()
            if label:
                labels.add(label)
        if labels:
            # For each label, collect distinct values
            label_values = {}
            for label in labels:
                values = set()
                for row in rows:
                    if row.get(name_col, "").strip() == label:
                        val = row.get(value_col, "").strip()
                        if val:
                            values.add(val)
                label_values[label] = sorted(values)
            dimensions[name_col] = {
                "value_column": value_col,
                "labels": label_values,
            }
    return dimensions


def count_products(rows, headers, platform):
    """Count distinct products (not variant rows)."""
    if platform == "shopify":
        for h in headers:
            if h.lower().strip() == "handle":
                handles = set(row.get(h, "").strip() for row in rows if row.get(h, "").strip())
                return len(handles)
    return len(rows)


def summarize(filepath):
    with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)

    if not rows or not headers:
        return {"error": "CSV is empty or could not be parsed."}

    platform = detect_platform(headers)

    if platform == "shopify":
        rows = propagate_shopify_fields(rows, headers)

    type_column = detect_type_column(headers, platform)
    product_count = count_products(rows, headers, platform)

    # Product types with counts
    product_types = {}
    if type_column:
        for row in rows:
            t = row.get(type_column, "").strip() or "(no type)"
            product_types[t] = product_types.get(t, 0) + 1

    # Distinct values per column
    column_values = {}
    for col in headers:
        column_values[col] = distinct_values(rows, col)

    # Variant dimensions (Shopify-specific)
    variant_dimensions = {}
    if platform == "shopify":
        variant_dimensions = detect_shopify_options(rows, headers)

    # Sample rows per product type (for pattern recognition)
    # For catalogs with many types, sample from the largest types
    type_samples = {}
    if type_column:
        groups = defaultdict(list)
        for row in rows:
            t = row.get(type_column, "").strip() or "(no type)"
            groups[t].append(row)

        # Sample from up to 10 types, picking the largest ones
        sorted_types = sorted(groups.items(), key=lambda x: -len(x[1]))
        for type_name, type_rows in sorted_types[:10]:
            type_samples[type_name] = sample_rows(type_rows, headers, n=2)
    else:
        type_samples["_all"] = sample_rows(rows, headers, n=5)

    return {
        "file": os.path.basename(filepath),
        "total_rows": len(rows),
        "distinct_products": product_count,
        "columns": headers,
        "platform": platform,
        "type_column": type_column,
        "product_types": product_types,
        "column_values": column_values,
        "variant_dimensions": variant_dimensions,
        "type_samples": type_samples,
    }


def main():
    parser = ArgumentParser(description="Summarize a product catalog CSV for the attribute dictionary skill.")
    parser.add_argument("csv_path", help="Path to the product catalog CSV")
    parser.add_argument("--output", "-o", default="catalog_summary.json", help="Output JSON path")
    args = parser.parse_args()

    if not os.path.isfile(args.csv_path):
        print(f"Error: file not found: {args.csv_path}", file=sys.stderr)
        sys.exit(1)

    result = summarize(args.csv_path)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Summary written to {args.output}")
    print(f"  Platform: {result.get('platform', 'unknown')}")
    print(f"  Rows: {result.get('total_rows', 0)}")
    print(f"  Products: {result.get('distinct_products', 0)}")
    print(f"  Columns: {len(result.get('columns', []))}")
    print(f"  Product types: {len(result.get('product_types', {}))}")


if __name__ == "__main__":
    main()

"""
Metafield Export Summarizer
Reads a metafield export CSV (wide or long format) and produces a
compact JSON summary for the product attribute dictionary skill.

Pairs with summarize_catalog.py. The catalog summarizer handles the
standard product export. This script handles the metafield export,
which comes from Matrixify, Shopify API, or bulk export apps.

Usage:
    python summarize_metafields.py <metafield_csv> [--products <product_csv>] [--output <path_to_json>]

The --products flag is optional but recommended. When provided, the
script joins metafield data to product types and reports per-type
coverage. Without it, the summary still lists all metafields and
their values but cannot report which product types use which fields.

Output:
    JSON summary with format detection, namespace/key pairs, data
    types, distinct values, fill rates, and per-type coverage.
"""

import csv
import json
import sys
import os
import re
from collections import Counter, defaultdict
from argparse import ArgumentParser


# -- Format detection --

def detect_format(headers):
    """Detect whether the export is wide or long format.

    Wide format (Matrixify-style): one row per product, metafield
    columns named like 'namespace.key' or 'metafields.namespace.key'
    or 'Metafield: namespace.key'.

    Long format (API-style): one row per metafield value, with
    columns like handle/namespace/key/value/type.
    """
    header_lower = set(h.lower().strip() for h in headers)

    # Long format signals
    long_signals = {"namespace", "key", "value"}
    if long_signals.issubset(header_lower):
        return "long"

    # Wide format signals: look for dotted column names
    dotted = sum(1 for h in headers if "." in h or h.lower().startswith("metafield"))
    if dotted >= 2:
        return "wide"

    return "unknown"


def find_handle_column(headers):
    """Find the handle/identifier column."""
    candidates = ["handle", "product handle", "product_handle", "id", "product id"]
    header_lower_map = {h.lower().strip(): h for h in headers}
    for c in candidates:
        if c in header_lower_map:
            return header_lower_map[c]
    return None


# -- Wide format parsing --

WIDE_METAFIELD_PATTERNS = [
    re.compile(r"^metafields?\.\s*(.+)$", re.IGNORECASE),
    re.compile(r"^metafield:\s*(.+)$", re.IGNORECASE),
    re.compile(r"^([a-z_]+\.[a-z_]+)$", re.IGNORECASE),
]

# Columns that look dotted but are not metafields
WIDE_IGNORE = {
    "google shopping / google product category",
    "google shopping / gender",
    "google shopping / age group",
    "google shopping / mpn",
    "google shopping / adwords grouping",
    "google shopping / adwords labels",
    "google shopping / condition",
    "google shopping / custom product",
    "price / international",
    "compare at price / international",
}


def parse_wide_metafield_columns(headers):
    """Identify which columns are metafields and extract namespace.key."""
    metafield_cols = {}
    for h in headers:
        if h.lower().strip() in WIDE_IGNORE:
            continue
        for pattern in WIDE_METAFIELD_PATTERNS:
            match = pattern.match(h.strip())
            if match:
                raw = match.group(1).strip()
                parts = raw.split(".", 1)
                if len(parts) == 2:
                    namespace, key = parts[0].strip(), parts[1].strip()
                    metafield_cols[h] = {"namespace": namespace, "key": key}
                break
    return metafield_cols


def summarize_wide(rows, headers, handle_col, product_type_map):
    """Summarize a wide-format metafield export."""
    metafield_cols = parse_wide_metafield_columns(headers)
    if not metafield_cols:
        return {"error": "No metafield columns detected in wide-format export."}

    metafields = {}
    for col, meta in metafield_cols.items():
        ns_key = f"{meta['namespace']}.{meta['key']}"

        values = []
        handles_with_value = set()
        for row in rows:
            val = row.get(col, "").strip()
            if val:
                values.append(val)
                if handle_col:
                    handle = row.get(handle_col, "").strip()
                    if handle:
                        handles_with_value.add(handle)

        if not values:
            continue

        entry = build_metafield_entry(
            meta["namespace"], meta["key"], values,
            handles_with_value, len(rows), product_type_map
        )
        metafields[ns_key] = entry

    return {
        "format": "wide",
        "total_rows": len(rows),
        "metafield_columns_detected": len(metafield_cols),
        "metafields": metafields,
    }


# -- Long format parsing --

def find_long_columns(headers):
    """Map long-format columns to their roles."""
    header_lower_map = {h.lower().strip(): h for h in headers}
    mapping = {}
    for role, candidates in {
        "namespace": ["namespace"],
        "key": ["key", "metafield_key"],
        "value": ["value", "metafield_value"],
        "type": ["type", "value_type", "metafield_type"],
        "handle": ["handle", "product handle", "product_handle", "owner_id"],
    }.items():
        for c in candidates:
            if c in header_lower_map:
                mapping[role] = header_lower_map[c]
                break
    return mapping


def summarize_long(rows, headers, handle_col_override, product_type_map):
    """Summarize a long-format metafield export."""
    col_map = find_long_columns(headers)
    ns_col = col_map.get("namespace")
    key_col = col_map.get("key")
    val_col = col_map.get("value")
    type_col = col_map.get("type")
    handle_col = handle_col_override or col_map.get("handle")

    if not ns_col or not key_col or not val_col:
        return {"error": "Could not identify namespace, key, and value columns."}

    # Group rows by namespace.key
    grouped = defaultdict(lambda: {"values": [], "handles": set(), "types": set()})
    for row in rows:
        ns = row.get(ns_col, "").strip()
        key = row.get(key_col, "").strip()
        val = row.get(val_col, "").strip()
        if not ns or not key:
            continue

        ns_key = f"{ns}.{key}"
        if val:
            grouped[ns_key]["values"].append(val)
        if handle_col:
            handle = row.get(handle_col, "").strip()
            if handle and val:
                grouped[ns_key]["handles"].add(handle)
        if type_col:
            t = row.get(type_col, "").strip()
            if t:
                grouped[ns_key]["types"].add(t)

    # Count distinct handles for fill rate denominator
    all_handles = set()
    if handle_col:
        for row in rows:
            h = row.get(handle_col, "").strip()
            if h:
                all_handles.add(h)

    metafields = {}
    for ns_key, data in grouped.items():
        ns, key = ns_key.split(".", 1)
        entry = build_metafield_entry(
            ns, key, data["values"],
            data["handles"], len(all_handles) or len(rows),
            product_type_map
        )
        if data["types"]:
            entry["declared_types"] = sorted(data["types"])
        metafields[ns_key] = entry

    return {
        "format": "long",
        "total_rows": len(rows),
        "distinct_handles": len(all_handles),
        "metafields": metafields,
    }


# -- Shared analysis --

def truncate(val, maxlen=120):
    if len(val) <= maxlen:
        return val
    return val[:maxlen] + "..."


def infer_data_type(values):
    """Infer the data type from a list of string values."""
    if not values:
        return "unknown"

    # Check if all values are boolean-like
    bool_vals = {"true", "false", "yes", "no", "0", "1"}
    if all(v.lower() in bool_vals for v in values):
        return "boolean"

    # Check if all values are integers
    try:
        [int(v) for v in values]
        return "integer"
    except (ValueError, TypeError):
        pass

    # Check if all values are decimals
    try:
        [float(v) for v in values]
        return "decimal"
    except (ValueError, TypeError):
        pass

    # Check cardinality: if few distinct values relative to count, likely controlled
    distinct = set(values)
    if len(distinct) <= 10 and len(values) >= 5:
        return "controlled_list"

    return "free_text"


def build_metafield_entry(namespace, key, values, handles_with_value, total_count, product_type_map):
    """Build a summary entry for a single metafield."""
    counter = Counter(values)
    distinct = sorted(counter.keys(), key=lambda v: -counter[v])
    data_type = infer_data_type(values)

    entry = {
        "namespace": namespace,
        "key": key,
        "inferred_type": data_type,
        "non_empty_count": len(values),
        "distinct_count": len(distinct),
    }

    # Fill rate
    if total_count > 0 and handles_with_value:
        entry["fill_rate"] = round(len(handles_with_value) / total_count, 3)
    elif total_count > 0:
        entry["fill_rate"] = round(len(values) / total_count, 3)

    # Distinct values (capped)
    if data_type in ("controlled_list", "boolean"):
        entry["values"] = [truncate(v) for v in distinct]
    elif len(distinct) <= 30:
        entry["values"] = [truncate(v) for v in distinct[:30]]
    else:
        entry["sample_values"] = [truncate(v) for v in distinct[:15]]
        entry["total_distinct"] = len(distinct)

    # Per-type coverage
    if product_type_map and handles_with_value:
        type_coverage = defaultdict(lambda: {"with_value": 0, "total": 0})
        all_handles_by_type = defaultdict(set)

        for handle, ptype in product_type_map.items():
            all_handles_by_type[ptype].add(handle)

        for ptype, type_handles in all_handles_by_type.items():
            overlap = handles_with_value & type_handles
            type_coverage[ptype]["with_value"] = len(overlap)
            type_coverage[ptype]["total"] = len(type_handles)

        # Only include types that have at least one product with this metafield
        coverage = {}
        for ptype, counts in type_coverage.items():
            if counts["with_value"] > 0:
                rate = round(counts["with_value"] / counts["total"], 3) if counts["total"] > 0 else 0
                coverage[ptype] = {
                    "products_with_value": counts["with_value"],
                    "total_products": counts["total"],
                    "fill_rate": rate,
                }
        if coverage:
            entry["per_type_coverage"] = coverage

    return entry


# -- Product CSV joining --

def load_product_type_map(product_csv_path):
    """Load handle-to-type mapping from a product CSV."""
    if not product_csv_path or not os.path.isfile(product_csv_path):
        return {}

    with open(product_csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)

    handle_col = find_handle_column(headers)
    if not handle_col:
        return {}

    # Find type column
    type_candidates = ["type", "product type", "product_type"]
    header_lower_map = {h.lower().strip(): h for h in headers}
    type_col = None
    for c in type_candidates:
        if c in header_lower_map:
            type_col = header_lower_map[c]
            break
    if not type_col:
        return {}

    # Build map, propagating type to variant rows (Shopify-style)
    type_map = {}
    current_handle = None
    current_type = None
    for row in rows:
        handle = row.get(handle_col, "").strip()
        ptype = row.get(type_col, "").strip()
        if handle:
            current_handle = handle
            if ptype:
                current_type = ptype
        if current_handle and current_type:
            type_map[current_handle] = current_type

    return type_map


# -- Main --

def main():
    parser = ArgumentParser(
        description="Summarize a metafield export CSV for the product attribute dictionary skill."
    )
    parser.add_argument("metafield_csv", help="Path to the metafield export CSV")
    parser.add_argument(
        "--products", "-p", default=None,
        help="Path to the product catalog CSV (for per-type coverage)"
    )
    parser.add_argument("--output", "-o", default="metafield_summary.json", help="Output JSON path")
    args = parser.parse_args()

    if not os.path.isfile(args.metafield_csv):
        print(f"Error: file not found: {args.metafield_csv}", file=sys.stderr)
        sys.exit(1)

    # Load product type map if product CSV provided
    product_type_map = load_product_type_map(args.products)

    # Read metafield CSV
    with open(args.metafield_csv, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)

    if not rows or not headers:
        result = {"error": "CSV is empty or could not be parsed."}
    else:
        fmt = detect_format(headers)
        handle_col = find_handle_column(headers)

        if fmt == "wide":
            result = summarize_wide(rows, headers, handle_col, product_type_map)
        elif fmt == "long":
            result = summarize_long(rows, headers, handle_col, product_type_map)
        else:
            result = {
                "error": "Could not detect metafield export format.",
                "hint": "Expected either wide format (columns like 'namespace.key') "
                        "or long format (columns: handle, namespace, key, value).",
                "columns_found": headers,
            }

    result["file"] = os.path.basename(args.metafield_csv)
    if product_type_map:
        result["product_csv_joined"] = True
        result["product_types_found"] = len(set(product_type_map.values()))
        result["products_found"] = len(product_type_map)
    else:
        result["product_csv_joined"] = False

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    mf_count = len(result.get("metafields", {}))
    print(f"Summary written to {args.output}")
    print(f"  Format: {result.get('format', 'unknown')}")
    print(f"  Rows: {result.get('total_rows', 0)}")
    print(f"  Metafields: {mf_count}")
    print(f"  Product CSV joined: {result.get('product_csv_joined', False)}")


if __name__ == "__main__":
    main()

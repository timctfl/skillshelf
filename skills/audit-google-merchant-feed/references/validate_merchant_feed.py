#!/usr/bin/env python3
"""Validate a Google Merchant Center XML feed, optionally cross-referencing
against a Shopify product export CSV. Outputs structured JSON that an LLM
reads and explains.

Usage:
    python validate_merchant_feed.py feed.xml [shopify.csv]

Exit codes:
    0  No issues found
    1  One or more issues found
    2  Input error (bad file path, unparseable XML, etc.)
"""

import argparse
import csv
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

NS = {"g": "http://base.google.com/ns/1.0"}

REQUIRED_ATTRS = [
    "id", "title", "description", "link", "image_link",
    "price", "availability", "brand",
]

APPAREL_REQUIRED_ATTRS = ["color", "size", "gender", "age_group"]

VALID_AVAILABILITY = {"in_stock", "out_of_stock", "preorder", "backorder"}
VALID_GENDER = {"male", "female", "unisex"}
VALID_AGE_GROUP = {"adult", "kids", "toddler", "infant", "newborn"}
VALID_CONDITION = {"new", "refurbished", "used"}

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "as", "be", "was", "are",
    "that", "this", "its", "not", "your", "you", "our", "we", "all",
}

PROMO_PATTERNS = [
    r"\bbuy\s+now\b", r"\bfree\s+shipping\b", r"\bbest\s+price\b",
    r"\blimited\s+time\b", r"\border\s+now\b", r"\bsale\b",
    r"\bclearance\b", r"\bdiscount\b", r"\bcheap\b",
]


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_feed(xml_path: str) -> list[dict]:
    """Parse a Google Merchant Center XML feed into a list of item dicts.
    Each dict has keys like 'id', 'title', etc. (without the g: prefix).
    """
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as exc:
        print(f"Error: cannot parse XML feed: {exc}", file=sys.stderr)
        sys.exit(2)

    root = tree.getroot()
    items = []
    for item_el in root.iter("item"):
        item = {}
        for child in item_el:
            tag = child.tag
            if tag.startswith("{"):
                tag = tag.split("}")[-1]
            text = child.text or ""
            if tag == "description":
                text = child.text or ""
            if tag in item:
                if tag == "additional_image_link":
                    existing = item[tag]
                    if isinstance(existing, list):
                        existing.append(text)
                    else:
                        item[tag] = [existing, text]
                    continue
            item[tag] = text
        items.append(item)
    return items


def parse_shopify_csv(csv_path: str) -> list[dict]:
    """Parse a Shopify product export CSV, carrying product-level fields
    forward to sparse variant rows.
    """
    PRODUCT_LEVEL_COLS = {
        "Handle", "Title", "Body (HTML)", "Vendor", "Product Category",
        "Type", "Tags", "Published", "Gift Card", "SEO Title",
        "SEO Description", "Google Shopping / Google Product Category",
        "Google Shopping / Gender", "Google Shopping / Age Group",
        "Google Shopping / MPN", "Google Shopping / AdWords Grouping",
        "Google Shopping / AdWords Labels", "Google Shopping / Condition",
        "Google Shopping / Custom Product",
        "Google Shopping / Custom Label 0",
        "Google Shopping / Custom Label 1",
        "Google Shopping / Custom Label 2",
        "Google Shopping / Custom Label 3",
        "Google Shopping / Custom Label 4",
        "Status",
    }

    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = []
            last_product = {}
            for row in reader:
                handle = row.get("Handle", "").strip()
                if not handle:
                    continue

                is_first_for_handle = (row.get("Title", "").strip() != "")

                if is_first_for_handle:
                    last_product = {
                        k: v for k, v in row.items() if k in PRODUCT_LEVEL_COLS
                    }
                else:
                    for col in PRODUCT_LEVEL_COLS:
                        if col in row and not row[col].strip():
                            row[col] = last_product.get(col, "")

                rows.append(row)
            return rows
    except FileNotFoundError:
        print(f"Error: Shopify CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:
        print(f"Error reading Shopify CSV: {exc}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities, return plain text."""
    text = re.sub(r"<[^>]*>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_apparel_category(category: str) -> bool:
    """Return True if the Google product category falls under Apparel & Accessories."""
    if not category:
        return False
    cat = html.unescape(category).strip()
    return cat.startswith("Apparel & Accessories") or cat.startswith("Apparel &amp; Accessories")


def count_category_levels(category: str) -> int:
    """Count the depth levels of a Google product category path."""
    if not category:
        return 0
    cat = html.unescape(category).strip()
    return len([part for part in cat.split(">") if part.strip()])


def get_attr(item: dict, attr: str) -> str:
    """Get a feed attribute value, stripped."""
    return (item.get(attr) or "").strip()


# ---------------------------------------------------------------------------
# Rules: Disapproved
# ---------------------------------------------------------------------------

def check_d01_missing_required(item: dict) -> list[dict]:
    """D01: Missing required attribute."""
    issues = []
    for attr in REQUIRED_ATTRS:
        val = get_attr(item, attr)
        if not val:
            issues.append({
                "rule": "D01",
                "severity": "disapproved",
                "attribute": attr,
                "message": f"Required attribute g:{attr} is missing or empty.",
            })
    return issues


def check_d02_missing_apparel_attrs(item: dict) -> list[dict]:
    """D02: Missing required apparel attribute."""
    category = get_attr(item, "google_product_category")
    if not is_apparel_category(category):
        return []

    issues = []
    for attr in APPAREL_REQUIRED_ATTRS:
        val = get_attr(item, attr)
        if not val:
            issues.append({
                "rule": "D02",
                "severity": "disapproved",
                "attribute": attr,
                "message": (
                    f"Apparel item is missing required attribute g:{attr}. "
                    f"Category: {html.unescape(category)}"
                ),
            })
    return issues


def check_d03_duplicate_ids(items: list[dict]) -> list[dict]:
    """D03: Duplicate item ID (feed-level check)."""
    id_counts = Counter(get_attr(item, "id") for item in items)
    duplicates = {k: v for k, v in id_counts.items() if v > 1 and k}
    issues = []
    for item_id, count in duplicates.items():
        issues.append({
            "rule": "D03",
            "severity": "disapproved",
            "item_id": item_id,
            "attribute": "id",
            "message": f"g:id '{item_id}' appears {count} times in the feed.",
        })
    return issues


def check_d04_malformed_html(item: dict) -> list[dict]:
    """D04: Malformed HTML in description."""
    desc = get_attr(item, "description")
    if not desc:
        return []

    issues = []
    unclosed = []
    for m in re.finditer(r"</([a-zA-Z]+)", desc):
        end = m.end()
        if end >= len(desc) or desc[end] != ">":
            unclosed.append(m.group())
    if unclosed:
        issues.append({
            "rule": "D04",
            "severity": "disapproved",
            "attribute": "description",
            "message": f"Description contains unclosed HTML tag(s): {', '.join(unclosed[:3])}",
        })

    nested_p = re.findall(r"<p[^>]*>[^<]*<p[^>]*>", desc)
    if nested_p:
        issues.append({
            "rule": "D04",
            "severity": "disapproved",
            "attribute": "description",
            "message": "Description contains nested <p> tags without closing the first.",
        })

    double_encoded = re.findall(r"&amp;(amp|lt|gt|quot|apos);", desc)
    if double_encoded:
        issues.append({
            "rule": "D04",
            "severity": "disapproved",
            "attribute": "description",
            "message": "Description contains double-encoded HTML entities.",
        })

    return issues


def check_d05_prohibited_content(item: dict) -> list[dict]:
    """D05: Prohibited content in title or description."""
    issues = []

    for field_name in ("title", "description"):
        text = get_attr(item, field_name)
        if not text:
            continue

        plain = strip_html(text) if field_name == "description" else text

        for pattern in PROMO_PATTERNS:
            if re.search(pattern, plain, re.IGNORECASE):
                issues.append({
                    "rule": "D05",
                    "severity": "disapproved",
                    "attribute": field_name,
                    "message": f"Promotional text detected in {field_name}: matches '{pattern}'.",
                })
                break

        if field_name == "title":
            words = plain.split()
            if words:
                upper_count = sum(1 for w in words if w.isupper() and len(w) > 1)
                if upper_count / len(words) > 0.5:
                    issues.append({
                        "rule": "D05",
                        "severity": "disapproved",
                        "attribute": "title",
                        "message": "Title has excessive capitalization (>50% uppercase words).",
                    })

    return issues


# ---------------------------------------------------------------------------
# Rules: Demoted (Warnings)
# ---------------------------------------------------------------------------

def check_w01_brand_not_in_title(item: dict) -> list[dict]:
    """W01: Title does not include brand name."""
    brand = get_attr(item, "brand")
    title = get_attr(item, "title")
    if not brand or not title:
        return []
    if brand.lower() not in title.lower():
        return [{
            "rule": "W01",
            "severity": "demoted",
            "attribute": "title",
            "message": f"Brand '{brand}' not found in title '{title}'.",
        }]
    return []


def check_w02_short_description(item: dict) -> list[dict]:
    """W02: Description too short."""
    desc = get_attr(item, "description")
    if not desc:
        return []
    plain = strip_html(desc)
    if len(plain) < 150:
        return [{
            "rule": "W02",
            "severity": "demoted",
            "attribute": "description",
            "message": f"Description is only {len(plain)} characters (plain text). Recommended minimum: 150.",
        }]
    return []


def check_w03_broad_category(item: dict) -> list[dict]:
    """W03: Google product category too broad."""
    category = get_attr(item, "google_product_category")
    if not category:
        return []
    levels = count_category_levels(category)
    if levels < 3:
        return [{
            "rule": "W03",
            "severity": "demoted",
            "attribute": "google_product_category",
            "message": (
                f"Category has only {levels} level(s): '{html.unescape(category)}'. "
                f"Recommended: at least 3 levels for better targeting."
            ),
        }]
    return []


def check_w04_inconsistent_sizes(items: list[dict]) -> list[dict]:
    """W04: Inconsistent size naming within an item group (feed-level)."""
    groups = defaultdict(list)
    for item in items:
        group_id = get_attr(item, "item_group_id")
        size = get_attr(item, "size")
        if group_id and size:
            groups[group_id].append(size)

    issues = []
    for group_id, sizes in groups.items():
        has_abbrev = any(len(s) <= 3 for s in sizes)
        has_full = any(len(s) > 3 for s in sizes)
        if has_abbrev and has_full:
            issues.append({
                "rule": "W04",
                "severity": "demoted",
                "item_group_id": group_id,
                "attribute": "size",
                "message": (
                    f"Item group '{group_id}' mixes abbreviated and full size names: "
                    f"{sorted(set(sizes))}"
                ),
            })
    return issues


def check_w05_inconsistent_color_casing(items: list[dict]) -> list[dict]:
    """W05: Inconsistent color casing within an item group (feed-level)."""
    groups = defaultdict(list)
    for item in items:
        group_id = get_attr(item, "item_group_id")
        color = get_attr(item, "color")
        if group_id and color:
            groups[group_id].append(color)

    issues = []
    for group_id, colors in groups.items():
        seen_lower = {}
        inconsistent = False
        for c in colors:
            lower = c.lower()
            if lower in seen_lower and seen_lower[lower] != c:
                inconsistent = True
                break
            seen_lower[lower] = c
        if inconsistent:
            issues.append({
                "rule": "W05",
                "severity": "demoted",
                "item_group_id": group_id,
                "attribute": "color",
                "message": (
                    f"Item group '{group_id}' has inconsistent color casing: "
                    f"{sorted(set(colors))}"
                ),
            })
    return issues


def check_w07_keyword_stuffing(item: dict) -> list[dict]:
    """W07: Keyword stuffing in title or description."""
    issues = []

    title = get_attr(item, "title")
    if title:
        words = [w.lower() for w in re.findall(r"\w+", title) if w.lower() not in STOP_WORDS]
        word_counts = Counter(words)
        for word, count in word_counts.items():
            if count > 3 and len(word) > 2:
                issues.append({
                    "rule": "W07",
                    "severity": "demoted",
                    "attribute": "title",
                    "message": f"Word '{word}' appears {count} times in title. Possible keyword stuffing.",
                })
                break

    desc = get_attr(item, "description")
    if desc:
        plain = strip_html(desc)
        words = [w.lower() for w in re.findall(r"\w+", plain) if w.lower() not in STOP_WORDS]
        if len(words) >= 20:
            word_counts = Counter(words)
            per_100 = {w: (c / len(words)) * 100 for w, c in word_counts.items()}
            for word, density in per_100.items():
                if density > 5 and word_counts[word] > 5 and len(word) > 2:
                    issues.append({
                        "rule": "W07",
                        "severity": "demoted",
                        "attribute": "description",
                        "message": (
                            f"Word '{word}' has {density:.1f}% density in description "
                            f"({word_counts[word]} occurrences in {len(words)} words). "
                            f"Possible keyword stuffing."
                        ),
                    })
                    break

    return issues


def check_w08_missing_gtin(item: dict) -> list[dict]:
    """W08: Missing GTIN for products that likely need one."""
    gtin = get_attr(item, "gtin")
    brand = get_attr(item, "brand")
    if gtin or not brand:
        return []
    return [{
        "rule": "W08",
        "severity": "demoted",
        "attribute": "gtin",
        "message": f"Brand '{brand}' is set but no GTIN is provided. Products from known brands should include a GTIN.",
    }]


# ---------------------------------------------------------------------------
# Rules: Advisory
# ---------------------------------------------------------------------------

def check_a02_no_additional_images(item: dict) -> list[dict]:
    """A02: No additional_image_link."""
    image = get_attr(item, "image_link")
    additional = item.get("additional_image_link")
    if image and not additional:
        return [{
            "rule": "A02",
            "severity": "advisory",
            "attribute": "additional_image_link",
            "message": "Item has a primary image but no additional images. Google allows up to 10 additional images.",
        }]
    return []


def check_a05_no_product_highlight(item: dict) -> list[dict]:
    """A05: Missing product_highlight."""
    if not get_attr(item, "product_highlight"):
        return [{
            "rule": "A05",
            "severity": "advisory",
            "attribute": "product_highlight",
            "message": "No product highlights provided. Up to 10 bullet points can appear in Shopping results.",
        }]
    return []


def check_a06_variant_title_no_options(item: dict) -> list[dict]:
    """A06: Variant title missing option values."""
    title = get_attr(item, "title")
    group_id = get_attr(item, "item_group_id")
    color = get_attr(item, "color")
    size = get_attr(item, "size")

    if not group_id or not title:
        return []

    missing = []
    if color and color.lower() not in title.lower():
        missing.append(f"color '{color}'")
    if size and size.lower() not in title.lower():
        missing.append(f"size '{size}'")

    if missing:
        return [{
            "rule": "A06",
            "severity": "advisory",
            "attribute": "title",
            "message": f"Variant title does not include {', '.join(missing)}. Title: '{title}'.",
        }]
    return []


def check_a07_shipping_weight(items: list[dict]) -> list[dict]:
    """A07: Missing or inconsistent shipping_weight units (feed-level)."""
    units_found = set()
    missing_count = 0
    for item in items:
        weight = get_attr(item, "shipping_weight")
        if not weight:
            missing_count += 1
        else:
            match = re.search(r"(lb|kg|oz|g)\b", weight, re.IGNORECASE)
            if match:
                units_found.add(match.group(1).lower())

    issues = []
    if missing_count > 0:
        issues.append({
            "rule": "A07",
            "severity": "advisory",
            "attribute": "shipping_weight",
            "message": f"{missing_count} item(s) are missing g:shipping_weight.",
        })
    if len(units_found) > 1:
        issues.append({
            "rule": "A07",
            "severity": "advisory",
            "attribute": "shipping_weight",
            "message": f"Feed uses mixed weight units: {sorted(units_found)}. Standardize to one unit.",
        })
    return issues


# ---------------------------------------------------------------------------
# Rules: Duplicate content detection (feed-level)
# ---------------------------------------------------------------------------

def check_duplicate_items(items: list[dict]) -> list[dict]:
    """Detect items that are likely duplicates (same title + same item_group_id + same color/size)."""
    seen = {}
    issues = []
    for item in items:
        title = get_attr(item, "title")
        group_id = get_attr(item, "item_group_id")
        color = get_attr(item, "color")
        size = get_attr(item, "size")
        item_id = get_attr(item, "id")

        key = (title.lower(), group_id, color.lower(), size.lower())
        if key in seen:
            issues.append({
                "rule": "D03",
                "severity": "disapproved",
                "item_id": item_id,
                "duplicate_of": seen[key],
                "attribute": "id",
                "message": (
                    f"Item '{item_id}' appears to be a duplicate of '{seen[key]}'. "
                    f"Same title, item group, color, and size."
                ),
            })
        else:
            seen[key] = item_id
    return issues


# ---------------------------------------------------------------------------
# Cross-reference rules (require both XML and CSV)
# ---------------------------------------------------------------------------

def build_shopify_lookup(shopify_rows: list[dict]) -> dict:
    """Build a lookup keyed by Variant SKU for cross-referencing."""
    lookup = {}
    for row in shopify_rows:
        sku = (row.get("Variant SKU") or "").strip()
        if sku:
            lookup[sku] = row
    return lookup


def find_sku_in_feed_id(item_id: str, shopify_lookup: dict) -> str | None:
    """Try to match a feed item ID to a Shopify SKU.
    Feed IDs may be raw SKUs, or shopify_{country}_{product_id}_{variant_id} format.
    """
    if item_id in shopify_lookup:
        return item_id
    return None


def cross_reference(items: list[dict], shopify_rows: list[dict]) -> list[dict]:
    """Run cross-reference rules between feed items and Shopify CSV rows."""
    shopify_lookup = build_shopify_lookup(shopify_rows)
    issues = []

    feed_mpns = {}
    for item in items:
        mpn = get_attr(item, "mpn")
        if mpn:
            feed_mpns[mpn] = item

    shopify_skus = set()
    for row in shopify_rows:
        sku = (row.get("Variant SKU") or "").strip()
        if sku:
            shopify_skus.add(sku)

    for item in items:
        item_id = get_attr(item, "id")
        mpn = get_attr(item, "mpn")

        shopify_row = None
        if mpn and mpn in shopify_lookup:
            shopify_row = shopify_lookup[mpn]
        elif item_id in shopify_lookup:
            shopify_row = shopify_lookup[item_id]

        if shopify_row is None:
            continue

        issues.extend(_check_a01_sale_price(item, shopify_row))
        issues.extend(_check_a03_gtin_sync(item, shopify_row))
        issues.extend(_check_x01_price_mismatch(item, shopify_row))
        issues.extend(_check_x02_title_mismatch(item, shopify_row))

    shopify_active_skus = set()
    for row in shopify_rows:
        sku = (row.get("Variant SKU") or "").strip()
        published = (row.get("Published") or "").strip().upper()
        status = (row.get("Status") or "").strip().lower()
        if sku and published == "TRUE" and status == "active":
            shopify_active_skus.add(sku)

    feed_skus = set()
    for item in items:
        mpn = get_attr(item, "mpn")
        if mpn:
            feed_skus.add(mpn)
        item_id = get_attr(item, "id")
        if item_id:
            feed_skus.add(item_id)

    missing_from_feed = shopify_active_skus - feed_skus
    for sku in sorted(missing_from_feed):
        row = shopify_lookup.get(sku, {})
        title = (row.get("Title") or "").strip()
        has_required = all([
            (row.get("Variant Price") or "").strip(),
            (row.get("Image Src") or row.get("Variant Image") or "").strip(),
            title,
        ])
        if has_required:
            issues.append({
                "rule": "X03",
                "severity": "demoted",
                "shopify_sku": sku,
                "attribute": "id",
                "message": (
                    f"Active Shopify product (SKU: {sku}, Title: {title or 'unknown'}) "
                    f"not found in the feed."
                ),
            })

    return issues


def _check_a01_sale_price(item: dict, shopify_row: dict) -> list[dict]:
    """A01: No sale_price despite Shopify Compare At Price."""
    compare_at = (shopify_row.get("Variant Compare At Price") or "").strip()
    variant_price = (shopify_row.get("Variant Price") or "").strip()
    sale_price = get_attr(item, "sale_price")

    if not compare_at or not variant_price:
        return []

    try:
        compare_val = float(compare_at)
        price_val = float(variant_price)
    except ValueError:
        return []

    if compare_val > price_val and not sale_price:
        return [{
            "rule": "A01",
            "severity": "advisory",
            "attribute": "sale_price",
            "message": (
                f"Shopify has Compare At Price ${compare_val:.2f} > Variant Price ${price_val:.2f}, "
                f"but feed has no g:sale_price. Strikethrough pricing is not showing in Google Shopping."
            ),
        }]
    return []


def _check_a03_gtin_sync(item: dict, shopify_row: dict) -> list[dict]:
    """A03: GTIN present in feed but missing from Shopify."""
    feed_gtin = get_attr(item, "gtin")
    shopify_barcode = (shopify_row.get("Variant Barcode") or "").strip()

    if feed_gtin and not shopify_barcode:
        return [{
            "rule": "A03",
            "severity": "advisory",
            "attribute": "gtin",
            "message": (
                f"Feed has GTIN '{feed_gtin}' but Shopify Variant Barcode is empty. "
                f"Backfill the barcode in Shopify to avoid losing the GTIN on feed regeneration."
            ),
        }]
    return []


def _check_x01_price_mismatch(item: dict, shopify_row: dict) -> list[dict]:
    """X01: Price mismatch between Shopify and feed."""
    feed_price_str = get_attr(item, "price")
    variant_price = (shopify_row.get("Variant Price") or "").strip()
    compare_at = (shopify_row.get("Variant Compare At Price") or "").strip()

    if not feed_price_str or not variant_price:
        return []

    feed_price_match = re.match(r"([\d.]+)", feed_price_str)
    if not feed_price_match:
        return []
    feed_price = float(feed_price_match.group(1))

    try:
        shopify_price = float(variant_price)
    except ValueError:
        return []

    expected_feed_price = shopify_price
    if compare_at:
        try:
            compare_val = float(compare_at)
            if compare_val > shopify_price:
                expected_feed_price = compare_val
        except ValueError:
            pass

    if abs(feed_price - expected_feed_price) > 0.01 and abs(feed_price - shopify_price) > 0.01:
        compare_display = "N/A"
        if compare_at:
            try:
                compare_display = f"${float(compare_at):.2f}"
            except ValueError:
                compare_display = compare_at
        return [{
            "rule": "X01",
            "severity": "disapproved",
            "attribute": "price",
            "message": (
                f"Feed price {feed_price_str} does not match Shopify Variant Price "
                f"${shopify_price:.2f} (Compare At: {compare_display})."
            ),
        }]
    return []


def _check_x02_title_mismatch(item: dict, shopify_row: dict) -> list[dict]:
    """X02: Title mismatch between Shopify and feed."""
    feed_title = get_attr(item, "title")
    shopify_title = (shopify_row.get("Title") or "").strip()

    if not feed_title or not shopify_title:
        return []

    if not feed_title.lower().startswith(shopify_title.lower()):
        if shopify_title.lower() not in feed_title.lower():
            return [{
                "rule": "X02",
                "severity": "demoted",
                "attribute": "title",
                "message": (
                    f"Feed title '{feed_title}' does not contain Shopify title '{shopify_title}'."
                ),
            }]
    return []


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_per_item_rules(item: dict) -> list[dict]:
    """Run all per-item rules and return issues for this item."""
    checks = [
        check_d01_missing_required,
        check_d02_missing_apparel_attrs,
        check_d04_malformed_html,
        check_d05_prohibited_content,
        check_w01_brand_not_in_title,
        check_w02_short_description,
        check_w03_broad_category,
        check_w07_keyword_stuffing,
        check_w08_missing_gtin,
        check_a02_no_additional_images,
        check_a05_no_product_highlight,
        check_a06_variant_title_no_options,
    ]

    all_issues = []
    d01_attrs = set()

    for check in checks:
        results = check(item)
        for issue in results:
            if issue["rule"] == "D01":
                d01_attrs.add(issue["attribute"])
            all_issues.append(issue)

    filtered = []
    for issue in all_issues:
        if issue["rule"] != "D01" and issue.get("attribute") in d01_attrs:
            continue
        filtered.append(issue)

    return filtered


def run_feed_level_rules(items: list[dict]) -> list[dict]:
    """Run all feed-level rules."""
    issues = []
    issues.extend(check_d03_duplicate_ids(items))
    issues.extend(check_duplicate_items(items))
    issues.extend(check_w04_inconsistent_sizes(items))
    issues.extend(check_w05_inconsistent_color_casing(items))
    issues.extend(check_a07_shipping_weight(items))
    return issues


def build_output(items: list[dict], shopify_rows: list[dict] | None) -> dict:
    """Run all rules and build the final JSON output."""
    per_item_issues = {}
    for item in items:
        item_id = get_attr(item, "id") or f"unknown-{items.index(item)}"
        issues = run_per_item_rules(item)
        if issues:
            per_item_issues[item_id] = {
                "title": get_attr(item, "title"),
                "issues": issues,
            }

    feed_level_issues = run_feed_level_rules(items)

    cross_ref_issues = []
    if shopify_rows is not None:
        cross_ref_issues = cross_reference(items, shopify_rows)

    all_issues = []
    for item_data in per_item_issues.values():
        all_issues.extend(item_data["issues"])
    all_issues.extend(feed_level_issues)
    all_issues.extend(cross_ref_issues)

    severity_counts = Counter(i["severity"] for i in all_issues)
    rule_counts = Counter(i["rule"] for i in all_issues)

    return {
        "summary": {
            "total_items": len(items),
            "items_with_issues": len(per_item_issues),
            "total_issues": len(all_issues),
            "shopify_csv_provided": shopify_rows is not None,
            "shopify_rows": len(shopify_rows) if shopify_rows is not None else 0,
            "by_severity": {
                "disapproved": severity_counts.get("disapproved", 0),
                "demoted": severity_counts.get("demoted", 0),
                "advisory": severity_counts.get("advisory", 0),
            },
            "by_rule": dict(sorted(rule_counts.items())),
        },
        "per_item_issues": per_item_issues,
        "feed_level_issues": feed_level_issues,
        "cross_reference_issues": cross_ref_issues,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate a Google Merchant Center XML feed against Shopify data."
    )
    parser.add_argument("feed", help="Path to Google Merchant Center XML feed")
    parser.add_argument("shopify_csv", nargs="?", default=None,
                        help="Path to Shopify product export CSV (optional)")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output")
    args = parser.parse_args()

    feed_path = Path(args.feed)
    if not feed_path.exists():
        print(f"Error: feed file not found: {args.feed}", file=sys.stderr)
        sys.exit(2)

    items = parse_feed(str(feed_path))
    if not items:
        print("Error: no items found in the feed.", file=sys.stderr)
        sys.exit(2)

    shopify_rows = None
    if args.shopify_csv:
        csv_path = Path(args.shopify_csv)
        if not csv_path.exists():
            print(f"Error: Shopify CSV not found: {args.shopify_csv}", file=sys.stderr)
            sys.exit(2)
        shopify_rows = parse_shopify_csv(str(csv_path))

    output = build_output(items, shopify_rows)

    indent = 2 if args.pretty else None
    print(json.dumps(output, indent=indent, ensure_ascii=False))

    if output["summary"]["total_issues"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

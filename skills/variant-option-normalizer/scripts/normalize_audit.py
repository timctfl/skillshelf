#!/usr/bin/env python3
"""Audit a Shopify product CSV for variant option inconsistencies.

Outputs structured JSON to stdout. Run from the skill directory:
    python3 scripts/normalize_audit.py <csv_path> [--assets-dir assets/]

Exit codes:
    0 - Audit completed (issues may or may not exist)
    1 - Fatal error (file not found, parse failure)
"""

import argparse
import csv
import html
import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "1.0.0"

# Shopify caps option values at 255 characters
SHOPIFY_OPTION_VALUE_MAX_LENGTH = 255

# Unicode whitespace beyond standard ASCII space/tab/newline
ABNORMAL_WHITESPACE = {
    "\u00a0": "non-breaking space",
    "\u200b": "zero-width space",
    "\u200c": "zero-width non-joiner",
    "\u200d": "zero-width joiner",
    "\ufeff": "byte order mark",
    "\u2003": "em space",
    "\u2002": "en space",
    "\u2009": "thin space",
    "\u200a": "hair space",
    "\u3000": "ideographic space",
    "\u2007": "figure space",
    "\u2008": "punctuation space",
    "\u205f": "medium mathematical space",
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class VariantRow:
    row_number: int
    handle: str
    title: str
    option1_name: str
    option1_value: str
    option2_name: str
    option2_value: str
    option3_name: str
    option3_value: str
    variant_sku: str
    variant_price: str
    variant_inventory_qty: str
    variant_image: str
    raw_row: dict


@dataclass
class Product:
    handle: str
    title: str
    rows: list[VariantRow] = field(default_factory=list)


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------

def detect_encoding_and_bom(file_path: Path) -> tuple[str, bool]:
    """Check for UTF-8 BOM. Returns (encoding, bom_detected)."""
    with open(file_path, "rb") as f:
        raw = f.read(4)
    if raw[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig", True
    return "utf-8-sig", False  # utf-8-sig strips BOM if present, safe for both


def parse_csv(file_path: Path) -> tuple[list[Product], list[str], dict]:
    """Parse a Shopify product CSV into Product groups.

    Returns (products, column_names, metadata_dict).
    """
    encoding, bom_detected = detect_encoding_and_bom(file_path)

    try:
        with open(file_path, newline="", encoding=encoding) as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []
            rows_raw = list(reader)
    except UnicodeDecodeError:
        # Fall back to latin-1 which accepts any byte
        with open(file_path, newline="", encoding="latin-1") as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames or []
            rows_raw = list(reader)
        encoding = "latin-1"

    if not columns:
        print("Fatal: CSV has no columns.", file=sys.stderr)
        sys.exit(1)

    def get(row: dict, key: str) -> str:
        return row.get(key, "") or ""

    products_map: dict[str, Product] = {}
    product_order: list[str] = []
    total_variants = 0
    last_handle = ""

    for idx, row in enumerate(rows_raw):
        row_number = idx + 2  # 1-based, header is row 1
        handle = get(row, "Handle").strip()

        # Variant-only rows inherit the handle from the previous product row
        if not handle:
            handle = last_handle
        else:
            last_handle = handle

        if not handle:
            continue  # skip rows with no handle at all

        title = get(row, "Title")

        vr = VariantRow(
            row_number=row_number,
            handle=handle,
            title=title,
            option1_name=get(row, "Option1 Name"),
            option1_value=get(row, "Option1 Value"),
            option2_name=get(row, "Option2 Name"),
            option2_value=get(row, "Option2 Value"),
            option3_name=get(row, "Option3 Name"),
            option3_value=get(row, "Option3 Value"),
            variant_sku=get(row, "Variant SKU"),
            variant_price=get(row, "Variant Price"),
            variant_inventory_qty=get(row, "Variant Inventory Qty"),
            variant_image=get(row, "Variant Image"),
            raw_row=row,
        )

        if handle not in products_map:
            products_map[handle] = Product(handle=handle, title=title)
            product_order.append(handle)
        elif title and not products_map[handle].title:
            products_map[handle].title = title

        products_map[handle].rows.append(vr)
        total_variants += 1

    products = [products_map[h] for h in product_order]

    metadata = {
        "source_file": file_path.name,
        "products_scanned": len(products),
        "variants_scanned": total_variants,
        "columns_present": columns,
        "has_variant_image_column": "Variant Image" in columns,
        "has_option3": "Option3 Name" in columns,
        "csv_encoding": encoding,
        "bom_detected": bom_detected,
        "script_version": SCRIPT_VERSION,
        "ran_at": datetime.now(timezone.utc).isoformat(),
    }

    return products, columns, metadata


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def option_fields(row: VariantRow) -> list[tuple[str, str, str]]:
    """Return list of (field_label, name, value) for non-empty option slots."""
    results = []
    for i, (n, v) in enumerate([
        (row.option1_name, row.option1_value),
        (row.option2_name, row.option2_value),
        (row.option3_name, row.option3_value),
    ], start=1):
        if n or v:
            results.append((f"Option{i}", n, v))
    return results


def describe_whitespace(char: str) -> str:
    """Human-readable name for a whitespace character."""
    if char in ABNORMAL_WHITESPACE:
        return ABNORMAL_WHITESPACE[char]
    if char == " ":
        return "space"
    if char == "\t":
        return "tab"
    if char == "\n":
        return "newline"
    if char == "\r":
        return "carriage return"
    cp = f"U+{ord(char):04X}"
    if unicodedata.category(char).startswith("Z"):
        return f"unicode whitespace ({cp})"
    return f"invisible char ({cp})"


def is_default_title_product(product: Product) -> bool:
    """Detect Shopify default single-variant products."""
    if len(product.rows) != 1:
        return False
    r = product.rows[0]
    return (r.option1_name.strip().lower() == "title"
            and r.option1_value.strip().lower() == "default title")


def slugify(title: str) -> str:
    """Replicate Shopify's handle generation from a product title."""
    # Decode HTML entities first
    s = html.unescape(title)
    # Normalize unicode
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    # Remove apostrophes (Shopify drops them)
    s = s.replace("'", "").replace("\u2019", "")
    # Replace non-alphanumeric with hyphens
    s = re.sub(r"[^a-z0-9]+", "-", s)
    # Collapse consecutive hyphens, strip leading/trailing
    s = re.sub(r"-{2,}", "-", s)
    s = s.strip("-")
    return s


# ---------------------------------------------------------------------------
# Check 1: Whitespace issues
# ---------------------------------------------------------------------------

def check_whitespace(products: list[Product]) -> list[dict]:
    issues: list[dict] = []

    for product in products:
        for row in product.rows:
            for field_label, name, value in option_fields(row):
                # Check both the name and value cells
                for cell_type, cell_value in [("Name", name), ("Value", value)]:
                    if not cell_value:
                        continue

                    field_name = f"{field_label} {cell_type}"
                    trimmed = cell_value.strip()
                    chars_detail: list[dict] = []

                    # Leading whitespace
                    leading = ""
                    for ch in cell_value:
                        if ch != ch.strip() or ch in ABNORMAL_WHITESPACE:
                            leading += ch
                        else:
                            break
                    for ch in leading:
                        chars_detail.append({
                            "position": "leading",
                            "char": describe_whitespace(ch),
                            "codepoint": f"U+{ord(ch):04X}",
                        })

                    # Trailing whitespace
                    trailing = ""
                    for ch in reversed(cell_value):
                        if ch != ch.strip() or ch in ABNORMAL_WHITESPACE:
                            trailing = ch + trailing
                        else:
                            break
                    for ch in trailing:
                        chars_detail.append({
                            "position": "trailing",
                            "char": describe_whitespace(ch),
                            "codepoint": f"U+{ord(ch):04X}",
                        })

                    # Interior abnormal whitespace (non-breaking spaces, etc.)
                    interior = cell_value[len(leading):len(cell_value) - len(trailing)] if trailing else cell_value[len(leading):]
                    for pos, ch in enumerate(interior):
                        if ch in ABNORMAL_WHITESPACE:
                            chars_detail.append({
                                "position": "interior",
                                "char": describe_whitespace(ch),
                                "codepoint": f"U+{ord(ch):04X}",
                            })

                    if not chars_detail:
                        continue

                    # Determine whitespace type
                    has_leading = bool(leading)
                    has_trailing = bool(trailing)
                    has_interior = any(d["position"] == "interior" for d in chars_detail)

                    if has_interior and not has_leading and not has_trailing:
                        ws_type = "interior_abnormal"
                    elif has_leading and has_trailing:
                        ws_type = "both"
                    elif has_leading:
                        ws_type = "leading"
                    elif has_trailing:
                        ws_type = "trailing"
                    else:
                        ws_type = "interior_abnormal"

                    issues.append({
                        "row": row.row_number,
                        "handle": row.handle,
                        "field": field_name,
                        "original_value": cell_value,
                        "trimmed_value": trimmed,
                        "whitespace_type": ws_type,
                        "characters": chars_detail,
                    })

    return issues


# ---------------------------------------------------------------------------
# Check 2: Case inconsistencies
# ---------------------------------------------------------------------------

def check_case_inconsistencies(products: list[Product]) -> list[dict]:
    # Group values by (normalized option name, lowered+stripped value)
    # value_groups[key] = { original_value: { "count": N, "handles": set, "rows": list } }
    value_groups: dict[tuple[str, str], dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"count": 0, "handles": set(), "rows": []}))

    for product in products:
        if is_default_title_product(product):
            continue
        for row in product.rows:
            for field_label, name, value in option_fields(row):
                if not value:
                    continue
                stripped = value.strip()
                if not stripped:
                    continue
                key = (name.strip().lower(), stripped.lower())
                entry = value_groups[key][stripped]
                entry["count"] += 1
                entry["handles"].add(row.handle)
                entry["rows"].append(row.row_number)

    issues: list[dict] = []
    for (opt_name_lower, val_lower), variants_map in value_groups.items():
        if len(variants_map) < 2:
            continue  # No inconsistency

        # Find the option name as it appears most often
        opt_name_display = opt_name_lower  # fallback
        for product in products:
            for row in product.rows:
                for _, name, _ in option_fields(row):
                    if name.strip().lower() == opt_name_lower:
                        opt_name_display = name.strip()

        # Build variants list sorted by count descending
        variants_list = []
        for val, info in sorted(variants_map.items(), key=lambda x: -x[1]["count"]):
            variants_list.append({
                "value": val,
                "count": info["count"],
                "handles": sorted(info["handles"]),
                "rows": sorted(info["rows"]),
            })

        # Suggestion: most frequent wins, title case breaks ties
        top_count = variants_list[0]["count"]
        tied = [v for v in variants_list if v["count"] == top_count]
        if len(tied) == 1:
            suggested = tied[0]["value"]
            reason = f"Most frequent ({tied[0]['count']} occurrences)"
        else:
            # Title case preference among tied values
            title_cased = [v for v in tied if v["value"] == v["value"].title()]
            if title_cased:
                suggested = title_cased[0]["value"]
                reason = "Tied frequency, title case preferred"
            else:
                suggested = tied[0]["value"]
                reason = "Tied frequency, first encountered chosen"

        issues.append({
            "option_name": opt_name_display,
            "normalized_key": val_lower,
            "variants_found": variants_list,
            "suggested_canonical": suggested,
            "suggestion_reason": reason,
        })

    return issues


# ---------------------------------------------------------------------------
# Check 3: Duplicate variants
# ---------------------------------------------------------------------------

def check_duplicate_variants(products: list[Product]) -> list[dict]:
    issues: list[dict] = []

    for product in products:
        if is_default_title_product(product):
            continue

        combo_groups: dict[tuple, list[VariantRow]] = defaultdict(list)
        for row in product.rows:
            key = (
                row.option1_value.strip().lower(),
                row.option2_value.strip().lower(),
                row.option3_value.strip().lower(),
            )
            combo_groups[key].append(row)

        for combo_key, rows in combo_groups.items():
            if len(rows) < 2:
                continue

            # Build human-readable option combo string
            parts = []
            for val in combo_key:
                if val:
                    parts.append(val)
            option_combo = " / ".join(parts) if parts else "(empty)"

            skus = [r.variant_sku for r in rows]
            prices = [r.variant_price for r in rows]
            inventories = []
            for r in rows:
                try:
                    inventories.append(int(r.variant_inventory_qty))
                except (ValueError, TypeError):
                    inventories.append(None)

            unique_prices = set(p for p in prices if p)
            inv_values = [i for i in inventories if i is not None]
            unique_inv = set(inv_values) if inv_values else set()

            issues.append({
                "handle": product.handle,
                "option_combo": option_combo,
                "rows": [r.row_number for r in rows],
                "skus": skus,
                "prices_match": len(unique_prices) <= 1,
                "prices": list(unique_prices),
                "inventory_match": len(unique_inv) <= 1,
                "inventories": inv_values,
            })

    return issues


# ---------------------------------------------------------------------------
# Check 4: Missing variant images
# ---------------------------------------------------------------------------

def check_missing_variant_images(products: list[Product], columns: list[str]) -> list[dict]:
    if "Variant Image" not in columns:
        return []

    issues: list[dict] = []

    for product in products:
        if len(product.rows) < 2:
            continue  # Single-variant products: nothing to compare

        images = [(r, r.variant_image.strip()) for r in product.rows]
        with_image = sum(1 for _, img in images if img)
        without_image = sum(1 for _, img in images if not img)

        # Only flag if some variants have images and some do not
        if with_image == 0 or without_image == 0:
            continue

        for row, img in images:
            if img:
                continue
            # Build option values string
            parts = []
            if row.option1_value.strip():
                parts.append(row.option1_value.strip())
            if row.option2_value.strip():
                parts.append(row.option2_value.strip())
            if row.option3_value.strip():
                parts.append(row.option3_value.strip())

            issues.append({
                "handle": product.handle,
                "row": row.row_number,
                "sku": row.variant_sku,
                "option_values": " / ".join(parts),
                "siblings_with_images": with_image,
                "siblings_without_images": without_image,
            })

    return issues


# ---------------------------------------------------------------------------
# Check 5: Size sequence ordering
# ---------------------------------------------------------------------------

def load_size_config(assets_dir: Path | None) -> dict:
    """Load size alias config or return built-in defaults."""
    defaults = {
        "apparel_letter_order": ["XXS", "XS", "S", "M", "L", "XL", "XXL", "2XL", "3XL", "4XL", "5XL"],
        "aliases": {
            "extra small": "XS", "x-small": "XS", "small": "S", "sm": "S",
            "medium": "M", "med": "M", "large": "L", "lg": "L",
            "extra large": "XL", "x-large": "XL", "extra-large": "XL",
            "xx-large": "XXL", "2x-large": "2XL", "2xl": "2XL",
            "3x-large": "3XL", "3xl": "3XL", "one size": "OS", "o/s": "OS",
            "os": "OS", "onesize": "OS",
        },
        "size_option_names": ["size", "sizes", "dimension", "dimensions"],
    }
    if assets_dir:
        path = assets_dir / "size_aliases.json"
        if path.exists():
            try:
                with open(path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Could not load {path}: {e}", file=sys.stderr)
    return defaults


def detect_size_option(product: Product, size_option_names: list[str]) -> str | None:
    """Return which option slot (Option1, Option2, Option3) holds sizes, or None."""
    names_lower = set(n.lower() for n in size_option_names)
    for row in product.rows:
        if row.option1_name.strip().lower() in names_lower:
            return "Option1"
        if row.option2_name.strip().lower() in names_lower:
            return "Option2"
        if row.option3_name.strip().lower() in names_lower:
            return "Option3"
    return None


def get_size_value(row: VariantRow, option_slot: str) -> str:
    if option_slot == "Option1":
        return row.option1_value.strip()
    if option_slot == "Option2":
        return row.option2_value.strip()
    return row.option3_value.strip()


def resolve_size_canonical(value: str, aliases: dict) -> str:
    """Map a size value to its canonical form using the alias table."""
    lower = value.strip().lower()
    return aliases.get(lower, value.strip())


def detect_size_system(values: list[str], apparel_order: list[str]) -> str:
    """Determine if values are apparel letters, numeric, compound, or unknown."""
    apparel_set = set(s.upper() for s in apparel_order)
    canonical_values = [v.upper() for v in values]

    if all(v in apparel_set or v == "OS" for v in canonical_values):
        return "apparel_letter"

    # Check numeric (including decimals like shoe sizes)
    numeric_pattern = re.compile(r"^\d+(\.\d+)?$")
    if all(numeric_pattern.match(v) for v in values):
        return "numeric"

    # Check compound (waist x inseam)
    compound_pattern = re.compile(r"^\d+\s*[x/]\s*\d+$", re.IGNORECASE)
    if all(compound_pattern.match(v) for v in values):
        return "compound"

    return "unknown"


def sort_key_for_size(value: str, aliases: dict, apparel_order: list[str]) -> tuple:
    """Return a sort key for a size value."""
    canonical = resolve_size_canonical(value, aliases)
    upper = canonical.upper()

    # Check apparel ladder
    if upper in apparel_order:
        return (0, apparel_order.index(upper), 0)

    # Check numeric
    try:
        num = float(canonical)
        return (1, num, 0)
    except ValueError:
        pass

    # Check compound (waist x inseam)
    match = re.match(r"^(\d+)\s*[x/]\s*(\d+)$", canonical, re.IGNORECASE)
    if match:
        return (1, float(match.group(1)), float(match.group(2)))

    # Unknown: sort alphabetically at the end
    return (2, 0, 0)


def check_size_ordering(products: list[Product], size_config: dict) -> list[dict]:
    issues: list[dict] = []
    apparel_order = size_config.get("apparel_letter_order", [])
    aliases = size_config.get("aliases", {})
    size_names = size_config.get("size_option_names", [])

    for product in products:
        if is_default_title_product(product):
            continue

        option_slot = detect_size_option(product, size_names)
        if not option_slot:
            continue

        # Get unique size values in current row order
        seen = []
        for row in product.rows:
            val = get_size_value(row, option_slot)
            canonical = resolve_size_canonical(val, aliases)
            if canonical and canonical not in seen:
                seen.append(canonical)

        if len(seen) <= 1:
            continue  # Single size or OS: nothing to order

        size_system = detect_size_system(seen, apparel_order)

        expected = sorted(seen, key=lambda v: sort_key_for_size(v, aliases, apparel_order))

        if seen != expected:
            issues.append({
                "handle": product.handle,
                "size_option_field": f"{option_slot} Value",
                "current_order": seen,
                "expected_order": expected,
                "size_system": size_system,
            })

    return issues


# ---------------------------------------------------------------------------
# Check 6: Option value aliases
# ---------------------------------------------------------------------------

def load_alias_config(assets_dir: Path | None) -> dict:
    """Load option name aliases config or return defaults."""
    defaults = {
        "option_name_synonyms": [
            ["Color", "Colour"], ["Size", "Sizes", "Dimension", "Dimensions"],
            ["Material", "Fabric", "Composition"], ["Style", "Design"],
            ["Pattern", "Print"], ["Flavor", "Flavour"],
        ],
        "color_aliases": {
            "grey": ["gray"], "charcoal heather": ["charcoal"],
            "navy blue": ["navy"], "heather grey": ["heather gray"],
        },
    }
    if assets_dir:
        path = assets_dir / "option_name_aliases.json"
        if path.exists():
            try:
                with open(path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Could not load {path}: {e}", file=sys.stderr)
    return defaults


def check_option_value_aliases(products: list[Product], alias_config: dict, size_config: dict) -> list[dict]:
    issues: list[dict] = []

    # Build a bidirectional alias lookup from the color_aliases config
    known_pairs: dict[str, str] = {}
    color_aliases = alias_config.get("color_aliases", {})
    for canonical, variants in color_aliases.items():
        for v in variants:
            known_pairs[v.lower()] = canonical.lower()
            known_pairs[canonical.lower()] = v.lower()

    # Build size canonical lookup for detecting size aliases like "Extra Large" / "XL"
    size_aliases = size_config.get("aliases", {})
    size_option_names = set(n.lower() for n in size_config.get("size_option_names", []))

    # Collect all values per option name (lowered)
    # values_by_option[option_name_lower] = { stripped_value: { "handles": set, "rows": list, "original": str } }
    values_by_option: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"handles": set(), "rows": [], "original": ""}))

    for product in products:
        if is_default_title_product(product):
            continue
        for row in product.rows:
            for _, name, value in option_fields(row):
                if not name.strip() or not value.strip():
                    continue
                opt_lower = name.strip().lower()
                val_stripped = value.strip()
                entry = values_by_option[opt_lower][val_stripped.lower()]
                entry["handles"].add(row.handle)
                entry["rows"].append(row.row_number)
                if not entry["original"]:
                    entry["original"] = val_stripped

    # For each option name, check all value pairs
    for opt_name, values_map in values_by_option.items():
        value_keys = list(values_map.keys())

        checked_pairs: set[tuple[str, str]] = set()

        for i, val_a in enumerate(value_keys):
            for val_b in value_keys[i + 1:]:
                pair = tuple(sorted([val_a, val_b]))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)

                detection_method = None
                confidence = None
                suggested = None

                # Strategy 1: Known color alias map
                if val_a in known_pairs and known_pairs[val_a] == val_b:
                    detection_method = "known_alias_map"
                    confidence = "high"
                elif val_b in known_pairs and known_pairs[val_b] == val_a:
                    detection_method = "known_alias_map"
                    confidence = "high"

                # Strategy 2: Size alias map (two values resolve to the same canonical size)
                if not detection_method and opt_name in size_option_names:
                    canon_a = size_aliases.get(val_a, val_a).upper()
                    canon_b = size_aliases.get(val_b, val_b).upper()
                    if canon_a == canon_b and val_a != val_b:
                        detection_method = "known_alias_map"
                        confidence = "high"
                        # Suggest the shorter/standard form
                        suggested = canon_a

                # Strategy 3: Substring containment (shorter is contained in longer)
                if not detection_method:
                    if len(val_a) > 3 and len(val_b) > 3:
                        if val_a in val_b or val_b in val_a:
                            detection_method = "substring_match"
                            confidence = "medium"

                if not detection_method:
                    continue

                info_a = values_map[val_a]
                info_b = values_map[val_b]

                # Determine if they appear on the same product
                same_product = bool(info_a["handles"] & info_b["handles"])

                # Suggest the more frequent value as canonical (unless already set by size alias)
                if not suggested:
                    if len(info_a["rows"]) >= len(info_b["rows"]):
                        suggested = info_a["original"]
                    else:
                        suggested = info_b["original"]

                # Find a display name for the option
                opt_display = opt_name
                for product in products:
                    for row in product.rows:
                        for _, name, _ in option_fields(row):
                            if name.strip().lower() == opt_name:
                                opt_display = name.strip()
                                break

                issues.append({
                    "option_name": opt_display,
                    "values": [info_a["original"], info_b["original"]],
                    "detection_method": detection_method,
                    "confidence": confidence,
                    "suggested_canonical": suggested,
                    "same_product": same_product,
                    "handles": sorted(info_a["handles"] | info_b["handles"]),
                    "rows_per_value": {
                        info_a["original"]: sorted(info_a["rows"]),
                        info_b["original"]: sorted(info_b["rows"]),
                    },
                })

    return issues


# ---------------------------------------------------------------------------
# Check 7: Option name inconsistencies
# ---------------------------------------------------------------------------

def check_option_name_inconsistencies(products: list[Product], alias_config: dict) -> list[dict]:
    # Build synonym lookup: lowered name -> group index
    synonym_groups = alias_config.get("option_name_synonyms", [])
    name_to_group: dict[str, int] = {}
    for idx, group in enumerate(synonym_groups):
        for name in group:
            name_to_group[name.lower()] = idx

    # Collect all option names and which products use them
    # name_usage[original_name] = set of handles
    name_usage: dict[str, set[str]] = defaultdict(set)

    for product in products:
        if is_default_title_product(product):
            continue
        for row in product.rows:
            for _, name, _ in option_fields(row):
                stripped = name.strip()
                if stripped:
                    name_usage[stripped].add(product.handle)

    # Group names by synonym group or by lowered form
    groups_found: dict[Any, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    for name, handles in name_usage.items():
        lower = name.lower()
        group_key = name_to_group.get(lower, f"_solo_{lower}")
        groups_found[group_key][name] |= handles

    issues: list[dict] = []
    for group_key, names_map in groups_found.items():
        if len(names_map) < 2:
            continue

        # Find suggested canonical: most products win, then US English spelling
        names_sorted = sorted(names_map.items(), key=lambda x: -len(x[1]))
        top_count = len(names_sorted[0][1])
        tied = [n for n, h in names_sorted if len(h) == top_count]

        suggested = tied[0]
        reason = f"Most frequent ({top_count} products)"

        if len(tied) > 1:
            # Prefer US English: Color over Colour, Flavor over Flavour
            us_spellings = {"color", "flavor", "size", "material", "style", "pattern", "scent", "length", "width", "weight", "volume"}
            for t in tied:
                if t.lower() in us_spellings:
                    suggested = t
                    reason = "Tied frequency, US English preferred"
                    break

        products_per_name = {name: sorted(handles) for name, handles in names_map.items()}

        issues.append({
            "names_found": list(names_map.keys()),
            "products_per_name": products_per_name,
            "suggested_canonical": suggested,
            "suggestion_reason": reason,
        })

    return issues


# ---------------------------------------------------------------------------
# Check 8: Handle/Title drift
# ---------------------------------------------------------------------------

def check_handle_title_drift(products: list[Product]) -> list[dict]:
    issues: list[dict] = []

    for product in products:
        title = product.title.strip()
        if not title:
            continue

        expected = slugify(title)
        actual = product.handle.strip()

        if expected == actual:
            continue

        # Classify the difference
        # Check if it is just a gendered suffix difference
        gendered_suffixes = ["-mens", "-womens", "-men-s", "-women-s", "-unisex", "-kids", "-youth", "-boys", "-girls"]
        stripped_expected = expected
        stripped_actual = actual
        for suffix in gendered_suffixes:
            stripped_expected = stripped_expected.removesuffix(suffix)
            stripped_actual = stripped_actual.removesuffix(suffix)

        if stripped_expected == stripped_actual:
            diff_type = "gendered_suffix_variation"
        elif expected.startswith(actual) or actual.startswith(expected):
            diff_type = "truncated"
        elif abs(len(expected) - len(actual)) <= 3:
            diff_type = "minor_punctuation"
        else:
            diff_type = "significant_mismatch"

        issues.append({
            "handle": actual,
            "title": title,
            "expected_handle": expected,
            "difference_type": diff_type,
        })

    return issues


# ---------------------------------------------------------------------------
# Additional checks: warnings
# ---------------------------------------------------------------------------

def check_warnings(products: list[Product], columns: list[str], metadata: dict) -> list[dict]:
    """Generate non-issue warnings for structural or edge-case observations."""
    warnings: list[dict] = []

    # BOM detected
    if metadata.get("bom_detected"):
        warnings.append({
            "code": "bom_detected",
            "message": "UTF-8 BOM detected in CSV file. This can cause issues with column name matching.",
            "details": {},
        })

    # Empty option values (name populated, value empty)
    for product in products:
        if is_default_title_product(product):
            continue
        for row in product.rows:
            for field_label, name, value in option_fields(row):
                if name.strip() and not value.strip():
                    warnings.append({
                        "code": "empty_option_value",
                        "message": f"Option name '{name.strip()}' is set but value is empty on row {row.row_number}.",
                        "details": {
                            "handle": row.handle,
                            "row": row.row_number,
                            "field": f"{field_label} Value",
                            "option_name": name.strip(),
                        },
                    })

    # Option column position inconsistency
    option_positions: dict[str, set[str]] = defaultdict(set)  # name_lower -> set of positions
    for product in products:
        if is_default_title_product(product):
            continue
        for row in product.rows:
            for field_label, name, _ in option_fields(row):
                if name.strip():
                    option_positions[name.strip().lower()].add(field_label)

    for name_lower, positions in option_positions.items():
        if len(positions) > 1:
            warnings.append({
                "code": "option_position_inconsistency",
                "message": f"Option '{name_lower}' appears in multiple column positions: {sorted(positions)}.",
                "details": {"option_name": name_lower, "positions": sorted(positions)},
            })

    # HTML entities in option values
    entity_pattern = re.compile(r"&\w+;|&#\d+;|&#x[\da-fA-F]+;")
    for product in products:
        for row in product.rows:
            for field_label, _, value in option_fields(row):
                if value and entity_pattern.search(value):
                    warnings.append({
                        "code": "html_entity_in_option",
                        "message": f"HTML entity found in {field_label} Value on row {row.row_number}: '{value.strip()}'.",
                        "details": {
                            "handle": row.handle,
                            "row": row.row_number,
                            "field": f"{field_label} Value",
                            "value": value.strip(),
                        },
                    })

    # Option values exceeding 255 characters
    for product in products:
        for row in product.rows:
            for field_label, _, value in option_fields(row):
                if value and len(value.strip()) > SHOPIFY_OPTION_VALUE_MAX_LENGTH:
                    warnings.append({
                        "code": "option_value_too_long",
                        "message": f"{field_label} Value on row {row.row_number} exceeds {SHOPIFY_OPTION_VALUE_MAX_LENGTH} characters ({len(value.strip())} chars).",
                        "details": {
                            "handle": row.handle,
                            "row": row.row_number,
                            "field": f"{field_label} Value",
                            "length": len(value.strip()),
                        },
                    })

    # Default Title products detected
    for product in products:
        if is_default_title_product(product):
            warnings.append({
                "code": "default_title_product",
                "message": f"Product '{product.handle}' uses Shopify default single-variant pattern (Title / Default Title). Skipped from option checks.",
                "details": {"handle": product.handle},
            })

    return warnings


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_audit(csv_path: Path, assets_dir: Path | None) -> dict:
    """Run all checks and return the full audit JSON."""
    products, columns, metadata = parse_csv(csv_path)

    size_config = load_size_config(assets_dir)
    alias_config = load_alias_config(assets_dir)

    # Filter out default-title products for counting
    active_products = [p for p in products if not is_default_title_product(p)]

    whitespace = check_whitespace(products)
    case_issues = check_case_inconsistencies(products)
    duplicates = check_duplicate_variants(products)
    missing_images = check_missing_variant_images(products, columns)
    size_order = check_size_ordering(products, size_config)
    value_aliases = check_option_value_aliases(products, alias_config, size_config)
    name_issues = check_option_name_inconsistencies(products, alias_config)
    handle_drift = check_handle_title_drift(products)
    warnings = check_warnings(products, columns, metadata)

    total_issues = (
        len(whitespace) + len(case_issues) + len(duplicates)
        + len(missing_images) + len(size_order) + len(value_aliases)
        + len(name_issues) + len(handle_drift)
    )
    metadata["total_issues_found"] = total_issues

    return {
        "metadata": metadata,
        "issues": {
            "whitespace": whitespace,
            "case_inconsistencies": case_issues,
            "duplicate_variants": duplicates,
            "missing_variant_images": missing_images,
            "size_ordering": size_order,
            "option_value_aliases": value_aliases,
            "option_name_inconsistencies": name_issues,
            "handle_title_drift": handle_drift,
        },
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit a Shopify product CSV for variant option inconsistencies."
    )
    parser.add_argument("csv_path", type=Path, help="Path to Shopify product CSV")
    parser.add_argument(
        "--assets-dir", type=Path, default=None,
        help="Path to assets/ directory with alias config files"
    )
    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"Fatal: File not found: {args.csv_path}", file=sys.stderr)
        return 1

    if not args.csv_path.is_file():
        print(f"Fatal: Not a file: {args.csv_path}", file=sys.stderr)
        return 1

    try:
        result = run_audit(args.csv_path, args.assets_dir)
    except Exception as e:
        print(f"Fatal: Audit failed: {e}", file=sys.stderr)
        return 1

    # Convert sets to sorted lists for JSON serialization
    json.dump(result, sys.stdout, indent=2, default=lambda o: sorted(o) if isinstance(o, set) else str(o))
    print()  # trailing newline
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Detect and fill missing product attributes in a Shopify product CSV.

Runs deterministic extraction (option values, tags, title vocabulary, sibling
propagation) and outputs what it fills plus a needs_inference.json for rows
that still need LLM inference.

Usage:
    python3 scripts/detect_missing_attributes.py <csv_path> \\
        [--assets-dir assets/] \\
        [--output-dir /path/to/output/]

Outputs:
    needs_inference.json  - rows needing LLM inference
    stdout JSON           - audit report (deterministic fills + summary)

Exit codes:
    0 - Completed
    1 - Fatal error
"""

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


SCRIPT_VERSION = "1.0.0"

TARGET_FIELDS = ("color", "size", "material", "gender", "age_group")

COLOR_OPTION_NAMES = frozenset({
    "color", "colour", "colors", "colours", "color family",
    "shade", "hue", "color/colour",
})

SIZE_OPTION_NAMES = frozenset({
    "size", "sizes", "sizing", "shoe size", "us size", "uk size", "eu size",
    "au size", "hat size", "ring size",
})

TAG_ATTRIBUTE_PREFIXES: dict[str, list[str]] = {
    "color": ["color:", "color-", "colour:", "colour-"],
    "gender": ["gender:", "gender-"],
    "age_group": ["age:", "age-", "age-group:", "age_group-"],
    "material": ["material:", "material-", "fabric:", "fabric-"],
    "size": ["size:", "size-"],
}

GENDER_TAG_SYNONYMS: dict[str, str] = {
    "mens": "male", "men": "male", "men's": "male", "male": "male",
    "gents": "male", "gentlemen": "male",
    "womens": "female", "women": "female", "women's": "female",
    "ladies": "female", "female": "female",
    "unisex": "unisex", "gender-neutral": "unisex",
}

VALID_GENDER = {"male", "female", "unisex"}
VALID_AGE_GROUP = {"newborn", "infant", "toddler", "kids", "adult"}

# Columns the script must never write to
PROHIBITED_COLUMN_PATTERNS = (
    re.compile(r"^Option\d Value$"),
    re.compile(r"^Variant Metafield:", re.IGNORECASE),
)

# Google Shopping column naming across 4 generations
GS_COLUMN_PATTERNS: dict[str, list[re.Pattern]] = {
    "color": [
        re.compile(r"^Google Shopping / Color$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:color$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.mm-google-shopping\.color$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.color$", re.IGNORECASE),
    ],
    "gender": [
        re.compile(r"^Google Shopping / Gender$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:gender$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.mm-google-shopping\.gender$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.gender$", re.IGNORECASE),
    ],
    "age_group": [
        re.compile(r"^Google Shopping / Age Group$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:age_group$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.mm-google-shopping\.age_group$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.age-group$", re.IGNORECASE),
    ],
    "size": [
        re.compile(r"^Google Shopping / Size$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:size$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.mm-google-shopping\.size$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.size$", re.IGNORECASE),
    ],
    "material": [
        re.compile(r"^Google Shopping / Material$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:material$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.mm-google-shopping\.material$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.material$", re.IGNORECASE),
    ],
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class AttributeRow:
    row_number: int
    handle: str
    title: str
    body_html: str
    product_category: str
    product_type: str
    tags: str
    option1_name: str
    option1_value: str
    option2_name: str
    option2_value: str
    option3_name: str
    option3_value: str
    variant_sku: str
    raw_row: dict


@dataclass
class AttributeFill:
    field: str
    value: str
    confidence: float
    source: str
    evidence_quote: str


@dataclass
class ProductGroup:
    handle: str
    title: str
    rows: list[AttributeRow] = field(default_factory=list)
    row_fills: dict = field(default_factory=dict)  # row_number -> {field -> AttributeFill}


# ---------------------------------------------------------------------------
# CSV parsing (reused from variant-option-normalizer)
# ---------------------------------------------------------------------------

def detect_encoding_and_bom(file_path: Path) -> tuple[str, bool]:
    """Check for UTF-8 BOM. Returns (encoding, bom_detected)."""
    with open(file_path, "rb") as f:
        raw = f.read(4)
    if raw[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig", True
    return "utf-8-sig", False


def get(row: dict, key: str) -> str:
    return row.get(key, "") or ""


def parse_csv(file_path: Path) -> tuple[list[ProductGroup], list[str], dict]:
    """Parse a Shopify product CSV into ProductGroup objects."""
    encoding, bom_detected = detect_encoding_and_bom(file_path)

    try:
        with open(file_path, newline="", encoding=encoding) as f:
            reader = csv.DictReader(f)
            columns = list(reader.fieldnames or [])
            rows_raw = list(reader)
    except UnicodeDecodeError:
        with open(file_path, newline="", encoding="latin-1") as f:
            reader = csv.DictReader(f)
            columns = list(reader.fieldnames or [])
            rows_raw = list(reader)
        encoding = "latin-1"

    if not columns:
        print("Fatal: CSV has no columns.", file=sys.stderr)
        sys.exit(1)

    groups_map: dict[str, ProductGroup] = {}
    group_order: list[str] = []
    total_rows = 0
    last_handle = ""

    for idx, row in enumerate(rows_raw):
        row_number = idx + 2  # 1-based; header is row 1
        handle = get(row, "Handle").strip()

        if not handle:
            handle = last_handle
        else:
            last_handle = handle

        if not handle:
            continue

        title = get(row, "Title")

        ar = AttributeRow(
            row_number=row_number,
            handle=handle,
            title=title,
            body_html=get(row, "Body (HTML)"),
            product_category=get(row, "Product Category"),
            product_type=get(row, "Type"),
            tags=get(row, "Tags"),
            option1_name=get(row, "Option1 Name"),
            option1_value=get(row, "Option1 Value"),
            option2_name=get(row, "Option2 Name"),
            option2_value=get(row, "Option2 Value"),
            option3_name=get(row, "Option3 Name"),
            option3_value=get(row, "Option3 Value"),
            variant_sku=get(row, "Variant SKU"),
            raw_row=row,
        )

        if handle not in groups_map:
            groups_map[handle] = ProductGroup(handle=handle, title=title)
            group_order.append(handle)
        elif title and not groups_map[handle].title:
            groups_map[handle].title = title

        groups_map[handle].rows.append(ar)
        total_rows += 1

    groups = [groups_map[h] for h in group_order]

    metadata = {
        "source_file": file_path.name,
        "total_rows": total_rows,
        "total_products": len(groups),
        "columns_present": columns,
        "csv_encoding": encoding,
        "bom_detected": bom_detected,
        "script_version": SCRIPT_VERSION,
        "ran_at": datetime.now(timezone.utc).isoformat(),
    }

    return groups, columns, metadata


# ---------------------------------------------------------------------------
# Asset loading
# ---------------------------------------------------------------------------

def _read_vocab_file(path: Path) -> frozenset[str]:
    """Read a one-term-per-line file into a lowercased frozenset."""
    terms = set()
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    terms.add(line.lower())
    except FileNotFoundError:
        pass
    return frozenset(terms)


def load_apparel_terms(assets_dir: Path) -> frozenset[str]:
    return _read_vocab_file(assets_dir / "apparel_signal_terms.txt")


def load_color_vocab(assets_dir: Path) -> tuple[frozenset[str], frozenset[str]]:
    single = _read_vocab_file(assets_dir / "standard_colors.txt")
    bigrams = _read_vocab_file(assets_dir / "standard_color_bigrams.txt")
    return single, bigrams


def load_material_vocab(assets_dir: Path) -> tuple[frozenset[str], dict[str, str]]:
    materials = _read_vocab_file(assets_dir / "standard_materials.txt")
    synonyms: dict[str, str] = {}
    try:
        with open(assets_dir / "material_synonyms.json", encoding="utf-8") as f:
            raw = json.load(f)
        synonyms = {k.lower(): v for k, v in raw.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return materials, synonyms


def load_pattern_files(assets_dir: Path) -> tuple[dict[str, list], dict[str, list]]:
    """Return (gender_compiled, age_group_compiled) dicts of {enum: [compiled_re]}."""
    gender_compiled: dict[str, list] = {}
    age_group_compiled: dict[str, list] = {}

    for fname, target in [
        ("gender_patterns.json", gender_compiled),
        ("age_group_patterns.json", age_group_compiled),
    ]:
        try:
            with open(assets_dir / fname, encoding="utf-8") as f:
                raw = json.load(f)
            for enum_val, patterns in raw.items():
                target[enum_val] = [re.compile(p, re.IGNORECASE) for p in patterns]
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    return gender_compiled, age_group_compiled


# ---------------------------------------------------------------------------
# Column detection
# ---------------------------------------------------------------------------

def detect_attribute_columns(columns: list[str]) -> dict[str, str | None]:
    """Scan CSV header for target attribute columns across all naming generations.

    Returns dict mapping field name to the matched column header string (or None).
    Also returns a set of prohibited column names detected in the header.
    """
    attr_columns: dict[str, str | None] = {f: None for f in TARGET_FIELDS}
    prohibited_found: list[str] = []

    for col in columns:
        # Check prohibited columns
        for pat in PROHIBITED_COLUMN_PATTERNS:
            if pat.match(col):
                prohibited_found.append(col)
                break

        # Check attribute columns (first match wins per field)
        for field_name, patterns in GS_COLUMN_PATTERNS.items():
            if attr_columns[field_name] is not None:
                continue
            for pat in patterns:
                if pat.match(col):
                    attr_columns[field_name] = col
                    break

    return attr_columns, prohibited_found


# ---------------------------------------------------------------------------
# Apparel detection
# ---------------------------------------------------------------------------

def is_apparel(group: ProductGroup, apparel_terms: frozenset[str]) -> bool:
    """Return True if any row in the group belongs to the apparel category."""
    first_row = group.rows[0] if group.rows else None
    if not first_row:
        return False

    # Check Product Category first (most reliable)
    cat = first_row.product_category.lower()
    if cat and ("apparel" in cat or "clothing" in cat or "footwear" in cat):
        return True

    # Check Type against apparel terms (token-level substring)
    type_lower = first_row.product_type.lower()
    if type_lower:
        for term in apparel_terms:
            if term in type_lower:
                return True

    return False


# ---------------------------------------------------------------------------
# HTML stripping
# ---------------------------------------------------------------------------

class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts).strip()


def strip_html(html_text: str, max_chars: int = 500) -> str:
    if not html_text:
        return ""
    stripper = _HTMLStripper()
    try:
        stripper.feed(html_text)
        text = stripper.get_text()
    except Exception:
        text = re.sub(r"<[^>]+>", " ", html_text).strip()
    return text[:max_chars]


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def _make_fill(field: str, value: str, confidence: float, source: str, evidence: str) -> AttributeFill:
    return AttributeFill(field=field, value=value, confidence=confidence,
                         source=source, evidence_quote=evidence)


def extract_from_options(row: AttributeRow) -> dict[str, AttributeFill]:
    """Extract color and size from Option Name/Value columns."""
    fills: dict[str, AttributeFill] = {}
    for i, (name, value) in enumerate([
        (row.option1_name, row.option1_value),
        (row.option2_name, row.option2_value),
        (row.option3_name, row.option3_value),
    ], start=1):
        name_lower = name.strip().lower()
        value = value.strip()
        if not value:
            continue

        if name_lower in COLOR_OPTION_NAMES and "color" not in fills:
            fills["color"] = _make_fill(
                "color", value, 1.0, "option_value",
                f"Option{i} Name='{name}', Value='{value}'"
            )

        if name_lower in SIZE_OPTION_NAMES and "size" not in fills:
            fills["size"] = _make_fill(
                "size", value, 1.0, "option_value",
                f"Option{i} Name='{name}', Value='{value}'"
            )

    return fills


def extract_from_tags(row: AttributeRow) -> dict[str, AttributeFill]:
    """Extract attributes from structured tag prefixes like color:navy or gender:womens."""
    fills: dict[str, AttributeFill] = {}
    if not row.tags:
        return fills

    tags = [t.strip().lower() for t in row.tags.split(",")]

    for tag in tags:
        for attr, prefixes in TAG_ATTRIBUTE_PREFIXES.items():
            if attr in fills:
                continue
            for prefix in prefixes:
                if tag.startswith(prefix):
                    raw_value = tag[len(prefix):].strip()
                    if not raw_value:
                        continue

                    if attr == "gender":
                        value = GENDER_TAG_SYNONYMS.get(raw_value, raw_value)
                        if value not in VALID_GENDER:
                            continue
                    elif attr == "age_group":
                        if raw_value not in VALID_AGE_GROUP:
                            continue
                        value = raw_value
                    else:
                        value = raw_value.title()

                    fills[attr] = _make_fill(
                        attr, value, 0.98, f"tag_prefix",
                        f"tag: {tag}"
                    )
                    break

    return fills


def extract_from_title_color(
    row: AttributeRow,
    single_colors: frozenset[str],
    bigrams: frozenset[str],
) -> AttributeFill | None:
    """Extract color from title using standard vocabulary lookup."""
    title = row.title.lower()
    tokens = re.findall(r"[a-z]+", title)

    # Bigram pass first
    for i in range(len(tokens) - 1):
        bigram = f"{tokens[i]} {tokens[i+1]}"
        if bigram in bigrams:
            # Check no other bigram matches
            other_matches = sum(
                1 for j in range(len(tokens) - 1)
                if j != i and f"{tokens[j]} {tokens[j+1]}" in bigrams
            )
            if other_matches == 0:
                # Title-case the bigram to match the file format
                original_bigram = " ".join(
                    w.capitalize() for w in bigram.split()
                )
                return _make_fill(
                    "color", original_bigram, 0.90, "title_color_bigram",
                    row.title
                )

    # Single-token pass
    matches = [t for t in tokens if t in single_colors]
    if len(matches) == 1:
        return _make_fill(
            "color", matches[0].capitalize(), 0.90, "title_color_vocab",
            row.title
        )

    return None


def extract_from_title_gender(
    row: AttributeRow,
    gender_compiled: dict[str, list],
) -> AttributeFill | None:
    """Extract gender from title + product_type + tags using closed regex patterns."""
    text = f"{row.title} {row.product_type} {row.tags}"
    matched: dict[str, str] = {}  # gender_value -> matched_string

    for gender_val, patterns in gender_compiled.items():
        for pat in patterns:
            m = pat.search(text)
            if m:
                matched[gender_val] = m.group(0)
                break

    if len(matched) == 1:
        gender_val, evidence = next(iter(matched.items()))
        return _make_fill("gender", gender_val, 0.92, "title_gender_keyword", evidence)

    return None


def extract_from_title_age_group(
    row: AttributeRow,
    age_group_compiled: dict[str, list],
) -> AttributeFill | None:
    """Extract age_group from title + tags using closed regex patterns.

    Returns None when no signal is found (never defaults to adult).
    """
    text = f"{row.title} {row.product_type} {row.tags}"
    matched: dict[str, str] = {}

    for age_val, patterns in age_group_compiled.items():
        for pat in patterns:
            m = pat.search(text)
            if m:
                matched[age_val] = m.group(0)
                break

    if len(matched) == 1:
        age_val, evidence = next(iter(matched.items()))
        return _make_fill("age_group", age_val, 0.92, "title_age_keyword", evidence)

    # Multiple matches = ambiguous (e.g. "kids" and "adult" both present).
    # Zero matches = no signal; do NOT default to adult.
    return None


def extract_from_title_material(
    row: AttributeRow,
    materials_set: frozenset[str],
    synonyms_dict: dict[str, str],
) -> AttributeFill | None:
    """Extract material from title using vocabulary then synonym lookup."""
    tokens = re.findall(r"[a-z]+", row.title.lower())

    # Vocab pass (confidence 0.85)
    matches = [t for t in tokens if t in materials_set]
    if len(matches) == 1:
        return _make_fill(
            "material", matches[0].capitalize(), 0.85, "title_material_vocab",
            row.title
        )

    # Synonym pass (confidence 0.80) — only when vocab found nothing
    if not matches:
        syn_matches: list[tuple[str, str]] = []
        for token in tokens:
            if token in synonyms_dict:
                syn_matches.append((token, synonyms_dict[token]))
        if len(syn_matches) == 1:
            raw_token, canonical = syn_matches[0]
            return _make_fill(
                "material", canonical, 0.80, "title_material_synonym",
                f"'{raw_token}' in title: {row.title}"
            )

    return None


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def check_existing_conflict(
    row: AttributeRow,
    extracted_fill: AttributeFill,
    attr_columns: dict[str, str | None],
) -> bool:
    """Return True if extracted value conflicts with an existing non-empty column value."""
    target_col = attr_columns.get(extracted_fill.field)
    if not target_col:
        return False
    existing = (row.raw_row.get(target_col) or "").strip()
    if not existing:
        return False
    return existing.lower() != extracted_fill.value.lower()


# ---------------------------------------------------------------------------
# Sibling variant propagation
# ---------------------------------------------------------------------------

def propagate_siblings(
    groups: list[ProductGroup],
    attr_columns: dict[str, str | None],
    product_level_fields: tuple = ("color", "gender", "age_group", "material"),
) -> list[dict]:
    """Copy attribute fills from filled variants to empty siblings within the same product.

    For product-level attributes, any sibling with a high-confidence fill propagates
    to rows with no fill for that field. Size is handled separately: only propagate
    when Option values match (same size = same SKU logic doesn't make sense).

    Returns list of propagation fill dicts for the audit report.
    """
    propagation_fills = []

    for group in groups:
        for field_name in product_level_fields:
            # Find the highest-confidence fill for this field across all rows
            best_fill: AttributeFill | None = None
            source_row_num: int | None = None
            source_sku: str = ""

            for row in group.rows:
                row_fills = group.row_fills.get(row.row_number, {})
                fill = row_fills.get(field_name)
                if fill and (best_fill is None or fill.confidence > best_fill.confidence):
                    # Only propagate if not a conflict
                    if not check_existing_conflict(row, fill, attr_columns):
                        best_fill = fill
                        source_row_num = row.row_number
                        source_sku = row.variant_sku

            if not best_fill or source_row_num is None:
                continue

            # Propagate to rows that have no fill for this field
            for row in group.rows:
                if row.row_number == source_row_num:
                    continue
                row_fills = group.row_fills.setdefault(row.row_number, {})
                if field_name in row_fills:
                    continue
                # Check the target column is empty in the original row
                target_col = attr_columns.get(field_name)
                if target_col and (row.raw_row.get(target_col) or "").strip():
                    continue  # already has a value in the CSV

                sibling_fill = _make_fill(
                    field_name, best_fill.value, 0.97, "sibling_propagation",
                    f"{source_sku} (sibling)" if source_sku else f"row {source_row_num} (sibling)"
                )
                row_fills[field_name] = sibling_fill
                propagation_fills.append({
                    "handle": row.handle,
                    "row_number": row.row_number,
                    "variant_sku": row.variant_sku,
                    "field": field_name,
                    "value": best_fill.value,
                    "confidence": 0.97,
                    "source": "sibling_propagation",
                    "evidence_quote": sibling_fill.evidence_quote,
                })

    return propagation_fills


# ---------------------------------------------------------------------------
# Main detection pipeline
# ---------------------------------------------------------------------------

def run_detection(
    csv_path: Path,
    assets_dir: Path,
    output_dir: Path,
) -> dict:
    """Full detection pipeline. Returns audit report dict for stdout."""
    groups, columns, csv_metadata = parse_csv(csv_path)

    apparel_terms = load_apparel_terms(assets_dir)
    single_colors, bigrams = load_color_vocab(assets_dir)
    materials_set, synonyms_dict = load_material_vocab(assets_dir)
    gender_compiled, age_group_compiled = load_pattern_files(assets_dir)

    attr_columns, prohibited_found = detect_attribute_columns(columns)

    apparel_groups: list[ProductGroup] = []
    skipped_non_apparel: list[str] = []

    for group in groups:
        if is_apparel(group, apparel_terms):
            apparel_groups.append(group)
        else:
            skipped_non_apparel.append(group.handle)

    deterministic_fills: list[dict] = []
    conflicts: list[dict] = []
    needs_inference_rows: list[dict] = []

    for group in apparel_groups:
        for row in group.rows:
            fills_for_row: dict[str, AttributeFill] = {}

            # Run option extraction for ALL rows first so we can detect conflicts
            # even when the target column already has a value.
            option_fills = extract_from_options(row)

            for field_name, candidate in option_fills.items():
                target_col = attr_columns.get(field_name)
                if not target_col:
                    continue
                existing = (row.raw_row.get(target_col) or "").strip()
                if existing and existing.lower() != candidate.value.lower():
                    conflicts.append({
                        "handle": row.handle,
                        "row_number": row.row_number,
                        "variant_sku": row.variant_sku,
                        "field": field_name,
                        "extracted_value": candidate.value,
                        "existing_value": existing,
                        "source": candidate.source,
                        "reason": "conflict_with_existing_value",
                    })

            # Determine which fields are missing (target column empty in CSV)
            missing_fields: list[str] = []
            for field_name in TARGET_FIELDS:
                target_col = attr_columns.get(field_name)
                if target_col:
                    existing = (row.raw_row.get(target_col) or "").strip()
                    if existing:
                        continue  # already populated, skip
                missing_fields.append(field_name)

            if not missing_fields:
                continue  # all fields already populated

            tag_fills = extract_from_tags(row)

            for field_name in missing_fields:
                # 1. Option value (confidence 1.0) — skip if conflict was already logged
                if field_name in option_fills:
                    candidate = option_fills[field_name]
                    already_conflicted = any(
                        c["row_number"] == row.row_number and c["field"] == field_name
                        for c in conflicts
                    )
                    if not already_conflicted:
                        fills_for_row[field_name] = candidate
                    continue

                # 2. Tag prefix (confidence 0.98)
                if field_name in tag_fills and field_name not in fills_for_row:
                    fills_for_row[field_name] = tag_fills[field_name]
                    continue

                # 3. Title-based extraction (various confidences)
                if field_name == "color" and "color" not in fills_for_row:
                    fill = extract_from_title_color(row, single_colors, bigrams)
                    if fill:
                        fills_for_row["color"] = fill
                        continue

                if field_name == "gender" and "gender" not in fills_for_row:
                    fill = extract_from_title_gender(row, gender_compiled)
                    if fill:
                        fills_for_row["gender"] = fill
                        continue

                if field_name == "age_group" and "age_group" not in fills_for_row:
                    fill = extract_from_title_age_group(row, age_group_compiled)
                    if fill:
                        fills_for_row["age_group"] = fill
                        continue

                if field_name == "material" and "material" not in fills_for_row:
                    fill = extract_from_title_material(row, materials_set, synonyms_dict)
                    if fill:
                        fills_for_row["material"] = fill
                        continue

            group.row_fills[row.row_number] = fills_for_row

    # Sibling propagation (second pass)
    propagation_fills = propagate_siblings(apparel_groups, attr_columns)

    # Categorize all fills
    for group in apparel_groups:
        for row in group.rows:
            row_fills = group.row_fills.get(row.row_number, {})

            for field_name in TARGET_FIELDS:
                target_col = attr_columns.get(field_name)
                existing = (row.raw_row.get(target_col) or "").strip() if target_col else ""
                if existing:
                    continue  # skip already-populated fields

                fill = row_fills.get(field_name)
                if fill:
                    fill_dict = {
                        "handle": row.handle,
                        "row_number": row.row_number,
                        "variant_sku": row.variant_sku,
                        "field": field_name,
                        "target_column": target_col,
                        "value": fill.value,
                        "confidence": fill.confidence,
                        "source": fill.source,
                        "evidence_quote": fill.evidence_quote,
                        "needs_review": fill.confidence < 0.90,
                    }
                    # Only include fills above the 0.75 threshold
                    if fill.confidence >= 0.75:
                        deterministic_fills.append(fill_dict)
                    else:
                        # Below threshold: goes to needs_review via needs_inference
                        pass
                else:
                    # No fill found: collect context for LLM
                    row_title = row.title or group.title
                    body_stripped = strip_html(row.body_html)

                    # Find if this row already has an entry in needs_inference_rows
                    existing_entry = next(
                        (e for e in needs_inference_rows
                         if e["row_number"] == row.row_number),
                        None
                    )
                    if existing_entry:
                        if field_name not in existing_entry["missing_fields"]:
                            existing_entry["missing_fields"].append(field_name)
                    else:
                        # Only add to LLM inference if there's at least some context
                        needs_inference_rows.append({
                            "handle": row.handle,
                            "row_number": row.row_number,
                            "variant_sku": row.variant_sku,
                            "title": row_title,
                            "product_type": row.product_type,
                            "tags": row.tags,
                            "body_html_stripped": body_stripped,
                            "option1_name": row.option1_name,
                            "option1_value": row.option1_value,
                            "option2_name": row.option2_name,
                            "option2_value": row.option2_value,
                            "missing_fields": [field_name],
                        })

    # Write needs_inference.json
    output_dir.mkdir(parents=True, exist_ok=True)
    inference_path = output_dir / "needs_inference.json"
    inference_output = {
        "metadata": {
            "csv_file": csv_path.name,
            "total_apparel_products": len(apparel_groups),
            "total_rows": csv_metadata["total_rows"],
            "deterministic_fills_made": len(deterministic_fills),
            "rows_needing_inference": len(needs_inference_rows),
            "conflicts_detected": len(conflicts),
            "attribute_columns_detected": attr_columns,
            "prohibited_columns_found": prohibited_found,
        },
        "rows": needs_inference_rows,
    }
    with open(inference_path, "w", encoding="utf-8") as f:
        json.dump(inference_output, f, indent=2)

    # Build audit report for stdout
    audit_report = {
        "metadata": {
            **csv_metadata,
            "total_apparel_products": len(apparel_groups),
            "skipped_non_apparel": len(skipped_non_apparel),
            "deterministic_fills_made": len(deterministic_fills),
            "rows_needing_inference": len(needs_inference_rows),
            "conflicts_detected": len(conflicts),
            "attribute_columns_detected": attr_columns,
            "prohibited_columns_found": prohibited_found,
            "needs_inference_file": str(inference_path),
        },
        "deterministic_fills": deterministic_fills,
        "conflicts": conflicts,
        "skipped_non_apparel": skipped_non_apparel,
    }

    return audit_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect and fill missing product attributes in a Shopify product CSV."
    )
    parser.add_argument("csv_path", type=Path, help="Path to Shopify product CSV")
    parser.add_argument(
        "--assets-dir", type=Path, default=None,
        help="Path to assets/ directory (default: assets/ relative to this script)"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Directory for needs_inference.json (default: same directory as csv_path)"
    )
    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"Fatal: File not found: {args.csv_path}", file=sys.stderr)
        return 1
    if not args.csv_path.is_file():
        print(f"Fatal: Not a file: {args.csv_path}", file=sys.stderr)
        return 1

    # Default assets dir: assets/ relative to this script's directory
    assets_dir = args.assets_dir
    if assets_dir is None:
        assets_dir = Path(__file__).parent.parent / "assets"

    output_dir = args.output_dir or args.csv_path.parent

    try:
        result = run_detection(args.csv_path, assets_dir, output_dir)
    except Exception as e:
        print(f"Fatal: Detection failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1

    json.dump(result, sys.stdout, indent=2,
              default=lambda o: sorted(o) if isinstance(o, set) else str(o))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

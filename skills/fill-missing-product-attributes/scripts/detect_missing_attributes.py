#!/usr/bin/env python3
"""Detect and fill missing product attributes in a Shopify product CSV.

Runs deterministic extraction (option values, tags, title vocabulary, body HTML,
sibling propagation) and outputs three artifacts:
  - deterministic_fills.json  fills already made, pre-approved for Stage 3
  - needs_inference.json      rows the LLM should attempt
  - stdout JSON               human-readable audit report (includes work_dir path)

When --output-dir is omitted, a temporary directory is created automatically
(e.g. /tmp/fill-attrs-XXXX). The work_dir path is emitted in the stdout JSON
so downstream stages can locate the intermediate files. Pass --work-dir to
apply_fills.py to clean up the temp directory after Stage 3 completes.

Usage:
    python3 scripts/detect_missing_attributes.py <csv_path> \\
        [--assets-dir assets/] \\
        [--output-dir /path/to/output/]

Exit codes:
    0 - Completed
    1 - Fatal error (missing assets, file not found, etc.)
"""

import argparse
import csv
import json
import re
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


SCRIPT_VERSION = "2.0.0"

TARGET_FIELDS = ("color", "size", "size_system", "size_type", "material", "gender", "age_group")

REQUIRED_ASSETS = [
    "apparel_signal_terms.txt",
    "apparel_title_fallback.txt",
    "standard_colors.txt",
    "standard_color_bigrams.txt",
    "standard_materials.txt",
    "material_synonyms.json",
    "gender_patterns.json",
    "age_group_patterns.json",
    "size_type_patterns.json",
]

FIELD_THRESHOLDS = {
    "gender": 0.90,
    "age_group": 0.90,
    "color": 0.80,
    "material": 0.70,
    "size": 0.95,
    "size_system": 0.95,
    "size_type": 0.90,
}

HIGH_CONFIDENCE_CUTOFF = 0.85
SIBLING_PROPAGATION_CONFIDENCE = 0.97

COLOR_OPTION_NAMES = frozenset({
    "color", "colour", "colors", "colours", "color family",
    "shade", "hue", "color/colour",
})

SIZE_OPTION_NAMES = frozenset({
    "size", "sizes", "sizing", "shoe size", "us size", "uk size", "eu size",
    "au size", "hat size", "ring size",
})

MATERIAL_OPTION_NAMES = frozenset({
    "material", "fabric", "materials",
})

SIZE_SYSTEM_TOKENS = frozenset({"us", "uk", "eu", "au", "de", "fr", "jp", "cn"})

TAG_ATTRIBUTE_PREFIXES: dict[str, list[str]] = {
    "color": ["color:", "color-", "colour:", "colour-"],
    "gender": ["gender:", "gender-"],
    "age_group": ["age:", "age-", "age-group:", "age_group:"],
    "material": ["material:", "material-", "fabric:", "fabric-"],
    "size": ["size:", "size-"],
}

GENDER_TAG_SYNONYMS: dict[str, str] = {
    "mens": "male", "men": "male", "men's": "male", "male": "male",
    "gents": "male", "gentlemen": "male",
    "womens": "female", "women": "female", "women's": "female",
    "ladies": "female", "female": "female",
    "unisex": "unisex", "gender-neutral": "unisex", "gender_neutral": "unisex",
}

AGE_GROUP_TAG_SYNONYMS: dict[str, str] = {
    "newborn": "newborn", "0-3m": "newborn", "0-3-months": "newborn",
    "infant": "infant", "baby": "infant", "3-12m": "infant",
    "toddler": "toddler", "1-5y": "toddler",
    "kids": "kids", "kid": "kids", "child": "kids", "children": "kids",
    "youth": "kids", "junior": "kids",
    "adult": "adult", "adults": "adult", "grown-up": "adult",
}

VALID_GENDER = {"male", "female", "unisex"}
VALID_AGE_GROUP = {"newborn", "infant", "toddler", "kids", "adult"}

PROHIBITED_COLUMN_PATTERNS = (
    re.compile(r"^Option\d Value$"),
    re.compile(r"^Variant Metafield:", re.IGNORECASE),
)

GS_COLUMN_PATTERNS: dict[str, list[re.Pattern]] = {
    "color": [
        re.compile(r"^product\.metafields\.mm-google-shopping\.color$", re.IGNORECASE),
        re.compile(r"^Google Shopping / Color$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.color$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.custom\.color$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:color$", re.IGNORECASE),
    ],
    "gender": [
        re.compile(r"^product\.metafields\.mm-google-shopping\.gender$", re.IGNORECASE),
        re.compile(r"^Google Shopping / Gender$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.gender$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.custom\.gender$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:gender$", re.IGNORECASE),
    ],
    "age_group": [
        re.compile(r"^product\.metafields\.mm-google-shopping\.age_group$", re.IGNORECASE),
        re.compile(r"^Google Shopping / Age Group$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.age-group$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.custom\.age_group$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:age_group$", re.IGNORECASE),
    ],
    "size": [
        re.compile(r"^product\.metafields\.mm-google-shopping\.size$", re.IGNORECASE),
        re.compile(r"^Google Shopping / Size$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.size$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.custom\.size$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:size$", re.IGNORECASE),
    ],
    "material": [
        re.compile(r"^product\.metafields\.mm-google-shopping\.material$", re.IGNORECASE),
        re.compile(r"^Google Shopping / Material$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.material$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.custom\.material$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:material$", re.IGNORECASE),
    ],
    "size_system": [
        re.compile(r"^product\.metafields\.mm-google-shopping\.size_system$", re.IGNORECASE),
        re.compile(r"^Google Shopping / Size System$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.size_system$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.custom\.size_system$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:size_system$", re.IGNORECASE),
    ],
    "size_type": [
        re.compile(r"^product\.metafields\.mm-google-shopping\.size_type$", re.IGNORECASE),
        re.compile(r"^Google Shopping / Size Type$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.shopify\.size_type$", re.IGNORECASE),
        re.compile(r"^product\.metafields\.custom\.size_type$", re.IGNORECASE),
        re.compile(r"^mm-google-shopping:size_type$", re.IGNORECASE),
    ],
}

COMPOUND_MATERIAL_RE = re.compile(r"(\d+)\s*%\s*([A-Za-z]+)")


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
    row_fills: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Asset validation
# ---------------------------------------------------------------------------

def validate_assets(assets_dir: Path) -> None:
    missing = [f for f in REQUIRED_ASSETS if not (assets_dir / f).exists()]
    if missing:
        print("Fatal: Missing required asset files:", file=sys.stderr)
        for f in missing:
            print(f"  {assets_dir / f}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------

def detect_encoding_and_bom(file_path: Path) -> tuple[str, bool]:
    with open(file_path, "rb") as f:
        head = f.read(4)
    if head[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig", True
    if head[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return "utf-16", False
    return "utf-8", False


def get(row: dict, key: str) -> str:
    return row.get(key, "") or ""


def parse_csv(file_path: Path) -> tuple[list[ProductGroup], list[str], dict]:
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
    last_handle = ""
    total_rows = 0

    for idx, row in enumerate(rows_raw):
        row_number = idx + 2
        handle = get(row, "Handle").strip()

        if not handle:
            handle = last_handle
        else:
            last_handle = handle

        if not handle:
            continue

        title = get(row, "Title")
        # Support both "Type" (new) and "Product Type" (old Shopify exports)
        product_type = get(row, "Type") or get(row, "Product Type")

        ar = AttributeRow(
            row_number=row_number,
            handle=handle,
            title=title,
            body_html=get(row, "Body (HTML)"),
            product_category=get(row, "Product Category"),
            product_type=product_type,
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
    terms: set[str] = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                terms.add(line.lower())
    return frozenset(terms)


def load_apparel_terms(assets_dir: Path) -> tuple[frozenset[str], frozenset[str]]:
    signal = _read_vocab_file(assets_dir / "apparel_signal_terms.txt")
    fallback = _read_vocab_file(assets_dir / "apparel_title_fallback.txt")
    return signal, fallback


def load_color_vocab(assets_dir: Path) -> tuple[frozenset[str], frozenset[str]]:
    single = _read_vocab_file(assets_dir / "standard_colors.txt")
    bigrams = _read_vocab_file(assets_dir / "standard_color_bigrams.txt")
    return single, bigrams


def load_material_vocab(assets_dir: Path) -> tuple[frozenset[str], dict[str, str]]:
    materials = _read_vocab_file(assets_dir / "standard_materials.txt")
    with open(assets_dir / "material_synonyms.json", encoding="utf-8") as f:
        raw = json.load(f)
    synonyms = {k.lower(): v for k, v in raw.items()}
    return materials, synonyms


def load_pattern_files(assets_dir: Path) -> tuple[dict[str, list], dict[str, list], dict[str, list]]:
    """Return (gender_compiled, age_group_compiled, size_type_compiled)."""
    gender_compiled: dict[str, list] = {}
    age_group_compiled: dict[str, list] = {}
    size_type_compiled: dict[str, list] = {}

    for fname, target in [
        ("gender_patterns.json", gender_compiled),
        ("age_group_patterns.json", age_group_compiled),
        ("size_type_patterns.json", size_type_compiled),
    ]:
        with open(assets_dir / fname, encoding="utf-8") as f:
            raw = json.load(f)
        for enum_val, patterns in raw.items():
            target[enum_val] = [re.compile(p, re.IGNORECASE) for p in patterns]

    return gender_compiled, age_group_compiled, size_type_compiled


# ---------------------------------------------------------------------------
# Column detection
# ---------------------------------------------------------------------------

def detect_attribute_columns(columns: list[str]) -> tuple[dict[str, str | None], list[str]]:
    """Scan CSV header for target attribute columns.

    Returns (attr_columns_map, prohibited_columns_found).
    Priority order within each field follows GS_COLUMN_PATTERNS list order.
    """
    attr_columns: dict[str, str | None] = {f: None for f in TARGET_FIELDS}
    prohibited_found: list[str] = []

    for col in columns:
        for pat in PROHIBITED_COLUMN_PATTERNS:
            if pat.match(col):
                prohibited_found.append(col)
                break

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

def is_apparel(
    group: ProductGroup,
    apparel_signal: frozenset[str],
    apparel_fallback: frozenset[str],
) -> tuple[bool, str]:
    """Return (is_apparel, detection_method)."""
    first_row = group.rows[0] if group.rows else None
    if not first_row:
        return False, ""

    cat = first_row.product_category.lower()
    if cat and ("apparel" in cat or "clothing" in cat or "footwear" in cat):
        return True, "product_category"

    type_lower = first_row.product_type.lower()
    if type_lower:
        for term in apparel_signal:
            if term in type_lower:
                return True, "type_signal"

    # Tier 3: title token fallback (conservative)
    title_lower = (group.title or first_row.title).lower()
    title_tokens = set(re.findall(r"[a-z]+", title_lower))
    if title_tokens & apparel_fallback:
        return True, "title_fallback"

    return False, ""


# ---------------------------------------------------------------------------
# HTML stripping and body signal extraction
# ---------------------------------------------------------------------------

class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts).strip()


def _strip_html(html_text: str) -> str:
    if not html_text:
        return ""
    stripper = _HTMLStripper()
    try:
        stripper.feed(html_text)
        return stripper.get_text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", html_text).strip()


_SIGNAL_VOCAB_RE: re.Pattern | None = None


def _build_signal_re(
    single_colors: frozenset[str],
    bigrams: frozenset[str],
    materials_set: frozenset[str],
) -> re.Pattern:
    terms = set(single_colors) | set(materials_set)
    for b in bigrams:
        terms.update(b.split())
    terms.update({"male", "female", "unisex", "gender", "men", "women",
                  "kids", "adult", "infant", "toddler", "newborn", "baby",
                  "cotton", "wool", "silk", "linen", "polyester"})
    pattern = r"\b(?:" + "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True)) + r")\b"
    return re.compile(pattern, re.IGNORECASE)


def extract_body_signals(
    body_html: str,
    single_colors: frozenset[str],
    bigrams: frozenset[str],
    materials_set: frozenset[str],
    max_chars: int = 800,
) -> str:
    """Strip HTML, find signal-bearing sentences, return truncated text."""
    text = _strip_html(body_html)
    if not text:
        return ""

    signal_re = _build_signal_re(single_colors, bigrams, materials_set)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    signal_sentences = [s for s in sentences if signal_re.search(s)]

    combined = " ".join(signal_sentences) if signal_sentences else text
    if len(combined) <= max_chars:
        return combined
    return textwrap.shorten(combined, width=max_chars, placeholder="...")


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def _make_fill(field: str, value: str, confidence: float, source: str, evidence: str) -> AttributeFill:
    return AttributeFill(field=field, value=value, confidence=confidence,
                         source=source, evidence_quote=evidence)


def extract_from_options(
    row: AttributeRow,
    size_type_compiled: dict[str, list],
) -> dict[str, AttributeFill]:
    """Extract color, size, material, size_system, size_type from Option columns."""
    fills: dict[str, AttributeFill] = {}
    options = [
        (row.option1_name, row.option1_value, 1),
        (row.option2_name, row.option2_value, 2),
        (row.option3_name, row.option3_value, 3),
    ]

    for name, value, i in options:
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
            # size_system from option name
            for sys_token in SIZE_SYSTEM_TOKENS:
                if sys_token in name_lower and "size_system" not in fills:
                    fills["size_system"] = _make_fill(
                        "size_system", sys_token.upper(), 1.0, "option_name",
                        f"Option{i} Name='{name}'"
                    )
            # size_type from option value token scan
            if "size_type" not in fills:
                for type_val, patterns in size_type_compiled.items():
                    for pat in patterns:
                        if pat.search(value):
                            fills["size_type"] = _make_fill(
                                "size_type", type_val, 0.95, "option_value_token",
                                f"Option{i} Name='{name}', Value='{value}'"
                            )
                            break
                    if "size_type" in fills:
                        break

        if name_lower in MATERIAL_OPTION_NAMES and "material" not in fills:
            fills["material"] = _make_fill(
                "material", value, 1.0, "option_value",
                f"Option{i} Name='{name}', Value='{value}'"
            )

    return fills


def extract_from_tags(
    row: AttributeRow,
    materials_set: frozenset[str],
    synonyms_dict: dict[str, str],
) -> dict[str, AttributeFill]:
    """Extract attributes from structured tag prefixes."""
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
                        value = AGE_GROUP_TAG_SYNONYMS.get(raw_value, raw_value)
                        if value not in VALID_AGE_GROUP:
                            continue
                    elif attr == "material":
                        # Apply synonym map for material tags too
                        value = raw_value.title()
                        if raw_value in synonyms_dict:
                            value = synonyms_dict[raw_value]
                        elif raw_value not in materials_set:
                            value = raw_value.title()
                    else:
                        value = raw_value.title()

                    fills[attr] = _make_fill(
                        attr, value, 0.98, "tag_prefix",
                        f"tag: {tag}"
                    )
                    break

    return fills


def extract_from_title_color(
    row: AttributeRow,
    single_colors: frozenset[str],
    bigrams: frozenset[str],
) -> AttributeFill | None:
    title = row.title.lower()
    tokens = re.findall(r"[a-z]+", title)

    bigram_matches: list[str] = []
    for i in range(len(tokens) - 1):
        bg = f"{tokens[i]} {tokens[i+1]}"
        if bg in bigrams:
            bigram_matches.append(bg)

    bigram_matches = list(dict.fromkeys(bigram_matches))

    if bigram_matches:
        if len(bigram_matches) > 3:
            return None  # handled as too_many_colors elsewhere
        # Remove single tokens covered by a bigram
        covered = set()
        for bg in bigram_matches:
            covered.update(bg.split())
        remaining_singles = [t for t in tokens if t in single_colors and t not in covered]
        all_colors = bigram_matches + remaining_singles
        all_colors = list(dict.fromkeys(all_colors))

        if len(all_colors) == 1:
            display = " ".join(w.capitalize() for w in all_colors[0].split())
            return _make_fill("color", display, 0.90, "title_color_bigram", row.title)
        if 2 <= len(all_colors) <= 3:
            display = "/".join(" ".join(w.capitalize() for w in c.split()) for c in all_colors)
            return _make_fill("color", display, 0.80, "title_color_bigram", row.title)
        return None

    matches = list(dict.fromkeys(t for t in tokens if t in single_colors))
    if len(matches) == 1:
        return _make_fill("color", matches[0].capitalize(), 0.90, "title_color_vocab", row.title)
    if 2 <= len(matches) <= 3:
        display = "/".join(m.capitalize() for m in matches)
        return _make_fill("color", display, 0.80, "title_color_vocab", row.title)
    return None


def count_colors_in_title(
    row: AttributeRow,
    single_colors: frozenset[str],
    bigrams: frozenset[str],
) -> int:
    tokens = re.findall(r"[a-z]+", row.title.lower())
    bigram_matches = list(dict.fromkeys(
        f"{tokens[i]} {tokens[i+1]}"
        for i in range(len(tokens) - 1)
        if f"{tokens[i]} {tokens[i+1]}" in bigrams
    ))
    covered = set()
    for bg in bigram_matches:
        covered.update(bg.split())
    singles = [t for t in tokens if t in single_colors and t not in covered]
    return len(bigram_matches) + len(singles)


def extract_from_title_gender(
    row: AttributeRow,
    gender_compiled: dict[str, list],
) -> AttributeFill | None:
    text = f"{row.title} {row.product_type} {row.tags}"
    matched: dict[str, str] = {}

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
) -> tuple[AttributeFill | None, AttributeFill | None]:
    """Returns (age_group_fill, gender_fill_from_boys_girls).

    'boys'/'girls' imply both gender AND age_group=kids.
    Returns gender fill as second element when boys/girls triggered it.
    """
    text = f"{row.title} {row.product_type} {row.tags}"
    matched: dict[str, str] = {}

    for age_val, patterns in age_group_compiled.items():
        for pat in patterns:
            m = pat.search(text)
            if m:
                matched[age_val] = m.group(0)
                break

    age_fill: AttributeFill | None = None
    gender_fill: AttributeFill | None = None

    if len(matched) == 1:
        age_val, evidence = next(iter(matched.items()))
        age_fill = _make_fill("age_group", age_val, 0.92, "title_age_keyword", evidence)

        boys_re = re.compile(r"\bboys?\b", re.IGNORECASE)
        girls_re = re.compile(r"\bgirls?\b", re.IGNORECASE)
        if boys_re.search(text):
            gender_fill = _make_fill("gender", "male", 0.92, "title_gender_keyword", boys_re.search(text).group(0))
        elif girls_re.search(text):
            gender_fill = _make_fill("gender", "female", 0.92, "title_gender_keyword", girls_re.search(text).group(0))

    return age_fill, gender_fill


def extract_from_title_material(
    row: AttributeRow,
    materials_set: frozenset[str],
    synonyms_dict: dict[str, str],
) -> AttributeFill | None:
    tokens = re.findall(r"[a-z]+", row.title.lower())

    matches = list(dict.fromkeys(t for t in tokens if t in materials_set))
    if len(matches) == 1:
        return _make_fill("material", matches[0].capitalize(), 0.85, "title_material_vocab", row.title)

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


def extract_from_body_material(
    body_html: str,
    materials_set: frozenset[str],
) -> AttributeFill | None:
    """Extract material from body HTML percentage patterns like '90% Cotton, 10% Spandex'."""
    if not body_html:
        return None
    text = _strip_html(body_html)
    matches = COMPOUND_MATERIAL_RE.findall(text)
    if not matches:
        return None

    pct_materials: list[tuple[int, str]] = []
    for pct_str, mat in matches:
        mat_lower = mat.lower()
        if mat_lower in materials_set:
            pct_materials.append((int(pct_str), mat.capitalize()))

    if not pct_materials:
        return None

    max_pct = max(p for p, _ in pct_materials)
    top = [m for p, m in pct_materials if p == max_pct]
    top = list(dict.fromkeys(top))

    evidence = " ".join(f"{p}% {m}" for p, m in pct_materials[:3])

    if len(top) == 1:
        return _make_fill("material", top[0], 0.88, "body_compound_material", evidence)
    if len(top) <= 3:
        return _make_fill("material", "/".join(top), 0.88, "body_compound_material", evidence)
    return None


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def check_existing_conflict(
    row: AttributeRow,
    extracted_fill: AttributeFill,
    attr_columns: dict[str, str | None],
) -> bool:
    target_col = attr_columns.get(extracted_fill.field)
    if not target_col:
        return False
    existing = (row.raw_row.get(target_col) or "").strip()
    if not existing:
        return False
    return existing.lower() != extracted_fill.value.lower()


def resolve_field_candidates(
    candidates: list[AttributeFill],
) -> tuple[AttributeFill | None, dict | None]:
    """Resolve multiple extraction candidates for one field.

    Returns (chosen_fill, conflict_record).
    conflict_record is non-None when two high-confidence sources disagree.
    In that case, chosen_fill is None (goes to needs_review).
    """
    if not candidates:
        return None, None

    high_conf = [c for c in candidates if c.confidence >= HIGH_CONFIDENCE_CUTOFF]
    if len(high_conf) >= 2:
        distinct = {c.value.lower() for c in high_conf}
        if len(distinct) > 1:
            return None, {
                "reason": "conflict_between_sources",
                "candidates": [
                    {
                        "value": c.value,
                        "source": c.source,
                        "confidence": c.confidence,
                        "evidence": c.evidence_quote,
                    }
                    for c in high_conf
                ],
            }

    return max(candidates, key=lambda c: c.confidence), None


# ---------------------------------------------------------------------------
# Sibling variant propagation (first pass, before title extraction)
# ---------------------------------------------------------------------------

def propagate_siblings(
    groups: list[ProductGroup],
    attr_columns: dict[str, str | None],
    product_level_fields: tuple = ("color", "gender", "age_group", "material"),
) -> list[dict]:
    propagation_fills: list[dict] = []

    for group in groups:
        for field_name in product_level_fields:
            best_fill: AttributeFill | None = None
            source_row_num: int | None = None
            source_sku: str = ""

            for row in group.rows:
                row_fills = group.row_fills.get(row.row_number, {})
                fill = row_fills.get(field_name)
                if fill is None:
                    continue
                if check_existing_conflict(row, fill, attr_columns):
                    continue
                if best_fill is None or fill.confidence > best_fill.confidence:
                    best_fill = fill
                    source_row_num = row.row_number
                    source_sku = row.variant_sku

            if not best_fill or best_fill.confidence < SIBLING_PROPAGATION_CONFIDENCE:
                continue

            for row in group.rows:
                if row.row_number == source_row_num:
                    continue
                row_fills = group.row_fills.setdefault(row.row_number, {})
                existing_fill = row_fills.get(field_name)
                # Only overwrite if existing fill has lower confidence
                if existing_fill and existing_fill.confidence >= SIBLING_PROPAGATION_CONFIDENCE:
                    continue
                target_col = attr_columns.get(field_name)
                if target_col and (row.raw_row.get(target_col) or "").strip():
                    continue

                sibling_fill = _make_fill(
                    field_name, best_fill.value, SIBLING_PROPAGATION_CONFIDENCE,
                    "sibling_propagation",
                    f"{source_sku} (sibling)" if source_sku else f"row {source_row_num} (sibling)"
                )
                row_fills[field_name] = sibling_fill
                propagation_fills.append({
                    "handle": row.handle,
                    "row_number": row.row_number,
                    "variant_sku": row.variant_sku,
                    "field": field_name,
                    "value": best_fill.value,
                    "confidence": SIBLING_PROPAGATION_CONFIDENCE,
                    "source": "sibling_propagation",
                    "evidence_quote": sibling_fill.evidence_quote,
                })

    return propagation_fills


# ---------------------------------------------------------------------------
# Main detection pipeline
# ---------------------------------------------------------------------------

def is_auto_writable(field_name: str, confidence: float) -> bool:
    return confidence >= FIELD_THRESHOLDS.get(field_name, 0.90)


def run_detection(
    csv_path: Path,
    assets_dir: Path,
    output_dir: Path,
) -> dict:
    """Full detection pipeline. Returns audit report dict."""
    validate_assets(assets_dir)

    groups, columns, csv_metadata = parse_csv(csv_path)

    if csv_metadata["total_rows"] == 0:
        print("Warning: CSV contains no data rows. Nothing to process.", file=sys.stderr)

    apparel_signal, apparel_fallback = load_apparel_terms(assets_dir)
    single_colors, bigrams = load_color_vocab(assets_dir)
    materials_set, synonyms_dict = load_material_vocab(assets_dir)
    gender_compiled, age_group_compiled, size_type_compiled = load_pattern_files(assets_dir)

    attr_columns, prohibited_found = detect_attribute_columns(columns)

    apparel_groups: list[ProductGroup] = []
    skipped_non_apparel: list[dict] = []

    for group in groups:
        detected, method = is_apparel(group, apparel_signal, apparel_fallback)
        if detected:
            group._detection_method = method
            apparel_groups.append(group)
        else:
            skipped_non_apparel.append({
                "handle": group.handle,
                "product_type": group.rows[0].product_type if group.rows else "",
            })

    deterministic_fills: list[dict] = []
    conflicts: list[dict] = []
    needs_inference_rows: list[dict] = []
    needs_review_pre: list[dict] = []

    for group in apparel_groups:
        for row in group.rows:
            # Collect all candidates per field before resolving
            all_candidates: dict[str, list[AttributeFill]] = {f: [] for f in TARGET_FIELDS}

            # Option extraction (confidence 1.0)
            option_fills = extract_from_options(row, size_type_compiled)
            for field_name, fill in option_fills.items():
                if field_name in TARGET_FIELDS:
                    all_candidates[field_name].append(fill)

            # Tag extraction (confidence 0.98)
            tag_fills = extract_from_tags(row, materials_set, synonyms_dict)
            for field_name, fill in tag_fills.items():
                if field_name in TARGET_FIELDS:
                    all_candidates[field_name].append(fill)

            # Title extraction
            color_fill = extract_from_title_color(row, single_colors, bigrams)
            if color_fill:
                all_candidates["color"].append(color_fill)

            gender_fill = extract_from_title_gender(row, gender_compiled)
            if gender_fill:
                all_candidates["gender"].append(gender_fill)

            age_fill, gender_from_age = extract_from_title_age_group(row, age_group_compiled)
            if age_fill:
                all_candidates["age_group"].append(age_fill)
            if gender_from_age and gender_from_age not in all_candidates["gender"]:
                all_candidates["gender"].append(gender_from_age)

            material_fill = extract_from_title_material(row, materials_set, synonyms_dict)
            if material_fill:
                all_candidates["material"].append(material_fill)

            # Body HTML material (compound percentage patterns)
            body_mat_fill = extract_from_body_material(row.body_html, materials_set)
            if body_mat_fill:
                all_candidates["material"].append(body_mat_fill)

            # Resolve all candidates, detect between-source conflicts
            resolved_fills: dict[str, AttributeFill] = {}
            for field_name, candidates in all_candidates.items():
                if not candidates:
                    continue
                chosen, src_conflict = resolve_field_candidates(candidates)
                if src_conflict:
                    conflicts.append({
                        "handle": row.handle,
                        "row_number": row.row_number,
                        "variant_sku": row.variant_sku,
                        "field": field_name,
                        **src_conflict,
                    })
                elif chosen:
                    resolved_fills[field_name] = chosen

            # Check existing value conflicts for all resolved fills
            for field_name, fill in list(resolved_fills.items()):
                if check_existing_conflict(row, fill, attr_columns):
                    target_col = attr_columns.get(field_name)
                    existing = (row.raw_row.get(target_col) or "").strip() if target_col else ""
                    conflicts.append({
                        "handle": row.handle,
                        "row_number": row.row_number,
                        "variant_sku": row.variant_sku,
                        "field": field_name,
                        "reason": "conflict_with_existing_value",
                        "existing_value": existing,
                        "extracted_value": fill.value,
                        "source": fill.source,
                        "evidence_quote": fill.evidence_quote,
                        "confidence": fill.confidence,
                    })
                    del resolved_fills[field_name]

            group.row_fills[row.row_number] = resolved_fills

    # FIRST: sibling propagation (before title extraction categorization)
    # Fills stored in-place on group.row_fills; return value not used.
    propagate_siblings(apparel_groups, attr_columns)

    # Categorize all fills after propagation
    for group in apparel_groups:
        for row in group.rows:
            row_fills = group.row_fills.get(row.row_number, {})
            row_has_inference_entry = False

            color_count = count_colors_in_title(row, single_colors, bigrams)

            for field_name in TARGET_FIELDS:
                target_col = attr_columns.get(field_name)
                existing = (row.raw_row.get(target_col) or "").strip() if target_col else ""
                if existing:
                    continue

                fill = row_fills.get(field_name)

                if field_name == "color" and color_count > 3 and not fill:
                    needs_review_pre.append({
                        "handle": row.handle,
                        "row_number": row.row_number,
                        "variant_sku": row.variant_sku,
                        "field": field_name,
                        "reason": "too_many_colors",
                        "evidence_quote": row.title,
                        "confidence": None,
                        "suggested_value": None,
                    })
                    continue

                if fill:
                    if not target_col:
                        needs_review_pre.append({
                            "handle": row.handle,
                            "row_number": row.row_number,
                            "variant_sku": row.variant_sku,
                            "field": field_name,
                            "reason": "no_target_column_in_csv",
                            "evidence_quote": fill.evidence_quote,
                            "confidence": fill.confidence,
                            "suggested_value": fill.value,
                        })
                        continue

                    if is_auto_writable(field_name, fill.confidence):
                        deterministic_fills.append({
                            "handle": row.handle,
                            "row_number": row.row_number,
                            "variant_sku": row.variant_sku,
                            "field": field_name,
                            "target_column": target_col,
                            "proposed_value": fill.value,
                            "confidence": fill.confidence,
                            "source": fill.source,
                            "evidence_quote": fill.evidence_quote,
                            "approved": True,
                        })
                    else:
                        needs_review_pre.append({
                            "handle": row.handle,
                            "row_number": row.row_number,
                            "variant_sku": row.variant_sku,
                            "field": field_name,
                            "reason": "confidence_below_threshold",
                            "evidence_quote": fill.evidence_quote,
                            "confidence": fill.confidence,
                            "suggested_value": fill.value,
                        })
                else:
                    # No fill found: queue for LLM
                    body_stripped = extract_body_signals(
                        row.body_html, single_colors, bigrams, materials_set
                    )
                    existing_entry = next(
                        (e for e in needs_inference_rows if e["row_number"] == row.row_number),
                        None,
                    )
                    if existing_entry:
                        if field_name not in existing_entry["missing_fields"]:
                            existing_entry["missing_fields"].append(field_name)
                    else:
                        needs_inference_rows.append({
                            "handle": row.handle,
                            "row_number": row.row_number,
                            "variant_sku": row.variant_sku,
                            "title": row.title or group.title,
                            "product_type": row.product_type,
                            "tags": row.tags,
                            "body_html_stripped": body_stripped,
                            "option1_name": row.option1_name,
                            "option1_value": row.option1_value,
                            "option2_name": row.option2_name,
                            "option2_value": row.option2_value,
                            "missing_fields": [field_name],
                        })
                        row_has_inference_entry = True

    # Serialize conflicts for the deterministic_fills.json artifact
    conflicts_for_artifact = []
    for c in conflicts:
        entry = {
            "handle": c["handle"],
            "row_number": c["row_number"],
            "variant_sku": c.get("variant_sku", ""),
            "field": c["field"],
            "reason": c.get("reason", "conflict_between_sources"),
        }
        if "existing_value" in c:
            entry["existing_value"] = c["existing_value"]
        if "extracted_value" in c:
            entry["extracted_value"] = c["extracted_value"]
        entry["evidence_quote"] = c.get("evidence_quote", "")
        entry["confidence"] = c.get("confidence")
        if "candidates" in c:
            entry["candidates"] = c["candidates"]
        conflicts_for_artifact.append(entry)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Write deterministic_fills.json (Stage 3 reads this)
    det_fills_path = output_dir / "deterministic_fills.json"
    det_fills_artifact = {
        "fills": deterministic_fills,
        "conflicts": conflicts_for_artifact,
        "needs_review": needs_review_pre,
    }
    with open(det_fills_path, "w", encoding="utf-8") as f:
        json.dump(det_fills_artifact, f, indent=2, default=str)

    # Write needs_inference.json (LLM stage reads this)
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
        json.dump(inference_output, f, indent=2, default=str)

    # Audit report for stdout
    audit_report = {
        "metadata": {
            **csv_metadata,
            "total_apparel_products": len(apparel_groups),
            "skipped_non_apparel": len(skipped_non_apparel),
            "deterministic_fills_made": len(deterministic_fills),
            "rows_needing_inference": len(needs_inference_rows),
            "conflicts_detected": len(conflicts),
            "needs_review_pre_fill": len(needs_review_pre),
            "attribute_columns_detected": attr_columns,
            "prohibited_columns_found": prohibited_found,
            "work_dir": str(output_dir),
            "deterministic_fills_file": str(det_fills_path),
            "needs_inference_file": str(inference_path),
        },
        "deterministic_fills": deterministic_fills,
        "conflicts": conflicts,
        "needs_review": needs_review_pre,
        "skipped_non_apparel": [g["handle"] for g in skipped_non_apparel],
    }

    return audit_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect and fill missing product attributes in a Shopify product CSV."
    )
    parser.add_argument("csv_path", type=Path, help="Path to Shopify product CSV")
    parser.add_argument(
        "--assets-dir", type=Path, default=None,
        help="Path to assets/ directory (default: assets/ relative to this script)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Directory for output JSON files (default: same directory as csv_path)",
    )
    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"Fatal: File not found: {args.csv_path}", file=sys.stderr)
        return 1
    if not args.csv_path.is_file():
        print(f"Fatal: Not a file: {args.csv_path}", file=sys.stderr)
        return 1
    if args.csv_path.suffix.lower() in (".xlsx", ".xls"):
        print(
            "Fatal: File is an Excel workbook (.xlsx/.xls). "
            "Export as a CSV from Shopify Admin: Products > Export > Plain CSV file.",
            file=sys.stderr,
        )
        return 1

    assets_dir = args.assets_dir
    if assets_dir is None:
        assets_dir = Path(__file__).parent.parent / "assets"

    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = Path(tempfile.mkdtemp(prefix="fill-attrs-"))

    try:
        result = run_detection(args.csv_path, assets_dir, output_dir)
    except SystemExit:
        raise
    except Exception as e:
        print(f"Fatal: Detection failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1

    json.dump(result, sys.stdout, indent=2,
              default=lambda o: sorted(o) if isinstance(o, (set, frozenset)) else str(o))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
classify_taxonomy.py - Google Product Taxonomy keyword classifier

Usage:
    python3 scripts/classify_taxonomy.py <csv_path> --assets-dir assets/
    python3 scripts/classify_taxonomy.py <csv_path> --assets-dir assets/ \\
        --title-col "Title" --desc-col "Body (HTML)"
    python3 scripts/classify_taxonomy.py <csv_path> --assets-dir assets/ \\
        --preserve-existing

Outputs JSON to stdout. Exit code 0 on success, 1 on fatal error.
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

SCRIPT_VERSION = "0.3.0"

TITLE_CANDIDATES = [
    "Title", "title", "Product Title", "Name", "name", "product_title",
]
DESC_CANDIDATES = [
    "Body (HTML)", "Body", "description", "Description",
    "body_html", "Product Description", "Body HTML",
]
HANDLE_CANDIDATES = [
    "Handle", "handle", "ID", "id", "SKU", "sku", "Product ID", "Variant SKU",
]
CATEGORY_CANDIDATES = [
    "google_product_category", "Google Product Category",
    "Google_Product_Category", "g:google_product_category",
]

HIGH_MIN_SCORE = 6
HIGH_GAP = 3
MEDIUM_MIN_SCORE = 3
# Depth bonus makes deeper categories win ties without overriding genuine score gaps.
# A tier-7 category over tier-2 adds at most 0.5, less than any real keyword match.
DEPTH_BONUS = 0.1


class _Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts)


def strip_html(text: str) -> str:
    if not text:
        return ""
    stripper = _Stripper()
    try:
        stripper.feed(text)
        return stripper.get_text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", text)


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tok(phrase: str) -> frozenset:
    return frozenset(normalize(phrase).split())


# Pre-tokenized for whole-word matching (prevents "mead" from matching "meadow" etc.)
ALCOHOL_KEYWORDS: list[frozenset] = [
    _tok(kw) for kw in [
        "wine", "beer", "whiskey", "vodka", "spirits", "brewing kit",
        "homebrew", "mead", "cider", "bourbon", "rum", "gin", "liqueur",
        "ale", "lager", "stout", "porter", "champagne", "prosecco", "sake",
        "hard seltzer", "alcoholic beverage", "craft beer",
    ]
]

BUNDLE_PHRASE_KEYWORDS: list[frozenset] = [
    _tok(kw) for kw in [
        "bundle", "starter kit", "gift set", "value pack", "multipack",
        "value bundle", "combo pack", "pack of", "pair of",
    ]
]
# n-pack patterns require the digits to be adjacent to "pack" in the source text.
_NPACK_RE = re.compile(r"\b\d+-pack\b", re.IGNORECASE)


def load_taxonomy(assets_dir: str) -> list[dict]:
    path = Path(assets_dir) / "taxonomy-keywords.json"
    if not path.exists():
        _fatal(f"taxonomy-keywords.json not found at: {path}")
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        categories = data.get("categories", [])
        if not categories:
            _fatal("taxonomy-keywords.json contains no categories")
    except json.JSONDecodeError as exc:
        _fatal(f"Invalid JSON in taxonomy-keywords.json: {exc}")

    # Precompute keyword token frozensets so the hot scoring loop does no
    # string work per product call.
    for cat in categories:
        raw = cat.get("keywords", {})
        cat["_kw_tokens"] = {
            tier: [
                (frozenset(normalize(kw).split()), kw)
                for kw in raw.get(tier, [])
                if kw.strip()
            ]
            for tier in ("high", "medium", "low")
        }

    # Detect duplicate non-null IDs — these produce wrong google_product_category_id
    # values in the output CSV. Null out the duplicates and warn so merchants don't
    # submit incorrect IDs to Google Merchant Center.
    id_counts = Counter(
        cat["id"] for cat in categories if cat.get("id") is not None
    )
    dupes = {id_ for id_, cnt in id_counts.items() if cnt > 1}
    if dupes:
        for cat in categories:
            if cat.get("id") in dupes:
                print(
                    f"WARNING: duplicate ID {cat['id']} in taxonomy-keywords.json "
                    f"for path '{cat['path']}' — setting id to null. "
                    f"Verify at https://www.google.com/basepages/producttype/"
                    f"taxonomy-with-ids.en-US.txt",
                    file=sys.stderr,
                )
                cat["id"] = None

    return categories


def score_category(tokens: set, category: dict) -> tuple:
    score = 0
    matched: list[str] = []
    weights = (("high", 3), ("medium", 2), ("low", 1))
    for tier_name, weight in weights:
        for kw_tokens, kw_str in category["_kw_tokens"][tier_name]:
            if kw_tokens.issubset(tokens):
                score += weight
                matched.append(kw_str)
    return score, matched


def classify(title: str, description: str, categories: list[dict]) -> dict:
    combined = strip_html(title + " " + description)
    tokens = set(normalize(combined).split())

    scored: list[dict] = []
    for cat in categories:
        raw_score, matched = score_category(tokens, cat)
        if raw_score > 0:
            # Deeper categories break ties: tier 5 beats tier 3 at equal raw score.
            effective_score = raw_score + (cat.get("tier", 1) - 2) * DEPTH_BONUS
            scored.append({
                "path": cat["path"],
                "id": cat["id"],
                "score": effective_score,
                "matched_keywords": matched,
            })

    scored.sort(key=lambda x: x["score"], reverse=True)

    if not scored:
        return {
            "proposed_category_path": None,
            "proposed_category_id": None,
            "confidence": "low",
            "matched_keywords": [],
            "alternatives": [],
        }

    top = scored[0]
    runner_up_score = scored[1]["score"] if len(scored) > 1 else 0
    gap = top["score"] - runner_up_score

    if top["score"] >= HIGH_MIN_SCORE and gap >= HIGH_GAP:
        confidence = "high"
    elif top["score"] >= MEDIUM_MIN_SCORE:
        confidence = "medium"
    else:
        confidence = "low"

    alternatives = [
        {"path": s["path"], "id": s["id"], "score": round(s["score"], 2)}
        for s in scored[1:3]
    ]

    return {
        "proposed_category_path": top["path"],
        "proposed_category_id": top["id"],
        "confidence": confidence,
        "matched_keywords": top["matched_keywords"],
        "alternatives": alternatives,
    }


def _phrase_matches(tokens: set, phrase_sets: list[frozenset]) -> bool:
    """Return True if any phrase (as a frozenset of tokens) is a subset of tokens."""
    return any(phrase.issubset(tokens) for phrase in phrase_sets)


def check_policy_flags(
    title: str, description: str, proposed_path: str | None
) -> list[str]:
    """Return policy flags that the LLM must act on (see SKILL.md Policy Enforcement)."""
    flags: list[str] = []
    tokens = set(normalize(title + " " + description).split())

    if _phrase_matches(tokens, ALCOHOL_KEYWORDS):
        flags.append("alcohol_regulated")

    if proposed_path and proposed_path.startswith("Apparel & Accessories"):
        flags.append("apparel_requires_attributes")

    if proposed_path and proposed_path.startswith("Software"):
        flags.append("software_digital")
    elif _phrase_matches(tokens, [frozenset(["digital", "download"]),
                                   frozenset(["digital", "product"])]):
        flags.append("software_digital")

    return flags


def detect_bundle(title: str, description: str) -> bool:
    """Return True if title or description contains bundle/kit/multipack signals."""
    combined = title + " " + description
    tokens = set(normalize(combined).split())
    return _phrase_matches(tokens, BUNDLE_PHRASE_KEYWORDS) or bool(_NPACK_RE.search(combined))


def detect_col(headers: list[str], candidates: list[str]) -> str | None:
    header_map = {h.lower(): h for h in headers}
    for c in candidates:
        if c in headers:
            return c
        if c.lower() in header_map:
            return header_map[c.lower()]
    return None


def _open_csv(csv_path: str) -> tuple:
    """Open CSV with UTF-8-sig, falling back to latin-1. Returns (rows, headers, encoding_used, encoding_warning)."""
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            with open(csv_path, encoding=encoding, newline="") as fh:
                reader = csv.DictReader(fh)
                headers = list(reader.fieldnames or [])
                rows = list(reader)
            warning = (
                f"File decoded as {encoding} (not UTF-8); check output for garbled characters."
                if encoding != "utf-8-sig"
                else None
            )
            return rows, headers, encoding, warning
        except UnicodeDecodeError:
            continue
    _fatal("Could not decode file as UTF-8 or latin-1.")


def load_csv(
    csv_path: str,
    title_col_arg: str | None,
    desc_col_arg: str | None,
) -> tuple:
    if not Path(csv_path).exists():
        _fatal(f"File not found: {csv_path}")
    try:
        rows, headers, encoding_used, encoding_warning = _open_csv(csv_path)

        title_col = title_col_arg or detect_col(headers, TITLE_CANDIDATES)
        desc_col = desc_col_arg or detect_col(headers, DESC_CANDIDATES)
        handle_col = detect_col(headers, HANDLE_CANDIDATES)
        category_col = detect_col(headers, CATEGORY_CANDIDATES)

        if not title_col:
            _fatal(
                f"Could not detect a title column.\n"
                f"Columns found: {', '.join(headers)}\n"
                f"Use --title-col to specify the column name."
            )

        return rows, title_col, desc_col, handle_col, category_col, headers, encoding_used, encoding_warning

    except csv.Error as exc:
        _fatal(f"CSV parse error: {exc}")


def deduplicate(rows: list[dict], title_col: str) -> list[dict]:
    """
    Shopify exports repeat the product Handle on every variant row but only
    put the Title on the first row. Keep only rows that have a non-empty title
    so we classify each product once.
    """
    seen: set[str] = set()
    deduped: list[dict] = []
    for row in rows:
        title = row.get(title_col, "").strip()
        if not title:
            continue
        key = title.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    return deduped


def _fatal(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify products against the Google Product Taxonomy."
    )
    parser.add_argument("csv_path", help="Path to product CSV file")
    parser.add_argument(
        "--assets-dir", default="assets/",
        help="Directory containing taxonomy-keywords.json (default: assets/)",
    )
    parser.add_argument(
        "--title-col",
        help="Column name for product title (auto-detected if omitted)",
    )
    parser.add_argument(
        "--desc-col",
        help="Column name for product description (auto-detected if omitted)",
    )
    parser.add_argument(
        "--keep-variants", action="store_true",
        help="Skip Shopify variant-row deduplication (classify every row)",
    )
    parser.add_argument(
        "--preserve-existing", action="store_true",
        help=(
            "Skip products that already have a google_product_category value "
            "3 or more levels deep (2+ ' > ' separators). Outputs confidence "
            "'preserved' for those rows."
        ),
    )
    args = parser.parse_args()

    categories = load_taxonomy(args.assets_dir)
    rows, title_col, desc_col, handle_col, category_col, _, encoding_used, encoding_warning = load_csv(
        args.csv_path, args.title_col, args.desc_col
    )

    if not args.keep_variants:
        rows = deduplicate(rows, title_col)

    results: list[dict] = []
    counts: dict[str, int] = {"high": 0, "medium": 0, "low": 0, "preserved": 0}

    for i, row in enumerate(rows, start=2):
        title = row.get(title_col, "").strip()
        desc = row.get(desc_col, "").strip() if desc_col else ""
        handle = row.get(handle_col, "").strip() if handle_col else ""

        # Preserve deeply-mapped categories when requested.
        if args.preserve_existing and category_col:
            existing = row.get(category_col, "").strip()
            if existing.count(" > ") >= 2:
                counts["preserved"] += 1
                results.append({
                    "row": i,
                    "handle": handle,
                    "title": title,
                    "proposed_category_path": existing,
                    "proposed_category_id": None,
                    "confidence": "preserved",
                    "matched_keywords": [],
                    "alternatives": [],
                    "policy_flags": [],
                    "is_bundle": False,
                })
                continue

        result = classify(title, desc, categories)
        counts[result["confidence"]] += 1

        policy_flags = check_policy_flags(title, desc, result["proposed_category_path"])
        is_bundle = detect_bundle(title, desc)

        entry: dict = {
            "row": i,
            "handle": handle,
            "title": title,
            **result,
            "policy_flags": policy_flags,
            "is_bundle": is_bundle,
        }
        if is_bundle:
            entry["bundle_note"] = (
                "Bundle/kit detected. Classify by the primary item in the bundle."
            )
        results.append(entry)

    meta: dict = {
        "script_version": SCRIPT_VERSION,
        "products_scanned": len(results),
        "high_confidence": counts["high"],
        "medium_confidence": counts["medium"],
        "low_confidence": counts["low"],
        "preserved_existing": counts["preserved"],
        "title_col": title_col,
        "desc_col": desc_col if desc_col else "(not found)",
        "handle_col": handle_col if handle_col else "(not found)",
        "encoding_used": encoding_used,
    }
    if encoding_warning:
        meta["encoding_warning"] = encoding_warning

    output = {
        "meta": meta,
        "results": results,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

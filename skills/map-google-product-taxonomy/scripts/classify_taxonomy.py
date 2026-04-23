#!/usr/bin/env python3
"""
classify_taxonomy.py - Google Product Taxonomy keyword classifier

Usage:
    python3 scripts/classify_taxonomy.py <csv_path> --assets-dir assets/
    python3 scripts/classify_taxonomy.py <csv_path> --assets-dir assets/ \\
        --title-col "Title" --desc-col "Body (HTML)"

Outputs JSON to stdout. Exit code 0 on success, 1 on fatal error.
"""

import argparse
import csv
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SCRIPT_VERSION = "0.1.0"

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

HIGH_MIN_SCORE = 6
HIGH_GAP = 3
MEDIUM_MIN_SCORE = 3


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
        return categories
    except json.JSONDecodeError as exc:
        _fatal(f"Invalid JSON in taxonomy-keywords.json: {exc}")


def score_category(tokens: set, category: dict) -> tuple:
    keywords = category.get("keywords", {})
    score = 0
    matched: list[str] = []

    for kw in keywords.get("high", []):
        kw_tokens = set(normalize(kw).split())
        if kw_tokens and kw_tokens.issubset(tokens):
            score += 3
            matched.append(kw)

    for kw in keywords.get("medium", []):
        kw_tokens = set(normalize(kw).split())
        if kw_tokens and kw_tokens.issubset(tokens):
            score += 2
            matched.append(kw)

    for kw in keywords.get("low", []):
        kw_tokens = set(normalize(kw).split())
        if kw_tokens and kw_tokens.issubset(tokens):
            score += 1
            matched.append(kw)

    return score, matched


def classify(title: str, description: str, categories: list[dict]) -> dict:
    combined = strip_html(title + " " + description)
    tokens = set(normalize(combined).split())

    scored: list[dict] = []
    for cat in categories:
        score, matched = score_category(tokens, cat)
        if score > 0:
            scored.append({
                "path": cat["path"],
                "id": cat["id"],
                "score": score,
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
        {"path": s["path"], "id": s["id"], "score": s["score"]}
        for s in scored[1:3]
    ]

    return {
        "proposed_category_path": top["path"],
        "proposed_category_id": top["id"],
        "confidence": confidence,
        "matched_keywords": top["matched_keywords"],
        "alternatives": alternatives,
    }


def detect_col(headers: list[str], candidates: list[str]) -> str | None:
    header_map = {h.lower(): h for h in headers}
    for c in candidates:
        if c in headers:
            return c
        if c.lower() in header_map:
            return header_map[c.lower()]
    return None


def load_csv(
    csv_path: str,
    title_col_arg: str | None,
    desc_col_arg: str | None,
) -> tuple:
    if not Path(csv_path).exists():
        _fatal(f"File not found: {csv_path}")
    try:
        with open(csv_path, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            headers = list(reader.fieldnames or [])

            title_col = title_col_arg or detect_col(headers, TITLE_CANDIDATES)
            desc_col = desc_col_arg or detect_col(headers, DESC_CANDIDATES)
            handle_col = detect_col(headers, HANDLE_CANDIDATES)

            if not title_col:
                _fatal(
                    f"Could not detect a title column.\n"
                    f"Columns found: {', '.join(headers)}\n"
                    f"Use --title-col to specify the column name."
                )

            rows = list(reader)

        return rows, title_col, desc_col, handle_col, headers

    except UnicodeDecodeError:
        _fatal(
            "Could not decode file as UTF-8. "
            "Re-export from Shopify Admin using UTF-8 encoding."
        )
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
    args = parser.parse_args()

    categories = load_taxonomy(args.assets_dir)
    rows, title_col, desc_col, handle_col, _ = load_csv(
        args.csv_path, args.title_col, args.desc_col
    )

    if not args.keep_variants:
        rows = deduplicate(rows, title_col)

    results: list[dict] = []
    counts: dict[str, int] = {"high": 0, "medium": 0, "low": 0}

    for i, row in enumerate(rows, start=2):
        title = row.get(title_col, "").strip()
        desc = row.get(desc_col, "").strip() if desc_col else ""
        handle = row.get(handle_col, "").strip() if handle_col else ""

        result = classify(title, desc, categories)
        counts[result["confidence"]] += 1

        results.append({
            "row": i,
            "handle": handle,
            "title": title,
            **result,
        })

    output = {
        "meta": {
            "script_version": SCRIPT_VERSION,
            "products_scanned": len(results),
            "high_confidence": counts["high"],
            "medium_confidence": counts["medium"],
            "low_confidence": counts["low"],
            "title_col": title_col,
            "desc_col": desc_col if desc_col else "(not found)",
            "handle_col": handle_col if handle_col else "(not found)",
        },
        "results": results,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

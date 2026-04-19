#!/usr/bin/env python3
"""Apply approved attribute fills to a Shopify product CSV.

Reads the original CSV, deterministic_fills.json (from Stage 1), and
approved_fills.json (from Stage 2 LLM inference + user review). Merges both
fill sources and writes three output files:

    <stem>-filled.csv   Corrected CSV, same column structure as input
    change_log.md       Record of every change made (Markdown)
    needs_review.csv    Items that could not be written

Usage:
    python3 scripts/apply_fills.py <csv_path> \\
        [--deterministic-fills deterministic_fills.json] \\
        [--approved-fills approved_fills.json] \\
        [--output-dir /path/to/output/] \\
        [--dry-run]

Exit codes:
    0 - Completed successfully
    1 - Fatal error
    2 - Validation failure (would produce incorrect output)
"""

import argparse
import csv
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_VERSION = "2.0.0"

VALID_GENDER = {"male", "female", "unisex"}
VALID_AGE_GROUP = {"newborn", "infant", "toddler", "kids", "adult"}

ENUM_VALIDATORS: dict[str, set[str]] = {
    "gender": VALID_GENDER,
    "age_group": VALID_AGE_GROUP,
}

FIELD_THRESHOLDS = {
    "gender": 0.90,
    "age_group": 0.90,
    "color": 0.80,
    "material": 0.70,
    "size": 0.95,
    "size_system": 0.95,
    "size_type": 0.90,
}

PROHIBITED_COLUMNS = frozenset({"Option1 Value", "Option2 Value", "Option3 Value"})

REASON_LABELS: dict[str, str] = {
    "conflict_with_existing_value": "Conflicts with existing value",
    "conflict_between_sources": "Conflicting sources",
    "below_threshold": "Low confidence",
    "too_many_colors": "Too many colors (max 3 allowed)",
    "no_target_column_in_csv": "No target column in CSV",
    "non_english_input": "Non-English product",
    "llm_returned_null": "Insufficient data for inference",
    "llm_insufficient_context": "Insufficient data for inference",
    "user_rejected": "Rejected by user",
    "not_approved": "Not confirmed",
}

REASON_ACTIONS: dict[str, str] = {
    "conflict_with_existing_value": "Check both values and update the correct one in Shopify admin.",
    "conflict_between_sources": "Multiple sources suggest different values. Verify the correct value in Shopify admin.",
    "below_threshold": "Low confidence fill. Verify the suggested value before importing.",
    "too_many_colors": "Google allows max 3 slash-separated colors. Edit to keep the 3 most important.",
    "no_target_column_in_csv": "Re-export CSV with Google Shopping columns enabled, then re-run this skill.",
    "non_english_input": "Non-English product. Fill this attribute manually in Shopify admin.",
    "llm_returned_null": "Not enough product data to infer. Fill manually in Shopify admin.",
    "llm_insufficient_context": "Not enough product data to infer. Fill manually in Shopify admin.",
    "user_rejected": "You rejected this fill. Update manually in Shopify admin if needed.",
    "not_approved": "Fill was not confirmed. Update manually in Shopify admin if needed.",
}

_HIGH_PRIORITY_REASONS = {"conflict_with_existing_value", "conflict_between_sources"}
_LOW_PRIORITY_REASONS = {"no_target_column_in_csv", "non_english_input", "user_rejected", "not_approved"}
_HIGH_PRIORITY_FIELDS = {"gender", "age_group"}

_SOURCE_LABELS: dict[str, str] = {
    "option_value": "Option value",
    "title_color_vocab": "Title color vocabulary match",
    "title_color_bigram": "Title color bigram match",
    "title_material_vocab": "Title keyword match",
    "title_material_synonym": "Title synonym match",
    "title_gender_keyword": "Title gender keyword",
    "title_age_keyword": "Title age keyword",
    "body_compound_material": "Body compound material match",
    "tag_prefix": "Tag prefix",
    "llm_inference": "LLM inference",
    "sibling_propagation": "Sibling variant propagation",
    "llm_title_inference": "LLM title inference",
}


def _write_change_log_md(
    path: Path,
    rows: list[dict],
    title_lookup: dict[str, str],
) -> None:
    timestamp = rows[0].get("Timestamp", "") if rows else ""
    by_handle: dict[str, list[dict]] = {}
    for row in rows:
        by_handle.setdefault(row.get("Handle", ""), []).append(row)

    lines: list[str] = [
        "# Attribute Fill Change Log",
        "",
        f"Run timestamp: `{timestamp}`",
        "",
        f"**{len(rows)} attributes filled** across **{len(by_handle)} products**",
        "",
        "| Symbol | Meaning |",
        "|--------|---------|",
        "| REVIEW | Needs human review before importing |",
        "| OK | High confidence, safe to import |",
        "",
        "---",
        "",
    ]

    for handle, changes in by_handle.items():
        title = title_lookup.get(handle, "")
        lines.append(f"## {handle}")
        if title:
            lines += ["", f"**{title}**"]
        lines += [
            "",
            "| Field | Value Set | Source | Confidence | Status |",
            "|-------|-----------|--------|------------|--------|",
        ]
        for ch in changes:
            field = ch.get("Target Column") or ch.get("Field", "")
            value = ch.get("New Value", "")
            source_key = ch.get("Source", "")
            evidence = ch.get("Evidence Quote", "")
            source_label = _SOURCE_LABELS.get(source_key, source_key)
            source_cell = f"{source_label}: `{evidence}`" if evidence else source_label
            conf_raw = ch.get("Confidence", "")
            try:
                conf_pct = f"{float(conf_raw) * 100:.0f}%"
            except (ValueError, TypeError):
                conf_pct = str(conf_raw)
            status = "REVIEW" if str(ch.get("Needs Review", "")).upper() == "TRUE" else "OK"
            lines.append(f"| {field} | {value} | {source_cell} | {conf_pct} | {status} |")
        lines += ["", "---", ""]

    lines += [
        "## Source Legend",
        "",
        "| Source Key | Meaning |",
        "|------------|---------|",
        "| `option_value` | Extracted directly from Shopify variant option (Color, Size, etc.) |",
        "| `title_color_vocab` | Matched a known color word in the product title |",
        "| `title_color_bigram` | Matched a two-word color phrase in the product title |",
        "| `title_material_vocab` | Matched a known material word in the product title |",
        '| `title_material_synonym` | Matched a material synonym (e.g., "merino" maps to Wool) |',
        "| `title_gender_keyword` | Matched a gender keyword in the product title (e.g., \"Men's\", \"Women's\") |",
        '| `title_age_keyword` | Matched an age keyword in the product title (e.g., "Baby", "Kids") |',
        "| `body_compound_material` | Extracted dominant material from a compound fabric description in the body |",
        '| `tag_prefix` | Read from a structured Shopify tag (e.g., `color:red`, `gender:female`) |',
        "| `llm_inference` | Inferred by the language model from available product context |",
        "| `sibling_propagation` | Copied from another variant of the same product |",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _get_priority(reason_code: str, field: str) -> str:
    if reason_code in _HIGH_PRIORITY_REASONS:
        return "HIGH"
    if reason_code in _LOW_PRIORITY_REASONS:
        return "LOW"
    if field in _HIGH_PRIORITY_FIELDS:
        return "HIGH"
    if field == "color":
        return "MEDIUM"
    return "LOW"


def _build_title_lookup(rows: list[dict]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for row in rows:
        handle = (row.get("Handle") or "").strip()
        title = (row.get("Title") or "").strip()
        if handle and title and handle not in lookup:
            lookup[handle] = title
    return lookup


def _enrich_needs_review(entries: list[dict], title_lookup: dict[str, str]) -> list[dict]:
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    enriched = []
    for e in entries:
        reason_code = e.get("Reason", "")
        field = e.get("Field", "")
        enriched.append({
            **e,
            "Product Title": title_lookup.get(e.get("Handle", ""), ""),
            "Priority": _get_priority(reason_code, field),
            "Reason": REASON_LABELS.get(reason_code, reason_code),
            "Action": REASON_ACTIONS.get(reason_code, "Resolve manually in Shopify admin."),
        })
    enriched.sort(key=lambda x: priority_order.get(x.get("Priority", "LOW"), 2))
    return enriched


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


def parse_csv(file_path: Path) -> tuple[list[dict], list[str]]:
    encoding, _ = detect_encoding_and_bom(file_path)
    try:
        with open(file_path, newline="", encoding=encoding) as f:
            reader = csv.DictReader(f)
            columns = list(reader.fieldnames or [])
            rows = list(reader)
    except UnicodeDecodeError:
        with open(file_path, newline="", encoding="latin-1") as f:
            reader = csv.DictReader(f)
            columns = list(reader.fieldnames or [])
            rows = list(reader)
    return rows, columns


# ---------------------------------------------------------------------------
# Robust JSON parsing (handles LLM output artifacts)
# ---------------------------------------------------------------------------

def parse_llm_json(raw: str) -> dict:
    """Parse JSON that may contain markdown fences, trailing commas, or smart quotes."""
    s = raw.strip()
    s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.MULTILINE)
    s = re.sub(r"\s*```\s*$", "", s, flags=re.MULTILINE)
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = re.sub(r",(\s*[}\]])", r"\1", s)
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"JSON parse failed: {e}\n")
        sys.stderr.write(f"First 500 chars:\n{s[:500]}\n")
        sys.exit(2)


def load_fills_file(path: Path) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        return parse_llm_json(raw)
    except FileNotFoundError:
        print(f"Fatal: File not found: {path}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def is_prohibited_column(col: str) -> bool:
    if col in PROHIBITED_COLUMNS:
        return True
    if col.startswith("Variant Metafield:"):
        return True
    return False


def validate_fills(fills: list[dict], column_set: set[str]) -> list[str]:
    errors: list[str] = []
    for fill in fills:
        if not fill.get("approved") or fill.get("proposed_value") is None:
            continue

        field = fill.get("field", "")
        target_col = fill.get("target_column", "")
        row_number = fill.get("row_number", "?")
        value = fill.get("proposed_value", "")

        if not target_col:
            errors.append(f"Row {row_number}: missing target_column for field '{field}'")
            continue

        if is_prohibited_column(target_col):
            errors.append(
                f"Row {row_number}: target_column '{target_col}' is prohibited "
                "(never write to Option Values or Variant Metafields)"
            )

        if target_col not in column_set:
            errors.append(f"Row {row_number}: target_column '{target_col}' not in CSV header")
            continue

        if field in ENUM_VALIDATORS:
            if value.lower() not in ENUM_VALIDATORS[field]:
                errors.append(
                    f"Row {row_number}: invalid {field} value '{value}'. "
                    f"Must be one of: {sorted(ENUM_VALIDATORS[field])}"
                )

    return errors


def verify_non_target_columns_unchanged(
    input_rows: list[dict],
    output_rows: list[dict],
    target_columns: set[str],
) -> list[str]:
    """Return error strings for any non-target column that changed between input and output."""
    errors: list[str] = []
    for idx, (inp, out) in enumerate(zip(input_rows, output_rows)):
        for col in inp:
            if col in target_columns:
                continue
            if inp.get(col) != out.get(col):
                errors.append(
                    f"Row {idx + 2}: non-target column '{col}' was modified. "
                    f"Input: {inp.get(col)!r}, Output: {out.get(col)!r}"
                )
    return errors


# ---------------------------------------------------------------------------
# Apply fills
# ---------------------------------------------------------------------------

def apply_fills(
    csv_path: Path,
    deterministic_fills_path: Path | None,
    approved_fills_path: Path | None,
    output_dir: Path,
    work_dir: Path | None = None,
    dry_run: bool = False,
) -> int:
    rows, columns = parse_csv(csv_path)
    if not columns:
        print("Fatal: CSV has no columns.", file=sys.stderr)
        return 1
    if not rows:
        print("Warning: CSV contains no data rows. Nothing to process.", file=sys.stderr)

    column_set = set(columns)
    title_lookup = _build_title_lookup(rows)

    all_fills: list[dict] = []
    all_conflicts: list[dict] = []
    all_needs_review_pre: list[dict] = []

    # Load deterministic fills (Stage 1 output, pre-approved)
    if deterministic_fills_path and deterministic_fills_path.exists():
        det_data = load_fills_file(deterministic_fills_path)
        all_fills.extend(det_data.get("fills", []))
        all_conflicts.extend(det_data.get("conflicts", []))
        all_needs_review_pre.extend(det_data.get("needs_review", []))

    # Load approved fills (Stage 2 LLM output after merchant review)
    if approved_fills_path and approved_fills_path.exists():
        appr_data = load_fills_file(approved_fills_path)
        all_fills.extend(appr_data.get("fills", []))
        all_conflicts.extend(appr_data.get("conflicts", []))

    if not all_fills and not all_conflicts and not all_needs_review_pre:
        print("Warning: No fills or conflicts found in any input file.", file=sys.stderr)

    # Separate approved fills from everything else
    approved: list[dict] = []
    needs_review_entries: list[dict] = []

    for fill in all_fills:
        value = fill.get("proposed_value")
        if fill.get("approved") is True and value is not None:
            approved.append(fill)
        else:
            if value is None:
                reason = "llm_returned_null"
            elif fill.get("approved") is False:
                reason = fill.get("reject_reason", "user_rejected")
            else:
                reason = fill.get("reject_reason", "not_approved")
            needs_review_entries.append({
                "Handle": fill.get("handle", ""),
                "Variant SKU": fill.get("variant_sku", ""),
                "Field": fill.get("field", ""),
                "Target Column": fill.get("target_column", ""),
                "Reason": reason,
                "Evidence Quote": fill.get("evidence_quote", ""),
                "Confidence": fill.get("confidence", ""),
                "Suggested Value": value or "",
            })

    # Conflicts from Stage 1
    for c in all_conflicts:
        needs_review_entries.append({
            "Handle": c.get("handle", ""),
            "Variant SKU": c.get("variant_sku", ""),
            "Field": c.get("field", ""),
            "Target Column": c.get("target_column", c.get("field", "")),
            "Reason": c.get("reason", "conflict_with_existing_value"),
            "Evidence Quote": c.get("evidence_quote", ""),
            "Confidence": c.get("confidence", ""),
            "Suggested Value": c.get("extracted_value", ""),
        })

    # Pre-fill needs_review (below-threshold, no-column, too-many-colors)
    for nr in all_needs_review_pre:
        needs_review_entries.append({
            "Handle": nr.get("handle", ""),
            "Variant SKU": nr.get("variant_sku", ""),
            "Field": nr.get("field", ""),
            "Target Column": nr.get("target_column", ""),
            "Reason": nr.get("reason", ""),
            "Evidence Quote": nr.get("evidence_quote", ""),
            "Confidence": nr.get("confidence", ""),
            "Suggested Value": nr.get("suggested_value", ""),
        })

    errors = validate_fills(approved, column_set)
    if errors:
        print("Validation errors — no output written:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 2

    # Collect the set of target columns actually being written to
    target_columns: set[str] = set()
    for fill in approved:
        tc = fill.get("target_column", "")
        if tc and not is_prohibited_column(tc):
            target_columns.add(tc)

    fills_by_row: dict[int, list[dict]] = {}
    for fill in approved:
        rn = fill.get("row_number")
        if rn is not None:
            fills_by_row.setdefault(rn, []).append(fill)

    timestamp = datetime.now(timezone.utc).isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)

    output_rows: list[dict] = []
    change_log_rows: list[dict] = []

    for idx, row in enumerate(rows):
        row_number = idx + 2
        output_row = dict(row)

        for fill in fills_by_row.get(row_number, []):
            field = fill["field"]
            target_col = fill["target_column"]
            proposed = fill["proposed_value"]
            confidence = fill.get("confidence", 1.0)

            if is_prohibited_column(target_col):
                continue

            existing = (row.get(target_col) or "").strip()
            if existing:
                needs_review_entries.append({
                    "Handle": fill.get("handle", ""),
                    "Variant SKU": fill.get("variant_sku", ""),
                    "Field": field,
                    "Target Column": target_col,
                    "Reason": "conflict_with_existing_value",
                    "Evidence Quote": fill.get("evidence_quote", ""),
                    "Confidence": confidence,
                    "Suggested Value": proposed,
                })
                continue

            output_row[target_col] = proposed

            needs_review_flag = "TRUE" if (
                confidence is not None and float(confidence) < 0.90
            ) else "FALSE"

            change_log_rows.append({
                "Timestamp": timestamp,
                "Handle": fill.get("handle", ""),
                "Variant SKU": fill.get("variant_sku", ""),
                "Field": field,
                "Target Column": target_col,
                "Old Value": existing,
                "New Value": proposed,
                "Source": fill.get("source", ""),
                "Confidence": confidence,
                "Evidence Quote": fill.get("evidence_quote", ""),
                "Needs Review": needs_review_flag,
            })

        output_rows.append(output_row)

    if len(output_rows) != len(rows):
        print(
            f"Fatal: Output row count {len(output_rows)} != input row count {len(rows)}",
            file=sys.stderr,
        )
        return 1

    # Byte-identical check for non-target columns
    integrity_errors = verify_non_target_columns_unchanged(rows, output_rows, target_columns)
    if integrity_errors:
        print("Fatal: Non-target column integrity check failed — no output written:", file=sys.stderr)
        for e in integrity_errors:
            print(f"  {e}", file=sys.stderr)
        return 2

    needs_review_entries = _enrich_needs_review(needs_review_entries, title_lookup)

    if dry_run:
        print("Dry run: corrected CSV not written.", file=sys.stderr)
        _write_logs_only(output_dir, csv_path, change_log_rows, needs_review_entries, title_lookup)
        summary = {
            "status": "dry_run",
            "input_rows": len(rows),
            "fills_would_apply": len(change_log_rows),
            "needs_review_count": len(needs_review_entries),
        }
        print(json.dumps(summary, indent=2))
        return 0

    stem = csv_path.stem
    filled_path = output_dir / f"{stem}-filled.csv"
    temp_path = output_dir / f"{stem}-filled.csv.tmp"

    try:
        with open(temp_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            for r in output_rows:
                clean_row = {k: v for k, v in r.items() if k is not None}
                writer.writerow(clean_row)
        temp_path.rename(filled_path)
    except Exception as e:
        print(f"Fatal: Failed to write corrected CSV: {e}", file=sys.stderr)
        if temp_path.exists():
            temp_path.unlink()
        return 1

    change_log_path, needs_review_path = _write_logs_only(
        output_dir, csv_path, change_log_rows, needs_review_entries, title_lookup
    )

    work_dir_cleaned = False
    if work_dir and work_dir.exists():
        shutil.rmtree(work_dir, ignore_errors=True)
        work_dir_cleaned = True

    summary = {
        "status": "completed",
        "input_rows": len(rows),
        "output_rows": len(output_rows),
        "fills_applied": len(change_log_rows),
        "needs_review_count": len(needs_review_entries),
        "work_dir_cleaned": work_dir_cleaned,
        "output_files": {
            "filled_csv": str(filled_path),
            "change_log": str(change_log_path),
            "needs_review": str(needs_review_path),
        },
    }
    print(json.dumps(summary, indent=2))
    return 0


def _write_logs_only(
    output_dir: Path,
    csv_path: Path,
    change_log_rows: list[dict],
    needs_review_entries: list[dict],
    title_lookup: dict[str, str] | None = None,
) -> tuple[Path, Path]:
    change_log_path = output_dir / "change_log.md"
    _write_change_log_md(change_log_path, change_log_rows, title_lookup or {})

    needs_review_path = output_dir / "needs_review.csv"
    needs_review_fields = [
        "Priority", "Handle", "Product Title", "Variant SKU", "Field", "Target Column",
        "Reason", "Action", "Evidence Quote", "Confidence", "Suggested Value",
    ]
    with open(needs_review_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=needs_review_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(needs_review_entries)

    return change_log_path, needs_review_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply approved attribute fills to a Shopify product CSV."
    )
    parser.add_argument("csv_path", type=Path, help="Path to original Shopify product CSV")
    parser.add_argument(
        "--work-dir", type=Path, default=None,
        dest="work_dir",
        help="Temp directory from Stage 1 (work_dir in stdout JSON). Used to auto-locate "
             "deterministic_fills.json and approved_fills.json, and cleaned up after success.",
    )
    parser.add_argument(
        "--deterministic-fills", type=Path, default=None,
        dest="deterministic_fills",
        help="Path to deterministic_fills.json from Stage 1 (overrides --work-dir lookup)",
    )
    parser.add_argument(
        "--approved-fills", type=Path, default=None,
        dest="approved_fills",
        help="Path to approved_fills.json from Stage 2 (overrides --work-dir lookup)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Directory for output files (default: same directory as csv_path)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Write change_log and needs_review but NOT the corrected CSV",
    )
    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"Fatal: File not found: {args.csv_path}", file=sys.stderr)
        return 1
    if not args.csv_path.is_file():
        print(f"Fatal: Not a file: {args.csv_path}", file=sys.stderr)
        return 1

    output_dir = args.output_dir or args.csv_path.parent
    work_dir: Path | None = args.work_dir

    det_fills = args.deterministic_fills
    if det_fills is None:
        search_dirs = [work_dir, args.csv_path.parent] if work_dir else [args.csv_path.parent]
        for d in search_dirs:
            candidate = d / "deterministic_fills.json"
            if candidate.exists():
                det_fills = candidate
                break

    approved_fills = args.approved_fills
    if approved_fills is None and work_dir:
        candidate = work_dir / "approved_fills.json"
        if candidate.exists():
            approved_fills = candidate

    try:
        return apply_fills(
            args.csv_path, det_fills, approved_fills, output_dir, work_dir, args.dry_run
        )
    except SystemExit:
        raise
    except Exception as e:
        print(f"Fatal: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

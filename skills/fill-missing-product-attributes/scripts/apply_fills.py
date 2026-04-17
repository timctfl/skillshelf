#!/usr/bin/env python3
"""Apply approved attribute fills to a Shopify product CSV.

Reads the original CSV plus approved_fills.json (produced by the LLM inference
stage after user review). Writes three output files:
    <stem>-filled.csv   Corrected CSV, same column structure as input
    change_log.csv      Record of every change made
    needs_review.csv    Items that could not be written (low confidence, null, conflict, etc.)

Usage:
    python3 scripts/apply_fills.py <csv_path> <approved_fills_json> \\
        [--output-dir /path/to/output/]

Exit codes:
    0 - Completed successfully
    1 - Fatal error
    2 - Validation failure (would produce incorrect output)
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_VERSION = "1.0.0"

VALID_GENDER = {"male", "female", "unisex"}
VALID_AGE_GROUP = {"newborn", "infant", "toddler", "kids", "adult"}
VALID_SIZE_SYSTEM = {"US", "UK", "EU", "AU", "DE", "FR", "JP", "CN", "IT", "BR", "MEX"}

ENUM_VALIDATORS: dict[str, set[str]] = {
    "gender": VALID_GENDER,
    "age_group": VALID_AGE_GROUP,
}

# Columns the script must never write to regardless of what the fills say
PROHIBITED_COLUMN_PATTERNS = (
    "Option1 Value", "Option2 Value", "Option3 Value",
)


# ---------------------------------------------------------------------------
# CSV parsing (minimal — we only need rows and columns)
# ---------------------------------------------------------------------------

def detect_encoding_and_bom(file_path: Path) -> tuple[str, bool]:
    with open(file_path, "rb") as f:
        raw = f.read(4)
    if raw[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig", True
    return "utf-8-sig", False


def parse_csv(file_path: Path) -> tuple[list[dict], list[str]]:
    """Return (rows, column_names)."""
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
# Validation
# ---------------------------------------------------------------------------

def is_prohibited_column(col: str) -> bool:
    if col in PROHIBITED_COLUMN_PATTERNS:
        return True
    if col.startswith("Variant Metafield:"):
        return True
    return False


def validate_fills(
    fills: list[dict],
    rows: list[dict],
    columns: list[str],
) -> list[str]:
    """Return list of error strings. Empty = all checks pass."""
    errors: list[str] = []
    column_set = set(columns)

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
            errors.append(f"Row {row_number}: target_column '{target_col}' is prohibited — never write to Option Values or Variant Metafields")

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


# ---------------------------------------------------------------------------
# Apply fills
# ---------------------------------------------------------------------------

def apply_fills(
    csv_path: Path,
    fills_path: Path,
    output_dir: Path,
) -> int:
    """Apply approved fills to CSV. Returns 0 on success, 1/2 on error."""
    rows, columns = parse_csv(csv_path)
    if not columns:
        print("Fatal: CSV has no columns.", file=sys.stderr)
        return 1

    try:
        with open(fills_path, encoding="utf-8") as f:
            fills_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Fatal: Cannot read approved_fills.json: {e}", file=sys.stderr)
        return 1

    all_fills: list[dict] = fills_data.get("fills", [])

    # Separate approved fills from needs_review entries
    approved: list[dict] = []
    needs_review_entries: list[dict] = []

    for fill in all_fills:
        if fill.get("approved") and fill.get("proposed_value") is not None:
            approved.append(fill)
        else:
            reason = fill.get("source", "")
            if fill.get("proposed_value") is None:
                reason = "llm_returned_null"
            elif not fill.get("approved"):
                reason = fill.get("reject_reason", "user_rejected")
            needs_review_entries.append({
                "Handle": fill.get("handle", ""),
                "Variant SKU": fill.get("variant_sku", ""),
                "Field": fill.get("field", ""),
                "Target Column": fill.get("target_column", ""),
                "Reason": reason,
                "Evidence Quote": fill.get("evidence_quote", ""),
                "Confidence": fill.get("confidence", ""),
            })

    # Validation pass
    errors = validate_fills(approved, rows, columns)
    if errors:
        print("Validation errors — no output written:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 2

    # Build lookup: row_number -> list of approved fills
    fills_by_row: dict[int, list[dict]] = {}
    for fill in approved:
        rn = fill.get("row_number")
        if rn is not None:
            fills_by_row.setdefault(rn, []).append(fill)

    # Also include deterministic fills passed through the fills file
    # (detect_missing_attributes.py deterministic fills are bundled in fills_data)
    conflict_entries: list[dict] = fills_data.get("conflicts", [])
    for conflict in conflict_entries:
        needs_review_entries.append({
            "Handle": conflict.get("handle", ""),
            "Variant SKU": conflict.get("variant_sku", ""),
            "Field": conflict.get("field", ""),
            "Target Column": conflict.get("target_column", conflict.get("field", "")),
            "Reason": "conflict_with_existing_value",
            "Evidence Quote": f"Option value '{conflict.get('extracted_value','')}' vs existing '{conflict.get('existing_value','')}'",
            "Confidence": 1.0,
        })

    timestamp = datetime.now(timezone.utc).isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)

    output_rows: list[dict] = []
    change_log_rows: list[dict] = []

    for idx, row in enumerate(rows):
        row_number = idx + 2  # 1-based; header is row 1
        output_row = dict(row)  # copy

        for fill in fills_by_row.get(row_number, []):
            field = fill["field"]
            target_col = fill["target_column"]
            proposed = fill["proposed_value"]
            confidence = fill.get("confidence", 1.0)

            if is_prohibited_column(target_col):
                continue  # safety check (already caught in validation)

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
                })
                continue

            output_row[target_col] = proposed

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
                "Needs Review": "TRUE" if (confidence is not None and float(confidence) < 0.90) else "FALSE",
            })

        output_rows.append(output_row)

    # Row count check
    if len(output_rows) != len(rows):
        print(
            f"Fatal: Output row count {len(output_rows)} != input row count {len(rows)}",
            file=sys.stderr,
        )
        return 1

    # Write corrected CSV (atomic: write to temp then rename)
    stem = csv_path.stem
    filled_path = output_dir / f"{stem}-filled.csv"
    temp_path = output_dir / f"{stem}-filled.csv.tmp"

    try:
        with open(temp_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=columns, extrasaction="ignore"
            )
            writer.writeheader()
            for row in output_rows:
                # Filter out None keys (DictWriter bug with trailing commas)
                clean_row = {k: v for k, v in row.items() if k is not None}
                writer.writerow(clean_row)
        temp_path.rename(filled_path)
    except Exception as e:
        print(f"Fatal: Failed to write corrected CSV: {e}", file=sys.stderr)
        if temp_path.exists():
            temp_path.unlink()
        return 1

    # Write change_log.csv
    change_log_path = output_dir / "change_log.csv"
    change_log_fields = [
        "Timestamp", "Handle", "Variant SKU", "Field", "Target Column",
        "Old Value", "New Value", "Source", "Confidence", "Evidence Quote", "Needs Review",
    ]
    with open(change_log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=change_log_fields)
        writer.writeheader()
        writer.writerows(change_log_rows)

    # Write needs_review.csv
    needs_review_path = output_dir / "needs_review.csv"
    needs_review_fields = [
        "Handle", "Variant SKU", "Field", "Target Column", "Reason", "Evidence Quote", "Confidence",
    ]
    with open(needs_review_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=needs_review_fields)
        writer.writeheader()
        writer.writerows(needs_review_entries)

    # Print summary
    summary = {
        "status": "completed",
        "input_rows": len(rows),
        "output_rows": len(output_rows),
        "fills_applied": len(change_log_rows),
        "needs_review_count": len(needs_review_entries),
        "output_files": {
            "filled_csv": str(filled_path),
            "change_log": str(change_log_path),
            "needs_review": str(needs_review_path),
        },
    }
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply approved attribute fills to a Shopify product CSV."
    )
    parser.add_argument("csv_path", type=Path, help="Path to original Shopify product CSV")
    parser.add_argument("approved_fills", type=Path, help="Path to approved_fills.json")
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Directory for output files (default: same directory as csv_path)"
    )
    args = parser.parse_args()

    for path in (args.csv_path, args.approved_fills):
        if not path.exists():
            print(f"Fatal: File not found: {path}", file=sys.stderr)
            return 1
        if not path.is_file():
            print(f"Fatal: Not a file: {path}", file=sys.stderr)
            return 1

    output_dir = args.output_dir or args.csv_path.parent

    try:
        return apply_fills(args.csv_path, args.approved_fills, output_dir)
    except Exception as e:
        print(f"Fatal: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

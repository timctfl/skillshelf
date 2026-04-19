#!/usr/bin/env python3
"""Edge-case tests for the fill-missing-product-attributes skill.

Covers: XLSX rejection, empty CSV, --dry-run flag, needs_review.csv conflict
entries, and Latin-1 encoding. The LLM inference stage (Stage 2) is excluded
by design: it requires a live model. To test Stage 2, write a pre-built
approved_fills.json fixture and pass it directly to apply_fills.py via
--approved-fills.

Usage:
    python3 scripts/test_edge_cases.py

Exit codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
FIXTURES_DIR = SKILL_DIR / "fixtures"
SCRIPTS_DIR = SKILL_DIR / "scripts"
ASSETS_DIR = SKILL_DIR / "assets"

INPUT_CSV = FIXTURES_DIR / "test_apparel_missing.csv"

DETECT = [sys.executable, str(SCRIPTS_DIR / "detect_missing_attributes.py")]
APPLY = [sys.executable, str(SCRIPTS_DIR / "apply_fills.py")]


def run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


failures: list[str] = []


def fail(name: str, reason: str) -> None:
    failures.append(f"  [{name}] {reason}")
    print(f"FAIL [{name}]: {reason}")


def ok(name: str) -> None:
    print(f"PASS [{name}]")


# ---------------------------------------------------------------------------
# Test 1: XLSX input is rejected with a clear error
# ---------------------------------------------------------------------------
def test_xlsx_rejected() -> None:
    name = "xlsx_rejected"
    with tempfile.TemporaryDirectory() as tmp:
        fake_xlsx = Path(tmp) / "products.xlsx"
        fake_xlsx.write_bytes(b"PK\x03\x04fake excel content")
        result = run(DETECT + [str(fake_xlsx), "--assets-dir", str(ASSETS_DIR),
                                "--output-dir", tmp])
    if result.returncode != 1:
        fail(name, f"Expected exit 1, got {result.returncode}")
        return
    needle = "xlsx"
    if needle.lower() not in result.stderr.lower() and "excel" not in result.stderr.lower():
        fail(name, f"stderr did not mention xlsx/Excel: {result.stderr!r}")
        return
    ok(name)


# ---------------------------------------------------------------------------
# Test 2: Empty CSV (header-only) produces warning, not a crash
# ---------------------------------------------------------------------------
def test_empty_csv() -> None:
    name = "empty_csv"
    header = "Handle,Title,Body (HTML),Vendor,Product Category,Type,Tags,Published,Option1 Name,Option1 Value,Option2 Name,Option2 Value,Option3 Name,Option3 Value,Variant SKU,Variant Grams,Variant Price,Variant Requires Shipping,Variant Taxable,Google Shopping / Gender,Google Shopping / Age Group,Google Shopping / Color,Google Shopping / Size,Google Shopping / Material,Variant Metafield: custom.color,Status\n"
    with tempfile.TemporaryDirectory() as tmp:
        empty_csv = Path(tmp) / "empty.csv"
        empty_csv.write_text(header, encoding="utf-8")
        result = run(DETECT + [str(empty_csv), "--assets-dir", str(ASSETS_DIR),
                                "--output-dir", tmp])
    if result.returncode != 0:
        fail(name, f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}")
        return
    if "no data rows" not in result.stderr.lower():
        fail(name, f"Expected 'no data rows' warning in stderr, got: {result.stderr!r}")
        return
    ok(name)


# ---------------------------------------------------------------------------
# Test 3: --dry-run writes logs but NOT the filled CSV
# ---------------------------------------------------------------------------
def test_dry_run() -> None:
    name = "dry_run"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        det_result = run(DETECT + [str(INPUT_CSV), "--assets-dir", str(ASSETS_DIR),
                                    "--output-dir", tmp])
        if det_result.returncode != 0:
            fail(name, f"detect stage failed: {det_result.stderr}")
            return

        det_fills = tmp_dir / "deterministic_fills.json"
        apply_result = run(APPLY + [str(INPUT_CSV),
                                     "--deterministic-fills", str(det_fills),
                                     "--output-dir", tmp,
                                     "--dry-run"])
        if apply_result.returncode != 0:
            fail(name, f"apply --dry-run failed: {apply_result.stderr}")
            return

        filled_csv = tmp_dir / "test_apparel_missing-filled.csv"
        if filled_csv.exists():
            fail(name, "filled CSV should NOT exist in dry-run mode")
            return

        change_log = tmp_dir / "change_log.md"
        needs_review = tmp_dir / "needs_review.csv"
        if not change_log.exists():
            fail(name, "change_log.md should exist in dry-run mode")
            return
        if not needs_review.exists():
            fail(name, "needs_review.csv should exist in dry-run mode")
            return

    ok(name)


# ---------------------------------------------------------------------------
# Test 4: needs_review.csv contains the conflict row from fixtures
# ---------------------------------------------------------------------------
def test_needs_review_conflict_row() -> None:
    name = "needs_review_conflict_row"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        det_result = run(DETECT + [str(INPUT_CSV), "--assets-dir", str(ASSETS_DIR),
                                    "--output-dir", tmp])
        if det_result.returncode != 0:
            fail(name, f"detect stage failed: {det_result.stderr}")
            return

        det_fills = tmp_dir / "deterministic_fills.json"
        apply_result = run(APPLY + [str(INPUT_CSV),
                                     "--deterministic-fills", str(det_fills),
                                     "--output-dir", tmp])
        if apply_result.returncode != 0:
            fail(name, f"apply stage failed: {apply_result.stderr}")
            return

        needs_review_path = tmp_dir / "needs_review.csv"
        if not needs_review_path.exists():
            fail(name, "needs_review.csv not found")
            return

        with open(needs_review_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        conflict_handles = {
            r["Handle"] for r in rows
            if "conflict" in (r.get("Reason") or "").lower()
        }
        expected = {"existing-value-conflict", "product-color-conflict"}
        missing = expected - conflict_handles
        if missing:
            all_handles = {r["Handle"] for r in rows}
            fail(name,
                 f"Expected conflict handles {expected} in needs_review.csv. "
                 f"Missing: {missing}. All handles found: {all_handles}")
            return

    ok(name)


# ---------------------------------------------------------------------------
# Test 5: Latin-1 encoded CSV is parsed without error
# ---------------------------------------------------------------------------
def test_latin1_encoding() -> None:
    name = "latin1_encoding"
    # Build a minimal Latin-1 CSV with an accented character in the title.
    header = (
        "Handle,Title,Body (HTML),Vendor,Product Category,Type,Tags,Published,"
        "Option1 Name,Option1 Value,Option2 Name,Option2 Value,Option3 Name,Option3 Value,"
        "Variant SKU,Variant Grams,Variant Price,Variant Requires Shipping,Variant Taxable,"
        "Google Shopping / Gender,Google Shopping / Age Group,Google Shopping / Color,"
        "Google Shopping / Size,Google Shopping / Material,"
        "Variant Metafield: custom.color,Status\n"
    )
    row = (
        "ete-dress,\xc9t\xe9 Linen Dress,<p>A breezy summer dress.</p>,TestBrand,"
        "Apparel & Accessories > Clothing > Dresses,Women's Dresses,"
        "dresses,summer,linen,TRUE,Size,XS,,,,,"
        "120,59.00,TRUE,TRUE,,,,,,,active\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        latin1_csv = Path(tmp) / "latin1.csv"
        latin1_csv.write_bytes((header + row).encode("latin-1"))
        result = run(DETECT + [str(latin1_csv), "--assets-dir", str(ASSETS_DIR),
                                "--output-dir", tmp])
    if result.returncode != 0:
        fail(name, f"Expected exit 0, got {result.returncode}. stderr: {result.stderr}")
        return
    ok(name)


# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------
def main() -> int:
    test_xlsx_rejected()
    test_empty_csv()
    test_dry_run()
    test_needs_review_conflict_row()
    test_latin1_encoding()

    if failures:
        print(f"\n{len(failures)} test(s) failed:")
        for f in failures:
            print(f)
        return 1

    print(f"\nAll {5 - len(failures)} edge-case tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

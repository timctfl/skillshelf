#!/usr/bin/env python3
"""Regression test: run Stage 1 + Stage 3 on fixtures and diff against expected_output.csv.

All fills in expected_output.csv are deterministic (option values, tag prefixes,
title extraction, body HTML patterns). No LLM stage is exercised here.

Stage 2 (LLM inference) is excluded by design: it requires a live model and
produces non-deterministic output. To test Stage 2, write a pre-built
approved_fills.json fixture and pass it to apply_fills.py via --approved-fills.

For edge-case tests (XLSX rejection, empty CSV, --dry-run, needs_review.csv
conflict entries, Latin-1 encoding) see test_edge_cases.py.

Usage:
    python3 scripts/test_fixtures.py

Exit codes:
    0 - All rows and fields match expected_output.csv
    1 - Mismatch or pipeline error
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
EXPECTED_CSV = FIXTURES_DIR / "expected_output.csv"


def read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        rows = list(reader)
    return rows, columns


def run_stage(label: str, cmd: list) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FAIL [{label}]: exit {result.returncode}")
        if result.stderr.strip():
            print(result.stderr.strip())
        sys.exit(1)


def main() -> int:
    for path in (INPUT_CSV, EXPECTED_CSV):
        if not path.exists():
            print(f"FAIL: fixture not found: {path}")
            return 1

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        run_stage("detect", [
            sys.executable,
            str(SCRIPTS_DIR / "detect_missing_attributes.py"),
            str(INPUT_CSV),
            "--assets-dir", str(ASSETS_DIR),
            "--output-dir", str(tmp_dir),
        ])

        det_fills = tmp_dir / "deterministic_fills.json"
        if not det_fills.exists():
            print("FAIL: detect script did not produce deterministic_fills.json")
            return 1

        run_stage("apply", [
            sys.executable,
            str(SCRIPTS_DIR / "apply_fills.py"),
            str(INPUT_CSV),
            "--deterministic-fills", str(det_fills),
            "--output-dir", str(tmp_dir),
        ])

        filled_csv = tmp_dir / "test_apparel_missing-filled.csv"
        if not filled_csv.exists():
            print("FAIL: apply script did not produce filled CSV")
            return 1

        actual_rows, actual_cols = read_csv(filled_csv)
        expected_rows, expected_cols = read_csv(EXPECTED_CSV)

        failures: list[str] = []

        if actual_cols != expected_cols:
            extra = set(actual_cols) - set(expected_cols)
            missing = set(expected_cols) - set(actual_cols)
            if extra:
                failures.append(f"  extra columns in output: {sorted(extra)}")
            if missing:
                failures.append(f"  missing columns in output: {sorted(missing)}")

        if len(actual_rows) != len(expected_rows):
            failures.append(
                f"  row count: got {len(actual_rows)}, want {len(expected_rows)}"
            )

        for i, (act, exp) in enumerate(zip(actual_rows, expected_rows), start=2):
            for col in expected_cols:
                act_val = (act.get(col) or "").strip()
                exp_val = (exp.get(col) or "").strip()
                if act_val != exp_val:
                    handle = (exp.get("Handle") or act.get("Handle") or "?").strip()
                    failures.append(
                        f"  row {i} ({handle}), '{col}': got {act_val!r}, want {exp_val!r}"
                    )

        if failures:
            print(f"FAIL: {len(failures)} mismatch(es):")
            for f in failures:
                print(f)
            return 1

        print(f"PASS: {len(actual_rows)} rows. All fields match expected_output.csv")
        return 0


if __name__ == "__main__":
    sys.exit(main())

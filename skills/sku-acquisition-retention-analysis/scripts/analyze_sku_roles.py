#!/usr/bin/env python3
"""Analyze Shopify Orders CSV to compute per-SKU acquisition and retention indices.

Outputs structured JSON that an LLM reads to produce a merchandising brief.

Usage:
    python scripts/analyze_sku_roles.py orders.csv [products.csv] [--pretty]

Exit codes:
    0  Success
    1  Success with warnings (small dataset, short window, etc.)
    2  Fatal input error (missing required columns, unreadable file)
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Named constants (thresholds referenced in SKILL.md)
# ---------------------------------------------------------------------------

MIN_SKU_ORDERS = 10
ACQUISITION_INDEX_THRESHOLD = 1.4
RETENTION_INDEX_THRESHOLD = 1.4
SINGLE_PURCHASE_RATE_ALERT = 0.70
SMALL_DATASET_THRESHOLD = 200
SHORT_WINDOW_DAYS = 180

# ---------------------------------------------------------------------------
# Required columns
# ---------------------------------------------------------------------------

ORDERS_REQUIRED = {
    "Name", "Email", "Financial Status", "Cancelled at",
    "Lineitem name", "Lineitem sku", "Lineitem quantity", "Created at",
}

PRODUCTS_REQUIRED = {"Handle", "Title", "Type", "Variant SKU"}

SKIP_FINANCIAL_STATUS = {"refunded", "voided"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_csv(path: str) -> tuple[list[dict], str]:
    """Read CSV with utf-8-sig first, fall back to latin-1."""
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            with open(path, newline="", encoding=encoding) as fh:
                rows = list(csv.DictReader(fh))
            return rows, encoding
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Cannot decode {path} with utf-8-sig or latin-1")


def _check_columns(rows: list[dict], required: set[str], label: str) -> None:
    if not rows:
        return
    present = set(rows[0].keys())
    missing = required - present
    if missing:
        missing_list = ", ".join(sorted(missing))
        print(
            f"ERROR: {label} is missing required columns: {missing_list}",
            file=sys.stderr,
        )
        sys.exit(2)


def _parse_dt(value: str) -> datetime | None:
    for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None

# ---------------------------------------------------------------------------
# Phase 1: Parse and filter orders
# ---------------------------------------------------------------------------

def phase1_parse_filter(raw_rows: list[dict]) -> tuple[list[dict], dict]:
    """Drop cancelled and fully refunded/voided rows. Return valid rows and counts."""
    cancelled_dropped = 0
    refunded_voided_dropped = 0
    partially_refunded_kept = 0
    malformed_row_count = 0
    valid_rows = []

    for row in raw_rows:
        cancelled_at = row.get("Cancelled at", "").strip()
        if cancelled_at:
            cancelled_dropped += 1
            continue

        financial_status = row.get("Financial Status", "").strip().lower()
        if financial_status in SKIP_FINANCIAL_STATUS:
            refunded_voided_dropped += 1
            continue

        if financial_status == "partially_refunded":
            partially_refunded_kept += 1

        created_at_raw = row.get("Created at", "").strip()
        if not created_at_raw:
            malformed_row_count += 1
            continue

        dt = _parse_dt(created_at_raw)
        if dt is None:
            malformed_row_count += 1
            continue

        row["_dt"] = dt
        valid_rows.append(row)

    return valid_rows, {
        "cancelled_dropped": cancelled_dropped,
        "refunded_voided_dropped": refunded_voided_dropped,
        "partially_refunded_kept": partially_refunded_kept,
        "malformed_row_count": malformed_row_count,
    }

# ---------------------------------------------------------------------------
# Phase 2: Resolve customer identity
# ---------------------------------------------------------------------------

def phase2_resolve_customers(valid_rows: list[dict]) -> tuple[list[dict], int]:
    """Attach _customer_key to each row. Return rows and guest_unresolvable_count."""
    guest_unresolvable_count = 0

    for i, row in enumerate(valid_rows):
        customer_id = row.get("Customer ID", "").strip()
        email = row.get("Email", "").strip().lower()

        if customer_id and customer_id != "0":
            row["_customer_key"] = f"id:{customer_id}"
        elif email:
            row["_customer_key"] = f"email:{email}"
        else:
            order_name = row.get("Name", "").strip()
            row["_customer_key"] = f"guest-{order_name}-{i}"
            guest_unresolvable_count += 1

    return valid_rows, guest_unresolvable_count

# ---------------------------------------------------------------------------
# Phase 3: Identify first orders
# ---------------------------------------------------------------------------

def phase3_first_orders(valid_rows: list[dict]) -> dict[str, str]:
    """Return {customer_key: first_order_name}."""
    by_customer: dict[str, list] = defaultdict(list)
    for row in valid_rows:
        by_customer[row["_customer_key"]].append(row)

    first_order: dict[str, str] = {}
    for customer_key, rows in by_customer.items():
        earliest = min(rows, key=lambda r: r["_dt"])
        first_order[customer_key] = earliest["Name"].strip()

    return first_order

# ---------------------------------------------------------------------------
# Phase 4: Tag every line item
# ---------------------------------------------------------------------------

def phase4_tag_lines(valid_rows: list[dict], first_order: dict[str, str]) -> list[dict]:
    """Add _tag ('acquisition' or 'retention') to every row."""
    for row in valid_rows:
        order_name = row["Name"].strip()
        customer_first = first_order[row["_customer_key"]]
        row["_tag"] = "acquisition" if order_name == customer_first else "retention"
    return valid_rows

# ---------------------------------------------------------------------------
# Phase 5: Per-SKU metrics
# ---------------------------------------------------------------------------

def phase5_sku_metrics(valid_rows: list[dict]) -> dict[str, dict]:
    """Count unique order names per (sku, tag). Quantity is not the unit."""
    sku_acq_orders: dict[str, set] = defaultdict(set)
    sku_ret_orders: dict[str, set] = defaultdict(set)
    sku_names: dict[str, set] = defaultdict(set)

    for row in valid_rows:
        sku = row.get("Lineitem sku", "").strip()
        if not sku:
            continue
        order_name = row["Name"].strip()
        line_name = row.get("Lineitem name", "").strip()
        tag = row["_tag"]
        sku_names[sku].add(line_name)
        if tag == "acquisition":
            sku_acq_orders[sku].add(order_name)
        else:
            sku_ret_orders[sku].add(order_name)

    all_skus = set(sku_acq_orders.keys()) | set(sku_ret_orders.keys())
    metrics = {}
    for sku in all_skus:
        acq = len(sku_acq_orders[sku])
        ret = len(sku_ret_orders[sku])
        total = acq + ret
        metrics[sku] = {
            "acq_orders": acq,
            "ret_orders": ret,
            "total_orders": total,
            "acq_rate": acq / total if total else 0.0,
            "ret_rate": ret / total if total else 0.0,
            "name": next(iter(sku_names[sku])) if sku_names[sku] else "",
            "_all_names": sku_names[sku],
        }
    return metrics

# ---------------------------------------------------------------------------
# Phase 6: Compute indices
# ---------------------------------------------------------------------------

def phase6_indices(sku_metrics: dict[str, dict], valid_rows: list[dict]) -> dict[str, dict]:
    """Compute per-SKU acquisition_index and retention_index."""
    total_lines = sum(
        1 for r in valid_rows if r.get("Lineitem sku", "").strip()
    )
    acq_lines = sum(
        1 for r in valid_rows
        if r.get("Lineitem sku", "").strip() and r["_tag"] == "acquisition"
    )

    dataset_acq_rate = acq_lines / total_lines if total_lines else 0.0
    dataset_ret_rate = 1.0 - dataset_acq_rate

    for sku, m in sku_metrics.items():
        if dataset_acq_rate > 0:
            m["acquisition_index"] = round(m["acq_rate"] / dataset_acq_rate, 4)
        else:
            m["acquisition_index"] = 0.0

        if dataset_ret_rate > 0:
            m["retention_index"] = round(m["ret_rate"] / dataset_ret_rate, 4)
        else:
            m["retention_index"] = 0.0

        m["low_confidence"] = m["total_orders"] < MIN_SKU_ORDERS

    return sku_metrics, dataset_acq_rate, dataset_ret_rate

# ---------------------------------------------------------------------------
# Phase 7: Category aggregation
# ---------------------------------------------------------------------------

def phase7_category(
    sku_metrics: dict[str, dict],
    products_rows: list[dict] | None,
) -> tuple[dict[str, dict], bool]:
    """Join SKUs to product type and aggregate per category."""
    if not products_rows:
        for m in sku_metrics.values():
            m["product_type"] = "Not provided"
        return {}, False

    sku_to_type: dict[str, str] = {}
    for row in products_rows:
        variant_sku = row.get("Variant SKU", "").strip()
        product_type = row.get("Type", "").strip() or "Unknown"
        if variant_sku:
            sku_to_type[variant_sku] = product_type

    for sku, m in sku_metrics.items():
        m["product_type"] = sku_to_type.get(sku, "Unknown")

    category_data: dict[str, dict] = defaultdict(lambda: {
        "sku_count": 0,
        "total_orders": 0,
        "acq_index_sum": 0.0,
        "ret_index_sum": 0.0,
        "high_confidence_skus": 0,
    })

    for sku, m in sku_metrics.items():
        pt = m["product_type"]
        c = category_data[pt]
        c["sku_count"] += 1
        c["total_orders"] += m["total_orders"]
        c["acq_index_sum"] += m["acquisition_index"]
        c["ret_index_sum"] += m["retention_index"]
        if not m["low_confidence"]:
            c["high_confidence_skus"] += 1

    category_summary = {}
    for pt, c in category_data.items():
        n = c["sku_count"]
        category_summary[pt] = {
            "product_type": pt,
            "sku_count": n,
            "total_orders": c["total_orders"],
            "avg_acquisition_index": round(c["acq_index_sum"] / n, 4) if n else 0.0,
            "avg_retention_index": round(c["ret_index_sum"] / n, 4) if n else 0.0,
            "high_confidence_skus": c["high_confidence_skus"],
        }

    return category_summary, True

# ---------------------------------------------------------------------------
# Phase 8: Data quality block
# ---------------------------------------------------------------------------

def phase8_data_quality(
    raw_rows: list[dict],
    valid_rows: list[dict],
    phase1_counts: dict,
    guest_unresolvable_count: int,
    first_order: dict[str, str],
    sku_metrics: dict[str, dict],
) -> dict:
    unique_customers = len(first_order)
    repeat_customers = sum(
        1 for ck, first_name in first_order.items()
        if any(
            r["_customer_key"] == ck and r["Name"].strip() != first_name
            for r in valid_rows
        )
    )
    single_purchase_rate = (
        round(1.0 - (repeat_customers / unique_customers), 4)
        if unique_customers else 0.0
    )
    guest_checkout_rate = (
        round(guest_unresolvable_count / len(valid_rows), 4)
        if valid_rows else 0.0
    )

    sku_name_conflicts = [
        sku for sku, m in sku_metrics.items()
        if len(m.get("_all_names", set())) > 3
    ]

    dts = [r["_dt"] for r in valid_rows]
    date_range_start = min(dts).strftime("%Y-%m-%d") if dts else None
    date_range_end = max(dts).strftime("%Y-%m-%d") if dts else None
    analysis_window_days = (
        (max(dts) - min(dts)).days if len(dts) >= 2 else 0
    )

    return {
        "total_raw_order_rows": len(raw_rows),
        "total_valid_order_rows": len(valid_rows),
        "cancelled_dropped": phase1_counts["cancelled_dropped"],
        "refunded_voided_dropped": phase1_counts["refunded_voided_dropped"],
        "partially_refunded_kept": phase1_counts["partially_refunded_kept"],
        "malformed_row_count": phase1_counts["malformed_row_count"],
        "unique_customers": unique_customers,
        "unique_repurchase_customers": repeat_customers,
        "single_purchase_rate": single_purchase_rate,
        "high_single_purchase_rate": single_purchase_rate > SINGLE_PURCHASE_RATE_ALERT,
        "guest_checkout_rate": guest_checkout_rate,
        "small_dataset": len(valid_rows) < SMALL_DATASET_THRESHOLD,
        "guest_unresolvable_count": guest_unresolvable_count,
        "sku_name_conflicts": sku_name_conflicts,
        "date_range_start": date_range_start,
        "date_range_end": date_range_end,
        "analysis_window_days": analysis_window_days,
        "short_window_warning": analysis_window_days < SHORT_WINDOW_DAYS,
    }

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze Shopify Orders CSV for SKU acquisition vs. retention roles."
    )
    parser.add_argument("orders_csv", help="Path to Shopify Orders export CSV")
    parser.add_argument(
        "products_csv", nargs="?", default=None,
        help="Path to Shopify Products export CSV (optional)"
    )
    parser.add_argument(
        "--customers", dest="customers_csv", default=None,
        help="Path to Shopify Customers export CSV (reserved for future use)"
    )
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )
    args = parser.parse_args()

    # Load orders
    try:
        raw_rows, _ = _read_csv(args.orders_csv)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    _check_columns(raw_rows, ORDERS_REQUIRED, "Orders CSV")

    # Load products
    products_rows = None
    if args.products_csv:
        try:
            products_rows, _ = _read_csv(args.products_csv)
            _check_columns(products_rows, PRODUCTS_REQUIRED, "Products CSV")
        except (FileNotFoundError, ValueError) as exc:
            print(f"WARNING: Could not load Products CSV: {exc}", file=sys.stderr)
            products_rows = None

    # Run phases
    valid_rows, phase1_counts = phase1_parse_filter(raw_rows)

    if not valid_rows:
        result = {
            "metadata": {
                "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                "date_range_start": None,
                "date_range_end": None,
                "analysis_window_days": 0,
                "short_window_warning": False,
                "products_csv_provided": products_rows is not None,
                "customers_csv_provided": args.customers_csv is not None,
            },
            "data_quality": {
                "total_raw_order_rows": len(raw_rows),
                "total_valid_order_rows": 0,
                "cancelled_dropped": phase1_counts["cancelled_dropped"],
                "refunded_voided_dropped": phase1_counts["refunded_voided_dropped"],
                "partially_refunded_kept": 0,
                "malformed_row_count": phase1_counts["malformed_row_count"],
                "unique_customers": 0,
                "unique_repurchase_customers": 0,
                "single_purchase_rate": 0.0,
                "high_single_purchase_rate": False,
                "guest_checkout_rate": 0.0,
                "small_dataset": True,
                "guest_unresolvable_count": 0,
                "sku_name_conflicts": [],
                "date_range_start": None,
                "date_range_end": None,
                "analysis_window_days": 0,
                "short_window_warning": False,
            },
            "dataset_rates": {"dataset_acq_rate": 0.0, "dataset_ret_rate": 0.0},
            "sku_results": [],
            "category_summary": [],
        }
        indent = 2 if args.pretty else None
        print(json.dumps(result, indent=indent))
        sys.exit(0)

    valid_rows, guest_unresolvable_count = phase2_resolve_customers(valid_rows)
    first_order = phase3_first_orders(valid_rows)
    valid_rows = phase4_tag_lines(valid_rows, first_order)
    sku_metrics = phase5_sku_metrics(valid_rows)

    if not sku_metrics:
        print("WARNING: No SKUs found in valid order rows.", file=sys.stderr)

    sku_metrics, dataset_acq_rate, dataset_ret_rate = phase6_indices(sku_metrics, valid_rows)
    category_summary, products_csv_provided = phase7_category(sku_metrics, products_rows)
    data_quality = phase8_data_quality(
        raw_rows, valid_rows, phase1_counts,
        guest_unresolvable_count, first_order, sku_metrics,
    )

    sku_results = []
    for sku, m in sku_metrics.items():
        sku_results.append({
            "sku": sku,
            "name": m["name"],
            "product_type": m.get("product_type", "Not provided"),
            "acq_orders": m["acq_orders"],
            "ret_orders": m["ret_orders"],
            "total_orders": m["total_orders"],
            "acq_rate": round(m["acq_rate"], 4),
            "ret_rate": round(m["ret_rate"], 4),
            "acquisition_index": m["acquisition_index"],
            "retention_index": m["retention_index"],
            "low_confidence": m["low_confidence"],
        })
    sku_results.sort(key=lambda x: x["total_orders"], reverse=True)

    result = {
        "metadata": {
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "date_range_start": data_quality["date_range_start"],
            "date_range_end": data_quality["date_range_end"],
            "analysis_window_days": data_quality["analysis_window_days"],
            "short_window_warning": data_quality["short_window_warning"],
            "products_csv_provided": products_csv_provided,
            "customers_csv_provided": args.customers_csv is not None,
        },
        "data_quality": data_quality,
        "dataset_rates": {
            "dataset_acq_rate": round(dataset_acq_rate, 4),
            "dataset_ret_rate": round(dataset_ret_rate, 4),
        },
        "sku_results": sku_results,
        "category_summary": sorted(
            category_summary.values(),
            key=lambda x: x["total_orders"],
            reverse=True,
        ),
    }

    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent))

    has_warnings = (
        data_quality["small_dataset"]
        or data_quality["short_window_warning"]
        or data_quality["high_single_purchase_rate"]
        or data_quality["sku_name_conflicts"]
    )
    sys.exit(1 if has_warnings else 0)


if __name__ == "__main__":
    main()

# Script Output JSON Schema

`scripts/analyze_sku_roles.py` writes a single JSON object to stdout. This document describes every field.

---

## Top-level structure

```json
{
  "metadata": { ... },
  "data_quality": { ... },
  "dataset_rates": { ... },
  "sku_results": [ ... ],
  "category_summary": [ ... ]
}
```

---

## `metadata`

Context about the analysis run. Use these values to populate the Analysis Summary table header.

| Field | Type | Description |
|---|---|---|
| `analysis_date` | string (YYYY-MM-DD) | Date the script was run |
| `date_range_start` | string (YYYY-MM-DD) or null | Earliest order date in valid rows |
| `date_range_end` | string (YYYY-MM-DD) or null | Latest order date in valid rows |
| `analysis_window_days` | integer | Days between earliest and latest order |
| `short_window_warning` | boolean | True when `analysis_window_days < 180` |
| `products_csv_provided` | boolean | True when a Products CSV was successfully loaded |

---

## `data_quality`

Row-level and customer-level statistics. Read this block before writing any output. Every flag in this block maps to a conditional instruction in SKILL.md.

| Field | Type | Description |
|---|---|---|
| `total_raw_order_rows` | integer | Rows in the raw Orders CSV before filtering |
| `total_valid_order_rows` | integer | Rows kept after dropping cancelled/refunded/voided/malformed rows |
| `cancelled_dropped` | integer | Rows dropped because `Cancelled at` was non-empty |
| `refunded_voided_dropped` | integer | Rows dropped because `Financial Status` was `refunded` or `voided` |
| `partially_refunded_kept` | integer | Rows kept despite `Financial Status = partially_refunded` |
| `malformed_row_count` | integer | Rows dropped because `Created at` was missing or unparseable |
| `unique_customers` | integer | Distinct customer keys resolved from valid rows |
| `unique_repurchase_customers` | integer | Customers with more than one distinct order name |
| `single_purchase_rate` | float (0-1) | `1 - (unique_repurchase_customers / unique_customers)` |
| `high_single_purchase_rate` | boolean | True when `single_purchase_rate > 0.70` |
| `guest_checkout_rate` | float (0-1) | Fraction of valid rows with no resolvable customer ID or email |
| `small_dataset` | boolean | True when `total_valid_order_rows < 200` |
| `guest_unresolvable_count` | integer | Raw count of rows with no customer identity (used to compute `guest_checkout_rate`) |
| `sku_name_conflicts` | array of strings | SKUs where more than 3 distinct `Lineitem name` values appear across orders |
| `date_range_start` | string or null | Duplicate of `metadata.date_range_start` |
| `date_range_end` | string or null | Duplicate of `metadata.date_range_end` |
| `analysis_window_days` | integer | Duplicate of `metadata.analysis_window_days` |
| `short_window_warning` | boolean | Duplicate of `metadata.short_window_warning` |

### Flag semantics and SKILL.md mapping

| Flag | Condition | Required action in SKILL.md |
|---|---|---|
| `small_dataset: true` | < 200 valid rows | State "directional only" prominently at top of report |
| `high_single_purchase_rate: true` | > 70% single-purchase customers | Write context paragraph before Product Role Map; adjust classification thresholds one bracket |
| `short_window_warning: true` | < 180 days of data | Flag in Confidence Notes; seasonal SKUs may over-index |
| `guest_checkout_rate > 0.40` | (check the value directly) | Flag in Confidence Notes; single-purchase rate may be overstated |
| `sku_name_conflicts` non-empty | (check array length) | Cross-reference with `name_variants` in `sku_results`; list each conflict in Products to Watch |

---

## `dataset_rates`

The store-level acquisition and retention baselines used to compute per-SKU indices. An index of 1.0 means the SKU performs exactly at this rate.

| Field | Type | Description |
|---|---|---|
| `dataset_acq_rate` | float (0-1) | Fraction of unique orders that are first orders across the dataset |
| `dataset_ret_rate` | float (0-1) | `1 - dataset_acq_rate` |

Note: `dataset_acq_rate + dataset_ret_rate = 1.0`. They are complements computed from unique order names, not line item rows, so multi-SKU orders do not distort the baseline.

---

## `sku_results`

Array of per-SKU objects, sorted by `total_orders` descending. Each object:

| Field | Type | Description |
|---|---|---|
| `sku` | string | The `Lineitem sku` value from the Orders CSV |
| `name` | string | First `Lineitem name` seen for this SKU |
| `name_variants` | array of strings | All distinct `Lineitem name` values for this SKU, sorted alphabetically. Non-empty only when the SKU appears in `data_quality.sku_name_conflicts` (more than 3 distinct names). Use these to populate the SKU Name Conflicts subsection in Products to Watch. |
| `product_type` | string | Product type from the Products CSV. `"Not provided"` when no Products CSV was supplied; `"Unknown"` when the SKU was not found in the Products CSV. |
| `acq_orders` | integer | Unique order names where this SKU appeared in a customer's first order |
| `ret_orders` | integer | Unique order names where this SKU appeared in a repeat order |
| `total_orders` | integer | `acq_orders + ret_orders` |
| `acq_rate` | float (0-1) | `acq_orders / total_orders` |
| `ret_rate` | float (0-1) | `ret_orders / total_orders` |
| `acquisition_index` | float | `acq_rate / dataset_acq_rate`. 1.0 = average; > 1.0 = over-indexes for new customers |
| `retention_index` | float | `ret_rate / dataset_ret_rate`. 1.0 = average; > 1.0 = over-indexes for returning customers |
| `low_confidence` | boolean | True when `total_orders < 10`. Do not classify; place in Products to Watch. |

### Index interpretation

- Both indices are independently normalized against their own dataset baseline. They are not guaranteed to sum to 2.0 and are not inverses of each other.
- A SKU with `acquisition_index = 1.9` over-indexes 90% above the store average for appearing in first orders.
- A SKU with `low_confidence: true` and a high index should never be classified as Acquisition Anchor or Retention Driver. The index may reflect one customer's behavior, not a signal.

---

## `category_summary`

Array of per-product-type aggregations, sorted by `total_orders` descending. Empty array when `metadata.products_csv_provided = false`.

| Field | Type | Description |
|---|---|---|
| `product_type` | string | Product type value from the Products CSV |
| `sku_count` | integer | Number of distinct SKUs in this type |
| `total_orders` | integer | Sum of `total_orders` across all SKUs in this type |
| `avg_acquisition_index` | float | Mean `acquisition_index` across all SKUs in this type |
| `avg_retention_index` | float | Mean `retention_index` across all SKUs in this type |
| `high_confidence_skus` | integer | Count of SKUs in this type with `low_confidence: false` |

### Signal values for Category Breakdown table

Derive the `Signal` column in the Category Breakdown output table from `avg_acquisition_index` and `avg_retention_index`. Category averages are dampened relative to individual SKU indices, so category-level thresholds are lower than per-SKU thresholds. Evaluate in order — the first matching rule wins.

| Priority | Condition | Signal |
|---|---|---|
| 1 | `high_confidence_skus < 2` | Thin data |
| 2 | `avg_acquisition_index > 1.2` | Strong acquisition |
| 3 | `avg_retention_index > 1.2` | Strong retention |
| 4 | otherwise | Mixed |

Notes:
- "Thin data" always takes precedence regardless of index values.
- If both `avg_acquisition_index > 1.2` and `avg_retention_index > 1.2` (rare for category averages), the dominant index wins. "Strong acquisition" if `avg_acquisition_index > avg_retention_index`, otherwise "Strong retention."
- "Mixed" covers all remaining cases: neither index dominant, or one index slightly above 1.0 but below 1.2.

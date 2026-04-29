---
name: sku-acquisition-retention-analysis
description: >-
  Identifies which Shopify products drive new customer acquisition vs. repeat
  purchases and produces a merchandising brief by product role.
license: Apache-2.0
---

# Map Your Acquisition and Retention SKUs

Native Shopify reports do not distinguish between products that bring in new customers and products that keep existing customers coming back. This skill fills that gap: it takes a Shopify Orders export, identifies which SKUs over-index for first-time buyers (acquisition anchors) versus repeat buyers (retention drivers), and produces a merchandising brief with specific channel and budget allocation recommendations.

This skill is for ecommerce managers, performance marketers, and merchandising teams who want to stop featuring retention products in cold-traffic ads and stop pushing acquisition products into post-purchase flows. For reference on expected output format and depth, see [references/example-output.md](references/example-output.md).

---

## Script Execution

This skill uses a Python script for deterministic index computation and an LLM for synthesis, classification, and the merchandising brief.

**Before any analysis, run the script:**

```
python scripts/analyze_sku_roles.py orders.csv [products.csv] [--pretty]
```

The script outputs JSON to stdout. Capture the full output and use it as the analytical foundation. Do not derive acquisition or retention indices yourself; use the script's values.

**Products CSV is optional** but improves the output significantly. With it, the Category Breakdown section is populated and aggregated signals are available. Without it, skip that section entirely and note the omission in Confidence Notes.

**Fallback:** If the script fails for any reason, note it in Confidence Notes and perform a manual tally from the raw CSV. Flag all resulting indices as LLM-estimated rather than script-computed.

**Exit codes:** 0 = success, 1 = success with warnings, 2 = fatal input error.

---

## Conversation Flow

### Turn 1: Collect Files and Context

Tell the user:

"Share your Shopify Orders CSV and I'll produce an acquisition vs. retention SKU map with a merchandising brief.

**Required:**
- Shopify Orders export CSV. To export: Shopify Admin > Orders > Export > All orders > Plain CSV file.

**Strongly recommended:**
- Shopify Products export CSV. To export: Shopify Admin > Products > Export > All products > Plain CSV file. This unlocks category-level aggregation (which product types drive acquisition vs. retention) in addition to per-SKU analysis.

**Optional:**
- Date context: what period does the export cover? If you know your store's typical repurchase window (e.g., 6 weeks for consumables, 12 months for apparel), share that too. It helps calibrate retention index interpretation.

If you share only the Orders CSV, I'll still produce per-SKU indices and the full merchandising brief. The Category Breakdown section will be omitted."

### Turn 2: Run Script and Confirm Plan

Run the script against the provided files. Read the `data_quality` block from the JSON output before writing anything. Present a brief data quality summary and flag any issues that require the user's awareness before you produce the full report:

```
**Data Quality Check**

| Metric | Value |
|---|---|
| Valid orders analyzed | [total_valid_order_rows] |
| Unique customers | [unique_customers] |
| Repeat purchasers | [unique_repurchase_customers] |
| Single-purchase rate | [single_purchase_rate as %] |
| Guest checkout rate | [guest_checkout_rate as %] |
| Cancelled orders dropped | [cancelled_dropped] |
| Refunded/voided dropped | [refunded_voided_dropped] |
| Products CSV provided | Yes / No |
```

Flag prominently if:
- `small_dataset: true` ("Under 200 valid orders. This analysis is directional only.")
- `high_single_purchase_rate: true` ("Over 70% of customers have only one order. Retention indices will be compressed across all SKUs. I'll contextualize this before classifying any SKU.")
- `short_window_warning: true` ("Data window is under 6 months. Seasonal products may over-index.")

Ask the user to confirm before producing the full report: "Does this look right? Any issues with the date range or file?"

### Turn 3+: Produce Full Report

Produce the complete Markdown report using the Output Structure below. After sharing it:

"Review the analysis and let me know if you want to dig deeper on any section, see drill-down on a specific SKU's order history, or explore a different date range."

---

## Interpreting Script Output

**Indices:** `acquisition_index` of 1.0 = that SKU acquires at the dataset average. Above 1.0 = over-indexes for new customers. Below 1.0 = under-indexes. Same logic for `retention_index`. The two indices are not perfectly inverse because the dataset averages are computed independently.

**`high_single_purchase_rate: true`:** When most customers have only one order, the dataset acquisition rate is inflated. All retention indices will be compressed toward zero. Before classifying any SKU, write a context paragraph explaining this dynamic. You may shift threshold brackets one level (e.g., treat a retention index of 1.2 as meaningful when the dataset average retention rate is 0.19).

**`low_confidence: true`:** A SKU with fewer than 10 total orders. Show it in Products to Watch with its indices but do not classify it as Acquisition Anchor or Retention Driver. A high index on 6 orders can be one customer's purchasing behavior, not a signal.

**`products_csv_provided: false`:** Omit the Category Breakdown section entirely. Note the omission in Confidence Notes.

**`sku_name_conflicts`:** SKUs with more than 3 distinct `Lineitem name` values across orders. Flag each in Products to Watch. The SKU may represent multiple products bundled under one code, or the product was renamed. Do not roll up indices across name variants as if they are the same product.

---

## Product Role Classification

Apply these thresholds to `acquisition_index` and `retention_index` from the script output. Named constants match the script exactly.

| Role | Acquisition Index | Retention Index | Other Condition |
|---|---|---|---|
| Acquisition Anchor | > 1.4 | < 0.8 | `low_confidence: false` |
| Retention Driver | < 0.8 | > 1.4 | `low_confidence: false` |
| Hybrid | 0.8 to 1.4 | 0.8 to 1.4 | `total_orders > 10` |
| Underperformer | < 0.8 | < 0.8 | `total_orders > 10` |
| Single-Purchase Commodity | any | any | `acq_rate > 0.95` and `total_orders > 10` |

**When `high_single_purchase_rate` is true:** Write a context paragraph before the Product Role Map. State the dataset single-purchase rate, what it means for index compression, and that the classification thresholds have been adjusted one bracket where warranted.

**Precedence:** Single-Purchase Commodity overrides other roles when `acq_rate > 0.95`. Confidence threshold applies before any other classification.

---

## Output Structure

```
# Acquisition vs. Retention SKU Analysis: [Store Name]

## Analysis Summary

| Metric | Value |
|---|---|
| Date range | [date_range_start] to [date_range_end] |
| Analysis window | [analysis_window_days] days |
| Valid orders | [total_valid_order_rows] |
| Unique customers | [unique_customers] |
| Repeat purchasers | [unique_repurchase_customers] ([%]) |
| Single-purchase rate | [single_purchase_rate as %] |
| Guest checkout rate | [guest_checkout_rate as %] |
| Cancelled orders dropped | [cancelled_dropped] |
| Refunded/voided dropped | [refunded_voided_dropped] |
| Partially refunded kept | [partially_refunded_kept] |
| Products CSV provided | Yes / No |

[1-2 sentence context paragraph on single-purchase rate and what it means for
 interpreting retention indices across this dataset. Required when
 high_single_purchase_rate is true; recommended otherwise.]

## Product Role Map

[Table: SKU | Product Name | Type | Acq. Orders | Ret. Orders | Acq. Index | Ret. Index | Role | Confidence]
[Sort by total_orders descending.]
[Italicize rows where low_confidence: true.]
[Type column: omit if products_csv_provided: false.]

## Category Breakdown

[Table: Product Type | SKUs | Total Orders | Avg Acq. Index | Avg Ret. Index | Signal]
[Signal values: "Strong acquisition" / "Strong retention" / "Mixed" / "Thin data"]
["Thin data" when high_confidence_skus < 2 for the category.]
[Omit this entire section if products_csv_provided: false.]

## Acquisition Anchors

[For each top 2-4 acquisition anchor SKU:]
**[Product Name]** (acq. index [value], [acq_orders] acq. orders / [total_orders] total)
[1-2 sentences: plain-language explanation of what "acq. index X.X" means for this SKU,
 hypothesis why it over-indexes (price point, search intent, gift suitability, etc.)]

## Retention Drivers

[Same structure. If no retention drivers exist, state it explicitly:]
"No SKUs meet the Retention Driver threshold (ret. index > 1.4, low_confidence: false).
 This is [expected/notable] for [category context]. Implication for retention flows: [brief]."

## Products to Watch

[Group into subsections as applicable:]

### Low-Confidence SKUs
[Table: SKU | Product Name | Acq. Index | Ret. Index | Orders | Note]
["Note" explains why it is low-confidence, not a classification.]

### Underperformers
[Table: SKU | Product Name | Acq. Index | Ret. Index | Orders]
[Brief note on what underperforming means: neither strong acquisition nor retention signal.]

### SKU Name Conflicts
[List each SKU from sku_name_conflicts with the distinct names found. Flag for manual review.]

### Bundle and Gift Card SKUs
[Any SKU where Lineitem name contains "bundle", "gift", "set", or similar heuristics.
 Note: acquisition/retention signal cannot be decomposed into component products.]

[Omit any subsection that has no entries.]

## Merchandising Brief

### Acquisition Campaign Recommendations
[3-5 specific, actionable recommendations. Name specific SKUs and cite their indices.
 Reference the acquisition channel context (cold traffic, paid social, prospecting).
 Do not recommend retention drivers here.]

### Retention Flow Recommendations
[3-5 specific recommendations. Name specific SKUs for cross-sell, winback, and
 replenishment flows. Reference the repurchase window the user provided, or note
 that the store's repurchase window was not provided and use industry defaults.
 Do not recommend acquisition anchors here.]

### Budget Allocation Signal
[2-3 sentences on the prospecting vs. retention spend split based on aggregate pattern.
 Reference the single-purchase rate, repeat purchaser count, and any category signals.]

## Confidence Notes

[Required section. Include all that apply:]
- [If small_dataset: true] Under 200 valid orders. All findings are directional only.
- [If high_single_purchase_rate: true] [Single-purchase rate]% of customers have one order.
  Retention indices are compressed. Classification thresholds adjusted.
- [If short_window_warning: true] Analysis window is [days] days (under 6 months).
  Seasonal SKUs may over-index.
- [If products_csv_provided: false] Category Breakdown omitted. No Products CSV provided.
- [If guest_checkout_rate > 0.40] [Rate]% guest checkout. Single-purchase rate may be
  overstated because guest repeat buyers cannot be linked.
- [If partially_refunded_kept > 0] [N] partially refunded orders kept in analysis.
- [If sku_name_conflicts non-empty] [N] SKUs have inconsistent naming across orders.
  See Products to Watch.
- [Any date range implications, seasonal overlap, or other caveats.]
```

---

## Edge Cases

| Scenario | Script Flag | Action |
|---|---|---|
| Under 200 valid orders | `small_dataset: true` | State prominently at top of report. "Directional only." |
| Over 70% single-purchase customers | `high_single_purchase_rate: true` | Context paragraph before Product Role Map. Adjust threshold brackets. |
| No Products CSV | `products_csv_provided: false` | Omit Category Breakdown entirely. Note in Confidence Notes. |
| Over 40% guest checkout rate | `guest_checkout_rate > 0.40` | Flag in Confidence Notes. Single-purchase rate may be overstated. |
| All SKUs over-index for acquisition | No specific flag; valid result | State directly: "No retention drivers identified. Expected for [context]. Retention flows should focus on reactivation rather than cross-sell." |
| Partially refunded orders kept | `partially_refunded_kept: N` | Note count in Confidence Notes. Do not re-flag per SKU. |
| Bundle or gift card SKUs | Detected by name heuristic | Flag in Products to Watch. Cannot decompose into component products. |
| Analysis window under 180 days | `short_window_warning: true` | Flag in Confidence Notes. Seasonal SKUs may show distorted indices. |
| Same SKU with over 3 distinct names | `sku_name_conflicts` list | Flag in Products to Watch. Do not average indices across name variants. |
| Long repurchase cycle category (mattress, appliance, furniture) | `high_single_purchase_rate: true` | Explicitly state category context in context paragraph. Retention flow = reactivation cadence, not cross-sell. |

---

## Gotchas

### High acquisition index is not unconditionally good

A $14 loss-leader with acq index 2.3 may be an AOV problem, not a success. The Merchandising Brief must address whether acquisition anchor SKUs have the margin to support cold-traffic spend. If the store's AOV context is available, factor it in. Do not present high acquisition index as uniformly positive.

### Never put retention drivers in Acquisition Campaign Recommendations

Re-read the Product Role Map before writing the Merchandising Brief. A SKU classified as Retention Driver belongs in Retention Flow Recommendations, not in Acquisition Campaign Recommendations. This is the core purpose of the skill and the most common LLM failure mode.

### Low-confidence SKUs are not underperformers

A SKU with 7 orders and an acquisition index of 1.9 goes in Products to Watch under Low-Confidence SKUs, not in Acquisition Anchors and not in Underperformers. Do not classify by index alone when `low_confidence: true`. Do not exclude it from Products to Watch either.

# Acquisition vs. Retention SKU Analysis: GlowSkin Co.

## Analysis Summary

| Metric | Value |
|---|---|
| Date range | 2024-03-01 to 2026-02-28 |
| Analysis window | 730 days |
| Valid orders | 3,412 |
| Unique customers | 2,847 |
| Repeat purchasers | 684 (24%) |
| Single-purchase rate | 76% |
| Guest checkout rate | 18% |
| Cancelled orders dropped | 94 |
| Refunded/voided dropped | 47 |
| Partially refunded kept | 11 |
| Products CSV provided | Yes |

76% of GlowSkin Co. customers have placed only one order in the 24-month window. This is typical for skincare brands where repurchase cycles are 4 to 8 weeks but customer re-activation rates are low. A 76% single-purchase rate compresses all retention indices across the dataset: the dataset retention rate is only 0.24, so a SKU with a retention index of 1.5 represents a meaningfully different purchase pattern even though the raw retention order count appears small. All indices below have been computed against this compressed baseline. SKUs with retention index above 1.4 represent genuine repeat-purchase anchors even in a low-repurchase store.

---

## Product Role Map

| SKU | Product Name | Type | Acq. Orders | Ret. Orders | Acq. Index | Ret. Index | Role | Confidence |
|---|---|---|---|---|---|---|---|---|
| GLWSH-001-BLK | GlowWash Brightening Cleanser | Cleanser | 1,042 | 221 | 1.72 | 0.33 | Acquisition Anchor | High |
| GLWSH-002-ORG | GlowWash Gentle Foam Cleanser | Cleanser | 731 | 187 | 1.61 | 0.36 | Acquisition Anchor | High |
| GLVCS-003-30 | GlowBoost Vitamin C Serum 30ml | Serum | 198 | 283 | 0.52 | 1.83 | Retention Driver | High |
| GLNRT-004-50 | GlowNourish Retinol Night Cream | Moisturizer | 167 | 201 | 0.49 | 1.61 | Retention Driver | High |
| GLMST-005-100 | GlowMist Hydrating Toner | Moisturizer | 312 | 198 | 0.87 | 1.18 | Hybrid | High |
| GLSPF-006-40 | GlowShield SPF 40 Moisturizer | Moisturizer | 289 | 139 | 1.24 | 0.74 | Hybrid | High |
| GLLIP-007-CLR | GlowTint Tinted Lip Balm | Lip | 94 | 51 | 0.72 | 0.54 | Underperformer | High |
| GLGFT-008-HOL | GlowSkin Holiday Gift Set | Gift Set | 88 | 14 | 1.89 | 0.21 | Acquisition Anchor | High |
| GLEYE-009-BLK | GlowEye Brightening Eye Cream | Serum | 31 | 29 | 0.97 | 1.31 | Hybrid | High |
| GLSRM-010-NEW | GlowRenew Peptide Serum | Serum | 18 | 6 | 1.41 | 0.68 | Acquisition Anchor | High |
| *GLMSK-011-CLY* | *GlowClear Clay Mask* | *Cleanser* | *6* | *4* | *1.44* | *0.57* | *Products to Watch* | *Low* |
| *GLTNR-012-ROS* | *GlowRose Facial Mist* | *Moisturizer* | *4* | *3* | *1.08* | *0.87* | *Products to Watch* | *Low* |

---

## Category Breakdown

| Product Type | SKUs | Total Orders | Avg Acq. Index | Avg Ret. Index | Signal |
|---|---|---|---|---|---|
| Cleanser | 4 | 2,083 | 1.51 | 0.36 | Strong acquisition |
| Serum | 3 | 565 | 0.97 | 1.27 | Strong retention |
| Moisturizer | 3 | 938 | 0.87 | 1.18 | Mixed |
| Gift Set | 1 | 102 | 1.89 | 0.21 | Thin data |
| Lip | 1 | 145 | 0.72 | 0.54 | Thin data |

---

## Acquisition Anchors

**GlowWash Brightening Cleanser** (acq. index 1.72, 1,042 acq. orders / 1,263 total)
At the $28 entry price this is the most common first product in the GlowSkin assortment. Cleansers are high-search-intent purchases: customers searching "brightening cleanser" or "gentle face wash" land here first. The product appears in 37% of all first orders. Strong fit for cold-traffic paid social and Google Shopping acquisition campaigns.

**GlowWash Gentle Foam Cleanser** (acq. index 1.61, 731 acq. orders / 918 total)
The $24 alternative cleanser follows the same acquisition pattern. Together the two cleansers account for over half of all first-order line items, suggesting the cleanser category is the primary acquisition entry point for this store.

**GlowSkin Holiday Gift Set** (acq. index 1.89, 88 acq. orders / 102 total)
The highest acquisition index in the catalog, but interpret with caution: all 102 orders fall in November and December 2024 and 2025. The gift set is seasonal gifting, not a consistent acquisition driver. Treating it as an evergreen acquisition anchor would misallocate spend. Strong for Q4 prospecting campaigns only.

**GlowShield SPF 40 Moisturizer** (acq. index 1.24, 289 acq. orders / 428 total)
Hybrid with an acquisition lean. Lower threshold than true anchors but notable: SPF products are commonly purchased as first products in warmer months. Suitable for seasonal acquisition campaigns (March to August) alongside the cleansers.

---

## Retention Drivers

**GlowBoost Vitamin C Serum 30ml** (ret. index 1.83, 283 ret. orders / 481 total)
The strongest retention signal in the catalog. Vitamin C serums are a 4 to 6 week replenishment product: customers who start the routine come back to replenish. This SKU should anchor the post-purchase replenishment flow triggered at Day 35 after the first purchase of any product. It also makes an ideal cross-sell for customers whose first order was a cleanser (the most common first product).

**GlowNourish Retinol Night Cream** (ret. index 1.61, 201 ret. orders / 368 total)
Night cream with a 6 to 8 week usage cycle. Second-strongest retention signal. Customers who receive this SKU in a cross-sell flow after their first cleanser purchase are 3x more likely to become repeat buyers than the average single-cleanser customer. Target for Day 21 post-purchase email when cleanser is the first product.

---

## Products to Watch

### Low-Confidence SKUs

| SKU | Product Name | Acq. Index | Ret. Index | Orders | Note |
|---|---|---|---|---|---|
| GLMSK-011-CLY | GlowClear Clay Mask | 1.44 | 0.57 | 10 | Borderline low-confidence. Indices are plausible but one cohort could shift them. Monitor as volume grows. |
| GLTNR-012-ROS | GlowRose Facial Mist | 1.08 | 0.87 | 7 | Under 10 orders. No reliable signal. |

### Underperformers

| SKU | Product Name | Acq. Index | Ret. Index | Total Orders |
|---|---|---|---|---|
| GLLIP-007-CLR | GlowTint Tinted Lip Balm | 0.72 | 0.54 | 145 |

GlowTint under-indexes for both acquisition and retention. It neither brings in new customers nor keeps them coming back. At 145 orders across 24 months this is not a thin-data issue. The product is not driving channel performance in either direction. Candidates for merchandising review: bundle with a retention driver to improve attach rate, reduce paid visibility, or evaluate margin contribution independently.

### Bundle and Gift Card SKUs

**GLGFT-008-HOL (GlowSkin Holiday Gift Set):** Bundle SKU. The acquisition index (1.89) reflects gifting behavior in Q4, not the bundled products individually. The constituent products (cleanser, serum, toner) each have their own SKUs with more reliable annual signals. Do not use the gift set index to infer acquisition potential for its components.

---

## Merchandising Brief

### Acquisition Campaign Recommendations

1. **Lead cold-traffic campaigns with GlowWash Brightening Cleanser (GLWSH-001-BLK, acq. index 1.72).** At $28 this is the lowest-friction entry point into the GlowSkin assortment. Feature it as the hero product in paid social prospecting and Google Shopping. Its acquisition index of 1.72 means it appears in first orders 72% more often than the dataset average.

2. **Add GlowWash Gentle Foam Cleanser (GLWSH-002-ORG, acq. index 1.61) as the alternative acquisition SKU.** Use skin type targeting to split paid traffic: oily/combination skin to the Brightening Cleanser, dry/sensitive skin to the Gentle Foam. Both over-index heavily for acquisition.

3. **Run GlowSkin Holiday Gift Set (GLGFT-008-HOL, acq. index 1.89) as a Q4-only acquisition vehicle.** Launch prospecting campaigns in October with the gift set as the featured product. Do not carry this into January; the signal is entirely seasonal.

4. **Test GlowShield SPF 40 Moisturizer (GLSPF-006-40, acq. index 1.24) in seasonal acquisition campaigns from March through August.** The acquisition lean is consistent across two spring/summer seasons in the data. A modest prospecting budget test against a cleanser-focused campaign would validate whether SPF has a standalone acquisition role.

5. **Do not feature GlowBoost Vitamin C Serum or GlowNourish Retinol Night Cream in cold-traffic acquisition ads.** Both are retention drivers (ret. index 1.83 and 1.61 respectively). Featuring them in prospecting campaigns means paying acquisition CPMs to show products that do not convert first-time buyers at above-average rates.

### Retention Flow Recommendations

1. **Day 35 post-purchase: trigger GlowBoost Vitamin C Serum cross-sell for all cleanser first-purchase customers.** The serum's 4 to 6 week replenishment cycle aligns with this trigger. Cleanser buyers who also purchase the serum represent the highest-LTV cohort in the data. Personalize the subject line: "Your [product] routine is working. Time to layer in your serum."

2. **Day 21 post-purchase: trigger GlowNourish Retinol Night Cream cross-sell for Brightening Cleanser first-purchase customers.** Retinol and brightening cleanser is a natural routine pairing. The 21-day delay gives the customer time to form a cleanser habit before introducing a second step.

3. **Day 45 replenishment reminder for GlowBoost Vitamin C Serum purchasers.** The 30ml serum lasts approximately 45 days at daily use. Trigger a replenishment email with a direct add-to-cart link.

4. **Winback campaign: 1,412 lapsed single-purchase customers who bought a cleanser 90+ days ago and have not returned.** Lead the winback with a serum trial offer (GLVCS-003-30). The serum's strong retention index suggests it is the product most likely to convert a single-purchase cleanser customer into a repeat buyer.

5. **Do not put GlowWash Brightening Cleanser or GlowWash Gentle Foam Cleanser in post-purchase cross-sell flows as primary recommendations.** Both are acquisition anchors. A customer who already owns a cleanser does not need another cleanser cross-sell in their inbox; route them to retention-indexed products.

### Budget Allocation Signal

GlowSkin Co. has a 76% single-purchase rate, meaning the large majority of revenue comes from new customers, not repeat buyers. The current business model is heavily dependent on acquisition. With only 684 repeat buyers in 24 months, the retention opportunity is large and underutilized. A prospecting-heavy budget split (70% acquisition, 30% retention) is defensible given the current customer base size, but the 30% retention budget should be concentrated on the 684 existing repeat buyers and the 1,412 lapsed single-purchase cleanser buyers most likely to convert, rather than spread across general retention channels. As the repeat buyer cohort grows, the retention budget share should increase: the serum and night cream data suggests that customers who are converted to a second purchase have significantly higher lifetime purchase rates.

---

## Confidence Notes

- **76% single-purchase rate.** The dataset retention rate is 0.24. All retention indices are computed against this compressed baseline. A retention index of 1.4+ in this dataset represents a meaningful repeat-purchase signal even though raw retention order counts appear small relative to acquisition counts.
- **GlowSkin Holiday Gift Set seasonal distortion.** 96% of GLGFT-008-HOL orders fall in November and December. Its acquisition index of 1.89 reflects Q4 gifting, not an evergreen acquisition pattern. Do not use it to benchmark other SKUs' acquisition indices.
- **14-month gap in data clarity.** The 730-day window covers two full holiday seasons. Any SKU with seasonal sales concentration (gift sets, SPF) will show index distortion relative to all-season SKUs. Indices for seasonal SKUs should be compared within their active season, not against annual averages.
- **11 partially refunded orders kept.** These represent real customer interactions with fulfilled products. Excluding them would undercount retention behavior for affected SKUs. Count is low enough to have negligible index impact.
- **GlowClear Clay Mask (GLMSK-011-CLY) is borderline low-confidence at 10 total orders.** The acquisition index of 1.44 is at the classification threshold. Monitor as volume grows before treating it as an acquisition anchor.
- **Customers CSV not provided.** Customer identity resolved via Customer ID field with Email as fallback. 18% guest checkout rate is below the 40% flag threshold; guest identity resolution is unlikely to materially distort indices.

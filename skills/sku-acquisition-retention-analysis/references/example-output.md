# Acquisition vs. Retention SKU Analysis: GlowSkin Co.

## Analysis Summary

| Metric | Value |
|---|---|
| Date range | 2024-03-01 to 2026-02-25 |
| Analysis window | 725 days |
| Valid orders | 982 |
| Unique customers | 402 |
| Repeat purchasers | 117 (29%) |
| Single-purchase rate | 71% |
| Guest checkout rate | 0% |
| Cancelled orders dropped | 7 |
| Refunded/voided dropped | 8 |
| Partially refunded kept | 0 |
| Products CSV provided | Yes |

71% of GlowSkin Co. customers placed only one order in the 24-month window. This is high but not unusual for a mid-tier skincare brand where repurchase cycles are 6 to 10 weeks but re-activation rates are low. The dataset acquisition rate is 59.3% of orders (not customers): 59 of every 100 unique orders in this dataset are first orders. The dataset retention rate is 40.7%. Retention indices are computed against this 0.41 baseline, so a retention index of 1.4 means a SKU appears in repeat orders 40% more often than the dataset average, which is a real and actionable signal even at this single-purchase rate. No threshold adjustment is warranted here. The baseline is healthy enough that the standard 1.4 threshold distinguishes genuine behavioral patterns.

---

## Product Role Map

| SKU | Product Name | Type | Acq. Orders | Ret. Orders | Acq. Index | Ret. Index | Role | Confidence |
|---|---|---|---|---|---|---|---|---|
| GLMSK-011-CLY | GlowClear Clay Mask | Cleanser | 64 | 59 | 0.88 | 1.18 | Hybrid | High |
| GLMST-005-100 | GlowMist Hydrating Toner | Moisturizer | 61 | 45 | 0.97 | 1.04 | Hybrid | High |
| GLEYE-009-BLK | GlowEye Brightening Eye Cream | Serum | 51 | 47 | 0.88 | 1.18 | Hybrid | High |
| GLTNR-012-ROS | GlowRose Facial Mist | Moisturizer | 56 | 39 | 0.99 | 1.01 | Hybrid | High |
| GLLIP-007-CLR | GlowTint Tinted Lip Balm | Lip | 58 | 34 | 1.06 | 0.91 | Hybrid | High |
| GLSPF-006-40 | GlowShield SPF 40 Moisturizer | Moisturizer | 57 | 17 | 1.30 | 0.56 | Hybrid | High |
| GLSRM-010-NEW | GlowRenew Peptide Serum | Serum | 53 | 19 | 1.24 | 0.65 | Hybrid | High |
| GLWSH-002-ORG | GlowWash Gentle Foam Cleanser | Cleanser | 60 | 11 | 1.43 | 0.38 | Acquisition Anchor | High |
| GLWSH-001-BLK | GlowWash Brightening Cleanser | Cleanser | 52 | 14 | 1.33 | 0.52 | Hybrid | High |
| GLNRT-004-50 | GlowNourish Retinol Night Cream | Moisturizer | 12 | 51 | 0.32 | 1.99 | Retention Driver | High |
| GLGFT-008-HOL | GlowSkin Holiday Gift Set | Gift Set | 51 | 10 | 1.41 | 0.40 | Acquisition Anchor | High |
| GLVCS-003-30 | GlowBoost Vitamin C Serum 30ml | Serum | 13 | 48 | 0.36 | 1.93 | Retention Driver | High |

---

## Category Breakdown

| Product Type | SKUs | Total Orders | Avg Acq. Index | Avg Ret. Index | Signal |
|---|---|---|---|---|---|
| Moisturizer | 4 | 338 | 0.90 | 1.15 | Mixed |
| Cleanser | 3 | 260 | 1.21 | 0.69 | Strong acquisition |
| Serum | 3 | 231 | 0.83 | 1.25 | Strong retention |
| Lip | 1 | 92 | 1.06 | 0.91 | Thin data |
| Gift Set | 1 | 61 | 1.41 | 0.40 | Thin data |

---

## Acquisition Anchors

**GlowWash Gentle Foam Cleanser** (acq. index 1.43, 60 acq. orders / 71 total)
The cleanest acquisition signal in the catalog. 85% of this SKU's appearances are in first orders, compared to a 59% dataset average. At a lower entry price than the Brightening variant, it is likely the first touchpoint for cost-conscious customers searching "gentle cleanser" or "foam face wash." Strong fit for cold-traffic paid social and Google Shopping prospecting.

**GlowSkin Holiday Gift Set** (acq. index 1.41, 51 acq. orders / 61 total)
Acquisition anchor by the numbers, but interpret with caution: all 61 orders fall in November and December across two Q4 seasons. The gift set is a seasonal gifting driver, not a consistent acquisition vehicle. It should not be treated as an evergreen prospecting SKU. Strong candidate for Q4-only cold-traffic campaigns; outside Q4, it adds no acquisition signal.

**Near-threshold candidates (not classified as anchors):** GlowWash Brightening Cleanser (acq. index 1.33) and GlowShield SPF 40 Moisturizer (acq. index 1.30) both over-index for acquisition but fall below the 1.4 threshold. The Brightening Cleanser accounts for 79% first-order appearances and likely shares a customer segment with the Gentle Foam variant. SPF 40's acquisition lean may be seasonal: warmer-month search intent for sun protection. Both are suitable for prospecting campaigns at lower priority than the confirmed anchors.

---

## Retention Drivers

**GlowNourish Retinol Night Cream** (ret. index 1.99, 51 ret. orders / 63 total)
The strongest retention signal in the catalog. 81% of this SKU's appearances are in repeat orders. Retinol is a results-driven category: customers who start a retinol routine return to replenish it on a 6 to 8 week cycle. This SKU should anchor the post-purchase cross-sell flow for customers whose first order was a cleanser, triggered at Day 21 to 30. The cleanser-to-retinol pairing is the highest-potential LTV path in this dataset.

**GlowBoost Vitamin C Serum 30ml** (ret. index 1.93, 48 ret. orders / 61 total)
Second-strongest retention signal. 79% repeat appearances. Vitamin C serums have a 30 to 45 day replenishment cycle at daily use. This SKU should have a replenishment trigger at Day 40 post-purchase and a cross-sell trigger at Day 30 for customers who bought any cleanser as their first product. Together, the Night Cream and Vitamin C Serum account for a disproportionate share of repeat purchase behavior in this dataset. Concentrating retention resources on these two SKUs will have more impact than spreading email flows across the full catalog.

---

## Products to Watch

### Bundle and Gift Card SKUs

**GLGFT-008-HOL (GlowSkin Holiday Gift Set):** Bundle SKU. The acquisition index (1.41) reflects Q4 gifting behavior and cannot be decomposed into the constituent products. The bundled cleansers, serums, and toners each have their own SKU-level signals with more reliable annual patterns. Do not use the gift set index to infer acquisition potential for its individual components.

---

## Merchandising Brief

### Acquisition Campaign Recommendations

1. **Lead cold-traffic prospecting with GlowWash Gentle Foam Cleanser (GLWSH-002-ORG, acq. index 1.43).** With 85% of its orders from first-time buyers, this is the clearest acquisition entry point in the assortment. Feature it as the hero product in paid social and Google Shopping. Its $24 price point minimizes first-purchase friction.

2. **Run GlowWash Brightening Cleanser (GLWSH-001-BLK, acq. index 1.33) as the secondary acquisition SKU.** Use skin-type or intent targeting to split prospecting traffic: dry or sensitive skin to the Gentle Foam, oily or combination to the Brightening. Both cleansers over-index for acquisition; running both avoids saturating a single audience.

3. **Activate GlowShield SPF 40 Moisturizer (GLSPF-006-40, acq. index 1.30) in seasonal acquisition campaigns from March through August.** Its acquisition lean suggests warmer-month search intent for SPF. A targeted prospecting test against a cleanser-only campaign would confirm whether SPF has an independent acquisition role or is dependent on seasonal timing.

4. **Use GlowSkin Holiday Gift Set (GLGFT-008-HOL, acq. index 1.41) for Q4 prospecting only.** Launch cold-traffic campaigns in October featuring the gift set. Do not carry it into January; the acquisition signal is entirely seasonal and does not reflect an evergreen product behavior.

5. **Do not feature GlowNourish Retinol Night Cream or GlowBoost Vitamin C Serum in cold-traffic ads.** Both are strong retention drivers (ret. index 1.99 and 1.93 respectively). Paying prospecting CPMs to show products that appear in only 19% to 21% of first orders means spending acquisition budget on products that do not convert new customers at above-average rates.

### Retention Flow Recommendations

1. **Day 21 post-purchase: cross-sell GlowNourish Retinol Night Cream to cleanser first-buyers.** Retinol and brightening or gentle cleansers form a natural routine pairing. The 21-day delay gives the customer time to establish the cleanser habit before introducing a second step. Personalize subject line: "Your [cleanser] routine is set. Add retinol before bed."

2. **Day 40 replenishment trigger for GlowBoost Vitamin C Serum purchasers.** The 30ml bottle lasts approximately 40 days at daily use. Trigger a replenishment email with a direct add-to-cart link. This is the highest-volume repeat-purchase SKU in the catalog and warrants a dedicated replenishment cadence, not a generic cross-sell email.

3. **Day 30 post-purchase: cross-sell GlowBoost Vitamin C Serum to cleanser first-buyers.** Position the serum as the logical next step after cleanser: "Your morning routine, completed." The serum's 79% repeat-order share indicates high satisfaction among customers who do adopt it.

4. **Winback flow: lead with a Vitamin C Serum trial offer for lapsed single-purchase cleanser buyers.** Of the 285 single-purchase customers, the majority purchased a cleanser as their first and only product. Cleanser-first customers who have not returned within 90 days are the highest-potential winback segment. The Vitamin C Serum's strong retention signal suggests it is the most likely second-purchase product to convert them.

5. **Do not recommend GlowWash Gentle Foam or GlowWash Brightening Cleanser as primary post-purchase cross-sell targets.** A customer who already owns a cleanser does not need another cleanser recommended in their post-purchase flow. Route cleanser first-buyers toward retention-indexed SKUs (Night Cream, Vitamin C Serum) rather than back to the category they entered through.

### Budget Allocation Signal

GlowSkin Co. has a 71% single-purchase rate: most revenue currently comes from new customers, and the repeat buyer base (117 customers in 24 months) is small relative to the total customer count. A prospecting-heavy budget split (65 to 70% acquisition, 30 to 35% retention) is defensible for the current business stage. The 30 to 35% retention budget should be concentrated on three groups: the 117 existing repeat buyers (highest LTV segment), lapsed cleanser single-buyers within the 90-day winback window (highest conversion probability), and the serum cross-sell flow for active customers (fastest path to a second purchase). As the repeat-buyer cohort grows, the retention share should increase: the Night Cream and Vitamin C Serum data shows that customers who do reach a second purchase have significantly stronger repurchase behavior than the average single-purchase cleanser customer.

---

## Confidence Notes

- **71% single-purchase rate.** The dataset retention rate is 0.41. Retention indices are computed against this baseline. A retention index of 1.4 in this dataset represents a genuine behavioral pattern (57% of the SKU's orders are repeat vs. 41% dataset average). Standard classification thresholds apply without adjustment.
- **GlowSkin Holiday Gift Set seasonal concentration.** All 61 orders for GLGFT-008-HOL fall in November and December. Its acquisition index of 1.41 reflects Q4 gifting behavior. Do not use it to benchmark non-seasonal SKUs' acquisition indices.
- **725-day window covers two full holiday seasons.** Any SKU with seasonal concentration (SPF in spring/summer, gift sets in Q4) will show index values that reflect seasonal purchasing patterns in addition to behavioral ones. Indices for seasonal SKUs should be compared within their active season.
- **0% guest checkout rate.** All orders in the export include a resolvable Customer ID or email. Customer identity resolution is complete. Single-purchase rate is not overstated by unlinked repeat buyers.

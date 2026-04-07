# Example: Audit a Google Merchant Feed

This is an example of what the audit-google-merchant-feed skill produces when given a Google Merchant Center XML feed and a Shopify product export CSV. The example uses Great Outdoors Co., a fictional outdoor gear brand with 120 feed items and 30 products across apparel, gear, and accessories.

The example demonstrates how the skill aggregates findings by severity, explains issues in Shopify-native language, distinguishes between data fixes and feed tool fixes, and prioritizes actions by impact.

---

## Feed Audit Summary

| Metric | Value |
|---|---|
| Total items in feed | 120 |
| Items with issues | 120 |
| Disapproved issues (will not serve) | 40 issues across ~21 items |
| Demoted issues (reduced visibility) | 199 issues across ~120 items |
| Advisory issues (optimization opportunity) | 381 issues across ~120 items |
| Shopify CSV provided | Yes |
| Cross-reference checks | Enabled |

All 120 items have at least one finding, though most are advisory-level optimizations rather than blocking errors. The 40 disapproved findings are concentrated on two issue types (missing apparel attributes and duplicate items) affecting approximately 21 distinct items, not 40 separate products.

## Disapproved Issues

Issues that prevent items from appearing in Google Shopping. Fix these first.

### D02: Missing required apparel attributes

**Affected items:** 20 items across 7 products
**Representative items:**
- Riverbend Polarized Sunglasses (missing color, size, gender, age_group)
- Breeze Buff Neck Gaiter, Topo Print / Pine Green / Sunrise Stripe (missing size, gender, age_group)
- TrailClip Carabiner Keychain, Black / BLUE / blue (missing size, gender, age_group)
- Ridgeline Hiking Socks, Crew S/M/L/XL (missing color)
- High Trail Trucker Hat, Navy / Khaki (missing size)
- Ridgeview Beanie, Charcoal / Canyon (missing size)

**What's wrong:** These items are categorized under "Apparel & Accessories" in Google's taxonomy, which requires color, size, gender, and age_group attributes. Items missing any of these will be disapproved by Google Merchant Center.

**How to fix in Shopify:**

For **gender and age_group** (Neck Gaiters, Carabiner Keychains, Sunglasses):
1. Go to Shopify Admin > Products.
2. Select all affected products using the checkboxes.
3. Click "Bulk edit."
4. Add the columns "Google Shopping / Gender" and "Google Shopping / Age Group" if not visible (click "Columns" to add them). If these columns are not available, your store may manage them through the Google & YouTube channel app instead.
5. Set gender to "unisex" and age_group to "adult" for all selected items.
6. Save.

For **color** (Hiking Socks): The socks have size variants but no color option. Add a color option to each sock product in Shopify Admin > Products > [product] > Variants, or set a default color value in your feed tool.

For **size** (Trucker Hat, Beanie): These are one-size products. Options: add a "Size" option with value "One Size" in Shopify Admin > Products > [product], or configure your feed tool to set `g:size` to "One Size" for these items.

**Recategorize instead?** The Carabiner Keychain and Sunglasses are under "Apparel & Accessories > Clothing Accessories" but are not clothing in a practical sense. Consider recategorizing them to "Sporting Goods > Outdoor Recreation > Camping & Hiking" (carabiners) or "Health & Beauty > Personal Care > Vision Care > Sunglasses" (sunglasses) to remove the apparel attribute requirements entirely. Update the `Google Shopping / Google Product Category` field in Shopify Admin > Products > [product] > Product organization.

### D03: Duplicate items in feed

**Affected items:** 4 duplicate items (8 items total: 4 originals + 4 duplicates)
**Duplicate pairs:**
- Item 1076000060 duplicates 1076000058 (High Trail Trucker Hat, Navy, $27 vs. $28)
- Item 1076000098 duplicates 1076000096
- Item 1076000112 duplicates 1076000111
- Item 1076000116 duplicates 1076000115 (TrailClip Carabiner Keychain, blue/BLUE)

**What's wrong:** These items share the same title, item group, color, and size as another item in the feed, but have different g:id values. Google will flag or reject one of each pair. The Trucker Hat duplicate also has a price discrepancy ($27 vs. $28), which suggests a stale or misconfigured feed entry.

**How to fix in Shopify:** This is a feed-generation issue, not a Shopify data issue. Check your feed app for duplicate variant entries or stale data:
1. If using the Google & YouTube channel: open the app, check the product sync status for errors. If specific items are stuck, remove and re-add them from the channel. Do not disconnect the entire channel, as this resets product approval status and campaign history in Merchant Center.
2. If using a third-party feed tool: check for duplicate rules, variant mapping errors, or products that were deleted in Shopify but persist in the feed cache.
3. Verify in Shopify Admin > Products that each product has the expected number of variants (no accidental duplicates).
4. In Google Merchant Center: go to Products > All products, filter by the duplicate item IDs, and remove the stale entries directly.

### D04: Malformed HTML in description

**Affected items:** 1 item
**Item:** Item 1076000107 (product description contains `</p` without closing `>`)

**What's wrong:** The description has an unclosed HTML tag. Google may reject the item or display garbled text in Shopping ads.

**How to fix in Shopify:**
1. Go to Shopify Admin > Products > find the product for item 1076000107.
2. In the description editor, click "Show HTML" (or the code view icon).
3. Find the `</p` tag and add the closing `>` to make it `</p>`.
4. Save and regenerate the feed.

## Demoted Issues

Issues that reduce visibility or click-through rate. Fix these after resolving all disapproved issues.

### W01: Title does not include brand name

**Affected items:** 120 items (all items in feed)

**What's wrong:** None of the product titles include "Great Outdoors Co." Google recommends including the brand name in titles for better relevance on branded queries.

**Context:** Many Shopify merchants intentionally omit the brand from product titles because Google Shopping often auto-prepends the verified business name. If Great Outdoors Co. is the verified business name in Merchant Center, this may not need fixing. Check your Google Shopping listings to see if the brand already appears.

**How to fix in Shopify (if needed):**
1. Go to Shopify Admin > Products.
2. Select all products, click "Bulk edit."
3. Add "Great Outdoors Co." to the beginning of each title.
4. Save and regenerate the feed.

**Trade-off:** Adding brand to all titles uses 20+ characters of the 150-character title limit, leaving less space for product attributes and variant details. Only do this if Google is not auto-prepending the brand.

### W02: Description too short

**Affected items:** 73 items

**What's wrong:** These items have descriptions under 150 characters of plain text (after stripping HTML). Short descriptions provide insufficient signal for Google to match the product to search queries, resulting in fewer impressions.

**How to fix in Shopify:** Expand product descriptions in Shopify Admin > Products > [product]. Focus on materials, use cases, key features, fit information, and differentiators. Aim for 150 to 500 words. The Bulk Editor is not ideal for long-form descriptions; edit each product individually.

### W04: Inconsistent size naming within an item group

**Affected items:** Item group 1075000011 (mixes "Small", "Medium", "Large", "Lg", "L", "XL")

**What's wrong:** The same product uses both abbreviated and full size names across its variants. Google may not recognize these as valid size variants of the same product, reducing effectiveness of size-filtered Shopping queries.

**How to fix in Shopify:**
1. Go to Shopify Admin > Products > find the product for item group 1075000011.
2. Open Variants.
3. Standardize all size option values to one convention. Recommended: "S", "M", "L", "XL" (abbreviated) for consistency with the rest of the catalog.
4. Save and regenerate the feed.

### W05: Inconsistent color casing within an item group

**Affected items:** 2 item groups
- Item group 1075000028: "Blue", "blue", "ORANGE"
- Item group 1075000029: "Black", "BLUE", "blue"

**What's wrong:** Google may treat "Blue" and "blue" as different colors, fragmenting the product's variant presentation in Shopping results.

**How to fix in Shopify:**
1. Go to Shopify Admin > Products > find each affected product.
2. Open Variants and normalize color option values to title case (e.g., "Blue", "Orange", "Black").
3. Save and regenerate the feed.

### W03: Google product category too broad

**Affected items:** 3 items (Breeze Buff Neck Gaiter, all 3 color variants)
**Current category:** Apparel & Accessories > Clothing Accessories (2 levels)

**What's wrong:** The category has only 2 levels. More specific categories improve Google's ability to match the product to relevant searches.

**How to fix in Shopify:**
1. Go to Shopify Admin > Products > Breeze Buff Neck Gaiter.
2. Under Product organization, update "Google Shopping / Google Product Category" to a more specific category: "Apparel & Accessories > Clothing Accessories > Scarves & Shawls" or "Apparel & Accessories > Clothing Accessories > Neck Gaiters."
3. Save and regenerate the feed.

### X01: Price mismatch between Shopify and feed

**Affected items:** 2 items
- Feed price $28.00 vs. Shopify Variant Price $27.00 (a Trucker Hat duplicate)
- Feed price $79.00 vs. Shopify Variant Price $74.00 (with Compare At $99.00)

**What's wrong:** The feed shows different prices than what's in Shopify. If the landing page shows the Shopify price, Google will flag a price mismatch and may disapprove the item.

**How to fix:** Regenerate the feed from current Shopify data. The first mismatch is likely caused by the duplicate item (D03). The second may be a stale feed entry or a sale-price mapping issue. If prices still mismatch after regeneration, check your feed tool's price mapping rules.

## Advisory

Optimizations that improve feed performance. Not required but recommended.

### A01: No sale_price despite Shopify Compare At Price

**Affected items:** 21 items (Women's Rain Shell variants and others with active sales)

**What you're missing:** These products have a Compare At Price in Shopify (e.g., $179.00 > Variant Price $149.00), indicating they're on sale. But the feed has no `g:sale_price` attribute, so Google Shopping doesn't show strikethrough pricing. Sale indicators in Shopping results typically improve click-through rate by 10 to 30%.

**How to add:** This is a feed-generation issue. The images and sale prices exist in Shopify; the feed tool isn't mapping them correctly.
- If using Shopify Google Channel: verify that automatic sale price syncing is enabled in the app settings.
- If using a third-party feed tool: set the price mapping to: when `Variant Compare At Price` is populated and greater than `Variant Price`, map `Compare At Price` to `g:price` and `Variant Price` to `g:sale_price`.

### A03: GTIN in feed but missing from Shopify

**Affected items:** 120 items (all items)

**What you're missing:** Every item in the feed has a GTIN (g:gtin), but all Shopify `Variant Barcode` fields are empty. This means the GTINs exist only in the feed (or a supplemental feed), not in Shopify. If you ever switch feed tools or regenerate from Shopify data alone, all 120 GTINs will be lost, causing a sudden drop in product visibility.

**How to add in Shopify:**
1. Export the GTINs from your current feed or Merchant Center.
2. Go to Shopify Admin > Products.
3. For each product, open Variants and enter the GTIN in the Barcode field.
4. For bulk updates: use the Bulk Editor or import a CSV with the Variant Barcode column populated.

This is a data backfill task. It ensures the source of truth (Shopify) contains all product identifiers.

### A02: No additional images in feed

**Affected items:** 120 items (all items)

**What you're missing:** No items have `g:additional_image_link` attributes. Google allows up to 10 additional images per item. Products with multiple images get higher engagement in Shopping results.

**How to add:** If products have multiple images in Shopify (most do), this is a feed-generation issue. Check that your feed tool is mapping additional Shopify product images to `g:additional_image_link`. In Shopify's CSV export, additional images appear as separate rows with only Handle, Image Src, and Image Position populated.

### A05: No product highlights

**Affected items:** 120 items (all items)

**What you're missing:** Product highlights appear as bullet points in some Shopping result formats. No standard Shopify field maps to `g:product_highlight`.

**How to add:** Create a Shopify metafield (e.g., `custom.product_highlights`) and populate it with 3 to 10 bullet points per product. Then configure your feed tool to map the metafield to `g:product_highlight`. Alternatively, add highlights directly in Google Merchant Center via a supplemental feed.

## Priority Fix Order

1. **D02: Add gender and age_group to apparel accessories.** 20 items disapproved. Use Bulk Editor to set gender = "unisex" and age_group = "adult" on all accessories. Consider recategorizing non-clothing items. Shopify data fix, 15 minutes.

2. **D03: Remove duplicate feed items.** 4 duplicate items. Resync or regenerate the feed. Feed tool fix, 5 minutes.

3. **D04: Fix unclosed HTML tag.** 1 item disapproved. Edit the product description HTML in Shopify Admin. Shopify data fix, 2 minutes.

4. **A01: Enable sale price mapping in feed tool.** 21 items missing strikethrough pricing. Reconfigure feed tool price mapping rules. Feed tool fix, 10 minutes.

5. **W04 + W05: Standardize size and color names.** 3 products with inconsistent naming. Edit variant options in Shopify Admin. Shopify data fix, 10 minutes.

6. **A03: Backfill GTINs into Shopify.** 120 items at risk of GTIN loss. Bulk import barcodes from the existing feed. Shopify data fix, 30 to 60 minutes depending on variant count.

7. **A02: Enable additional image mapping in feed tool.** 120 items missing additional images. Configure feed tool to export multiple product images. Feed tool fix, 10 minutes.

## Confidence Notes

- **Landing page verification:** The audit compares feed prices to Shopify CSV prices but cannot verify that the live storefront shows the same prices. If prices differ between the CSV export and the live site (due to Scripts, discounts, or geo-pricing), some X01 findings may not reflect the actual landing page state.
- **Feed freshness:** The 2 price mismatches (X01) and 4 duplicates (D03) suggest the feed may be stale or out of sync with Shopify. Regenerating the feed before acting on other issues may resolve some findings automatically.
- **Merchant Center account settings:** This audit checks the feed data only. Account-level settings (shipping, tax, return policies, feed rules, supplemental feeds) are not visible in the XML and may override or supplement feed attributes.
- **Non-English checks limited:** Keyword stuffing and promotional text detection use English-language patterns. All products in this feed are English, so this is not a limitation for this audit.

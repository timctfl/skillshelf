# Google Merchant Feed Audit Rules

This reference defines the complete rule set for auditing a Google Merchant Center feed sourced from Shopify. Each rule is classified into one of three severity tiers that match Google's own enforcement model. The Python validation script (`validate_merchant_feed.py`) implements these rules mechanically and outputs structured JSON. The LLM reads the JSON and explains the fixes in Shopify-native language.

## Severity tiers

### Disapproved

The item will be rejected by Google Merchant Center and will not appear in Shopping ads or free listings. These are blocking errors that must be fixed before the item can serve.

### Demoted

The item is accepted but will perform worse in auction ranking and may trigger warnings in Merchant Center. These errors reduce impression share, click-through rate, or both.

### Advisory

The item is accepted and functional but is missing an optimization that would improve performance. These are recommendations, not errors.

## Disapproved rules

### D01: Missing required attribute

- **Attributes checked**: `g:id`, `g:title`, `g:description`, `g:link`, `g:image_link`, `g:price`, `g:availability`, `g:brand`
- **Condition**: The attribute is absent or contains only whitespace.
- **Shopify fix**: The corresponding Shopify field must be populated. See the field map for which Shopify column feeds each attribute. `Title`, `Body (HTML)`, `Handle`, `Image Src`, `Variant Price`, and `Vendor` are the most common gaps. Navigate to Shopify Admin > Products > [product] and fill the empty field.
- **Google reference**: [Product data specification, Required attributes](https://support.google.com/merchants/answer/7052112)

### D02: Missing required apparel attribute

- **Attributes checked**: `g:color`, `g:size`, `g:gender`, `g:age_group`
- **Condition**: The item's `g:google_product_category` starts with "Apparel & Accessories" (or uses a numeric ID in the 166-5598 range) and one or more of these attributes is absent.
- **Shopify fix**: For gender and age_group, go to Shopify Admin > Products > select affected products > Bulk edit. Add the "Google Shopping / Gender" and "Google Shopping / Age Group" columns if not visible (click "Columns"). If these fields are not available in the product editor (some themes and newer Shopify versions manage them through the Google & YouTube channel), open the Google & YouTube channel app and check its product data mapping. For color and size, ensure the product's variant options include an option named "Color" and/or "Size".
- **Google reference**: [Apparel and accessories requirements](https://support.google.com/merchants/answer/6324463)

### D03: Duplicate item ID

- **Condition**: Two or more items in the feed share the same `g:id` value.
- **Shopify fix**: Each variant must have a unique SKU. Go to Shopify Admin > Products > [product] > edit the variant and assign a unique SKU. If the feed uses Shopify's internal ID format (`shopify_{country}_{product_id}_{variant_id}`), the issue is in the feed generation tool, not the Shopify data. To resolve feed-level duplicates: check your feed app's sync status page for errors, or go to Google Merchant Center > Products > All products, filter to the affected items, and remove the duplicate entries. Avoid disconnecting and reconnecting the Google & YouTube channel, as this resets product approval status and campaign history.
- **Google reference**: [Product data specification, id](https://support.google.com/merchants/answer/6324405)

### D04: Malformed HTML in description

- **Condition**: The `g:description` contains unclosed HTML tags (e.g., `</p` missing `>`), nested block elements (e.g., `<p>...<p>` without closing), or HTML entity artifacts (e.g., `&amp;amp;`). Google may reject items with broken HTML or display garbled text in Shopping ads.
- **Shopify fix**: Go to Shopify Admin > Products > [product] > in the description editor, click "Show HTML" (or the code view icon) to view the raw markup. Find and fix the broken tags. Common patterns:
  - `</p` at the end of a paragraph: add the closing `>`.
  - `<p>...<br><p>`: replace the second `<p>` with `</p><p>`.
  - For bulk fixes, export the CSV, fix the Body (HTML) column in a spreadsheet, and re-import.
- **Google reference**: [Product data specification, description](https://support.google.com/merchants/answer/6324468)

### D05: Prohibited content in title or description

- **Condition**: The title or description contains promotional text ("buy now", "free shipping", "best price"), excessive capitalization (more than 50% uppercase words), or foreign currency symbols that don't match the feed's target country.
- **Shopify fix**: Edit the product title and description in Shopify Admin. Promotional language belongs in custom labels or ad copy, not in product data.
- **Google reference**: [Product data specification, title](https://support.google.com/merchants/answer/6324415)

## Demoted rules

### W01: Title does not include brand name

- **Condition**: The `g:brand` value does not appear in the `g:title` (case-insensitive substring match).
- **Impact**: Titles without the brand name have lower relevance scores for branded queries. Google recommends brand at the start of the title for most product types.
- **Shopify fix**: Edit the product Title in Shopify Admin to include the brand name, typically as the first word. Example: "Cascade Rain Shell" becomes "Great Outdoors Co. Cascade Rain Shell".

### W02: Description too short

- **Condition**: The plain-text content of `g:description` (after stripping HTML tags) is under 150 characters.
- **Impact**: Thin descriptions provide insufficient signal for Google to match the product to search queries. Items with thin descriptions receive fewer impressions.
- **Shopify fix**: Expand the product description in Shopify Admin. Focus on materials, use cases, key features, and differentiators. A good product description is 150 to 500 words.

### W03: Google product category too broad

- **Condition**: The `g:google_product_category` value has fewer than 3 levels of specificity (fewer than 2 " > " separators in the path, or a numeric ID that maps to a category with fewer than 3 levels).
- **Impact**: Broad categories reduce Google's ability to match the product to specific search queries and may affect eligibility for category-specific features.
- **Shopify fix**: Go to Shopify Admin > Products > [product] > Product organization > Google Shopping / Google Product Category and select a more specific category. Example: "Sporting Goods" should be "Sporting Goods > Outdoor Recreation > Camping & Hiking > Sleeping Bags".

### W04: Inconsistent size naming within an item group

- **Condition**: Variants sharing the same `g:item_group_id` use inconsistent size naming (e.g., "Small" and "S", or "X-Large" and "XL" in the same product).
- **Impact**: Google may not recognize these as valid size variants of the same product, reducing the effectiveness of size-filtered Shopping queries.
- **Shopify fix**: Go to Shopify Admin > Products > [product] > Variants and standardize size option values across all variants. Pick one convention (abbreviated or full) and apply consistently.

### W05: Inconsistent color casing within an item group

- **Condition**: Variants sharing the same `g:item_group_id` use different casing for the same color concept (e.g., "slate" and "Slate", or "FOREST GREEN" and "Forest Green").
- **Impact**: Google may treat these as different colors, fragmenting the product's variant presentation.
- **Shopify fix**: Go to Shopify Admin > Products > [product] > Variants and normalize color option values to title case (e.g., "Forest Green", "Slate").

### W07: Keyword stuffing in title or description

- **Condition**: The title or description contains repeated keywords, lists of synonyms, or unnatural keyword density. Heuristic: any single word (excluding stop words) appearing more than 3 times in the title, or more than 5 times per 100 words in the description.
- **Impact**: Google may penalize keyword-stuffed listings with lower quality scores or editorial review flags.
- **Shopify fix**: Rewrite the title and description for readability. Include relevant keywords naturally, once.

### W08: Missing GTIN for products that should have one

- **Condition**: `g:gtin` is absent and the product is not custom-made, vintage, or a category-specific exemption (e.g., some apparel items, handmade goods). Specifically, the `g:brand` is populated (suggesting a manufactured product) but no GTIN is present.
- **Impact**: Products with GTINs get higher placement in Shopping results. Google has stated that items from known brands without GTINs may see reduced visibility.
- **Shopify fix**: Go to Shopify Admin > Products > [product] > Variants > edit the Barcode field for each variant. The UPC/EAN can typically be found on product packaging or obtained from the manufacturer.

### W09: Invalid GTIN format

- **Condition**: `g:gtin` is present but does not conform to a valid GTIN format. Valid formats are GTIN-8 (8 digits), GTIN-12/UPC (12 digits), GTIN-13/EAN (13 digits), or GTIN-14 (14 digits). The check digit (last digit) must pass the standard modulo-10 algorithm.
- **Impact**: Invalid GTINs cause disapproval or warnings in Google Merchant Center. Google validates GTIN check digits and cross-references them against the GS1 database.
- **Shopify fix**: Verify the barcode on the product packaging. Go to Shopify Admin > Products > [product] > Variants > correct the Barcode field. Common errors: transcription typos, using internal SKUs instead of UPCs, and entering ISBNs without converting to GTIN-13.

### W10: Invalid attribute value

- **Condition**: An attribute has a value that is not in Google's accepted set. Checked attributes:
  - `g:availability` must be one of: `in_stock`, `out_of_stock`, `preorder`, `backorder`
  - `g:gender` must be one of: `male`, `female`, `unisex`
  - `g:age_group` must be one of: `adult`, `kids`, `toddler`, `infant`, `newborn`
  - `g:condition` must be one of: `new`, `refurbished`, `used`
- **Impact**: Invalid values cause disapproval. Google rejects items with unrecognized attribute values.
- **Shopify fix**: Correct the value in Shopify Admin or in the feed tool's mapping configuration. For gender and age_group, use Bulk Editor to update across multiple products.

## Advisory rules

### A01: No sale_price despite Shopify Compare At Price

- **Condition**: The Shopify CSV shows `Variant Compare At Price` populated (non-empty, greater than `Variant Price`) but the feed item has no `g:sale_price` attribute.
- **Impact**: The product is on sale in Shopify but Google Shopping does not display strikethrough pricing. This reduces click-through rate by 10 to 30% compared to showing the sale indicator (Google internal data, various case studies).
- **Shopify fix**: This is a feed generation issue, not a Shopify data issue. The feed tool needs to map `Variant Compare At Price` to `g:price` and `Variant Price` to `g:sale_price`. If using Shopify Google Channel, verify the app settings. If using a third-party tool (DataFeedWatch, Feedonomics, GoDataFeed), check the price mapping rules.

### A02: No additional_image_link

- **Condition**: The feed item has a `g:image_link` but no `g:additional_image_link`.
- **Impact**: Products with multiple images get higher engagement in Shopping results. Google allows up to 10 additional images per item.
- **Shopify fix**: Ensure the product has multiple images uploaded in Shopify Admin. If images exist in Shopify but are missing from the feed, the issue is in the feed generation tool. Check that additional product image rows (rows in the Shopify CSV with only Handle, Image Src, and Image Position) are being parsed and mapped to `g:additional_image_link`.

### A03: GTIN present in feed but missing from Shopify

- **Condition**: The feed contains a `g:gtin` for an item, but the corresponding Shopify CSV row has an empty `Variant Barcode` field.
- **Impact**: Data integrity risk. If the feed is regenerated from Shopify data alone (e.g., switching feed tools), all GTINs will be lost. This causes a sudden drop in product visibility.
- **Shopify fix**: Backfill the Barcode field in Shopify Admin. Go to Products > [product] > Variants > edit the Barcode field and enter the GTIN that is currently only in the feed. This ensures the GTIN is stored at the source of truth.

### A05: Missing product_highlight

- **Condition**: No `g:product_highlight` attributes present on the item.
- **Impact**: Product highlights appear as bullet points in some Shopping result formats. Items without them may have less rich presentations.
- **Shopify fix**: No standard Shopify field maps to product highlights. Options: use a Shopify metafield to store highlights and configure the feed tool to map it, or add highlights directly in Google Merchant Center via a supplemental feed.

### A06: Variant title missing option values

- **Condition**: The `g:title` for variant items does not include the variant's option values (color, size, etc.), making multiple variants have identical titles.
- **Impact**: Identical titles across variants make it harder for Google to differentiate variants and may result in lower relevance for attribute-specific queries (e.g., "blue rain jacket size large").
- **Shopify fix**: This is a feed generation issue. The feed tool should append option values to the product title for each variant.

### A07: shipping_weight missing or inconsistent units

- **Condition**: `g:shipping_weight` is absent, or items in the same feed use different weight units (mixing "kg" and "lb").
- **Impact**: Missing shipping weight may cause less accurate shipping cost estimates in Google Shopping. Inconsistent units across items may confuse buyers comparing products.
- **Shopify fix**: Shopify stores weight in `Variant Grams` with unit in `Variant Weight Unit`. Ensure both columns are populated. Standardize units across all products (all kg or all lb). The feed tool should combine these into the `g:shipping_weight` attribute (e.g., "2.5 kg").

## Rules that apply only when cross-referencing

These rules require both the Google Merchant XML feed and the Shopify product export CSV to be provided. They cannot be checked from the feed alone.

### X01: Price mismatch between Shopify and feed

- **Condition**: `Variant Price` in the Shopify CSV does not match `g:price` in the feed (after accounting for sale price logic).
- **Impact**: Price mismatches between feed and landing page cause disapproval.
- **Shopify fix**: If the prices genuinely differ, the feed is stale and must be regenerated. If the mismatch is due to sale price mapping, see rule A01.

### X02: Title mismatch between Shopify and feed

- **Condition**: The Shopify CSV `Title` is substantially different from the feed `g:title` (beyond expected variant suffix appending).
- **Impact**: Major title differences may indicate a stale feed. Minor differences (appending variant options) are expected and acceptable.
- **Shopify fix**: Regenerate the feed from current Shopify data.

### X03: Items in Shopify but missing from feed

- **Condition**: An active, published product/variant exists in the Shopify CSV but has no corresponding item in the feed.
- **Impact**: Lost exposure. Every active product should be in the feed unless intentionally excluded.
- **Shopify fix**: Check if the product meets all feed requirements (has a price, image, title, description). If it does and is still missing, the issue is in the feed generation tool. Check for filtering rules or errors in the feed app.

## Rule interaction notes

Some items may trigger multiple rules. Priority for reporting:

1. **Disapproved rules always appear first.** A disapproved item should not also be listed under demoted for the same attribute.
2. **Cross-reference rules (X-rules) take precedence** over feed-only rules when both detect the same attribute issue.
3. **Advisory rules appear last** and are grouped separately. They should be framed as optimizations, not errors.
4. When an item triggers both D01 (missing attribute) and a W-rule for the same attribute, only report D01. A missing attribute subsumes quality issues about that attribute.

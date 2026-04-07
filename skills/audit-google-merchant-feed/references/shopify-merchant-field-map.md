# Shopify to Google Merchant Center Field Mapping

This reference maps every column in a Shopify product export CSV to its corresponding Google Merchant Center feed attribute. Use this to validate whether a feed correctly represents the source Shopify data, and to explain fixes in Shopify-native terminology.

## Required attributes

These Google Merchant attributes must be present and valid for every item. Missing any of them causes disapproval.

### g:id

- **Shopify CSV source**: `Variant SKU` (preferred) or Shopify's internal `variant_id`
- **How Shopify Google Channel maps it**: Generates IDs as `shopify_{country}_{product_id}_{variant_id}`
- **Validation**: Must be unique across all items. Max 50 characters.
- **Shopify note**: If a merchant switches feed tools, the ID format may change. Changing IDs after running campaigns resets ad quality scores and transaction history.

### g:title

- **Shopify CSV source**: `Title` column (first variant row only; continuation rows are blank)
- **How Shopify Google Channel maps it**: Appends variant option values. Example: "Cascade Rain Shell - Men's" becomes "Cascade Rain Shell - Men's - S / Slate" in the feed.
- **Validation**: Max 150 characters. Should include brand, product name, and distinguishing variant attributes (color, size). Should not include promotional text or all caps.
- **Shopify note**: Only the first CSV row for each `Handle` has the `Title` populated. The feed generator must carry the title forward to all variant rows and append option values.

### g:description

- **Shopify CSV source**: `Body (HTML)` column (first variant row only)
- **How Shopify Google Channel maps it**: Wraps in CDATA or strips HTML tags. Google recommends plain text.
- **Validation**: Max 5000 characters. Should be substantive (at least 150 characters recommended). Must not contain promotional text, links to the store, or competitor references.
- **Shopify note**: Shopify stores product descriptions as HTML. Common issues: unclosed tags (e.g., `</p` instead of `</p>`), nested paragraph tags (`<p>...<br><p>`), and HTML entity artifacts (`&amp;` instead of `&`). The `SEO Description` column is sometimes used as a fallback, but it is often truncated or boilerplate.

### g:link

- **Shopify CSV source**: Constructed from `Handle` as `https://{domain}/products/{handle}`
- **Validation**: Must use the verified domain in Merchant Center. Must start with `http` or `https`.
- **Shopify note**: Shopify internal URLs use `{store}.myshopify.com`, but the Merchant Center domain is typically the custom domain. URL mismatch between feed and Merchant Center causes errors.

### g:image_link

- **Shopify CSV source**: `Image Src` (product-level, first variant row) or `Variant Image` (variant-specific)
- **How Shopify Google Channel maps it**: Uses `Image Src` for all variants unless `Variant Image` is populated for a specific variant.
- **Validation**: Must be a crawlable URL. Non-apparel images minimum 100x100px, apparel minimum 250x250px.
- **Shopify note**: `Image Src` and `Image Position` appear only on the first variant row and on dedicated image rows (rows with only Handle, Image Src, and Image Position populated). `Variant Image` appears on variant rows and should be preferred when available, as it shows the correct color/style for that variant.

### g:price

- **Shopify CSV source**: `Variant Price` and `Variant Compare At Price` (see pricing section below)
- **Validation**: Must include currency code (e.g., "149.00 USD"). Must match the landing page price.
- **Shopify note**: This is the most common source of feed errors for Shopify merchants. See the dedicated pricing section below.

### g:availability

- **Shopify CSV source**: Derived from `Variant Inventory Qty` and `Variant Inventory Policy`
- **How Shopify Google Channel maps it**: qty > 0 = `in_stock`, qty = 0 + policy `deny` = `out_of_stock`, qty = 0 + policy `continue` = `backorder` or `in_stock` depending on configuration.
- **Validation**: Must be one of: `in_stock`, `out_of_stock`, `preorder`, `backorder`.
- **Shopify note**: The `Published` column (`TRUE`/`FALSE`) and `Status` column (`active`/`draft`/`archived`) also affect whether a product appears in the feed at all. Products with `Published = FALSE` or `Status != active` should not be in the feed.

### g:brand

- **Shopify CSV source**: `Vendor`
- **Validation**: Must not be empty for items requiring a brand (most product types).
- **Shopify note**: Direct rename. Some merchants store the brand in a metafield rather than the Vendor field.

## Required for apparel (Apparel and Accessories categories)

These attributes are required when `g:google_product_category` falls under "Apparel & Accessories". Missing them causes disapproval for items in those categories.

### g:color

- **Shopify CSV source**: Option column where the Option Name is "Color" (typically `Option2 Name` = "Color", `Option2 Value` = the color)
- **Validation**: Must use Google-recognized color names. Must be consistent casing within an item group.
- **Shopify note**: Option names are dynamic in Shopify. The script must read `Option1 Name`, `Option2 Name`, `Option3 Name` to find which one contains "Color" and then use the corresponding value column.

### g:size

- **Shopify CSV source**: Option column where the Option Name is "Size", "Waist", "Length", or similar size-related names
- **Validation**: Must use consistent naming within an item group (do not mix "Large", "L", "Lg" for the same size). Must match Google's size format expectations for the product type.
- **Shopify note**: Same dynamic option mapping as color. Common Shopify issue: merchants use inconsistent size names across variants of the same product (e.g., "Small" on some variants and "S" on others).

### g:gender

- **Shopify CSV source**: `Google Shopping / Gender`
- **Validation**: Must be one of: `male`, `female`, `unisex`.
- **Shopify note**: This column is often empty in Shopify exports, especially for accessories and unisex items. Merchants must manually populate it through the Shopify Admin product editor or via Bulk Editor.

### g:age_group

- **Shopify CSV source**: `Google Shopping / Age Group`
- **Validation**: Must be one of: `adult`, `kids`, `toddler`, `infant`, `newborn`.
- **Shopify note**: Same population issue as gender. Most outdoor/general apparel is "adult" but the field is frequently left blank.

## Strongly recommended attributes

These are not strictly required but significantly affect performance and can cause warnings in Merchant Center.

### g:gtin

- **Shopify CSV source**: `Variant Barcode`
- **Validation**: Must be a valid GTIN-8, GTIN-12 (UPC), GTIN-13 (EAN), or GTIN-14. If the product has a GTIN, it must be submitted.
- **Shopify note**: Many Shopify merchants leave `Variant Barcode` empty, even when GTINs exist in Merchant Center from a previous upload or supplemental feed. This creates a data integrity risk: if the feed is regenerated from Shopify data alone, all GTINs are lost. The audit should flag empty barcodes and recommend backfilling via Shopify Admin > Products > [product] > Variants > edit Barcode field.

### g:mpn

- **Shopify CSV source**: `Google Shopping / MPN` or `Variant SKU` as fallback
- **Validation**: Must be unique per product (not per variant, though variant-specific MPNs are acceptable). Required when GTIN is not available.
- **Shopify note**: Shopify's Google Channel typically uses the SKU as the MPN if `Google Shopping / MPN` is empty.

### g:google_product_category

- **Shopify CSV source**: `Google Shopping / Google Product Category`
- **Validation**: Must use Google's product taxonomy (either the full path or the numeric ID). More specific categories perform better.
- **Shopify note**: Shopify has its own `Product Category` column (using Shopify's taxonomy), which is different from `Google Shopping / Google Product Category` (using Google's taxonomy). These do not always align. The audit should compare both and flag cases where the Google category is too broad or mismatched with the Shopify category.

### g:condition

- **Shopify CSV source**: `Google Shopping / Condition`
- **Validation**: Must be one of: `new`, `refurbished`, `used`.
- **Shopify note**: Defaults to "new" for most Shopify stores.

### g:item_group_id

- **Shopify CSV source**: Derived from `Handle` (all variants of the same product share the same handle)
- **Validation**: Must be the same for all variants of a product. Required when a product has multiple variants.
- **Shopify note**: The Handle is a reliable item group identifier in Shopify because it is stable and unique per product.

## The Shopify pricing model (critical)

Shopify's pricing fields work differently from Google Merchant Center's, and this is the single most common source of feed errors for Shopify merchants.

### How Shopify stores prices

| State | `Variant Price` | `Variant Compare At Price` |
|---|---|---|
| Normal (no sale) | Current price (e.g., $149) | Empty |
| On sale | Sale price (e.g., $149) | Original price (e.g., $179) |

When a sale is active in Shopify, the discounted price occupies `Variant Price` and the original price moves to `Variant Compare At Price`.

### How Google Merchant Center expects prices

| State | `g:price` | `g:sale_price` |
|---|---|---|
| Normal (no sale) | Current price (149.00 USD) | Omitted |
| On sale | Original price (179.00 USD) | Sale price (149.00 USD) |

Google expects `g:price` to always be the non-discounted price. The sale price is a separate attribute.

### Correct mapping logic

```
If Variant Compare At Price is populated AND Variant Compare At Price > Variant Price:
    g:price = Variant Compare At Price (original price)
    g:sale_price = Variant Price (discounted price)
Else:
    g:price = Variant Price (normal price)
    g:sale_price = omitted
```

### What goes wrong

Many feed generators (including basic Shopify Google Channel configurations) map `Variant Price` directly to `g:price` and ignore `Variant Compare At Price` entirely. This means:

1. The item shows at the correct price in Google Shopping, but without strikethrough pricing
2. The merchant misses the visual sale indicator that significantly improves click-through rate
3. Google cannot identify the item as being on sale, which affects ad ranking for sale-related queries

The audit should flag every item where `Variant Compare At Price` is populated in the Shopify CSV but `g:sale_price` is absent from the feed.

### g:sale_price_effective_date

- **Shopify CSV source**: No corresponding column in Shopify export
- **Validation**: ISO 8601 date range format. If omitted when `g:sale_price` is present, Google treats the sale as indefinite.
- **Shopify note**: Shopify does not export sale date ranges. Merchants must set this in Merchant Center directly or through a supplemental feed.

## Optional attributes with no direct Shopify CSV column

These Google attributes have no corresponding column in the standard Shopify product export CSV:

| Google Attribute | Notes |
|---|---|
| `g:additional_image_link` | Shopify CSV has additional image rows (rows with only Handle, Image Src, Image Position). These should map to additional image links (up to 10 per item). |
| `g:sale_price_effective_date` | Not in Shopify export. Must be set in Merchant Center or supplemental feed. |
| `g:material` | Not in standard export. Some merchants use Shopify metafields. |
| `g:pattern` | Not in standard export. |
| `g:size_type` | Not in standard export. Values: regular, petite, plus, big_and_tall, maternity. |
| `g:size_system` | Not in standard export. Values: US, UK, EU, etc. |
| `g:multipack` | Not in standard export. Flag if description mentions "pair" or "pack of". |
| `g:is_bundle` | Not in standard export. Flag if title or description suggests a bundle. |
| `g:product_highlight` | Not in standard export. Up to 10 bullet points highlighting key attributes. |

## Shopify CSV columns not used in Google Merchant feeds

These columns exist in the Shopify export but do not map to any Google Merchant attribute:

| Shopify CSV Column | Purpose |
|---|---|
| `Product Category` | Shopify's own taxonomy. Useful for comparison with `Google Shopping / Google Product Category`. |
| `Tags` | Shopify tags. Not a feed attribute, but useful for internal organization and validation. |
| `Published` | Whether the product is visible on the storefront. Should be TRUE for feed items. |
| `Image Position` | Ordering of product images. Position 1 is the primary image. |
| `Image Alt Text` | Alt text for the image. Not mapped to feed but useful for SEO auditing. |
| `Gift Card` | Must be FALSE for items in Google Shopping feeds. Gift cards are prohibited. |
| `SEO Title` | Alternative title for search engines. Some feed tools use this instead of Title. |
| `SEO Description` | Alternative description. Often truncated or boilerplate in Shopify exports. |
| `Variant Grams` | Product weight in the unit specified by `Variant Weight Unit`. Maps to `g:shipping_weight` when combined with the unit. |
| `Variant Weight Unit` | Unit for `Variant Grams` (g, kg, lb, oz). |
| `Variant Inventory Tracker` | Usually "shopify". Indicates where inventory is tracked. |
| `Variant Requires Shipping` | Whether the variant requires shipping. Digital products set this to FALSE. |
| `Variant Taxable` | Whether the variant is taxable. |
| `Variant Tax Code` | Tax code for the variant. |
| `Cost per item` | Wholesale cost. Maps to Google's optional `g:cost_of_goods_sold`. |
| `Status` | Product status: active, draft, archived. Only active products should be in feeds. |
| `Google Shopping / AdWords Grouping` | Legacy field for campaign grouping. |
| `Google Shopping / AdWords Labels` | Legacy field for campaign labels. |
| `Google Shopping / Custom Product` | Boolean flag for custom products. |
| `Google Shopping / Custom Label 0-4` | Custom labels for Shopping campaign segmentation. |
| `Price / International` | International pricing overrides. |
| `Compare At Price / International` | International compare-at pricing overrides. |

## Shopify CSV structure: the sparse-row pattern

Shopify product export CSVs use a sparse-row format for variants:

1. The **first row** for each `Handle` contains all product-level fields (Title, Body, Vendor, Product Category, Type, Tags, SEO fields, Google Shopping fields) plus the first variant's data.
2. **Continuation rows** for the same Handle contain only variant-specific fields (Option values, SKU, Price, Inventory, Variant Image). All product-level columns are blank.
3. **Image-only rows** may appear with only Handle, Image Src, and Image Position populated. These represent additional product images.

When parsing the CSV, the parser must "carry forward" product-level fields from the first row to all subsequent rows sharing the same Handle.

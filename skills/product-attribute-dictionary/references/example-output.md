<!-- product-attribute-dictionary v0.1 -->

# Product Attribute Dictionary: TrailBound Co.

## Overview

TrailBound Co. runs on Shopify. The catalog spans three categories (Apparel, Footwear, Gear) across 15 product types. Metafield data was included in this export.

## Standard Fields

These are the columns in a standard Shopify product export.

| Column | Format | Description |
|---|---|---|
| Handle | Lowercase hyphenated slug | URL identifier. Auto-generated from Title by Shopify. |
| Title | Free text | Product name. Convention: [Product Line] + [Product Type] (e.g., "Ridgeline Trail Runner," "Summit Insulated Jacket"). |
| Body (HTML) | HTML | Product description. Long-form marketing copy. Does not contain structured specs; those are in metafields. |
| Vendor | Free text | Brand name. "TrailBound Co." for first-party products. Third-party collabs use the partner name (e.g., "TrailBound x Vibram"). |
| Type | Controlled list | One of the 15 product types listed in the Product Types section. Category-level, not product-specific. Multiple products share the same type. |
| Tags | Structured comma-separated list | Uses a prefix taxonomy. See Conventions. |
| Published | Boolean | Whether the product is visible on the storefront. |
| Status | String | "active" or "draft." |
| Option1 Name | String | Label for the first variant dimension (e.g., "Size," "Waist," "Volume"). Varies by product type. |
| Option1 Value | Varies | Value for the first variant dimension. Format depends on the dimension. See Variant Attributes. |
| Option2 Name | String | Label for the second variant dimension, if present (e.g., "Color," "Inseam," "Width"). |
| Option2 Value | Varies | Value for the second variant dimension. |
| Option3 Name | String | Label for the third variant dimension, if present. Only used on products with three dimensions (e.g., Footwear with Size, Width, Color). |
| Option3 Value | Varies | Value for the third variant dimension. |
| Variant SKU | Structured string | See Conventions for encoding. |
| Variant Price | Decimal (two places) | Retail price in USD. |
| Variant Compare At Price | Decimal (two places) | Original price when a variant is on sale. Blank at full price. |
| Variant Barcode | Numeric string (13 digits) | EAN-13. One per variant. |
| Variant Grams | Integer | Product weight in grams. Used for shipping rate calculation. |
| Variant Inventory Qty | Integer | Current stock count per variant. |
| Variant Inventory Policy | String | "deny" (stop selling at zero) or "continue" (allow oversell). |
| Variant Fulfillment Service | String | "manual" for warehouse-fulfilled. |
| Variant Requires Shipping | Boolean | true for physical goods. |
| Variant Taxable | Boolean | true for taxable items. |
| Image Src | URL | Product image URL. See Conventions for image position rules. |
| Image Position | Integer | Display order. Most products carry 4-8 images. |
| Image Alt Text | Free text | Alt text for accessibility and SEO. Convention: "[Product Name] - [angle or detail]" (e.g., "Ridgeline Trail Runner - outsole detail"). Not consistently populated. |
| SEO Title | Free text | Custom page title. Convention: "[Product Name] | TrailBound Co." Set on flagship products, not across the full catalog. |
| SEO Description | Free text | Custom meta description. Set on flagship products. |

## Metafields

These fields require a separate metafield export (Matrixify, Shopify API, or bulk export). They are not included in the standard product CSV.

| Namespace | Key | Format | Description |
|---|---|---|---|
| custom | fabric_composition | Free text | Fiber content with percentages. Convention: "[pct]% [fiber] / [pct]% [fiber]" in descending order (e.g., "87% Recycled Nylon / 13% Elastane"). |
| custom | garment_weight_g | Integer | Weight of a single garment in grams, size Medium. Used in product comparison and marketing copy. |
| custom | waterproof_rating_mm | Integer | Hydrostatic head in millimeters. Only set on waterproof products. |
| custom | breathability_rating | Integer | MVTR in g/m²/24h. Present alongside waterproof_rating_mm. |
| custom | insulation_type | Free text | Insulation material and weight (e.g., "700-fill RDS Down," "PrimaLoft Gold 133g"). Only set on insulated products. |
| custom | fit | Controlled list | "Slim," "Regular," or "Relaxed." How the garment fits relative to the body. |
| custom | gender | Controlled list | "Men's," "Women's," or "Unisex." Determines which size scale applies. |
| custom | care_instructions | Free text | Full sentences (e.g., "Machine wash cold. Tumble dry low. Do not iron."). |
| custom | country_of_origin | Two-letter code | ISO 3166-1 alpha-2 (e.g., "VN," "CN," "BD"). |
| custom | sun_protection | String | UPF rating when applicable (e.g., "UPF 50+"). |
| custom | upper_material | Free text | Footwear upper construction (e.g., "Recycled mesh with TPU overlays"). |
| custom | outsole_material | Free text | Outsole compound and brand (e.g., "Vibram Megagrip"). |
| custom | midsole | Free text | Midsole technology (e.g., "Dual-density EVA with rock plate"). |
| custom | drop_mm | Integer | Heel-to-toe drop in millimeters. |
| custom | stack_height_mm | String | Heel and forefoot stack. Format: "[heel]/[forefoot]mm" (e.g., "30/22mm"). |
| custom | lug_depth_mm | Decimal (one place) | Outsole lug depth in millimeters. |
| custom | waterproof_membrane | Boolean | Whether the shoe uses a waterproof membrane. |
| custom | capacity_liters | Integer | Internal volume in liters. Packs only. |
| custom | packed_dimensions | String | Format: "[L] x [W] x [H] cm" (e.g., "25 x 18 x 12 cm"). |
| custom | packed_weight_g | Integer | Weight when packed, in grams. |
| custom | setup_weight_g | Integer | Weight when set up (tent body + fly + poles). Tents only. |
| custom | floor_area_sqm | Decimal (one place) | Interior floor area in square meters. Tents only. |
| custom | peak_height_cm | Integer | Interior peak height in centimeters. Tents only. |
| custom | season_rating | Controlled list | "2-season," "3-season," "3-4 season," or "4-season." |
| custom | fill_type | Free text | Sleeping bag insulation (e.g., "650-fill RDS Down," "Climashield Apex 133g"). |
| custom | frame_type | Controlled list | "Internal" or "Frameless." Backpacking packs only. |
| custom | hipbelt | Boolean | Whether the pack has a load-bearing hipbelt. |
| custom | pole_material | Controlled list | "Carbon Fiber" or "Aluminum." Trekking poles only. |
| seo | google_product_category | Free text | Google Product Taxonomy string (e.g., "Apparel & Accessories > Clothing > Outerwear > Coats & Jackets"). |
| reviews | avg_rating | Decimal (one place) | Aggregate customer review rating. Updated by the review platform integration. |
| reviews | review_count | Integer | Total published reviews. |

## Product Types

| Category | Product Type | Variant Dimensions |
|---|---|---|
| Apparel | Rain Shell | Size, Color |
| Apparel | Insulated Jacket | Size, Color |
| Apparel | Fleece Midlayer | Size, Color |
| Apparel | Base Layer Top | Size, Color |
| Apparel | Base Layer Bottom | Size, Color |
| Apparel | Hiking Short | Waist, Color |
| Apparel | Hiking Pant | Waist + Inseam, Color |
| Footwear | Trail Runner | Size, Width, Color |
| Footwear | Hiking Boot | Size, Width, Color |
| Footwear | Camp Shoe | Size, Color |
| Gear | Daypack | Volume, Color |
| Gear | Backpacking Pack | Torso Size, Color |
| Gear | Sleeping Bag | Length, Temperature Rating |
| Gear | Tent | Capacity |
| Gear | Trekking Pole | (none) |

## Variant Attributes

How each variant dimension works across the catalog.

**Size (apparel tops and layers).** Letter sizing, abbreviated. Men's: S, M, L, XL, XXL. Women's: XS, S, M, L, XL. Gender metafield determines which scale applies.

**Waist (apparel bottoms).** Numeric, inches, even numbers. Men's: 28 through 40. Women's: 24 through 34.

**Inseam (hiking pants only).** Combined with Waist as a single option value. Format: "[waist]x[inseam]" (e.g., "32x30"). Inseam options: 30, 32, 34. Not all waist/inseam combinations are stocked in every color.

**Size (footwear).** US sizing, numeric with half sizes. Men's: 7 through 14. Women's: 5 through 12. No "US" prefix in the value.

**Width (footwear).** Single letter: "M" (standard) or "W" (wide). Not all styles offer wide. When wide is not available, the Width dimension is omitted from the product entirely, not defaulted to "M."

**Volume (daypacks).** Liters with unit suffix. Format: "[number]L" (e.g., "18L," "24L," "30L").

**Torso Size (backpacking packs).** Dual range. Values: "S/M" or "M/L."

**Length (sleeping bags).** Full words. Values: "Regular" (up to 6'0") or "Long" (up to 6'6").

**Temperature Rating (sleeping bags).** Fahrenheit comfort rating with unit suffix. Format: "[number]F" (e.g., "20F," "30F"). Lower number means warmer bag. This is a variant dimension because the same shell is sold at multiple temperature ratings with different insulation fills.

**Capacity (tents).** Person count with suffix. Format: "[number]P" (e.g., "2P," "3P").

**Color (all categories).** Descriptive names, title case, one to three words (e.g., "Storm Gray," "Ember," "Deep Forest"). No hex codes, no generic labels. Color names are brand-specific and may be reused across product types but are not guaranteed to refer to the same shade. Colorway count varies: flagship products carry 4-6 colors, core basics carry 2-3, seasonal runs may carry 1. Color options rotate seasonally; specific color names should not be treated as permanent.

## Product Type Profiles

### Apparel

Covers: Rain Shell, Insulated Jacket, Fleece Midlayer, Base Layer Top, Base Layer Bottom, Hiking Short, Hiking Pant.

**Metafields that apply to all Apparel:** fabric_composition, garment_weight_g, fit, gender, care_instructions, country_of_origin, google_product_category, avg_rating, review_count.

**Metafields that apply to some Apparel:** waterproof_rating_mm and breathability_rating (Rain Shell, Insulated Jacket). insulation_type (Insulated Jacket, some Fleece Midlayers). sun_protection (Base Layer Top, Base Layer Bottom, Hiking Short).

**Variant structure.** Tops and layers: Size x Color. Typical matrix: 5 sizes x 3 colors = 15 variants. Shorts: Waist x Color. Typical matrix: 7 waist sizes x 2-3 colors. Pants: (Waist x Inseam) x Color. Not a full matrix; expect 20-40 variants per product.

### Footwear

Covers: Trail Runner, Hiking Boot, Camp Shoe.

**Metafields that apply to all Footwear:** upper_material, outsole_material, midsole, drop_mm, stack_height_mm, lug_depth_mm, waterproof_membrane, gender, care_instructions, country_of_origin, google_product_category, avg_rating, review_count.

**Variant structure.** Trail Runner and Hiking Boot: Size x Width x Color. Not a full matrix; wide is not available in all sizes or colors. Typical: 16 sizes x 1-2 widths x 3 colors = 48-96 variants. Camp Shoe: Size x Color, no Width. Whole sizes only (Men's 7-13, Women's 5-11).

### Gear

Covers: Daypack, Backpacking Pack, Sleeping Bag, Tent, Trekking Pole.

**Metafields that apply to all Gear:** care_instructions, country_of_origin, google_product_category, avg_rating, review_count.

**Metafields by type:**

| Metafield | Daypack | Backpacking Pack | Sleeping Bag | Tent | Trekking Pole |
|---|---|---|---|---|---|
| capacity_liters | Yes | Yes | | | |
| packed_dimensions | | | Yes | Yes | |
| packed_weight_g | | | Yes | Yes | Yes |
| setup_weight_g | | | | Yes | |
| floor_area_sqm | | | | Yes | |
| peak_height_cm | | | | Yes | |
| season_rating | | | Yes | Yes | |
| fill_type | | | Yes | | |
| frame_type | | Yes | | | |
| hipbelt | | Yes | | | |
| pole_material | | | | | Yes |

**Variant structure.** Daypack: Volume x Color (2-3 volumes x 3 colors). Backpacking Pack: Torso Size x Color (2 sizes x 2-3 colors). Sleeping Bag: Length x Temperature Rating (2 lengths x 2-3 ratings; color is not a dimension, each rating maps to one colorway). Tent: Capacity only (2P, 3P, 4P as variants; single colorway). Trekking Pole: single-SKU, no variants, sold as a pair.

## Conventions

**SKU encoding.** Format: TB-[TYPE]-[GENDER]-[SIZE]-[COLOR]-[WIDTH]. Hyphen-separated. TYPE is a 2-3 character code (e.g., "RS" for Rain Shell, "TR" for Trail Runner). GENDER is "M," "W," or "U." SIZE is the value as entered (e.g., "L," "32x30," "9.5"). COLOR is a 3-4 character abbreviation (e.g., "STGR" for Storm Gray). WIDTH is present only on footwear with multiple widths ("W" for wide, omitted for standard). Examples: TB-RS-M-L-STGR, TB-TR-W-8.5-EMBR-W.

**Tag taxonomy.** Prefix system with colons. Prefixes: `activity:` (hiking, trail-running, camping, backpacking), `season:` (spring, summer, fall, winter, 3-season), `feature:` (waterproof, insulated, packable, recycled), `collection:` (spring-25, essentials, gift-guide), `material:` (down, merino, gore-tex, primaloft). Products also carry unprefixed tags for cross-cutting attributes ("bestseller," "new," "sale"). Typical product has 5-10 tags.

**Product type naming.** Types are category-level labels shared by multiple products. "Trail Runner" covers several models. Product-level identity comes from Title, not Type.

**Image positions.** Position 1: 3/4 front angle, white background. Position 2: back view. Position 3: detail shot (fabric, outsole, etc.). Position 4+: lifestyle or on-model. File naming follows SKU with position suffix (e.g., "tb-rs-m-stgr-01.jpg").

**Gender handling.** Gender is a metafield, not a variant dimension. Men's and Women's versions of the same product are separate Shopify products with separate handles. The gender metafield determines which size scale applies.

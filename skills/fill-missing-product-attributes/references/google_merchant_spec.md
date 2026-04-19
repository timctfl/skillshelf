# Google Merchant Center Attribute Specification

## Required and Recommended Attributes

| Attribute | Accepted Values | Required For | Notes |
|---|---|---|---|
| `color` | Standard color names (e.g. "Red", "Navy Blue"). Up to 3 colors separated by `/` (e.g. "Black/White/Red"). | All Apparel & Accessories | Must match landing page text |
| `gender` | `male`, `female`, `unisex` | All Apparel & Accessories | Lowercase enum only |
| `age_group` | `newborn` (0-3mo), `infant` (3-12mo), `toddler` (1-5yr), `kids` (5-13yr), `adult` (13+) | All Apparel & Accessories | Lowercase enum only |
| `size` | Size value (S, M, L, 8, 10, 36). Pair with `size_system` and `size_type`. | Apparel clothing and all shoes | |
| `material` | Primary fabric or material (e.g. "Cotton", "Polyester", "Leather") | Recommended | Improves matching for fabric-based queries |

## Non-Obvious Details

1. **Color must match the landing page.** If the PDP says "Desert Sand," the feed must say "Desert Sand," not "Tan." Google flags the mismatch as misrepresentation.

2. **Creative color names are mapped internally.** Google maps submitted colors like "Sunset Blush" to a standardized internal list. Merchants are advised to use standard color names where possible, but the PDP-match rule takes precedence.

3. **Multicolor limit is 3.** Slash-separate up to 3 colors. A fourth color must be omitted. Flag (do not truncate silently) when more than 3 are detected in a row.

4. **age_group has no safe default.** Absence of a child signal is not evidence of adult status. A product with no age signal must be flagged for review, not auto-assigned `adult`.

5. **size_system must be explicit for apparel.** Accepted values: `US`, `UK`, `EU`, `AU`, `DE`, `FR`, `JP`, `CN`, `IT`, `BR`, `MEX`. Without it, size interpretation is ambiguous across regions.

## Shopify Column Names (Google Shopping feed columns)

The columns where these values live in a Shopify product CSV vary by export generation:

| Attribute | Old format | Matrixify format | Current Shopify export |
|---|---|---|---|
| color | `Google Shopping / Color` | `mm-google-shopping:color` | `product.metafields.mm-google-shopping.color` |
| gender | `Google Shopping / Gender` | `mm-google-shopping:gender` | `product.metafields.mm-google-shopping.gender` |
| age_group | `Google Shopping / Age Group` | `mm-google-shopping:age_group` | `product.metafields.mm-google-shopping.age_group` |
| size | `Google Shopping / Size` | `mm-google-shopping:size` | `product.metafields.mm-google-shopping.size` |
| material | `Google Shopping / Material` | `mm-google-shopping:material` | `product.metafields.mm-google-shopping.material` |

See [shopify_csv_columns.md](shopify_csv_columns.md) for the full write-target decision tree.

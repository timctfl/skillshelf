# Shopify CSV Column Reference

## Column Detection Priority

The `detect_missing_attributes.py` script scans the CSV header for attribute columns. For each target attribute, it checks these naming patterns in priority order:

| Priority | Pattern | Example |
|---|---|---|
| 1 | `Google Shopping / <Attribute>` (old native format) | `Google Shopping / Gender` |
| 2 | `mm-google-shopping:<attribute>` (Matrixify format) | `mm-google-shopping:gender` |
| 3 | `product.metafields.mm-google-shopping.<attribute>` (current export) | `product.metafields.mm-google-shopping.gender` |
| 4 | `product.metafields.shopify.<attribute>` (Shopify Standard Taxonomy) | `product.metafields.shopify.age-group` |

If none of the above patterns are found in the header for a given attribute, the fill goes to `needs_review.csv` with reason `no_target_column_in_csv`. The script never invents new column names.

## Write-Target Decision Tree

```
For each target attribute (color, gender, age_group, size, material):

1. Does the CSV header contain a Google Shopping metafield column for this attribute?
   YES: write there
   NO: does it contain a Shopify Standard Taxonomy column?
          YES: write there
          NO: does it contain a custom merchant metafield column matching the attribute?
                YES: write there (never invent new namespace)
                NO: add to needs_review.csv with reason: no_target_column_in_csv
```

## Prohibited Columns (Never Write Here)

These columns are explicitly prohibited. Both scripts check this list before writing any cell.

| Column Pattern | Reason |
|---|---|
| `Option1 Value`, `Option2 Value`, `Option3 Value` | Changing these values deletes and recreates variant IDs, breaking inventory sync, subscription references, and Google product history |
| Any column starting with `Variant Metafield:` | Shopify CSV import silently drops variant metafield columns; writing there does nothing and misleads the merchant |

## Standard Shopify Product CSV Columns (Reference)

Key columns the scripts read:

| Column | Notes |
|---|---|
| `Handle` | Product identifier. Variant rows with empty Handle inherit the previous row's Handle. |
| `Title` | Product title. Present only on the first row of each product group. |
| `Body (HTML)` | Product description. HTML is stripped before passing to LLM inference. |
| `Product Category` | Shopify Standard Product Taxonomy category string. Used for apparel detection. |
| `Type` | Legacy product type field. Fallback for apparel detection when Product Category is absent. |
| `Tags` | Comma-separated tags. Checked for structured attribute prefixes (`color:navy`, `gender:womens`). |
| `Option1 Name` / `Option1 Value` | First option. If Name is "Color" or "Colour", Value is extracted as color. |
| `Option2 Name` / `Option2 Value` | Second option. Same logic. |
| `Option3 Name` / `Option3 Value` | Third option. Same logic. |
| `Variant SKU` | Used as a row identifier in change_log.md and needs_review.csv. |
| `Google Shopping / Gender` | Target write column for gender (old format, most common in existing exports). |
| `Google Shopping / Age Group` | Target write column for age_group. |
| `Google Shopping / Color` | Target write column for color (if present). |
| `Google Shopping / Size` | Target write column for size (if present). |
| `Google Shopping / Material` | Target write column for material (if present). |

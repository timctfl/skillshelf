# Audit Script JSON Output Schema

This document describes the JSON output produced by `scripts/normalize_audit.py`. The LLM reads this schema to interpret the script's findings and present them to the merchant.

---

## Top-Level Structure

```json
{
  "metadata": { ... },
  "issues": { ... },
  "warnings": [ ... ]
}
```

---

## metadata

| Field | Type | Description |
|---|---|---|
| source_file | string | Filename of the input CSV |
| products_scanned | integer | Number of unique product handles found |
| variants_scanned | integer | Total number of data rows (excluding header) |
| total_issues_found | integer | Sum of all issues across all check categories |
| columns_present | string[] | Column headers from the CSV, in order |
| has_variant_image_column | boolean | Whether the CSV contains a "Variant Image" column |
| has_option3 | boolean | Whether the CSV contains "Option3 Name" column |
| csv_encoding | string | Detected file encoding (e.g., "utf-8-sig", "latin-1") |
| bom_detected | boolean | Whether a UTF-8 BOM was found at the start of the file |
| script_version | string | Version of the audit script |
| ran_at | string | ISO 8601 timestamp of when the audit ran |

---

## issues

Each key is a check category. The value is an array of issue objects. Empty arrays mean no issues found for that category.

### issues.whitespace

Each entry represents one cell with whitespace problems.

| Field | Type | Description |
|---|---|---|
| row | integer | 1-based row number in the CSV (header = row 1) |
| handle | string | Product handle |
| field | string | Which field has the issue, e.g., "Option2 Value" |
| original_value | string | The raw value as it appears in the CSV |
| trimmed_value | string | The value after stripping whitespace |
| whitespace_type | string | One of: "leading", "trailing", "both", "interior_abnormal" |
| characters | object[] | Details of each problematic character: position, human-readable name, Unicode codepoint |

### issues.case_inconsistencies

Each entry represents a group of values that differ only in casing.

| Field | Type | Description |
|---|---|---|
| option_name | string | The option name as displayed (e.g., "Color") |
| normalized_key | string | Lowercased, stripped value used for grouping |
| variants_found | object[] | Each variant: value, count, handles[], rows[] |
| suggested_canonical | string | Recommended canonical form |
| suggestion_reason | string | Why this form was chosen (e.g., "Most frequent") |

### issues.duplicate_variants

Each entry represents a set of rows with identical option combinations on the same product.

| Field | Type | Description |
|---|---|---|
| handle | string | Product handle |
| option_combo | string | Human-readable combo, e.g., "s / deep teal" |
| rows | integer[] | Row numbers of the duplicate rows |
| skus | string[] | SKUs on each duplicate row |
| prices_match | boolean | Whether all duplicates have the same price |
| prices | string[] | Distinct price values found |
| inventory_match | boolean | Whether all duplicates have the same inventory |
| inventories | integer[] | Inventory quantities on each row |

### issues.missing_variant_images

Each entry represents a variant row missing an image when sibling variants have images.

| Field | Type | Description |
|---|---|---|
| handle | string | Product handle |
| row | integer | Row number |
| sku | string | Variant SKU |
| option_values | string | Human-readable option combo, e.g., "M / Black" |
| siblings_with_images | integer | How many sibling variants have images |
| siblings_without_images | integer | How many sibling variants lack images |

### issues.size_ordering

Each entry represents a product with out-of-order size variants.

| Field | Type | Description |
|---|---|---|
| handle | string | Product handle |
| size_option_field | string | Which column holds sizes, e.g., "Option1 Value" |
| current_order | string[] | Size values in their current row order |
| expected_order | string[] | Size values in the correct order |
| size_system | string | One of: "apparel_letter", "plus_size", "toddler", "youth", "infant", "petite", "tall", "numeric", "compound", "unknown" |

### issues.option_value_aliases

Each entry represents a pair of values that may refer to the same thing.

| Field | Type | Description |
|---|---|---|
| option_name | string | The option name (e.g., "Color", "Size") |
| values | string[] | The two values that may be aliases |
| detection_method | string | "known_alias_map" or "substring_match" |
| confidence | string | "high", "medium", or "low" |
| suggested_canonical | string | Recommended canonical form |
| same_product | boolean | Whether both values appear on the same product handle |
| handles | string[] | All affected product handles |
| rows_per_value | object | Maps each value to its row numbers |

### issues.option_name_inconsistencies

Each entry represents a group of option names that should be unified.

| Field | Type | Description |
|---|---|---|
| names_found | string[] | The distinct option names found |
| products_per_name | object | Maps each name to its product handles |
| suggested_canonical | string | Recommended canonical name |
| suggestion_reason | string | Why this name was chosen |

### issues.handle_title_drift

Each entry represents a product where the handle does not match the slugified title.

| Field | Type | Description |
|---|---|---|
| handle | string | Actual handle |
| title | string | Product title |
| expected_handle | string | What the handle would be if generated from the title |
| difference_type | string | One of: "gendered_suffix_variation", "truncated", "minor_punctuation", "significant_mismatch" |

---

## warnings

An array of non-issue observations. Each warning has:

| Field | Type | Description |
|---|---|---|
| code | string | Machine-readable code (see below) |
| message | string | Human-readable description |
| details | object | Additional context (varies by code) |

### Warning codes

| Code | Meaning |
|---|---|
| bom_detected | UTF-8 BOM found in the CSV file |
| empty_option_value | Option name is set but value is empty |
| option_position_inconsistency | Same option name appears in different column positions across products |
| html_entity_in_option | HTML entity found in an option value (likely a paste error) |
| option_value_too_long | Option value exceeds Shopify's 255-character limit |
| default_title_product | Product uses Shopify's default single-variant pattern; skipped from checks |

---
name: product-attribute-dictionary
description: >-
  Produces a structured data dictionary from a product catalog export
  documenting every field, valid values, variant attributes, and metafields
  organized by product type. Accepts CSV exports from Shopify, BigCommerce,
  WooCommerce, or any ecommerce platform. Output is consumed by skills that
  write product content, audit catalog completeness, optimize feeds, or
  generate bulk data operations.
license: Apache-2.0
---

# Map Your Product Attribute Dictionary

This skill reads a product catalog export and produces a structured reference defining how the catalog is organized: what fields exist, what values they accept, how variants work, and which fields apply to which product types. The output is a data dictionary, not a content or terminology document. It gives downstream skills a schema to work from so they can generate accurate content, validate data, or produce importable files.

This skill uses two Python scripts to read the raw data and produce compact summaries for the LLM to interpret:

- [scripts/summarize_catalog.py](scripts/summarize_catalog.py) reads the product catalog CSV and produces a summary of column headers, platform detection, product types, distinct values, variant dimensions, and sample rows.
- [scripts/summarize_metafields.py](scripts/summarize_metafields.py) reads a metafield export CSV (wide or long format) and produces a summary of every metafield with data types, distinct values, fill rates, and per-type coverage.

The scripts handle the data extraction. You do the interpretation and writing.

For reference on the expected output, see [references/example-output.md](references/example-output.md).

## Voice and Approach

You are a catalog data analyst helping the user define the structure of their product catalog. Be precise and declarative. Write definitions, not observations. The dictionary should read like a reference document that someone consults when they need to know how a field works, not like a report about what was found in a CSV. When the export reveals ambiguity (a field used two different ways across product types), document both usages clearly rather than flagging one as wrong.

## Conversation Flow

### Turn 1: Welcome and Collect

Ask the user to share their product catalog export. A CSV from their ecommerce platform (Shopify, BigCommerce, WooCommerce, or similar) is the expected input. Let them know that if they also have a metafield or custom field export, they should include it because metafields often contain the most valuable product attributes and they are not included in a standard product export.

When the user uploads files, run the scripts immediately:

**Step 1: Always run the catalog summarizer.**

```
python scripts/summarize_catalog.py <product_csv> --output catalog_summary.json
```

**Step 2: If a metafield export was provided, run the metafield summarizer.**

Pass the product CSV as a second argument so the script can join on handle and report per-type metafield coverage.

```
python scripts/summarize_metafields.py <metafield_csv> --products <product_csv> --output metafield_summary.json
```

The metafield script detects the export format automatically. Wide format (one row per product, columns like `namespace.key`) and long format (one row per metafield value, columns like handle/namespace/key/value) are both supported.

Read the resulting JSON summaries. Do not ask clarifying questions before running the scripts. The summaries will answer most questions about platform, structure, and scope.

### Turn 2: Confirm Scope and Follow Up

Using the script's JSON output:

1. Report the detected platform.
2. List distinct product types with product counts.
3. List detected variant dimensions and the values found for each.
4. Note whether metafield data is present.

Present this as a summary and confirm with the user before producing the dictionary. If the catalog has many product types (more than 8-10), ask whether the user wants to scope to specific types or cover everything. For large catalogs, suggest grouping similar types where their attribute structures are nearly identical.

If no metafield data was provided, note it and ask once whether the user can provide it. If they cannot, move forward. The dictionary will define standard fields fully and include a placeholder section for metafields with instructions on how to fill it in later.

### Turn 3: Produce the Dictionary

Generate the complete dictionary as a downloadable Markdown file following the output structure below. Stamp the document with a version marker: `<!-- product-attribute-dictionary v0.1 -->`.

After sharing, ask the user to review it. Explain that this document will be used as a reference by other skills when they need to understand the catalog's structure, so accuracy matters. Suggest they check the field definitions and variant attribute conventions closely, since those will drive content generation and data operations downstream.

### Turn 4+: Review and Refine

Edit the dictionary in place when the user requests changes. Do not regenerate the entire document for a single correction. If the user provides a metafield export after the initial dictionary was produced, add the Metafields section to the existing document rather than starting over.

## How to Use the Script Output

The script produces a JSON summary with these sections:

- **columns.** The exact column headers from the CSV, in order. Use these as the field names in the Standard Fields table.
- **platform.** Detected platform (shopify, bigcommerce, woocommerce, or unknown). Determines which platform conventions to apply.
- **product_types.** Every distinct product type with a row count. Use this to build the Product Types table and decide how to group the profiles.
- **column_values.** Distinct values per column (up to 30, most frequent first). For columns with unique-per-product values (Body HTML, Handle, Image Src), the script skips enumeration and reports a row count instead. Use the distinct values to understand conventions and patterns, not as exhaustive valid value lists.
- **variant_dimensions.** For Shopify exports, the Option Name labels and all values found for each. Use this to identify which variant dimensions exist and how they're structured per product type.
- **type_samples.** Sample rows from the largest product types, trimmed to pattern-relevant columns. Use these to recognize conventions: SKU encoding patterns, tag structure, title formatting, body HTML structure, option value formats.

Your job is to interpret these inputs and write clear, declarative definitions. The script's data tells you what the catalog looks like. You describe how it works.

### How to use the metafield summary

If a metafield export was provided, the metafield summarizer produces a JSON with:

- **metafields.** Every namespace/key pair found. Each entry includes the inferred data type, distinct values (or sample values for high-cardinality fields), fill rate, and per-type coverage when a product CSV was joined.
- **format.** Whether the export was wide or long format.
- **per_type_coverage.** For each metafield, which product types use it and what percentage of products in that type have a value. Use this to populate the Product Type Profiles section, noting which metafields apply to all products of a type vs. only some.

Use the inferred types and value sets to write the Metafields table. Use the per-type coverage to determine which metafields belong in which Product Type Profile. A metafield with 100% fill rate on Rain Shells and 0% on everything else is type-specific. A metafield with coverage across all types is catalog-wide.

### Key principles

1. **Describe conventions, not snapshots.** The script shows you current values. Use them to identify the pattern, then describe the pattern. "Letter sizing, abbreviated: S, M, L, XL, XXL" is a convention. Listing every size value in the catalog is a snapshot that goes stale when new products are added.
2. **Use current values as examples.** When describing a field's format or conventions, use actual values from the summary as illustrative examples. Put them in parentheses or after "e.g." to signal they are examples, not the complete set.
3. **Define fields by purpose and format.** Each field definition should answer: what is this field for, what format does it use, and are there any conventions or constraints. Do not report statistics about the field.
4. **Let metafield descriptions note which types use them.** Some metafields apply to all products; others apply to specific types. Note this in the metafield description (e.g., "Only set on waterproof products"). The product type profiles then reference which metafields apply.

### Platform-specific handling

- **Shopify.** Handle is auto-generated from Title. Options are labeled (Option1 Name/Value, Option2 Name/Value). Tags are comma-separated free text. The script propagates product-level fields to variant rows automatically.
- **BigCommerce.** Product ID is platform-assigned. Categories are hierarchical.
- **WooCommerce.** Uses WordPress post structure. Attributes can be global or per-product.

## Output Structure

```
<!-- product-attribute-dictionary v0.1 -->

# Product Attribute Dictionary: [Brand Name]

## Overview

[Brief paragraph: platform, number of categories and product
types, whether metafield data was included.]

## Standard Fields

[Every column in the standard product export, defined once.]

| Column | Format | Description |
|---|---|---|

Each row defines one field. "Format" describes the data type
and structure. "Description" explains what the field is for,
any conventions, and for controlled fields, what values it
accepts.

## Metafields

[Every metafield, defined once. If metafield data was not
provided, include a placeholder section explaining how to
obtain the export and listing probable metafields based on
the product categories in the catalog.]

| Namespace | Key | Format | Description |
|---|---|---|---|

## Product Types

[Table listing each product type, its category, and which
variant dimensions apply.]

| Category | Product Type | Variant Dimensions |
|---|---|---|

## Variant Attributes

[How each variant dimension works. One entry per dimension
as prose. Describe the convention: format, scale, range, any
product-type-specific behavior. Use current values as
examples, not as the complete valid set.]

## Product Type Profiles

### [Type or Group Name]

[Which metafields from the Metafields section apply to
this type. Which apply to all products of this type vs.
only some. How the variant matrix works: which dimensions,
typical matrix size, any incomplete matrix behavior.]

[Repeat for each type or group.]

## Conventions

[Catalog-wide structural patterns: SKU encoding, tag
taxonomy, image position conventions, naming conventions,
gender handling, or anything else that applies across
fields and types.]
```

## Edge Cases

### Single product type catalog

Skip the Product Types table and Product Type Profiles. The Standard Fields, Metafields, and Variant Attributes sections cover everything. Add a Conventions section if there are structural patterns worth documenting.

### Very large catalog (1,000+ products, many product types)

The script handles large files and caps its output to keep the summary compact. Group similar product types where their attribute structures are nearly identical. Name the group and list which types it contains. Produce one profile for the group and note per-type differences within it.

### Very small catalog (fewer than 10 products)

Produce the dictionary but note that variant attribute conventions are based on a small catalog and may expand as products are added.

### No metafield data provided

Define standard fields fully. Include a Metafields section with placeholder text explaining how to obtain a metafield export for the detected platform. List probable metafields based on the product categories so the section is useful even before metafield data is added.

### Inconsistent use of a field across product types

Document each usage in the relevant Product Type Profile. If the Size dimension means S/M/L for apparel and 5L/10L/20L for bags, those are two different conventions that happen to share a column name.

### Non-English catalogs

Produce the dictionary in the same language as the catalog data. Field names and section headings stay in English (they are structural), but values and descriptions reflect the language of the source data.

### CSV formatting issues

If the export has encoding problems, malformed rows, or inconsistent delimiters, note the issues in a short paragraph at the end of the Overview section. Parse what you can. Do not refuse to produce output because of formatting problems.

### Metafield export provided after the dictionary was produced

Run the metafield summarizer against the new file, passing the original product CSV for the join. Add the Metafields section to the existing dictionary and update the Product Type Profiles with per-type metafield coverage. Do not regenerate the entire document.

### User wants to update the dictionary after catalog changes

Let them know they can re-run the skill with a fresh export and the existing dictionary uploaded as a starting point. The skill will run the scripts on the new export, compare against the existing dictionary, and update sections that changed (new fields, new product types, changed conventions) rather than starting from scratch.

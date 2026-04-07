---
name: variant-option-normalizer
description: >-
  Detects inconsistent Shopify variant option values, proposes a canonical
  naming system, and produces a corrected CSV with a change log.
license: Apache-2.0
compatibility: "Requires Python 3.10+. Falls back to pure LLM analysis if Python is unavailable."
---

# Normalize and Repair Variant Options

This skill accepts a Shopify product CSV export, scans every Option Name and Option Value column across all variant rows, and detects inconsistencies: color aliases (Gray vs Grey), size label variants (XL vs Extra Large), case mismatches, whitespace issues, broken size ordering, duplicate variants, missing variant images, and option name drift across products.

It produces two outputs: a corrected CSV ready for Shopify bulk re-import and a structured change log documenting every modification. Ecommerce teams use this after supplier data imports, before seasonal launches, or during platform migrations to clean up catalog data in bulk.

For reference on the expected output format, see [references/example-output.md](references/example-output.md).

---

## Script Execution

This skill uses a hybrid approach: a Python script handles deterministic checks (whitespace, case, duplicates, size ordering, missing images) and outputs structured JSON. The LLM interprets the JSON, handles judgment calls (alias disambiguation, brand voice), and manages the merchant conversation.

**Before analyzing any CSV yourself, run the audit script:**

```
python3 scripts/normalize_audit.py <csv_path> --assets-dir assets/
```

The script outputs JSON to stdout. Capture the full output and use it as the basis for the audit report.

**Fallback:** If the script fails (wrong Python version, file not found, any error), fall back to the original approach: read the CSV directly and perform all checks manually. Note in the change log that the script was unavailable and the audit was performed by LLM analysis alone.

For a description of every field in the JSON output, see [references/json-schema.md](references/json-schema.md).

---

## Interpreting Script Output

When presenting the script's JSON findings to the merchant:

1. **Do not show raw JSON.** Translate every finding into the Markdown audit report format described in the Conversation Flow.
2. **Map confidence levels to presentation style:**
   - `high` confidence: state as a finding ("These values are aliases and should be merged.")
   - `medium` confidence: present as a likely issue ("These values may be aliases. Can you confirm?")
   - `low` confidence: present as a question ("Are these two values intended to be different?")
3. **Handle warnings selectively.** Surface BOM detection, encoding issues, empty option values, and HTML entities in option values. Skip routine metadata like script version and timestamp.
4. **For handle/title drift:** Apply your own judgment about acceptable differences. The script flags all mismatches; filter out gendered suffix variations (e.g., dropping "Men's" or "Women's" from handles) before presenting to the merchant.
5. **For alias candidates with `same_product: true`:** These are almost certainly errors. Present them confidently. Cross-product aliases (`same_product: false`) may be intentional and should be framed as questions.

**Supplement the script's findings with LLM-only checks:**

- **Semantic alias detection:** Values that are semantically equivalent but not in the known alias map (e.g., "Crimson" and "Red", "Burgundy" and "Wine"). Use your knowledge of colors, materials, and sizing to identify candidates.
- **Context-aware judgment:** Determine whether ambiguous values are sizes, colors, or something else based on the option name and product type.
- **Brand voice alignment:** Consider whether the store's positioning suggests spelled-out sizes ("Extra Large") or abbreviations ("XL").

---

## Voice and Approach

You are a catalog operations specialist helping an ecommerce team clean up variant data. Be direct and precise. The merchant knows their products better than you do. Your job is to find inconsistencies, explain them clearly, and produce a clean CSV they can re-import. Do not narrate your process or over-explain. When transitioning between steps, keep it brief. Match the merchant's level of formality.

---

## Conversation Flow

### Turn 1: Scan and Audit

Start by explicitly asking the merchant to provide their Shopify product CSV. Do not assume, guess, or look for an existing file. Wait for the merchant to share it before proceeding.

Example prompt: "Please share your Shopify product CSV. You can paste the rows directly or provide the file path."

Once you have the CSV:

1. Run the audit script: `python3 scripts/normalize_audit.py <csv_path> --assets-dir assets/`
2. Parse the JSON output. Use the metadata section for summary counts.
3. Translate each non-empty issues array into the corresponding audit report section.
4. Apply the Interpreting Script Output rules above to filter, frame, and supplement the findings.
5. Run your own semantic checks for aliases, context-dependent values, and brand voice considerations that the script cannot detect.
6. Present findings as a structured audit report, grouped by issue type.

Do not ask clarifying questions before producing the audit. Show the findings first so the merchant can see what needs attention.

**Audit report format:**

```
## Variant Option Audit

**Products scanned:** N
**Variants scanned:** N
**Issues found:** N

### 1. Option Value Aliases
[Table: Values | Products Affected | Suggested Canonical Value]

### 2. Case Inconsistencies
[Table: Values Found | Suggested Canonical Value | Products Affected]

### 3. Whitespace Issues
[Table: Field | Value (showing whitespace) | Product Handle]

### 4. Size Sequence Issues
[Table: Product Handle | Current Order | Expected Order]

### 5. Duplicate Variants
[Table: Product Handle | Option Combination | SKUs | Note]

### 6. Missing Variant Images
[Table: Product Handle | SKU | Option Values]

### 7. Option Name Inconsistencies
[Table: Option Names Found | Products Using Each | Suggested Canonical Name]

### 8. Handle/Title Drift
[Table: Handle | Title | Expected Handle | Note]
```

Only include sections where issues were found. Skip clean sections.

### Turn 2: Confirm Normalization Plan

After the merchant reviews the audit, present the proposed normalization plan:

1. **Canonical value mapping table.** For every value that will change, show the original and proposed canonical form.
2. **Ambiguous choices.** Where multiple valid canonical forms exist (e.g., "Grey" vs "Gray", "Navy Blue" vs "Navy"), ask the merchant to choose. Do not assume a preference.
3. **Size ordering.** Show the proposed size sequence for each product where reordering is needed.
4. **Duplicates.** Confirm what action to take (flag only, remove second row, or merge).

Wait for explicit confirmation before producing output. If the merchant overrides any proposed canonical value, update the plan accordingly.

### Turn 3: Produce Output

Generate two outputs:

1. **Corrected CSV** as a downloadable file. Same column structure as the input. All header columns preserved. Changes applied inline.
2. **Change log** as a Markdown document using the output structure below.

After generating both outputs, ask the merchant:

- Where to save the corrected CSV (suggest a filename based on the input, e.g. `shopify-products-normalized.csv` in the same directory).
- Where to save the change log (suggest a filename alongside the CSV, e.g. `shopify-products-normalized-changelog.md`).

Write both files to the confirmed paths before closing out the turn.

Invite the merchant to review the corrected CSV and flag anything that needs adjustment.

### Turn 4+: Revise

Edit specific changes in place when the merchant requests corrections. Do not regenerate the entire CSV for a single fix. If the merchant provides additional products to normalize, process them and append to the existing outputs.

---

## Detection Categories

Apply these checks in order. Each category is independent.

### 1. Option Value Aliases

Same color, size, or material referred to by different strings across variants or products. Common patterns:

- Color: Gray/Grey, Charcoal/Charcoal Heather, Navy/Navy Blue
- Size: XL/Extra Large/X-Large, S/Small, M/Medium
- Material: variations in fiber content descriptions

Compare values using normalized lowercase, whitespace-trimmed forms. Flag any pair of values within the same option name where one could be an alias of the other. When two values appear on the same product, note that explicitly (same-product aliases are almost certainly errors; cross-product aliases may be intentional).

### 2. Case Inconsistencies

Same value in different casing across variants: BLACK, Black, black. Compare within each option name across the full file. The most common casing form is the default canonical choice, but title case (e.g., "Black") is preferred when frequency is tied.

### 3. Whitespace Issues

Leading or trailing spaces in any Option Name or Option Value cell. These are invisible in spreadsheets but cause Shopify to treat "Black" and "Black " as different values, creating phantom variants.

### 4. Size Sequence Ordering

Variants should appear in logical size order within each product. Check whether variant rows follow the expected sequence:

- **Apparel letter sizes:** XS, S, M, L, XL, XXL, 2XL, 3XL
- **Numeric sizes:** ascending order (28, 30, 32, 34...)
- **Named sizes (e.g., Small, Medium, Large):** map to their letter equivalents first

Flag products where size-based variants are out of sequence. Note: this check only applies to Option columns that contain size values.

When reordering rows, keep product-level metadata (Title, Body, Vendor, Tags, Image Src, SEO fields, Published, Status) on the first row of each product handle group. If a row moves into the first position, transfer those fields to it and clear them from the displaced row.

### 5. Duplicate Variants

Two or more rows on the same product handle with identical Option1 + Option2 + Option3 value combinations. Compare after normalizing case and trimming whitespace to catch duplicates hidden by inconsistencies.

If duplicates have different prices or inventory quantities, flag them for manual review rather than auto-merging.

### 6. Missing Variant Images

The `Variant Image` column is empty on a variant row while other variants on the same product have images. This check only applies when the input CSV includes the Variant Image column. Note: this check detects missing URLs, not broken URLs. Populated image URLs are not validated.

### 7. Option Name Inconsistencies

The same dimension called different things across products: Size vs Dimensions, Color vs Colour, Material vs Fabric. Compare all Option1/Option2/Option3 Name values across the file. Flag any near-matches.

### 8. Handle/Title Drift

The product handle should be a slugified version of the product title. Flag cases where the handle does not match what the title would produce (lowercase, hyphens for spaces, apostrophes removed, consecutive hyphens collapsed, no other special characters). Minor differences (e.g., dropping "Men's" or "Women's" from the handle) are acceptable and should not be flagged.

---

## Output Structure

### Output 1: Corrected CSV

- Same columns as input, in the same order. Copy every non-option cell verbatim. Do not parse, reformat, or truncate HTML in the Body column. Do not drop columns, including Google Shopping fields, metafield columns, or any other columns present in the input.
- All non-option columns preserved exactly (SKUs, prices, inventory, images, SEO fields, Google Shopping fields).
- Only Option Name cells, Option Value cells, and row ordering are modified.
- Offer as a downloadable file.

### Output 2: Change Log

```markdown
# Variant Normalization Change Log

**Source file:** [original filename or "pasted CSV"]
**Products scanned:** N
**Variants scanned:** N
**Total changes made:** N

---

## Canonical Option Values Established

| Original Value | Canonical Value | Products Affected | Reason |
|---|---|---|---|

## Issues Fixed

### Option Value Aliases Merged
[Details per merge with affected products]

### Case Normalized
[Details per value with affected products]

### Whitespace Removed
[Details per field with affected products]

### Size Order Corrected
| Product Handle | Previous Order | Corrected Order |
|---|---|---|

### Duplicate Variants Flagged
| Product Handle | Option Combination | SKUs | Action Taken |
|---|---|---|---|

### Missing Variant Images Flagged
| Product Handle | SKU | Option Values | Note |
|---|---|---|---|

### Option Names Standardized
[Details per name change with affected products]

### Handle/Title Drift Flagged
| Handle | Title | Recommendation |
|---|---|---|

---

## Skipped / Needs Review

[Anything that could not be resolved automatically, with explanation]
```

Only include sections where changes were made. Skip clean sections.

---

## Edge Cases

### Partial CSV upload

The merchant may export only a subset of products. Normalize within the provided set. Note in the change log that cross-catalog consistency cannot be guaranteed for option values shared with products not in the export.

### Non-apparel size systems

Numeric shoe sizes, waist/inseam combinations (32x30), bottle volumes, equipment dimensions. Do not force the apparel letter-size ladder on these. Use ascending numeric order. If the size system is ambiguous, ask the merchant which ordering to apply.

### Ambiguous aliases

When two values might be the same thing (Slate vs Slate Grey) but could be intentionally distinct colors, flag for human review. Do not merge unless the merchant confirms. The audit report should present both values and ask.

### Duplicate variants with different prices

Flag but do not merge. The merchant must decide which price is correct. Present both rows in the change log with their price difference highlighted.

### No Variant Image column

Some exports do not include this column. If absent, skip the missing-image check and note it in the change log.

### Very large CSV (500+ rows)

Process all rows. If the full corrected CSV exceeds output limits, break it into product groups and produce multiple files. Note any grouping in the change log.

### Matrixify or other export formats

This skill expects Shopify's native product export CSV format. If the merchant provides a Matrixify export or another tool's format, identify the column mapping differences and proceed. Note the format in the change log.

### Products with Option3

Some products use all three option slots (e.g., Size + Color + Material). The skill handles up to three option columns. Apply all detection categories to each option column independently.

### Single-product CSV

The skill works with a single product. Cross-product checks (option name consistency, value aliases across products) will have limited scope. Note this in the change log.

---

## Closing

Once the merchant approves the corrected CSV, note that it is ready for Shopify bulk import via Settings > Import in the Shopify admin. Include these reminders:

- If variants were reordered, the import will update variant display order on the storefront.
- Shopify import overwrites existing product data for matching handles. Back up the current export before importing.
- Shopify import cannot delete variants, only add or update them. If a duplicate row was removed from the CSV, the merchant must also delete that variant manually in the admin.

Suggest running this skill again after the next supplier data import or seasonal catalog update to catch new inconsistencies before they reach customers.

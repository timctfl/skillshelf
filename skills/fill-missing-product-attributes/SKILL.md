---
name: fill-missing-product-attributes
description: >-
  Fills blank Google Shopping attributes in Shopify apparel CSVs using
  deterministic extraction and LLM inference. Never overwrites existing data.
license: Apache-2.0
compatibility: "Requires Python 3.10+ with code execution. Cannot run without script execution."
---

# Fill Missing Product Attributes

This skill accepts a Shopify product CSV export, identifies rows missing `color`, `size`, `material`, `gender`, and `age_group` values, infers them from the data already in the CSV, and produces three outputs: a corrected CSV ready for Shopify re-import, a `change_log.md` documenting every change with confidence scores and source evidence, and a `needs_review.csv` listing anything that could not be filled with confidence.

Missing attributes are the primary reason Shopify apparel products get disapproved in Google Merchant Center and the primary cause of broken product filters on Shopify storefronts. The data needed to fill them is almost always already present in the CSV, in option values, tags, or the product title. This skill extracts it. English catalogs only.

For a worked example of all four conversation turns, see [references/example-output.md](references/example-output.md).

---

## Voice and Approach

You are a catalog operations specialist helping a Shopify merchant clean up product data before a Google Shopping sync or storefront filter launch. Be direct and precise. Explain what you found and what you filled. Never narrate your process. When transitioning between turns, be brief. Match the merchant's formality level.

---

## Conservative Defaults

This skill applies two absolute constraints to prevent data corruption:

1. **Never modify Option1/2/3 Value columns.** Changing these values in a Shopify CSV import deletes and recreates variant IDs, breaking inventory sync, subscription references, and Google product history tracking. Fills go to Google Shopping metafield columns, never to option value cells.

2. **Never write to `Variant Metafield:` columns.** Shopify CSV import silently drops variant metafield columns. Writing there does nothing and misleads the merchant into thinking the fix was applied.

Additional defaults:

- Never overwrite an existing non-empty value. If a field already has data, it stays.
- Never default `age_group` to `adult` without evidence. Absence of a child signal is not adult evidence.
- Never invent a color not present in the row's own text. Evidence quote is required for every fill.
- Color values with more than 3 slash-separated colors are flagged in `needs_review.csv`, not truncated.

---

## Script Execution

This skill uses a hybrid approach: a Python script handles deterministic extraction (option values, tag prefixes, title vocabulary, sibling propagation). Claude handles semantic inference for cases the script cannot resolve.

**Stage 1: Run the detection script**

```
python3 scripts/detect_missing_attributes.py <csv_path> --assets-dir assets/
```

The script creates a temporary directory automatically (e.g. `/tmp/fill-attrs-XXXX`) and writes `deterministic_fills.json` and `needs_inference.json` there. The stdout JSON includes a `work_dir` key with the temp directory path — capture and retain this path for all subsequent stages. Do not pass `--output-dir` unless the merchant specifically requests a custom location for the intermediate files.

**Stage 3: Apply approved fills**

```
python3 scripts/apply_fills.py <csv_path> \
    --work-dir <work_dir> \
    --output-dir <confirmed_output_dir>
```

`--work-dir` is the path from the Stage 1 `work_dir` key. The script auto-discovers `deterministic_fills.json` and `approved_fills.json` inside it. After successful completion, the temp directory is deleted automatically. If only deterministic fills are available (no LLM inference needed), the script proceeds without `approved_fills.json`.

**If the script fails:** Report the error verbatim to the merchant. Do not attempt to fill attributes manually without the deterministic extraction stage running. This skill's safety guarantees (closed vocabulary matching, enum validation, evidence-required output) depend on the Python script.

For the full attribute column reference (all four naming generations of Google Shopping metafield columns), see [references/shopify_csv_columns.md](references/shopify_csv_columns.md).

---

## Confidence Scoring

Deterministic fills carry source-assigned confidence. LLM fills carry self-reported confidence (capped at 0.90). Thresholds are per-field because fields carry different risk profiles with Google.

**Auto-write thresholds (fills below threshold go to needs_review.csv):**

| Field | Threshold | Rationale |
|---|---|---|
| `gender` | 0.90 | Wrong value triggers Google misrepresentation flag |
| `age_group` | 0.90 | Same |
| `color` | 0.80 | Must match PDP; wrong value = disapproval |
| `material` | 0.70 | Cosmetic impact only |
| `size` | 0.95 | Only auto-written when extracted from option value |
| `size_system` | 0.95 | Explicit US/UK/EU from option name only |
| `size_type` | 0.90 | Token scan of option value only |

See [references/extraction_sources.md](references/extraction_sources.md) for confidence values by source.

---

## Conversation Flow

### Turn 1: Accept CSV and Run Stage 1

Before asking for the file, confirm the merchant has it ready. If they are unsure how to export:

1. In Shopify Admin, go to Products > Export.
2. Choose "All products" and select "Plain CSV file". Click Export.
3. The file arrives in your email as a `.csv` attachment — not `.xlsx`.
4. Google Shopping columns (the fields Shopify uses to send product attributes like color, size, and gender to Google Merchant Center — for example, "Google Shopping / Color") appear in the export automatically when the Google and YouTube sales channel is connected to a Merchant Center account. If they are absent from your export, the skill will tell you and explain what to do.

Python is run automatically by Claude Code — you do not need to install anything.

Ask the merchant to provide their Shopify product CSV. Once provided:

1. Run: `python3 scripts/detect_missing_attributes.py <csv_path> --assets-dir assets/`
2. Parse the JSON output. Use the metadata section for summary counts.
3. Present the audit report. Do not show raw JSON.

**Audit report format:**

```
## Missing Attribute Audit

**Products scanned:** N apparel / M total (N non-apparel skipped)
**Variant rows scanned:** N
**Deterministic fills made:** N (across N products)
**Fields needing LLM inference:** N rows

### Deterministic Fills Made
| Handle | SKU | Field | Value | Source | Confidence |
|---|---|---|---|---|---|

### Needs LLM Inference
| Handle | SKU | Title | Fields Missing | Context Available |
|---|---|---|---|---|

### Skipped (Non-Apparel)
[List: handle (product type)]

### Conflicts Detected (Not Overwritten)
[Table: Handle | Field | Option Value | Existing Value — if any]
```

Only include sections where there is something to show.

**Apparel detection:** The script gates on `Product Category` first (checks for "Apparel", "Clothing", "Footwear"). Falls back to the `Type` column against a known term list. If both are empty, falls back to high-signal title tokens (shirt, tee, dress, jacket, etc.). Products with no signal in any of the three tiers are skipped entirely.

### Turn 2: LLM Inference (Stage 2 — Claude does this autonomously)

After presenting the audit, read `needs_inference.json` from the `work_dir` path reported in Stage 1's stdout JSON and infer remaining fields without asking the merchant first.

**Rules for this stage:**

- Every fill must include an `evidence_quote` — the exact substring from `title`, `body_html_stripped`, or `tags` that supports the inference. If you cannot quote evidence, return `null`.
- For `gender` and `age_group`, only output values from the closed enums: `gender` = male/female/unisex; `age_group` = newborn/infant/toddler/kids/adult.
- Cap self-reported confidence at 0.90.
- If `title` has fewer than 3 meaningful words AND `tags` is empty AND `body_html_stripped` is empty, return `null` for all fields with source `llm_insufficient_context`.
- Do not default `age_group` to `adult` without evidence.

Hold all inferences in conversation memory. Do not write any file at this stage. Present a review table to the merchant:

```
## Proposed Fills (LLM Inference)

| Handle | SKU | Field | Proposed Value | Confidence | Evidence | Action |
|---|---|---|---|---|---|---|
```

Where "Action" is: "Auto-approve (high confidence)" / "Review recommended" / "Flagged — your input needed".

If any proposed color is not a Google standard color name but matches the product's own text, note: "Value preserved verbatim from product title to match PDP text per Google's feed matching requirement."

### Turn 3: User Approval

The merchant reviews the proposed fills. They can:
- Approve all (say "approve all" or "looks good")
- Reject specific rows by handle and field
- Override a value

Once confirmed, write `approved_fills.json` to `{work_dir}/approved_fills.json`, combining the approved LLM fills with the deterministic fills from Stage 1. The format is shown in [references/example-output.md](references/example-output.md).

Tell the merchant: "I'll save the output files in the same folder as your CSV. Let me know if you'd like them somewhere else." Proceed immediately using the CSV's directory as `--output-dir` unless they specify otherwise.

Run Stage 3:

```
python3 scripts/apply_fills.py <csv_path> \
    --work-dir <work_dir> \
    --output-dir <confirmed_output_dir>
```

### Turn 4: Deliver Output

Before presenting output, run this checklist:

- Row count in corrected CSV matches input row count.
- No Option1/2/3 Value columns were modified.
- No `Variant Metafield:` columns were written to.
- `change_log.md` has one entry per fill applied.

If all checks pass, report the exact paths where the three files were written:

1. **`<stem>-filled.csv`** — corrected Shopify CSV, ready for re-import.
2. **`change_log.md`** — human-readable Markdown log grouped by product: handle, field, value set, source (plain English), confidence %, and REVIEW/OK status.
3. **`needs_review.csv`** — items that could not be filled: Priority (HIGH/MEDIUM/LOW), Handle, Product Title, SKU, Field, Target Column, Reason (plain English), Action (what to do), Evidence Quote, Confidence, Suggested Value.

**Closing reminders:**

- Import path in Shopify admin: Products > Import (top right of the Products list page).
- Back up the current CSV export before importing.
- Shopify import overwrites existing product data for matching handles. It cannot delete variants, only add or update.
- If `needs_review.csv` has rows with `reason = conflict_with_existing_value`, those require manual inspection to resolve which value is correct.

Suggest running this skill again after the next supplier data import or before any Google Shopping campaign launch.

---

## Google Merchant Center Spec

For the exact accepted values, required/recommended status, and non-obvious rules for all five attributes, see [references/google_merchant_spec.md](references/google_merchant_spec.md).

Key rules to enforce during inference:

- `color` values must match the product's own landing page text. "Desert Sand" must stay "Desert Sand", not be normalized to "Tan".
- `size_system` must be set explicitly for apparel (US/UK/EU/AU etc.). Do not leave it ambiguous.
- `color` supports up to 3 slash-separated values. Flag more than 3 in `needs_review.csv`.
- `age_group` has no safe default. Flag products with no age signal rather than assuming `adult`.

---

## Edge Cases

### Non-apparel mixed catalogs

Products with no `Product Category` and no recognized `Type` are skipped. They appear in the "Skipped (Non-Apparel)" section of the audit report. Do not infer apparel attributes for mugs, candles, books, or other non-apparel items.

### No Google Shopping columns in CSV header

If the CSV has no target column for an attribute (e.g., no "Google Shopping / Color" column), the script logs those rows in `needs_review.csv` with reason `no_target_column_in_csv`. Tell the merchant to re-export with the Google Shopping columns included, or use Matrixify to add the columns.

### Multilingual product titles

Version 1 does not infer attributes from non-English titles. Return `null` for those fields and add a note in `needs_review.csv` with reason `non_english_input`. Document this clearly.

### Large catalogs (over 5,000 rows)

Shopify's CSV import limit is 15 MB. For catalogs over 5,000 rows, chunk the CSV by product handle groups and process each chunk separately. The script handles each run independently. Combine the change logs after all chunks are processed.

### Matrixify or third-party export formats

This skill expects Shopify's native product export format. If the merchant provides a Matrixify export, identify the column mapping differences and proceed. Note the format in the change log.

### All products are single-variant (default title)

If all products use the default "Title" option with no Color, Size, or Material options, the script will find no option-based fills. Title and tag extraction still runs. Note in the audit report that option-based extraction was not applicable.

---

## Error Handling

Stop and report to the merchant rather than proceeding with bad data.

| Error | What to do |
|---|---|
| Script exits with code 1 | Report the error message verbatim. Do not attempt to fill attributes without the script. |
| Script exits with code 2 (validation failure) | The validation error describes what would go wrong. Report it and do not apply any fills. |
| Missing required CSV columns (Handle, Title) | Tell the merchant which columns are missing. Ask them to re-export from Shopify Admin using the standard export format. |
| Wrong delimiter or unparseable CSV | Report that the file does not appear to be a standard comma-separated CSV. Shopify exports use UTF-8 with comma delimiters. Ask the merchant to re-export or check if the file was opened and re-saved by Excel. |
| All fills land in needs_review.csv | This means the CSV has no target columns for any attribute. Tell the merchant their CSV needs Google Shopping columns added before this skill can write anything. |

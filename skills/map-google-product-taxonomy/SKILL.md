---
name: map-google-product-taxonomy
description: >-
  Maps product titles and descriptions to Google Product Taxonomy categories
  and outputs a supplemental feed CSV with google_product_category filled in.
license: Apache-2.0
compatibility: "Requires Python 3.10+. Falls back to pure LLM analysis if Python is unavailable."
---

# Map Products to Google Product Taxonomy

This skill accepts a product CSV (Shopify export or any CSV with title and description columns) and assigns each product to the correct category in the Google Product Taxonomy. It outputs a supplemental feed CSV with `google_product_category` filled in for every product, ready to merge into a Google Shopping feed.

Google requires this field for apparel products and recommends it for all others. Without it, items are demoted or disapproved in Google Shopping. Products mapped to specific leaf categories (4 or more levels deep) receive better placement than those mapped to broad parent categories.

This skill is step 2 of a three-part Feed Compliance pipeline: normalize variants with the Variant Option Normalizer skill first, then map taxonomy here, then audit the finished feed with the Audit a Google Merchant Feed skill.

For reference on the expected output format, see [references/example-output.md](references/example-output.md).

---

## Script Execution

This skill uses a hybrid approach: a Python script handles deterministic keyword matching and outputs structured JSON with confidence levels. The LLM interprets the JSON, handles ambiguous cases the script cannot resolve, and manages the merchant conversation.

**Before analyzing any CSV yourself, run the classification script:**

```
python3 scripts/classify_taxonomy.py <csv_path> --assets-dir assets/
```

The script auto-detects title and description columns from common Shopify and ecommerce column names. If auto-detection fails, specify columns explicitly:

```
python3 scripts/classify_taxonomy.py <csv_path> --assets-dir assets/ --title-col "Title" --desc-col "Body (HTML)"
```

The script outputs JSON to stdout. Capture the full output and use it as the basis for the classification report.

**Fallback:** If the script fails for any reason, fall back to LLM-only classification using the rules in the LLM Classification section below. Note in the report that the script was unavailable and all classifications were produced by LLM analysis.

---

## Interpreting Script Output

The script assigns one of three confidence levels to each product:

- `high`: Score above threshold with a clear gap to the next candidate. Present as a finding ready for batch approval.
- `medium`: Score above threshold but competing categories are close. Present alternatives and ask the merchant to confirm.
- `low`: Score below threshold. No clear keyword signal. Apply LLM classification rules and present reasoning.

When presenting results:

1. Do not show raw JSON. Translate every finding into the report format described in Conversation Flow.
2. Group by confidence tier. Show high-confidence products in a batch approval table; show medium and low products individually with context.
3. For `medium` items: show the proposed category and the top alternative with a brief note on what signal each matched (e.g., "Matched 'fleece' and 'pullover' for Outerwear, but 'layer' also scored for Activewear").
4. For `low` items: apply LLM classification rules first, then present the LLM-proposed category with one-sentence reasoning.
5. If the merchant's CSV already has a `google_product_category` column with a valid leaf-level path (3 or more levels), preserve it and exclude that product from classification. Note what was preserved vs. newly classified in the report.

---

## LLM Classification Rules

Apply these when the script returns `confidence: "low"` or when the script is unavailable:

1. Read the full product title and description before classifying. Do not classify from title alone.
2. Prefer specific leaf categories (4 or more levels deep) over broad parent categories.
3. For apparel: use gender and age signals in the title to pick the most specific applicable subcategory. "Men's Rain Jacket" maps deeper than "Rain Jacket."
4. When two categories are equally valid, prefer the one that matches the product's primary use case. "Hiking Shorts" maps to hiking-specific activewear rather than generic shorts.
5. Never invent category paths. Every proposed path must be a real Google Product Taxonomy string. If uncertain, state the nearest confirmed parent and flag for merchant review.
6. State your reasoning in one sentence before giving the category path.

---

## Voice and Approach

You are a feed operations specialist helping a merchant get their catalog into Google Shopping. Be direct and accurate. Category mapping is a judgment task, not a creative one. When confidence is high, say so clearly. When it is not, say that too. Do not over-explain taxonomy structure unless the merchant asks. Match the merchant's level of formality.

---

## Conversation Flow

### Turn 1: Collect Input and Classify

Ask the merchant to share their product data. Accept any of:

- Shopify product export CSV (Admin > Products > Export > All products, Plain CSV file)
- Any CSV with at minimum a product title column and ideally a description column
- A Google Merchant Center feed XML file (the script parses `<g:title>` and `<g:description>` fields; note this in the report header)

Example prompt: "Share your Shopify product CSV or any product list with titles and descriptions. I will map each product to the correct Google Product Taxonomy category and produce a supplemental CSV ready to merge with your feed."

Once you have the file:

1. Run: `python3 scripts/classify_taxonomy.py <csv_path> --assets-dir assets/`
2. Parse the JSON. Check the `meta` section for summary counts and which columns were detected.
3. Separate results into three groups by confidence level.
4. Apply LLM classification rules to all `low` confidence items before presenting.
5. Present the full classification report using the format below. Do not ask questions before showing results.

**Report format:**

```
## Taxonomy Classification Report

Products scanned: N
High confidence (ready for batch approval): N
Medium confidence (needs your input): N
Low confidence (LLM-classified, needs review): N
Title column: [detected column name]
Description column: [detected column name or "not found - title only"]

### High Confidence: Proposed Mappings

| Product | Proposed Category | Matched Keywords |
|---|---|---|

### Medium Confidence: Please Confirm

| Product | Proposed Category | Alternative | Signal |
|---|---|---|---|

### Low Confidence: Needs Review

| Product | LLM Proposed Category | Reasoning |
|---|---|---|
```

Only include sections where products exist in that confidence tier.

### Turn 2: Confirm Mappings

1. For high-confidence items: the merchant can approve the entire batch in one reply. If they want to review individually, walk through them.
2. For medium items: present the top two candidates. Let the merchant choose or override.
3. For low-confidence items: present the LLM proposal with one-sentence reasoning. Ask the merchant to confirm, override, or flag for manual lookup.
4. Record any merchant-overridden categories with `classification_source: merchant-override`.
5. If the merchant overrides a high-confidence item after seeing the proposal, that is a merchant override. The script is not infallible.

### Turn 3: Output

Before producing output, verify:

- Every product in the input has a proposed category. None skipped silently.
- All category path strings are real Google taxonomy paths.
- Merchant-overridden items are marked with `classification_source: merchant-override`.

Generate two output files:

1. **Supplemental feed CSV**: one row per product, columns defined in Output Structure below.
2. **Classification report**: Markdown file with the full mapping table, confidence levels, and sources.

After generating both files, ask the merchant where to save each. Suggest filenames alongside the input (e.g., `taxonomy-mapping.csv` and `taxonomy-report.md`).

Pipeline handoff note: "This CSV is ready to merge with your main feed. If you run the Audit a Google Merchant Feed skill next, upload your feed XML and this supplemental CSV together. The audit will cross-reference your taxonomy assignments and flag any apparel items that are now missing required attributes like color, size, gender, and age group."

### Turn 4+: Revise

Edit corrections in place. Do not regenerate the entire CSV for a single change. If the merchant provides additional products, classify them and append to the existing outputs.

---

## Output Structure

### Output 1: Supplemental Feed CSV

Columns:

| Column | Description |
|---|---|
| `id` | Product identifier (Handle for Shopify, ID column otherwise) |
| `title` | Product title as-is from input |
| `google_product_category` | Full Google taxonomy path string |
| `google_product_category_id` | Numeric taxonomy ID |
| `classification_confidence` | high, medium, or low |
| `classification_source` | script, llm, or merchant-override |

One row per product. No variant rows. Offer as a downloadable file.

### Output 2: Classification Report

```markdown
# Google Product Taxonomy Classification Report

**Source file:** [filename]
**Products classified:** N
**High confidence (script):** N
**Medium confidence (script, confirmed):** N
**Low confidence (LLM-classified):** N
**Merchant overrides:** N

---

## Full Mapping Table

| Product | Category Path | Category ID | Confidence | Source |
|---|---|---|---|---|

---

## Merchant Overrides

| Product | Script Proposed | Merchant Chose | Reason |
|---|---|---|---|

---

## Unresolved Items

[Products that could not be classified, with explanation. Leave section out if none.]
```

---

## Edge Cases

| Scenario | Handling |
|---|---|
| CSV has no description column | Classify from title only. Note in report that accuracy may be lower. Do not fail. |
| Product is a bundle or kit | Classify by the primary product in the bundle. Note it is a bundle in the report. |
| Digital or downloadable product | Classify into Google's Software or Digital Goods subtrees. Not into physical goods categories. |
| Very broad product title (e.g., "Accessories") | Flag as low confidence. Ask the merchant for more context before assigning a category. |
| Non-English product titles | Script keyword matching will be less effective. LLM handles classification. Note in report that keyword matching was limited. |
| Large catalog (500+ products) | Script handles all rows. For medium and low confidence items, group by detected category pattern and present by pattern rather than product-by-product to avoid overwhelming the merchant. |
| Merchant provides an existing partial `google_product_category` column | Preserve existing values where the path is 3 or more levels deep. Only classify where the column is empty, absent, or contains only a top-level path (1 to 2 levels). Note what was preserved vs. newly classified. |

---

## Error Handling

| Error | Action |
|---|---|
| Script exits with code 1 | Report the error message verbatim. Fall back to LLM-only classification. Note in report that script was unavailable. |
| No title column found after auto-detection | List the columns found in the file. Ask the merchant to specify which column contains product titles using `--title-col`. Do not proceed without a title column. |
| Malformed CSV (encoding or delimiter issues) | Report the issue. Suggest re-exporting from Shopify Admin using UTF-8 encoding and comma delimiters. |
| Merchant provides Google Merchant Center XML | Parse `<g:title>` and `<g:description>` from feed items. Proceed with classification. Note the XML input format in the report header. |
| `taxonomy-keywords.json` not found in assets dir | Report the missing file. Fall back to LLM-only classification. Note in report. |
| All products return low confidence | Likely a niche catalog or non-English titles. Fall back entirely to LLM classification. Note in report that keyword matching had no hits. |

---

## Gotchas

1. **LLM invents category paths.** Every category string must be a real Google Product Taxonomy path. If uncertain, state the nearest confirmed parent and flag for merchant review. Never fabricate a path.
2. **Over-generalization.** Assigning "Apparel & Accessories" instead of "Apparel & Accessories > Clothing > Outerwear > Coats & Jackets" wastes the taxonomy depth Google rewards. Always go to the most specific applicable leaf node.
3. **Keyword collision in the script.** Some words appear across multiple categories (e.g., "boot" matches Footwear and Automotive). The script surfaces alternatives. Use product description and catalog context to resolve before presenting to the merchant.

---

## Closing

Once the merchant approves the taxonomy mapping, note that the supplemental CSV is ready to merge with their main feed before submitting to Google Merchant Center. Include these reminders:

- Google accepts both the full path string and the numeric ID in the `google_product_category` field. The supplemental CSV includes both.
- Correct category assignment for apparel triggers Google's requirement for `color`, `size`, `gender`, and `age_group` attributes. If those are missing from the feed, the Audit a Google Merchant Feed skill will surface them as disapproved items.
- Run this skill again after adding new product lines or importing supplier catalogs to catch any products that slip through without a category assignment.

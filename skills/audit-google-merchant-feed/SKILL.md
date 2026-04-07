---
name: audit-google-merchant-feed
description: >-
  Validates a Google Merchant Center feed against Shopify product data and
  produces a prioritized error report with Shopify-native fix instructions.
license: Apache-2.0
metadata:
  category: feeds-and-merchandising
  level: intermediate
  platforms: shopify
  primitive: "false"
---

# Audit a Google Merchant Feed

This skill takes a Google Merchant Center XML feed and, optionally, a Shopify product export CSV. It runs a Python validation script that checks the feed against Google's product data specification, detects data quality issues, and (when the CSV is provided) cross-references the feed against the Shopify source of truth. The output is a prioritized error report with fix instructions that reference Shopify Admin and Bulk Editor by name.

Every rule, severity classification, and fix instruction is grounded in the audit rules reference at [references/shopify-merchant-audit-rules.md](references/shopify-merchant-audit-rules.md). The field mapping between Shopify CSV columns and Google Merchant attributes is documented at [references/shopify-merchant-field-map.md](references/shopify-merchant-field-map.md).

For reference on the expected output, see [references/example-output.md](references/example-output.md).

## Conversation Flow

### Turn 1: Welcome and Collect

Tell the user:

"Share your Google Merchant Center feed and I'll produce a prioritized audit with Shopify-specific fix instructions. Here's what I need:

**Required:**
- Google Merchant Center XML feed file

**How to get your feed file:** If you use the Shopify Google & YouTube channel (or any feed app that submits directly), you may not have a local XML file. To download it: go to Google Merchant Center > Products > Feeds > click your primary feed > click the three-dot menu > Download file. Save the XML and upload it here.

**Strongly recommended:**
- Shopify product export CSV. To export: go to Shopify Admin > Products > click Export > select 'All products' and 'Plain CSV file' > Export. This unlocks cross-reference checks: sale price mapping, GTIN sync, price mismatches, and coverage gaps between your store and your feed.

Without the Shopify CSV, I'll still catch feed-level issues (missing attributes, duplicates, malformed HTML, category depth, inconsistent variants), but I won't be able to compare the feed against your store data."

Accept whatever the user provides. If they share only the XML feed, proceed with feed-only validation and note in the Confidence Notes section what cross-reference checks were skipped.

### Turn 2: Run Validation and Produce the Audit

Run the validation script against the provided files:

```
python references/validate_merchant_feed.py feed.xml [shopify.csv] --pretty
```

Read the JSON output. Read [references/shopify-merchant-audit-rules.md](references/shopify-merchant-audit-rules.md) and [references/shopify-merchant-field-map.md](references/shopify-merchant-field-map.md) before writing the report.

Produce the full audit as a downloadable Markdown file using the output structure below. The report must:

1. **Lead with the summary.** Total items, items with issues, breakdown by severity tier.
2. **Group by severity, not by rule.** Disapproved first, then demoted, then advisory.
3. **Aggregate same-rule findings.** If 35 items are missing `g:gender`, do not list all 35 individually. Report the rule once, state the count, and list 3 to 5 representative item titles or IDs. Provide the full affected item list only if the user asks for it.
4. **Explain every fix in Shopify terms.** Reference the Shopify Admin path, Bulk Editor workflow, or feed tool configuration. Never tell the user to "update the feed XML directly" because Shopify merchants regenerate feeds from their store data.
5. **Separate feed-generation issues from data issues.** Some problems (missing sale_price, missing additional images) are caused by the feed tool, not by the Shopify product data. Make this distinction clear so the user knows whether to fix the data in Shopify or reconfigure their feed app.

After sharing the audit: "Review the report and let me know if you want to dig deeper on any section, see the full list of affected items for a specific rule, or get step-by-step fix instructions for a particular issue."

### Turn 3+: Explain and Prioritize

When the user asks about a specific issue:

- Provide the full list of affected items if requested.
- Give step-by-step Shopify Admin instructions for the fix.
- For feed-generation issues, explain what the feed tool needs to do differently and suggest specific settings if the user names their feed app (Shopify Google Channel, DataFeedWatch, Feedonomics, GoDataFeed, etc.).
- If the user asks "what should I fix first," prioritize disapproved items (they're not showing in Shopping at all), then demoted items with the highest item count, then advisory items.

## Output Structure

```
## Feed Audit Summary

| Metric | Value |
|---|---|
| Total items in feed | [count] |
| Items with issues | [count] |
| Disapproved (will not serve) | [issue count] across [item count] items |
| Demoted (reduced visibility) | [issue count] across [item count] items |
| Advisory (optimization opportunity) | [issue count] across [item count] items |
| Shopify CSV provided | Yes / No |
| Cross-reference checks | Enabled / Skipped |

## Disapproved Issues

Issues that prevent items from appearing in Google Shopping. Fix these first.

### [Rule ID]: [Rule title]

**Affected items:** [count] items
**Representative items:** [3-5 item titles or IDs]

**What's wrong:** [Plain-language explanation of the issue]

**How to fix in Shopify:**
[Step-by-step instructions referencing Shopify Admin paths]

### [Next disapproved rule...]

## Demoted Issues

Issues that reduce visibility or click-through rate. Fix these after
resolving all disapproved issues.

### [Rule ID]: [Rule title]

**Affected items:** [count] items
**Representative items:** [3-5 item titles or IDs]

**What's wrong:** [Plain-language explanation]

**How to fix in Shopify:**
[Step-by-step instructions]

### [Next demoted rule...]

## Advisory

Optimizations that improve feed performance. Not required but recommended.

### [Rule ID]: [Optimization title]

**Affected items:** [count] items

**What you're missing:** [Plain-language explanation of the opportunity]

**How to add in Shopify:**
[Instructions, noting whether this is a data fix or a feed tool fix]

### [Next advisory rule...]

## Priority Fix Order

[Numbered list of the top 5-7 actions, ranked by impact. For each:
rule ID, one-sentence action, item count affected, and whether it's
a Shopify data fix or a feed tool fix.]

## Confidence Notes

[What the audit could not check. Common entries: Shopify CSV not provided
(cross-reference skipped), feed may be stale, landing page price
verification not possible from feed data alone, no visibility into
Merchant Center account-level settings.]
```

## Edge Cases

### Only XML feed provided (no Shopify CSV)

Run feed-only validation. The audit covers all D-rules, W-rules, and feed-level A-rules. In Confidence Notes, list the cross-reference checks that were skipped (A01 sale price, A03 GTIN sync, X01 price match, X02 title match, X03 missing from feed, X04 orphaned items) and explain what the user gains by also providing the CSV.

### Very small feed (fewer than 10 items)

Produce the audit without aggregation. List every affected item by title since the list is short enough to be actionable.

### Very large feed (1,000+ items)

Aggregate aggressively. Show counts and percentages rather than item lists. For disapproved items, still list representative examples (5 to 10) so the user can verify the pattern. Suggest the user export the full JSON output from the script for spreadsheet analysis.

### Feed has no issues

Do not manufacture problems. If the feed passes all checks, say so clearly and suggest the advisory optimizations as the only action items. A clean feed with 3 advisory notes is more useful than a padded report.

### Non-Shopify feed

The validation script works on any Google Merchant Center XML feed, but the fix instructions reference Shopify Admin. If the user mentions they're on WooCommerce, BigCommerce, or another platform, still run the validation but note in the opening paragraph that fix instructions are Shopify-specific and the user should adapt the admin paths to their platform.

### Feed with non-English product data

The keyword stuffing and promotional text checks are English-language patterns. Note in Confidence Notes that these checks may produce false positives or miss issues in non-English feeds. All structural checks (missing attributes, duplicates, category depth, HTML validation) work regardless of language.

### Stale feed

If the cross-reference reveals many X01 (price mismatch) or X04 (orphaned items) issues, the feed is likely stale. Note this prominently at the top of the report and recommend the user regenerate the feed before acting on other issues, since many findings may resolve after regeneration.

## Gotchas

### The LLM will list every affected item individually

When 120 items trigger the same advisory rule (e.g., A02 no additional images), resist the urge to list all 120. State the count, show 3 to 5 examples, and offer the full list on request. The user needs to understand the pattern, not read a 120-line table.

### Brand-not-in-title may not need fixing

W01 (brand not in title) fires on every item when the merchant intentionally omits the brand from product titles. Many Shopify merchants do this because Google often auto-prepends the business name. When presenting W01, note this context and let the user decide whether to add brand to titles. Do not present it as a high-priority fix unless the merchant specifically wants branded titles.

### Feed-generation issues get misattributed to Shopify data

A01 (missing sale_price) and A02 (missing additional images) are almost always feed-generation tool issues, not Shopify data issues. The images and Compare At prices exist in Shopify but the feed tool isn't mapping them. Make this distinction explicit. Telling a merchant to "add more images in Shopify" when the images are already there but the feed tool isn't exporting them wastes their time and erodes trust.

### Apparel category boundaries are fuzzy

The script classifies items as apparel based on whether `g:google_product_category` starts with "Apparel & Accessories." Some items in this category (carabiner keychains, water bottle accessories) are technically under Clothing Accessories but are not apparel in a practical sense. When presenting D02 for non-clothing items in apparel subcategories, note that the merchant may want to recategorize these items to a non-apparel category rather than adding gender/age_group attributes.

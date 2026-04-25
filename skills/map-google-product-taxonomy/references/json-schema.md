# classify_taxonomy.py — Output JSON Schema

This document defines the structure of the JSON object written to stdout by
`scripts/classify_taxonomy.py`. The LLM reads this output in Turn 1 of the
conversation and uses it to present the classification report to the merchant.

**Script version:** 0.3.0  
**Encoding:** UTF-8, no BOM

---

## Top-Level Structure

```json
{
  "meta": { ... },
  "results": [ ... ]
}
```

| Field     | Type  | Description                         |
|-----------|-------|-------------------------------------|
| `meta`    | object | Run metadata (counts, columns, version) |
| `results` | array  | One object per classified product   |

---

## meta

```json
{
  "script_version": "0.3.0",
  "products_scanned": 30,
  "high_confidence": 21,
  "medium_confidence": 9,
  "low_confidence": 0,
  "preserved_existing": 0,
  "title_col": "Title",
  "desc_col": "Body (HTML)",
  "handle_col": "Handle",
  "encoding_used": "utf-8-sig",
  "encoding_warning": null
}
```

| Field                | Type           | Description |
|----------------------|----------------|-------------|
| `script_version`     | string         | Script semver at time of run |
| `products_scanned`   | integer        | Total rows in `results` array |
| `high_confidence`    | integer        | Count of results with `confidence: "high"` |
| `medium_confidence`  | integer        | Count of results with `confidence: "medium"` |
| `low_confidence`     | integer        | Count of results with `confidence: "low"` |
| `preserved_existing` | integer        | Count of results skipped due to `--preserve-existing` |
| `title_col`          | string         | Column name used for product titles |
| `desc_col`           | string or `"(not found)"` | Column name used for descriptions; `"(not found)"` if no description column detected |
| `handle_col`         | string or `"(not found)"` | Column name used for product IDs/handles |
| `encoding_used`      | string         | `"utf-8-sig"` or `"latin-1"` |
| `encoding_warning`   | string or null | Present when file was decoded as latin-1; null otherwise |

**Invariant:** `high_confidence + medium_confidence + low_confidence + preserved_existing == products_scanned`

---

## results — per-product object

```json
{
  "row": 2,
  "handle": "cascade-rain-shell-mens",
  "title": "Cascade Rain Shell - Men's",
  "proposed_category_path": "Apparel & Accessories > Clothing > Outerwear > Coats & Jackets",
  "proposed_category_id": 5598,
  "confidence": "high",
  "matched_keywords": ["rain jacket", "waterproof"],
  "alternatives": [
    { "path": "Apparel & Accessories > Clothing > Activewear", "id": 5322, "score": 2.1 }
  ],
  "policy_flags": ["apparel_requires_attributes"],
  "is_bundle": false
}
```

| Field                    | Type              | Description |
|--------------------------|-------------------|-------------|
| `row`                    | integer           | 1-based row number in the source CSV (row 1 is the header) |
| `handle`                 | string            | Product ID or Shopify handle from the detected handle column; empty string if none |
| `title`                  | string            | Raw product title from the source CSV |
| `proposed_category_path` | string or null    | Full Google taxonomy path string (e.g. `"Apparel & Accessories > Clothing > Outerwear > Coats & Jackets"`); null when confidence is `"low"` and no keyword signal was found |
| `proposed_category_id`   | integer or null   | Numeric Google taxonomy ID; null when the ID is unverified (see taxonomy-keywords.json notes) or confidence is `"low"` |
| `confidence`             | string (enum)     | See Confidence Values below |
| `matched_keywords`       | array of strings  | Keywords from taxonomy-keywords.json that matched; empty array for `"low"` or `"preserved"` |
| `alternatives`           | array of objects  | Up to 2 runner-up categories; each has `path` (string), `id` (integer or null), `score` (number) |
| `policy_flags`           | array of strings  | Zero or more policy flags (see Policy Flags below) |
| `is_bundle`              | boolean           | True when title or description contains bundle/kit/multipack signals |
| `bundle_note`            | string (optional) | Present only when `is_bundle: true`; instructs the LLM to classify by the primary item |

### Confidence Values

| Value         | Meaning |
|---------------|---------|
| `"high"`      | Score ≥ 6 AND gap to runner-up ≥ 3. Batch-approvable without merchant review. |
| `"medium"`    | Score ≥ 3 (gap condition not met). Competing candidates — present alternatives to merchant. |
| `"low"`       | Score < 3 or no keyword match. No script signal; LLM must classify from title/description semantics. |
| `"preserved"` | Existing `google_product_category` value in the input was 3+ levels deep and `--preserve-existing` was passed. Not re-classified; the existing path is echoed back in `proposed_category_path`. |

### Policy Flags

| Flag                          | Meaning |
|-------------------------------|---------|
| `"alcohol_regulated"`         | Title or description contains alcohol-related keywords. Google requires the Alcoholic Beverages subtree — the LLM must override any other proposed category. |
| `"apparel_requires_attributes"` | Proposed path is under `Apparel & Accessories`. Google Shopping requires `color`, `size`, `gender`, and `age_group` fields for these products. |
| `"software_digital"`          | Proposed path starts with `Software` or title/description indicates a digital download. Different licensing and subscription requirements apply. |

---

## Null Semantics

- `proposed_category_path: null` — no keyword match; classify from product semantics using LLM rules
- `proposed_category_id: null` — one of two cases:
  1. `confidence` is `"low"` and no path was found
  2. The taxonomy-keywords.json entry has `"id": null` (ID pending verification; the path string is correct and accepted by Google)
- `handle: ""` — source CSV had no detectable handle/ID column

---

## Downstream Use

The LLM in Turn 1 reads this JSON and:
1. Separates results into three confidence tiers for the merchant report
2. Applies LLM classification rules to all `"low"` confidence items
3. Acts on `policy_flags` (see SKILL.md § Policy Enforcement)
4. Notes `is_bundle: true` items for primary-item heuristic
5. Presents `alternatives` to the merchant for `"medium"` items in Turn 2

The final supplemental feed CSV (from Turn 3) uses `proposed_category_path` as the `google_product_category` value and `proposed_category_id` (if non-null) as `google_product_category_id`.

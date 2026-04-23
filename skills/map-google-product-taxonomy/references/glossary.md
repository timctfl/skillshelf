# Glossary: map-google-product-taxonomy Output

This glossary defines the fields in the supplemental feed CSV produced by this skill. Downstream skills (such as Audit a Google Merchant Feed) use this file to interpret the output and cross-reference taxonomy assignments against feed data.

---

## Output File: Supplemental Feed CSV

### `id`

**Type:** string
**Required:** yes

The product identifier used as a primary key. For Shopify product exports, this is the `Handle` column value. For other CSV formats, it is the first ID-like column detected (ID, SKU, Product ID). Always a stable, non-localized slug.

**When missing:** The script falls back to using the row number (e.g., `row_2`). Downstream skills should treat a `row_N` id as a signal that the source CSV lacked a stable identifier.

---

### `title`

**Type:** string
**Required:** yes

The product title as-is from the input CSV. No transformation is applied. Used by downstream skills to match rows across files.

---

### `google_product_category`

**Type:** string (full Google taxonomy path)
**Required:** yes

The full Google Product Taxonomy path string, using the official ` > ` separator between levels. Example:

```
Apparel & Accessories > Clothing > Outerwear > Coats & Jackets
```

Google accepts either the full path string or the numeric ID in this field. The path string is preferred because it is human-readable and survives taxonomy ID updates. Downstream skills should use the path string, not the ID, for display and validation.

**Path depth:** Leaf-level categories are 3 to 7 levels deep depending on the vertical. A path with fewer than 3 levels (e.g., `Apparel & Accessories`) indicates an unresolved top-level assignment and should be treated as incomplete.

---

### `google_product_category_id`

**Type:** integer
**Required:** no

The numeric taxonomy ID corresponding to the `google_product_category` path. Sourced from the Sept 2021 taxonomy release (see `assets/taxonomy-keywords.json`). IDs may change across taxonomy versions. Verify against the current official taxonomy before submitting to Google Merchant Center.

**When null or 0:** The category was assigned by LLM from the full taxonomy and an ID was not available in `taxonomy-keywords.json`. The path string is still valid. The downstream skill should surface the missing ID as an advisory note.

---

### `classification_confidence`

**Type:** enum: `high`, `medium`, `low`
**Required:** yes

How confident the skill is in the assigned category:

| Value | Meaning |
|---|---|
| `high` | Script keyword score above threshold with a clear gap to the runner-up. High accuracy. Batch-approvable. |
| `medium` | Script score above threshold but close to an alternative. Confirmed by the merchant or accepted as-is. |
| `low` | Script score below threshold or script unavailable. Category was assigned by LLM and reviewed by the merchant. |

Downstream skills should surface `low` confidence assignments as advisory items, not errors. They represent valid categories that required human or LLM judgment rather than deterministic matching.

---

### `classification_source`

**Type:** enum: `script`, `llm`, `merchant-override`
**Required:** yes

How the category was determined:

| Value | Meaning |
|---|---|
| `script` | Assigned by `classify_taxonomy.py` keyword matching. Merchant approved without change. |
| `llm` | Script confidence was low or script was unavailable. LLM assigned the category. Merchant reviewed and accepted. |
| `merchant-override` | Merchant explicitly changed the proposed category during Turn 2 review. |

Downstream skills should flag `merchant-override` rows as authoritative: the merchant has domain knowledge the script and LLM do not.

---

## Usage by Downstream Skills

The Audit a Google Merchant Feed skill uses this supplemental CSV in two ways:

1. **Cross-reference check (X-rule):** Compares the `google_product_category` in this file against the `g:google_product_category` in the merchant's feed XML. Discrepancies are flagged as a data-freshness advisory: the feed tool may not have picked up the new category assignments yet.

2. **Apparel attribute trigger:** For any row where `google_product_category` begins with `Apparel & Accessories`, the audit checks whether the feed includes `g:color`, `g:size`, `g:gender`, and `g:age_group` for those items. Missing attributes are flagged as disapproved (D02).

---

## Versioning

The supplemental CSV format is stable. New columns will only be added, never renamed or removed, to preserve compatibility with downstream skills that reference columns by name.

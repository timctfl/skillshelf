# Example Output: Fill Missing Product Attributes

This example uses the fictional brand **BayTide Co.**, an apparel store selling coastal-lifestyle clothing.

---

## Turn 1: Audit Report (After Stage 1 Script)

The merchant provides `baytide-products.csv`. The script runs and outputs:

```
## Missing Attribute Audit

**Products scanned:** 6 apparel / 7 total (1 non-apparel skipped: "Ceramic Coffee Mug")
**Variant rows scanned:** 18
**Deterministic fills made:** 11 (across 5 products)
**Fields needing LLM inference:** 4 rows across 2 products

### Deterministic Fills Made

| Handle | Variant SKU | Field | Value | Source | Confidence |
|---|---|---|---|---|---|
| mens-linen-shirt | BT-001-S | gender | male | title_gender_keyword ("Men's") | 0.92 |
| mens-linen-shirt | BT-001-S | material | Linen | title_material_vocab | 0.85 |
| mens-linen-shirt | BT-001-M | gender | male | sibling_propagation | 0.97 |
| mens-linen-shirt | BT-001-M | material | Linen | sibling_propagation | 0.97 |
| womens-swim-top | BT-002-XS | color | Coral | option_value (Option1 Name = "Color") | 1.0 |
| womens-swim-top | BT-002-XS | gender | female | title_gender_keyword ("Women's") | 0.92 |
| womens-swim-top | BT-002-S | color | Coral | sibling_propagation | 0.97 |
| womens-swim-top | BT-002-S | gender | female | sibling_propagation | 0.97 |
| kids-board-shorts | BT-003-6 | age_group | kids | title_age_keyword ("Kids'") | 0.92 |
| kids-board-shorts | BT-003-6 | gender | male | tag_prefix ("gender:boys") | 0.98 |
| kids-board-shorts | BT-003-8 | age_group | kids | sibling_propagation | 0.97 |

### Needs LLM Inference (Stage 2)

| Handle | Variant SKU | Title | Fields Missing | Context Available |
|---|---|---|---|---|
| sunset-wrap-dress | BT-004-XS | "Sunset Wrap Dress" | color, material | Color in title ("Sunset") is non-standard; no material signal |
| sunset-wrap-dress | BT-004-S | "Sunset Wrap Dress" | color, material | Same product, second size variant |

### Skipped (Non-Apparel)

- `ceramic-mug` (Type: "Kitchen & Dining") — apparel attributes not applicable

### Conflicts Detected (No Overwrite Applied)

None.
```

---

## Turn 2: LLM Inference + Proposed Fills

Claude reads `needs_inference.json` and produces the following `proposed_fills.json`:

```json
{
  "fills": [
    {
      "handle": "sunset-wrap-dress",
      "row_number": 14,
      "variant_sku": "BT-004-XS",
      "field": "color",
      "proposed_value": "Sunset",
      "confidence": 0.82,
      "evidence_quote": "Sunset Wrap Dress",
      "source": "llm_title_inference",
      "approved": true
    },
    {
      "handle": "sunset-wrap-dress",
      "row_number": 14,
      "variant_sku": "BT-004-XS",
      "field": "material",
      "proposed_value": null,
      "confidence": null,
      "evidence_quote": null,
      "source": "llm_insufficient_context",
      "approved": false
    },
    {
      "handle": "sunset-wrap-dress",
      "row_number": 15,
      "variant_sku": "BT-004-S",
      "field": "color",
      "proposed_value": "Sunset",
      "confidence": 0.82,
      "evidence_quote": "Sunset Wrap Dress",
      "source": "llm_title_inference",
      "approved": true
    },
    {
      "handle": "sunset-wrap-dress",
      "row_number": 15,
      "variant_sku": "BT-004-S",
      "field": "material",
      "proposed_value": null,
      "confidence": null,
      "evidence_quote": null,
      "source": "llm_insufficient_context",
      "approved": false
    }
  ]
}
```

Claude presents the review table:

```
## Proposed Fills (LLM Inference)

| Handle | SKU | Field | Proposed Value | Confidence | Evidence | Action |
|---|---|---|---|---|---|---|
| sunset-wrap-dress | BT-004-XS | color | Sunset | 0.82 | "Sunset Wrap Dress" | Review recommended |
| sunset-wrap-dress | BT-004-XS | material | — | — | Insufficient context | Flagged — needs your input |
| sunset-wrap-dress | BT-004-S | color | Sunset | 0.82 | "Sunset Wrap Dress" | Review recommended |
| sunset-wrap-dress | BT-004-S | material | — | — | Insufficient context | Flagged — needs your input |

Note: "Sunset" is not in the standard color vocabulary. It is preserved verbatim from the product title, which matches the PDP text per Google's feed matching requirement. If this product has a different display color on your PDP (e.g. "Orange" or "Gold"), please update before approving.

2 rows flagged for manual review: no material signal found in title, tags, or description for sunset-wrap-dress.
```

---

## Turn 3: User Approval

Merchant approves the proposed color fills. Material remains blank (goes to `needs_review.csv`). Claude updates `approved` state and runs Stage 3.

---

## Turn 4: Output

Validation checklist passed:
- Row count: 18 in, 18 out
- No Option Value columns modified
- No Variant Metafield columns written
- Change log entries: 13 (11 deterministic + 2 approved LLM fills)

### Corrected CSV Fragment (changed rows only)

```
Handle,Title,...,Google Shopping / Gender,Google Shopping / Age Group,...
mens-linen-shirt,Men's Linen Relaxed Shirt,...,male,,,...
mens-linen-shirt,,,...,male,,,...
womens-swim-top,Women's Rash Guard Top,...,female,,,...
womens-swim-top,,,...,female,,,...
kids-board-shorts,Kids' Board Shorts,...,male,kids,...
kids-board-shorts,,,...,male,kids,...
sunset-wrap-dress,Sunset Wrap Dress,...,female,,,...
sunset-wrap-dress,,,...,female,,,...
```

### change_log.csv

```
Timestamp,Handle,Variant SKU,Field,Target Column,Old Value,New Value,Source,Confidence,Evidence Quote,Needs Review
2026-04-18T14:00:00Z,mens-linen-shirt,BT-001-S,gender,Google Shopping / Gender,,male,title_gender_keyword,0.92,"Men's Linen Relaxed Shirt",FALSE
2026-04-18T14:00:00Z,mens-linen-shirt,BT-001-S,material,Google Shopping / Material,,Linen,title_material_vocab,0.85,"Men's Linen Relaxed Shirt",FALSE
2026-04-18T14:00:00Z,mens-linen-shirt,BT-001-M,gender,Google Shopping / Gender,,male,sibling_propagation,0.97,BT-001-S (sibling),FALSE
2026-04-18T14:00:00Z,mens-linen-shirt,BT-001-M,material,Google Shopping / Material,,Linen,sibling_propagation,0.97,BT-001-S (sibling),FALSE
2026-04-18T14:00:00Z,womens-swim-top,BT-002-XS,color,Google Shopping / Color,,Coral,option_value,1.0,Coral,FALSE
2026-04-18T14:00:00Z,womens-swim-top,BT-002-XS,gender,Google Shopping / Gender,,female,title_gender_keyword,0.92,"Women's Rash Guard Top",FALSE
2026-04-18T14:00:00Z,womens-swim-top,BT-002-S,color,Google Shopping / Color,,Coral,sibling_propagation,0.97,BT-002-XS (sibling),FALSE
2026-04-18T14:00:00Z,womens-swim-top,BT-002-S,gender,Google Shopping / Gender,,female,sibling_propagation,0.97,BT-002-XS (sibling),FALSE
2026-04-18T14:00:00Z,kids-board-shorts,BT-003-6,age_group,Google Shopping / Age Group,,kids,title_age_keyword,0.92,"Kids' Board Shorts",FALSE
2026-04-18T14:00:00Z,kids-board-shorts,BT-003-6,gender,Google Shopping / Gender,,male,tag_prefix,0.98,gender:boys,FALSE
2026-04-18T14:00:00Z,kids-board-shorts,BT-003-8,age_group,Google Shopping / Age Group,,kids,sibling_propagation,0.97,BT-003-6 (sibling),FALSE
2026-04-18T14:00:00Z,sunset-wrap-dress,BT-004-XS,color,Google Shopping / Color,,Sunset,llm_title_inference,0.82,"Sunset Wrap Dress",TRUE
2026-04-18T14:00:00Z,sunset-wrap-dress,BT-004-S,color,Google Shopping / Color,,Sunset,llm_title_inference,0.82,"Sunset Wrap Dress",TRUE
```

### needs_review.csv

```
Handle,Variant SKU,Field,Target Column,Reason,Evidence Quote,Confidence
sunset-wrap-dress,BT-004-XS,material,Google Shopping / Material,llm_returned_null,,
sunset-wrap-dress,BT-004-S,material,Google Shopping / Material,llm_returned_null,,
```

---

## needs_inference.json (excerpt)

This is the file the LLM reads in Stage 2:

```json
{
  "metadata": {
    "csv_file": "baytide-products.csv",
    "total_apparel_products": 6,
    "total_rows": 18,
    "deterministic_fills_made": 11,
    "rows_needing_inference": 4,
    "attribute_columns_detected": {
      "color": "Google Shopping / Color",
      "gender": "Google Shopping / Gender",
      "age_group": "Google Shopping / Age Group",
      "size": null,
      "material": "Google Shopping / Material"
    }
  },
  "rows": [
    {
      "handle": "sunset-wrap-dress",
      "row_number": 14,
      "variant_sku": "BT-004-XS",
      "title": "Sunset Wrap Dress",
      "product_type": "Women's Dresses",
      "tags": "dresses,wrap,new-arrival",
      "body_html_stripped": "A breezy wrap dress with an adjustable waist tie. Perfect for warm evenings.",
      "option1_name": "Size",
      "option1_value": "XS",
      "missing_fields": ["color", "material"],
      "context_notes": "Title contains 'Sunset' which is a non-standard color name. Product type suggests women's apparel. No material signal found in title, tags, or body."
    }
  ]
}
```

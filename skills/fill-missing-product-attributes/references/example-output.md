## Turn 1: Extraction Report

```
## Attribute Extraction Report

**Products scanned:** 6 apparel / 7 total (1 non-apparel skipped: "Ceramic Coffee Mug")
**Variant rows scanned:** 18
**Values extracted (deterministic):** 11 (across 5 products)
**Rows needing LLM inference:** 4 rows across 2 products

### Values Extracted (Deterministic)

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

- `ceramic-mug` (Type: "Kitchen & Dining"): apparel attributes not applicable

### Conflicts Detected (No Overwrite Applied)

None.
```

---

## Turn 2: LLM Inference + Proposed Fills

Claude holds inferences in memory and presents a review table. No intermediate file is written at this stage.

```
## Proposed Fills (LLM Inference)

| Handle | SKU | Field | Proposed Value | Confidence | Evidence | Action |
|---|---|---|---|---|---|---|
| sunset-wrap-dress | BT-004-XS | color | Sunset | 0.82 | "Sunset Wrap Dress" | Review recommended |
| sunset-wrap-dress | BT-004-XS | material | - | - | Insufficient context | Flagged: your input needed |
| sunset-wrap-dress | BT-004-S | color | Sunset | 0.82 | "Sunset Wrap Dress" | Review recommended |
| sunset-wrap-dress | BT-004-S | material | - | - | Insufficient context | Flagged: your input needed |

Note: "Sunset" is not in the standard color vocabulary. It is preserved verbatim from the product title, which matches the PDP text per Google's feed matching requirement. If this product has a different display color on your PDP (e.g. "Orange" or "Gold"), please update before approving.

2 rows flagged for manual review: no material signal found in title, tags, or description for sunset-wrap-dress.
```

---

## Turn 3: User Approval

Merchant approves the proposed color fills. Material remains blank and goes to `needs_review.csv`.

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

### change_log.md

```markdown
# Attribute Fill Change Log

Run timestamp: `2026-04-18T14:00:00Z`

**13 attributes filled** across **4 products**

| Symbol | Meaning |
|--------|---------|
| REVIEW | Needs human review before importing |
| OK | High confidence, safe to import |

---

## mens-linen-shirt

**Men's Linen Relaxed Shirt**

| Field | Value Set | Source | Confidence | Status |
|-------|-----------|--------|------------|--------|
| Google Shopping / Gender | male | Title gender keyword: `Men's Linen Relaxed Shirt` | 92% | OK |
| Google Shopping / Material | Linen | Title keyword match: `Men's Linen Relaxed Shirt` | 85% | OK |
| Google Shopping / Gender | male | Sibling variant propagation: `BT-001-S (sibling)` | 97% | OK |
| Google Shopping / Material | Linen | Sibling variant propagation: `BT-001-S (sibling)` | 97% | OK |

---

## womens-swim-top

**Women's Rash Guard Top**

| Field | Value Set | Source | Confidence | Status |
|-------|-----------|--------|------------|--------|
| Google Shopping / Color | Coral | Option value: `Coral` | 100% | OK |
| Google Shopping / Gender | female | Title gender keyword: `Women's Rash Guard Top` | 92% | OK |
| Google Shopping / Color | Coral | Sibling variant propagation: `BT-002-XS (sibling)` | 97% | OK |
| Google Shopping / Gender | female | Sibling variant propagation: `BT-002-XS (sibling)` | 97% | OK |

---

## kids-board-shorts

**Kids' Board Shorts**

| Field | Value Set | Source | Confidence | Status |
|-------|-----------|--------|------------|--------|
| Google Shopping / Age Group | kids | Title age keyword: `Kids' Board Shorts` | 92% | OK |
| Google Shopping / Gender | male | Tag prefix: `gender:boys` | 98% | OK |
| Google Shopping / Age Group | kids | Sibling variant propagation: `BT-003-6 (sibling)` | 97% | OK |

---

## sunset-wrap-dress

**Sunset Wrap Dress**

| Field | Value Set | Source | Confidence | Status |
|-------|-----------|--------|------------|--------|
| Google Shopping / Color | Sunset | LLM title inference: `Sunset Wrap Dress` | 82% | REVIEW |
| Google Shopping / Color | Sunset | LLM title inference: `Sunset Wrap Dress` | 82% | REVIEW |

---
```

### needs_review.csv

```
Handle,Variant SKU,Field,Target Column,Reason,Evidence Quote,Confidence
sunset-wrap-dress,BT-004-XS,material,Google Shopping / Material,llm_returned_null,,
sunset-wrap-dress,BT-004-S,material,Google Shopping / Material,llm_returned_null,,
```


# Attribute Extraction: Trust Hierarchy and Confidence Scores

## Source Trust Table

The `detect_missing_attributes.py` script mines these sources in priority order. Higher-trust sources run first; if a value is found, lower-trust sources are skipped for that field.

| Source | Confidence | Notes |
|---|---|---|
| Option value exact match | 1.0 | Option1/2/3 Name is in the color or size option name set |
| Existing Google Shopping column value | 1.0 | Already in the correct column, used for conflict detection |
| Structured tag match | 0.98 | Tag like `color:navy`, `gender:womens`, `fabric:cotton` |
| Sibling variant propagation | 0.97 | Same handle group; one variant has the value, siblings are empty |
| Title single gender keyword | 0.92 | Closed regex set from `assets/gender_patterns.json` |
| Title single age_group keyword | 0.92 | Closed regex set from `assets/age_group_patterns.json` |
| Title single standard color word | 0.90 | Token in `assets/standard_colors.txt` vocab |
| Title color bigram | 0.90 | Token pair in `assets/standard_color_bigrams.txt` (e.g. "Navy Blue") |
| Title material standard vocab | 0.85 | Token in `assets/standard_materials.txt` |
| Title material-implying synonym | 0.80 | Token in `assets/material_synonyms.json` keys (e.g. "merino" implies wool) |
| LLM inference | as-reported, capped at 0.90 | From `proposed_fills.json` confidence field |

## Confidence Threshold Policy

| Confidence | Action |
|---|---|
| >= 0.90 | Auto-write to output CSV. Log as "high confidence" in change_log.csv (`Needs Review` = FALSE). |
| 0.75 to 0.89 | Auto-write to output CSV. Log as "review recommended" in change_log.csv (`Needs Review` = TRUE). |
| 0.50 to 0.74 | Do NOT write. Add to `needs_review.csv` with reason `confidence_below_threshold`. |
| < 0.50 | Do NOT write. Do not surface unless merchant explicitly requests low-confidence items. |
| No fill found | Do NOT write. Send to LLM stage via `needs_inference.json`. |

## What Each Stage Handles

### Deterministic script (Stage 1) handles:

- Color, size, material from Option1/2/3 Name + Value columns
- Color, gender, age_group, material from structured tag prefixes
- Color, gender, age_group, material from sibling variant propagation
- Gender from title/product_type/tags using closed regex patterns
- Age_group from title/product_type/tags using closed regex patterns
- Color from title using single-token standard vocabulary
- Color from title using adjacent-token bigram vocabulary
- Material from title using standard material vocabulary
- Material from title using synonym mapping (merino, chambray, etc.)

### LLM (Stage 2) handles:

- Color in title with creative/non-vocab name (e.g. "Sunset Blush")
- Gender when title is genuinely ambiguous (multiple signals)
- Age_group when no signal exists and context is needed
- Material from Body (HTML) prose
- Multi-color parsing from descriptive prose
- Any case where the deterministic script returned no fill

### Merchant review handles:

- Conflicts between extracted value and existing column value (never auto-resolved)
- LLM fills below the 0.75 threshold
- Rows where LLM returned null
- Any fill where the target column is absent from the CSV header

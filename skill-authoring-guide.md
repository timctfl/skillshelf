# Skill Authoring Guide

How to write a SkillShelf skill. This document covers SkillShelf-specific conventions and quality standards. For the underlying SKILL.md file format (frontmatter fields, directory structure, validation rules), see [skillmd-specs.md](skillmd-specs.md).

---

## 1. Format compliance

Every skill must conform to the SKILL.md specification documented in `skillmd-specs.md`. Key requirements:

- Valid YAML frontmatter with `name` and `description`.
- `name` matches the parent directory name.
- `description` is written in third person ("Produces a positioning brief..." not "I help you write...").
- Body under 500 lines (guideline, not hard limit).
- Forward slashes in all file paths.
- File references one level deep from SKILL.md.

SkillShelf skills should also include these metadata fields in frontmatter:

```yaml
metadata:
  category: product-content       # one of the 10 SkillShelf categories
  level: beginner                 # beginner, intermediate, or advanced
  platforms: platform-agnostic    # or specific platforms (shopify, klaviyo, etc.)
  primitive: "true"               # only if this is a foundational primitive skill
```

Level definitions are in `project-scaffold.md` under "Skill levels." The short version: beginner means the user just talks and gets output; intermediate means they bring prepared input; advanced means they work outside the chat window.

---

## 2. Skill ecosystem awareness

SkillShelf skills do not exist in isolation. Before writing a skill, understand what it consumes and what consumes it.

### Primitives

Primitives are foundational skills that produce reusable reference documents. The current primitives are documented in `launch-skill-ideas/primitives_claude.md`. If a skill would benefit from a primitive's output (brand voice guide, positioning brief, customer persona, benefit map), note that in the skill's instructions — tell the user what to upload alongside their request and explain what improves when they do.

Do not make primitives a hard prerequisite. Every skill must produce useful output without them. But the output quality difference between "with primitive" and "without" should be real and obvious.

### Downstream consumption

If a skill produces a document that other skills reference, structure the output with consistent, descriptive headings. Downstream skills will point users at specific sections by name (e.g., "read the Key Differentiators section of the positioning brief"). Heading names should be stable — changing them breaks references in other skills.

### Cross-skill references

When a skill would benefit from another skill's output, reference it by its natural-language name, not its directory name. "If you have a brand voice guide from the Document Your Brand Voice skill, upload it alongside your request" — not "see `document-brand-voice`."

---

## 3. Input design

### Accept what users already have

Do not force users through a rigid Q&A when they might already have the information in an existing document. The default input pattern for skills that need business context should be:

1. Tell the user what kinds of existing content are useful (About Us pages, pitch decks, homepage copy, exported CSVs, etc.).
2. Offer guided prompts as a fallback for users who don't have existing content.
3. Identify gaps in whatever they provide and ask targeted follow-up questions — only for what's missing.

This reduces friction for users who have material and provides structure for users who don't.

### Use standard ecommerce data sources

When a skill accepts product or business data, design it to work with the exports users already have. Do not invent custom input formats when standard ones exist.

Common exports skills should expect and handle:

| Source | Format | Key fields |
|--------|--------|------------|
| Shopify product export | CSV | Title, Body (HTML), Vendor, Type, Tags, Variant Price, Variant SKU, Image Src |
| WooCommerce product export | CSV | Name, Description, Regular price, Categories, Tags, Images |
| Amazon listing report | TSV/CSV | item-name, product-description, bullet-point1–5, generic-keyword |
| Google Merchant Center | CSV/TSV | title, description, price, brand, google_product_category, custom_label_0–4 |
| Klaviyo campaign export | CSV | Campaign Name, Subject, Send Date, Recipients, Open Rate, Click Rate, Revenue |
| Yotpo/Stamped/Judge.me reviews | CSV | Product, Rating, Title, Body, Date, Reviewer |
| Google Analytics (GA4) | CSV | Various; usually includes sessions, conversions, revenue by channel/page |

When a skill accepts CSV input, be explicit about which columns it needs and handle common variations in column naming (e.g., "Body (HTML)" vs. "Description" vs. "product_description" for the same concept).

### Do not require perfect input

Users frequently have messy, incomplete, or inconsistent data. Skills should handle imperfect input gracefully — produce the best output possible from what's provided, note what's missing, and suggest what would improve the result. Never refuse to produce output because the input isn't ideal.

---

## 4. Output design

### Structured and labeled

Every skill output should use consistent Markdown headings that downstream skills and human readers can reference by name. If a positioning brief has a "Why they choose us" section, that heading should be stable and descriptive enough that another skill can say "reference the Why They Choose Us section."

### Ready to use

Output should be ready to paste into a CMS, upload to a platform, or hand to a team member. If the output requires further editing or reformatting before it's useful, the skill isn't done.

For CSV-producing skills, output should be importable into the target platform without manual column renaming or reformatting.

### Honest about confidence

When a skill works from limited input, the output should say so. Use a "Confidence notes" section to flag which parts of the output are based on limited evidence and what additional input would strengthen them. Do not pad thin input into confident-sounding output.

---

## 5. Calibration steps

Some skills should include a calibration step where the user chooses between 2-3 variations before the final output is produced. This is not a default for every skill — it is appropriate only when the same input legitimately supports multiple good outputs and the user's preference is the tiebreaker.

**When to calibrate:**
- The output involves interpretation of voice, tone, or personality (brand voice extraction, positioning framing, creative direction).
- The user's input is ambiguous on a dimension that significantly changes the output (e.g., their content could read as playful or minimal, and the choice changes everything downstream).

**When not to calibrate:**
- The output is primarily determined by the input (product descriptions from specs, CSV formatting, data normalization, audits, checklists).
- The skill already receives a calibrated artifact as input (e.g., a description skill that consumes a brand voice guide — the voice guide already encodes the user's preferences).
- The skill produces structured analysis where there is a right answer, not a preference (review analysis, performance summaries, taxonomy mapping).

**The calibration pattern (when used):**

1. Analyze the user's input silently.
2. Present 2-3 variations that represent plausible but meaningfully different interpretations.
3. Ask the user which resonates — or what they'd change.
4. Use their selection to anchor the final output.

Present variations neutrally (A, B, C) without labeling them with descriptors. Let the user react to the output itself, not to a category name.

---

## 6. Example output

### Include an example file

Every skill should include an `examples/` directory with a sample output file that demonstrates the full format and level of detail expected. The example serves as both a quality benchmark for the LLM and a preview for the user.

### Fictional brand naming

Use **generic, category-obvious brand names** in examples. The name should make the product category immediately clear. Slightly punny names are fine if they fit naturally.

Good: "GreatOutdoors Co." (outdoor gear), "GoodBoy Treats" (pet products), "BeanThere Coffee" (coffee)

Bad: "Ridgeline Supply Co.", "Duskbloom", "Apex Provisions" — these sound like real brands and don't signal the category instantly.

The goal is that anyone reading the example immediately understands it's a template, not a case study.

### Example quality

The example should be good enough to use as a reference in production. It demonstrates the ceiling, not the floor. If the example is mediocre, the LLM will calibrate to mediocre output.

---

## 7. Edge cases

Every skill should include an "Edge cases" section that addresses at minimum:

- **Thin input:** What happens when the user provides minimal information. The skill should produce output and note what would improve it — not refuse.
- **Inconsistent input:** What happens when the user's input contradicts itself. Document the variation rather than averaging into a bland middle ground.
- **Missing context:** What happens when a key dimension (competitors, target customer, etc.) isn't provided. Produce the brief without that section and note it in confidence notes.

Skills that accept CSV data should also address:
- Missing columns
- Inconsistent formatting within columns
- Very small datasets (< 10 rows) and very large datasets (1,000+ rows)

---

## 8. Writing quality standards

### Specificity over generality

Every claim, differentiator, or recommendation in skill output should be specific to the user's brand, product, or data. Generic statements that could apply to any brand in the category are not useful. "High-quality ingredients" is generic. "Single-origin cacao from Piura, Peru, fermented on-site for 6 days" is specific.

If the user's input is generic, reflect that honestly and suggest how to sharpen it — do not fabricate specificity.

### Plain language

Skill instructions and output should use clear, direct language. Avoid marketing jargon, buzzwords, and abstraction. The output is a working document, not a manifesto.

### Do not over-scope

A skill does one thing well. If a skill's scope creeps beyond its description, split it into two skills. A positioning brief skill should not also try to write product descriptions. A product description skill should not also audit the page for conversion best practices.

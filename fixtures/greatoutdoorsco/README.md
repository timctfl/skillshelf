# Great Outdoors Co. Fixtures

Great Outdoors Co. is a **fictional** direct-to-consumer outdoor lifestyle brand created solely for testing SkillShelf skills. Any resemblance to real brands, products, or SKUs is coincidental.

These fixtures provide standardized, synthetic inputs for testing AI workflows such as:

- Writing product descriptions from structured catalogs
- Analyzing and cleaning messy exports
- Extracting brand voice from product detail pages
- Generating marketing copy from consistent product references

## Files

| File | Description |
|------|-------------|
| `shopify-products.csv` | Shopify-style product export CSV with 30 products and variants. |
| `shopify-products.json` | Same catalog in Shopify REST Admin API JSON format. |
| `google-merchant-feed.xml` | Google Merchant Center XML feed (variant-level items). |
| `product-attributes.csv` | Flat attribute/value pairs per product handle. |
| `product-taxonomy.json` | Category tree with product counts. |
| `pdp-apparel.md` | Clean, well-written PDP — Cascade Rain Shell (Women's). |
| `pdp-gear.md` | Technical, spec-heavy PDP — Cedar Ridge 45L Trek Pack. |
| `pdp-minimal.md` | Sparse PDP with almost no detail — Ridgeline Hiking Socks. |
| `pdp-messy.md` | Messy/migrated PDP — HTML artifacts, duplicated paragraphs, keyword stuffing. |

## Intentional data quality issues

Several files contain deliberate messiness to test how skills handle real-world data. These are features, not bugs:

- **Mixed weight units** in `product-attributes.csv` — "11.6 oz" vs "10.9 ounces" vs "3.5 lb"
- **Inconsistent waterproof ratings** — "15000 mm" vs "15K mm" vs "2000 mm"
- **Duplicate casing in color options** — "Blue, blue, ORANGE" and "Black, BLUE, blue"
- **Empty/missing values** — blank warranty, dimensions, and packed_size fields across multiple products
- **Trailing whitespace** — scattered throughout attribute values
- **Duplicate paragraph** in `pdp-messy.md` — same block of copy pasted twice
- **HTML artifacts** in `pdp-messy.md` — raw `<p>`, `<br>`, `<font>` tags from a platform migration
- **Keyword stuffing** in `pdp-messy.md` — a block of SEO spam at the bottom
- **Inconsistent list formatting** in `pdp-messy.md` — mixed `-`, `*`, and bare lines

## Skill outputs

The `skill-outputs/` directory contains example outputs from SkillShelf skills run against this fixture data. These are useful as inputs to downstream skills -- for example, a product description skill can consume the brand voice profile and positioning brief to produce on-brand copy.

| File | Produced by | Description |
|------|-------------|-------------|
| `skill-outputs/brand-voice-profile.md` | Document Your Brand Voice | Structured voice guide extracted from the PDPs and product copy. |
| `skill-outputs/brand-voice-glossary.md` | Document Your Brand Voice | Glossary defining how downstream skills should interpret the voice profile. |
| `skill-outputs/positioning-brief.md` | Write a Positioning Brief | Positioning brief covering target customer, differentiators, competitive context. |

These files are copies of the example outputs in each skill's `references/` directory. If they drift apart, the skill `references/` copies are authoritative (they're what the site displays and what the LLM reads as quality benchmarks).

## Coming next

Additional fixture sets (marketing content, customer content, emails, reviews, ads, and social posts) will be generated in a future pass and will reference the same products by name and handle.

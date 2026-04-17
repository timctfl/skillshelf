---
name: map-pdp-structure
description: >-
  Analyzes a Shopify product detail page to produce a structured content template
  that maps each section to its Shopify data source.
license: Apache-2.0
---

# Map Your Shopify PDP Structure

Produce a content template that describes how one Shopify store structures its product detail pages: what sections the PDP has, where each section's content comes from in Shopify (a standard product field, a specific metafield, or something outside the product data like a theme block or app), and how `body_html` reassembles when content is written back.

Other skills will consume this template to generate new PDP content and write it back to Shopify. If the mapping is wrong — content sourced to a metafield that doesn't exist, theme content treated as editable product copy, body_html sub-sections conflated or split badly — every subsequent run corrupts this store. The mapping has to be right. Schema validity is enforced automatically; accuracy is the real work.

## What you are given

- **A screenshot of the rendered PDP.** Authoritative for visual grouping, accordion/tab state, and image-embedded content.
- **The same PDP as markdown.** Authoritative for what words appear where on the page.
- **The product's Shopify data as JSON.** Includes all standard fields and every metafield. `metafield_definitions` is the canonical list of metafields that exist on this product — only those `namespace.key` values are valid sources for any metafield-backed section.
- **An evidence table.** For every Shopify field value (title, SEO fields, each metafield, each body_html chunk), whether it appears verbatim on the rendered page. `match_confidence: none` means the stored value doesn't substring-match; it doesn't mean the field isn't the source (a JSON metafield rendered by the theme as a styled chart will miss verbatim matching even though it is the source).
- **Optional: up to two additional reference products** with the same artifacts. When present, the evidence table classifies metafields as `static_candidates` (identical across products) or `dynamic_candidates` (varying).
- **Optional: theme schemas.** When the store has granted theme access, you also get the PDP's `templates/product.json` and the referenced section schemas. When present, this is the authoritative source mapping — block declarations name their exact data source (e.g., `content_source: product.metafields.custom.ingredients`).

## What to produce

A JSON template via the `emit_pdp_content_template` tool. See `references/output-schema.yaml` for the enforced shape and `references/example-output.md` for a worked example.

Each section needs a name, snake_case key, source, classification (dynamic or static), format, and one-sentence `guidance` telling a content-generation skill what that section should contain and how it should read. Metafield sources need the exact `namespace.key` from `metafield_definitions` plus the metafield type. External sources need a specific `source_detail` — name what it actually is, not "theme content." Heading wrappers in `shopify_assembly.body_html` need the heading text.

Don't chat. Don't ask clarifying questions. Your output goes to a review screen where the merchant corrects individual mappings.

## Edge cases

- Reference URL is from a different store than the connected one: refuse with a clear error.
- `body_html` is empty: template uses standard fields and metafields only.
- No metafields on the product: template uses standard fields only.
- Screenshot unavailable: proceed with text only; flag sections depending on visual grouping so the review step catches what you couldn't see.

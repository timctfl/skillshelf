# Example Output: Map Your Shopify PDP Structure

This is a completed template for a fictional apparel store, GreatOutdoors Co. The reference product is an "Alpine Hybrid Jacket" on a Shopify store that uses metafields extensively for structured PDP content. The example illustrates the three source types (`shopify_standard`, `shopify_metafield`, `external`), both classifications (`dynamic`, `static`), and an assembly pattern that combines body_html with metafield-driven sections.

The output is JSON that validates against `references/output-schema.yaml`. Every required field is filled. Every section has a clear source. Every `source: external` section names what it actually is.

## Template

```json
{
  "type": "product-detail-page",
  "generated_from_product": "https://greatoutdoorsco.example/products/alpine-hybrid-jacket",
  "generated_at": "2026-04-16T19:45:00Z",
  "sections": [
    {
      "name": "Product Title",
      "key": "title",
      "source": "shopify_standard",
      "classification": "dynamic",
      "format": "plain_text",
      "length": { "min": 3, "max": 8, "unit": "words" },
      "guidance": "Brand plus product name. Add a short modifier if the line has multiple variants."
    },
    {
      "name": "Short Description",
      "key": "short_description",
      "source": "shopify_metafield",
      "shopify_metafield": "custom.short_description",
      "metafield_type": "single_line_text_field",
      "classification": "dynamic",
      "format": "plain_text",
      "length": { "min": 10, "max": 20, "unit": "words" },
      "guidance": "One-sentence benefit statement shown between the title and the hero image. Leads with the most distinctive technical benefit."
    },
    {
      "name": "Description",
      "key": "description",
      "source": "shopify_standard",
      "classification": "dynamic",
      "format": "html",
      "length": { "min": 60, "max": 120, "unit": "words" },
      "guidance": "Benefit-led narrative paragraph. Describes the fabric, construction, and use case without technical jargon."
    },
    {
      "name": "Key Features",
      "key": "key_features",
      "source": "shopify_metafield",
      "shopify_metafield": "custom.key_features",
      "metafield_type": "list.single_line_text_field",
      "classification": "dynamic",
      "format": "list",
      "guidance": "Four to six bullets. Each bullet names a feature and its benefit, eight words or fewer per bullet."
    },
    {
      "name": "Care Instructions",
      "key": "care_instructions",
      "source": "shopify_metafield",
      "shopify_metafield": "custom.care_instructions",
      "metafield_type": "multi_line_text_field",
      "classification": "static",
      "format": "plain_text",
      "guidance": "Standard care instructions for technical fabric. Consistent across every jacket in this line."
    },
    {
      "name": "Size Guide",
      "key": "size_guide",
      "source": "external",
      "source_detail": "Theme block pulling from a shared sizing metaobject. Not tied to this product's data.",
      "classification": "static",
      "format": "plain_text",
      "guidance": "Managed in your theme. SkillShelf does not update this."
    },
    {
      "name": "SEO Title",
      "key": "seo_title",
      "source": "shopify_standard",
      "classification": "dynamic",
      "format": "plain_text",
      "length": { "max": 60, "unit": "characters" },
      "guidance": "Under 60 characters. Include brand name and primary search term."
    },
    {
      "name": "SEO Description",
      "key": "seo_description",
      "source": "shopify_standard",
      "classification": "dynamic",
      "format": "plain_text",
      "length": { "max": 155, "unit": "characters" },
      "guidance": "Action-oriented. Include the primary keyword and top benefit."
    },
    {
      "name": "Reviews",
      "key": "reviews",
      "source": "external",
      "source_detail": "Yotpo reviews widget. Review content is managed in the Yotpo app.",
      "classification": "static",
      "format": "plain_text",
      "guidance": "Managed outside Shopify product data. SkillShelf does not update this."
    },
    {
      "name": "Pair With",
      "key": "pair_with",
      "source": "external",
      "source_detail": "Theme cross-sell block using product tag matching.",
      "classification": "static",
      "format": "plain_text",
      "guidance": "Managed in your theme. SkillShelf does not update this."
    }
  ],
  "shopify_assembly": {
    "body_html": [
      { "key": "description", "wrapper": "none" },
      { "key": "care_instructions", "wrapper": "h3_heading", "heading": "Care" }
    ]
  }
}
```

## Why each section was classified this way

**`title` to `shopify_standard`.** The evidence table showed `title` matched exact on the page with a high-confidence position. No metafield overrode it.

**`short_description` to `shopify_metafield`.** One of the store's metafields (`custom.short_description`) contained the short blurb text displayed above the description. No standard field had a direct match. The evidence row was `exact`.

**`description` to `shopify_standard`.** `body_html` chunk matched the rendered paragraph. No metafield matched more specifically, so the body_html chunk is the authoritative source.

**`key_features` to `shopify_metafield`.** The bullets on the page matched the items in `custom.key_features` (list.single_line_text_field) one-for-one.

**`care_instructions` to `shopify_metafield`, `static`.** The multi-line text appeared verbatim inside a "Care" accordion. The same text appeared on the second and third reference products, so `static_candidates` flagged it. Classification is `static`.

**`size_guide` to `external`.** No metafield matched the size-chart content. The theme renders size guides from a shared metaobject reference, not per-product data. Source detail names the theme block.

**`seo_title` and `seo_description` to `shopify_standard`.** Matched the `seo.*` fields directly from the product JSON.

**`reviews` and `pair_with` to `external`.** App-driven sections, not tied to product fields. Source detail names the specific app and the theme pattern.

## Notes on edge cases this example surfaces

- **Borderline classification.** `care_instructions` matched a metafield (so it is not `external`), but the same value appeared across multiple reference products (so it behaves as `static`). Using `static` protects downstream skills from regenerating identical language for every product. The review UI surfaces this so the user can override if they want.
- **Small `shopify_assembly.body_html`.** Most sections are metafield-driven, so the assembly array is short. On write-back, the platform writes metafield content to each metafield directly and rebuilds `body_html` with only the description paragraph followed by a "Care" heading and the care instructions.
- **External sections have specific `source_detail` strings.** "Yotpo reviews widget" is more useful than "reviews app." The review UI shows this to the user and makes future decisions easier (e.g., if the store switches from Yotpo to Okendo, the section can be updated without re-running the skill).

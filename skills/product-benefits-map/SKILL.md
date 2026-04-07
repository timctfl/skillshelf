---
name: product-benefits-map
description: >-
  Produces a product reference document with enough specific information
  about each product or product line for a writer or downstream skill
  to produce good copy. Accepts a product catalog export and optional
  supporting material like homepage copy or brand docs. Output is consumed
  by downstream skills for writing product descriptions, emails, social
  copy, and landing pages.
license: Apache-2.0
---

# Map Your Product Benefits

This skill produces a benefits map: a reference document that gives a future writer or AI skill enough specific information about your products to write good copy without making things up or being generic. The map is organized at whatever level makes sense for your catalog, whether that's individual products, product lines, or categories.

The output is designed to be loaded into future conversations as a foundation document. When a downstream skill needs to write a product description, draft an email, or create social copy, the benefits map gives it specific, accurate material to work with instead of generic filler.

This is distinct from a positioning brief. A positioning brief captures brand-level strategy: who the customer is, what differentiates the brand, and competitive context. The benefits map is product-specific. It captures what individual products and product lines actually do, what features and materials back that up, and how those translate into customer value. A positioning brief tells you who you're talking to and why they should care about the brand. A benefits map tells you what to say about the products.

For reference on the expected output, see [references/example-output.md](references/example-output.md).

---

## Voice and Approach

You are helping the user build a structured reference document about their products. Be direct and practical. The user likely knows their products well but hasn't organized their benefit language in a structured way before. Your job is to extract, organize, and sharpen what's already there, not to invent marketing claims.

When you surface benefits from the product data, ground every statement in something specific from the input. If you can't tie a benefit to a real feature, material, spec, or customer outcome, don't include it. Specificity is the entire point of this document.

---

## Conversation Flow

### Turn 1: Collect Inputs

Ask the user to share their product catalog. A Shopify product export CSV is ideal because it includes the Body (HTML) field, which contains product description content. Other platform exports (BigCommerce, WooCommerce, custom) also work.

Encourage the user to share any other material that would help you understand their products. Homepage copy, key PDP pages, an About page, a brand deck, a product launch brief, marketing one-pagers, competitor pages, internal docs about a product line, or just a note about where to focus. The more context you have, the more specific the output will be. Don't limit the ask to homepage and feed.

When the user uploads a CSV, run a structural scan before reading the full file. Use bash to extract a lightweight overview: total row count, distinct product types with counts, and average description length per type. This tells you the catalog scope and input richness without consuming context window on hundreds of product descriptions.

For small catalogs (roughly 50 products or fewer), you can read the full CSV directly. For larger catalogs, do not try to read the entire file into context. Use the structural scan for the Turn 2 assessment and wait until the user confirms scope before reading description content.

If the user only provides a product export and the structural scan shows thin descriptions (short or empty Body HTML, specs-only, or generic copy), tell them what you're seeing and ask if they can share additional material. Be specific about what kinds of material would help based on what's missing. Nudge once, then work with what you have if the user doesn't provide more.

### Turn 2: Assess the Catalog and Propose an Approach

After receiving the input, do three things before producing any output:

**1. Assess catalog scope.** Using the structural scan, count the distinct products. Look at how they're distributed across product types, categories, or collections. Determine whether the catalog is small enough to map at the individual product level or whether it needs consolidation into product lines or categories.

**2. Assess input richness.** Look across the structural scan and everything else the user provided. The scan tells you which product types have rich descriptions and which are thin. Homepage copy, supporting documents, or user direction may fill gaps. Note what you have to work with and where the gaps are.

**3. Propose the grouping and approach.** Based on catalog size, product distribution, and description richness, propose how you'll organize the map. Explain your reasoning briefly so the user can adjust.

The right level of granularity depends on the brand and catalog:

- A 15-product skincare brand with a clear ingredient story might be best served by individual product entries, because every SKU is distinct and matters.
- A footwear brand with well-defined product lines (trail, road, lifestyle) might organize by line, with positioning relative to sibling lines and hero product callouts within each.
- A brand with deep categories (40 leggings across 6 fabric technologies) might organize at the category level, with technology and use-case differentiators rather than per-product entries.
- A smaller catalog can often be mapped comprehensively at the individual product level. As the catalog grows, some consolidation is needed to keep the output useful as a reference document rather than an exhaustive inventory.

Do not impose a rigid structure. Assess the catalog and propose the approach that will produce the most useful reference document for this specific brand. Present your recommendation to the user and ask them to confirm, adjust, or redirect before producing the full map.

If the user provided homepage copy, note what benefit themes and product lines the brand emphasizes on the homepage. This helps frame the approach and gives the user confidence you understood their priorities.

**After the user confirms scope:** For larger catalogs, use bash to filter the CSV to the confirmed product types or lines and read the Body HTML for that subset only. This gives you the full description content for the products that matter without trying to hold the entire catalog in context.

### Turn 3: Produce the Benefits Map

Generate the full benefits map as a downloadable document. Follow the synthesis instructions and output guidance below.

After sharing: "Review this and let me know what needs adjusting. I can restructure sections, add specificity where you have more detail to share, or shift emphasis."

### Turn 4+: Review and Refine

Edit sections in place when the user requests changes. Do not regenerate the entire document for a single correction.

Common refinements:
- Adding details the user knows but weren't in the data
- Splitting a grouped section into more specific subsections
- Adjusting which products get individual callouts
- Adding tradeoffs or limitations the data didn't surface
- Correcting the framing of a product line based on user knowledge

---

## Synthesis Instructions

### What the output needs to accomplish

The goal is a reference document that gives a future skill or writer enough specific, grounded information to write good copy about any product or product line in the catalog. The right information depends on the product and category. For some products that means materials and construction. For others it means use cases and tradeoffs. For others it means how the product relates to the rest of the lineup. The skill should figure out what matters for this brand and these products.

The format of each section should follow from the product and category, not from a rigid template. A fabric-driven apparel brand might organize by fabric technology and use case. A skincare brand might organize by product and lead with hero ingredients. A gear brand might lead with specs and construction. Let the catalog tell you what matters.

The hard requirement is specificity. Every statement needs to be grounded in something real from the input: a material, a spec, a design detail, a price point, a customer signal. "Comfortable and high quality" is useless. "Nulu fabric, buttery soft, prone to pilling with friction, not built for high-intensity work" is useful. If you can't tie a claim to something specific, don't include it.

Include tradeoffs and limitations where they exist. A benefits map that only lists positives is less useful than one that tells you what each product is not good at, because a writer needs to know what claims to avoid as much as what claims to make.

When a category has many similar products differentiated by a few key factors (fabric, pocket configuration, compression level, price), call out those differentiators explicitly. A downstream skill writing about one product in the lineup needs to understand what makes it different from its siblings.

### Working with the available input

Each input source contributes different things. Product descriptions (Body HTML or equivalent) often contain feature details, material callouts, and benefit-oriented copy at the product level. Homepage copy tends to surface brand-level positioning, emotional language, and which product lines the brand leads with. Supporting documents and user direction may add context that isn't captured anywhere on the site. Product titles, tags, and structured fields provide supplemental signals like naming patterns, price positioning, and collection membership.

The richness and usefulness of each source varies by brand. Some brands have detailed product descriptions and a sparse homepage. Others have a compelling homepage and thin product data. Assess what the user provided, determine where the strongest benefit language lives, and weight your extraction accordingly. If the user explicitly states priorities or direction, treat that as directional regardless of what the other sources suggest.

### What to do with thin input

If the combined input doesn't contain enough specific information to produce grounded statements, the skill still produces output. Work with whatever is available. Flag sections that are based on limited source material using confidence notes. Suggest what additional input would strengthen those sections.

Never pad thin input into confident-sounding output. If you don't have enough to say something specific, say what you do know and note what's missing.

---

## Output Guidance

The output structure should follow from the catalog, not be imposed on it. The skill's job is to produce the most useful reference document for this specific brand, and the shape of that document depends on what the brand looks like.

The primary downstream use is as a reference document loaded into future conversations. When a skill needs to write product descriptions, email copy, social captions, landing page content, or promotional materials, the benefits map gives it specific, grounded material about the products rather than forcing it to generate from scratch or work from generic claims.

Organize the map at whatever level makes sense for the catalog: by category, by product line, by individual product, or a mix. Each section should give a reader enough context to write about that product or line without needing to look anything up.

If there are cross-cutting product patterns across a category that a writer should know about (like a fabric technology system that defines the lineup, a shared construction approach, or a common material), call those out where relevant. These should be product-specific details that apply across multiple items, not brand positioning.

End with a confidence notes section flagging any parts of the map based on limited input. Be specific about what's thin and what would improve it.

Include `<!-- product-benefits-map v0.1 -->` at the top of the document so downstream skills can identify the producing skill and version.

---

## Edge Cases

### Product descriptions are empty or minimal across the catalog

Lean on whatever other sources are available: homepage copy, user guidance, product titles, tags, and structured attributes. Make the confidence notes section prominent and specific about what's missing. Suggest the user return with richer input (PDP copy, marketing materials, brand decks) to fill the gaps.

### Catalog is very large

The structural scan in Turn 1 handles this. For catalogs with hundreds of products, the scan gives you the scope and distribution without reading every description. Propose a focused scope in Turn 2: the top 3-5 product lines or categories by product count, revenue emphasis (if signaled by the user or their materials), or strategic priority. After confirmation, filter the CSV and read descriptions only for the confirmed subset. Make it clear to the user that focused depth is more valuable than broad but shallow coverage, and that they can run the skill again for additional product lines.

### Catalog has very few products

Map every product individually. For very small catalogs, the map is essentially a structured teardown of each product's benefit story.

### No supporting material was provided

Produce the map from the product export alone. Note in the confidence section which areas are thin and what additional material would strengthen them.

### Products don't group cleanly

Some catalogs have inconsistent product types, missing categories, or products that don't fit neatly into groups. Propose the best grouping you can and flag the outliers. Don't force products into groups where they don't belong. An "Other / Uncategorized" section is fine when it's honest.

### User provides a brand voice profile or positioning brief

If the user uploads a brand voice profile, positioning brief, or brand guidelines document alongside the product data, use it. The brand voice profile informs the tone of benefit statements. The positioning brief informs which benefits to emphasize and how to frame competitive differentiation. These are optional inputs that improve the output but are not required.


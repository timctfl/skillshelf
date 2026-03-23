---
name: audit-pdp
description: >-
  Audit a PDP from screenshots and a brand voice guide. Produces a prioritized
  report split into content/merchandising and dev/design changes.
license: Apache-2.0
---

# Audit a Product Detail Page

This skill takes screenshots of a product detail page (desktop and mobile), a brand voice guide, and optionally a GA4 performance screenshot, and produces a prioritized optimization report. The report is split into two buckets: changes the ecommerce team can make through their CMS and merchandising tools, and changes that need dev or design involvement.

Every recommendation is grounded in the best practices rubric in [references/pdp-best-practices.md](references/pdp-best-practices.md). When a recommendation maps to a specific finding, cite it inline so the reader can trace the reasoning.

For reference on the expected output, see [references/example-output.md](references/example-output.md).

## Conversation Flow

### Turn 1: Welcome and Collect

Tell the user:

"Share your PDP screenshots and I'll produce an optimization audit. Here's what I need:

**Required:**
- Desktop PDP screenshot (feel free to include a few screenshots if you need to cover the main parts of the page)
- Mobile PDP screenshot (same idea -- a few screenshots to cover the full page is fine)
- Brand voice guide or positioning brief

**Strongly recommended:**
- GA4 screenshot for this PDP. To pull it: go to Reports > Engagement > Pages and Screens in GA4, filter to the PDP URL, set the date range to last 30 days, add "Device category" as a secondary dimension (click the + next to the primary dimension), and screenshot. This takes about a minute and gives the audit a performance backbone with the mobile/desktop split.

The metrics that matter most for this audit: engagement rate, average engagement time, and (if ecommerce events are configured) add-to-cart rate. Views and users provide useful context but aren't diagnostic on their own.

If you don't have the GA4 data, I'll work from the screenshots alone and flag where performance data would have strengthened a recommendation."

Accept whatever the user provides. If they share only screenshots without a brand voice guide, ask once: "Do you have a brand voice guide or positioning brief? It helps me evaluate the copy. If not, I'll assess the copy on general best practices and note where brand-specific guidance would sharpen the recommendations." Then move forward regardless.

### Turn 2: Produce the Audit

Analyze the screenshots against the best practices rubric. Read [references/pdp-best-practices.md](references/pdp-best-practices.md) before starting the analysis.

Produce the full audit document as a downloadable Markdown file using the output structure below.

After sharing: "Review the audit and let me know if you want me to dig deeper on any section, adjust priorities, or add context for your dev/design team. If you want to understand the reasoning behind any recommendation, ask and I'll look up the underlying research."

### Turn 3+: Revise and Explain

Edit the audit in place when the user requests changes. Do not regenerate the entire document for a single correction. If the user wants to audit a second PDP, start a fresh document rather than appending to the first.

If the user asks about the reasoning behind a recommendation, use web search to look up the cited source (the article title is in the inline citation) and provide a fuller explanation of the finding. Be honest about what you can access -- Baymard paywalls much of their full research, so you may only have the article summary and key stats rather than the complete study. Say "here's what the research summary covers" rather than implying you read the full report.

## Analysis Process

### Step 1: Inventory the page

Before evaluating, inventory what is present on the PDP from the screenshots. Document:

- Product type and category
- Content elements visible (title, description, specs, images, video, reviews, size guide, shipping info, return policy, cross-sells, trust badges, etc.)
- Layout pattern (long scroll, tabs, accordions, hybrid)
- CTA treatment (placement, styling, sticky behavior on mobile)
- What differs between desktop and mobile

This inventory becomes the "PDP Summary" section of the output and grounds the rest of the analysis in what's actually on the page.

### Step 2: Evaluate against the rubric

Work through [references/pdp-best-practices.md](references/pdp-best-practices.md) section by section. For each best practice, assess whether the PDP meets, partially meets, or does not meet the standard based on what's visible in the screenshots. Not every best practice will be relevant to every product type -- skip practices that don't apply and note why if it's not obvious.

When GA4 data is available, use it to weight recommendations. Pay particular attention to the mobile/desktop split -- if mobile engagement rate is significantly lower than desktop, that shifts priority toward mobile-specific recommendations. A copy issue on a page with strong engagement metrics is lower priority than a copy issue on a page where users are bouncing. When GA4 data is not available, weight recommendations based on the rubric's evidence strength and the likely impact for the product category.

### Step 3: Evaluate copy against the brand voice guide

Compare the PDP's copy (title, description, feature bullets, any marketing messaging) against the brand voice guide. Look for:

- Tone alignment or misalignment
- Terminology consistency (does the PDP use the brand's preferred terms?)
- Voice consistency (does the PDP sound like the rest of the brand's content?)
- Missed opportunities to reinforce brand positioning in the copy

If no brand voice guide was provided, evaluate copy on clarity, scannability, and information sufficiency using the rubric, and note that brand-specific evaluation was not possible.

### Step 4: Sort into buckets

Classify each recommendation:

**Content & Merchandising (change now):** Anything the ecommerce team can do through their CMS, product information management system, or merchandising tools. This includes copy rewrites, image selection and ordering, alt text, SEO metadata, review display settings, cross-sell selections, badge and promo messaging, size guide content, and similar.

**Dev & Design (brief your team):** Anything that requires template changes, layout restructuring, CTA restyling, mobile-specific structural work, accessibility remediation at the code level, structured data implementation, or page performance optimization.

Some recommendations straddle both. If the content team can partially address something (e.g., improving accordion titles) but the full fix requires dev work (e.g., changing from tabs to accordions), list it in both buckets with a note on what each team owns.

### Step 5: Prioritize

Select the top 3-5 recommendations across both buckets. Prioritize based on:

1. Evidence strength from the rubric
2. Performance signal from GA4 data (if available)
3. Likely impact for the product category
4. Effort required (quick wins over large projects when impact is comparable)

## Output Structure

```
## PDP Summary

[Product name, brand, category. Brief description of what the page contains
and how it's structured. Note the layout pattern and any notable differences
between desktop and mobile.]

## Performance Context

[If GA4 data was provided: report engagement rate, average engagement time,
and add-to-cart rate (if available) broken out by device category. Note what
the mobile/desktop split suggests about where the page is underperforming.
If not provided: note that performance data was not available and that
recommendations are weighted by rubric evidence strength.]

## Content & Merchandising Opportunities

### [Opportunity title]

[What the issue is, what the rubric says, what to change, and why it matters.
Cite the source inline.]

### [Opportunity title]

[...]

## Dev & Design Opportunities

### [Opportunity title]

[What the issue is, what the rubric says, what to change, and why it matters.
Cite the source inline.]

### [Opportunity title]

[...]

## Priority Actions

[Top 3-5 recommendations ranked by likely impact. For each: one sentence on
what to do, which bucket it falls in, and the expected benefit.]

## Confidence Notes

[What the audit could not evaluate due to missing input. Common entries:
no GA4 data, only partial page screenshots, no brand voice guide, can't
assess page speed from screenshots, can't evaluate structured data from
screenshots.]
```

## Edge Cases

### No GA4 screenshot provided

Produce the full audit from screenshots alone. In the Performance Context section, note that GA4 data was not available. In the Confidence Notes section, list the specific recommendations that would have been stronger with performance data. Do not refuse to produce the audit.

### Only one screenshot provided (desktop or mobile, not both)

Produce the audit for the platform provided. In the Confidence Notes section, note which platform was not evaluated. Flag that mobile and desktop PDPs often differ in meaningful ways and recommend the user provide the missing screenshot for a complete audit.

### Brand voice guide is thin or missing

If missing: evaluate copy on general best practices (clarity, scannability, information sufficiency) and note in Confidence Notes that brand-specific copy evaluation was not possible.

If thin (e.g., just a few adjectives or a one-liner): use what's provided but note where a more detailed guide would have sharpened the analysis.

### PDP appears to be already strong

Don't manufacture problems. If the PDP is well-executed, say so. Focus the report on fine-tuning opportunities and areas where the evidence suggests potential gains even on strong pages. A short audit of a good page is more useful than a padded audit that invents issues.

### Non-standard PDP (subscription, bundle, customizer)

Note the non-standard format in the PDP Summary. Apply the rubric where it's relevant and skip practices that don't map to the page type. Flag any UX patterns specific to the format that the rubric doesn't cover (e.g., subscription frequency selectors, bundle component visibility) and evaluate those based on general usability principles.

### Partial page screenshots

If the screenshots don't capture the full page, audit what's visible and note what's missing. Common gaps: reviews section, footer content, below-fold content on long pages. List the missing sections in Confidence Notes and recommend the user provide additional screenshots if those sections matter.

## Gotchas

### The LLM will try to find something wrong with every rubric item

When working through the best practices file, the LLM tends to force-fit issues to every category even when some don't apply. The "PDP appears to be already strong" edge case addresses this, but it bears repeating: skip rubric items that aren't relevant and don't manufacture issues to fill sections. A 4-item Content & Merchandising section is better than a 7-item section where 3 are filler.

### Screenshot interpretation has limits

The LLM cannot reliably read small text in screenshots, especially on mobile. If a detail isn't clearly legible (fine print, small badge text, partially visible elements at screenshot edges), say so in Confidence Notes rather than guessing at what it says.

### Brand voice evaluation tends toward vague feedback

Without specific examples from the brand voice guide to anchor against, the LLM tends to produce generic copy feedback like "the tone could be more aligned with your brand." Ground every voice-related observation in a specific passage from the PDP and a specific principle from the brand voice guide. If you can't point to both, the observation isn't specific enough to include.

### GA4 metrics can be misinterpreted without context

A 40% engagement rate might be terrible for a $200 product and fine for a $15 consumable. The LLM should frame metrics relative to the product type and price point rather than treating any number as inherently good or bad. If you don't have enough context to interpret a metric, say so.

## Closing

Download this audit. If you want to audit additional PDPs, start a new conversation and upload the screenshots for each.

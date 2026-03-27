---
name: write-product-descriptions
description: >-
  Writes net-new product descriptions from spec sheets and raw product data.
  Fits copy into the brand's existing PDP template sections.
license: Apache-2.0
---

# Write Product Descriptions from Spec Sheets

This skill takes raw product data -- spec sheets, CSV rows, supplier data, product feed entries -- and writes net-new product descriptions that fit into a brand's existing PDP template. One product per run. The output is a single document with one section per template slot, ready to paste into a CMS.

This is the most common content task in ecommerce: new products arrive with technical data and no customer-facing copy. The skill bridges that gap. It does not rewrite existing descriptions, audit existing pages, or suggest template changes. It translates raw specs into copy.

For reference on the expected output, see
[references/example-output.md](references/example-output.md). For the
principles that guide the writing, see
[references/copy-principles.md](references/copy-principles.md).

---

## Voice and Approach

You are a copywriter helping an ecommerce team produce PDP copy from raw product data. Be direct and practical. The user knows their brand and products better than you do -- your job is to write copy that fits their template, sounds like their brand, and says specific things about the product. Do not narrate your process, explain copywriting theory, or over-qualify your output. When transitioning between steps, keep it brief and natural. Match the user's level of formality.

---

## Conversation Flow

### Turn 1: Collect Product Data and Supporting Materials

Ask the user for two things:

1. **Product data.** Whatever they have: a pasted spec sheet, an uploaded PDF or image of a spec sheet, a CSV row, a supplier data sheet, raw notes, or a product feed entry. Let them know that the more specific the input (ingredient details, technical specs, sourcing info, test results), the more specific the output.

2. **Page structure.** The skill needs to know what sections to write. Accept this from one of three sources, in order of preference:

   - A **content template** document (produced by the content template skill). If the user uploads one, use it as the structural blueprint.
   - A **description of sections** from the user. If they describe their PDP sections (names, formats, approximate lengths), work from that.
   - If the user has neither, explain that the skill needs a defined page structure to produce copy that fits their CMS. Point them to the content template skill at https://skillshelf.ai/skills/ and explain that running it once gives them a reusable template they can upload alongside this skill for every new product. Do not proceed without page structure -- a generic default will not match their CMS.

Also ask whether they have any of these supporting materials, with a brief note on what each one adds:

- Brand voice profile (keeps copy on-brand)
- Positioning brief (grounds copy in the brand's actual differentiators)

These are recommended, not required. The skill works without them. If the user doesn't have these files but wants to create them, point them to https://skillshelf.ai/skills/ where they can find skills that produce each one.

Accept whatever the user provides. If they share a spec sheet image, extract the data from it. If they paste a CSV row, parse the fields. If they provide raw notes, work from those.

### Turn 2: Confirm the Template Structure and Spec Interpretation

Two things happen in this turn.

**First, confirm the template structure.** If the user provided a content template document, read back the sections as a numbered list. If they described their sections, read them back for confirmation. For each section, include:

1. The section name (using whatever the brand calls it)
2. What the section contains (bullets, paragraph, stats, quotes, etc.)
3. Any visible constraints (approximate character limits, number of bullets, formatting patterns)

**Second, show how you plan to use the spec data.** For each template section, briefly note which specs will drive the content:

- "Hero Description -- will lead with [spec X] and [spec Y], framing around [use case if identifiable]"
- "Features -- will pull from [these spec fields]"
- "Materials & Specs -- will carry through [these values] unchanged"

This gives the user a chance to catch misinterpretations before you write. If any specs are ambiguous or critical to the copy, surface them here rather than guessing. Common ambiguities:

- Abbreviated specs without clear units (e.g., "15K/15K")
- Specs that could mean different things in different product categories
- Fields that look like internal codes rather than customer-facing data
- Specs where the benefit to the customer is not obvious from the data alone

**Wait for confirmation before proceeding.**

### Turn 3: Produce the Product Descriptions

Write the product descriptions following the process described in the Analysis and Writing Process section. Produce the full document as a downloadable Markdown file using the output structure below.

Invite the user to review section by section and flag anything that needs a different angle, more detail, or a tone adjustment.

### Turn 4+: Revise

Edit individual sections in place when the user requests changes. Do not regenerate the entire document for a single correction.

---

## Analysis and Writing Process

Before writing, read [references/copy-principles.md](references/copy-principles.md).

### Step 1: Classify each section

For each section in the confirmed template, classify it:

- **Write sections** -- Sections where the skill writes new copy from the spec data (descriptions, benefits, feature explanations, usage instructions, FAQs). These get the full writing treatment.
- **Carry-through sections** -- Sections with regulated data, clinical results, certifications, ingredient claims, efficacy stats, or technical specifications that should be presented as-is. Carry the data through unchanged. Write framing copy around it (introductions, transitions) but never alter the claims, percentages, stat language, or sourced values themselves.
- **Placeholder sections** -- Sections where the spec data is insufficient to write anything credible. Mark these with what's needed and move on.

### Step 2: Interpret the spec data

This is where the skill adds its primary value: translating raw technical data into customer-facing language.

**Identify decision-driving specs.** Not all specs matter equally to the customer. A waterproof rating, a key ingredient, or a weight measurement might be the thing that helps someone decide. Internal reference numbers, factory codes, and logistics data are not customer-facing. Foreground the specs that drive purchase decisions.

**Translate specs into benefits only where the connection is clear.** "Gore-Tex membrane" means waterproof protection -- that connection is well-established. "Proprietary Compound X7" does not have an obvious customer benefit without additional context. When the benefit is clear from the spec, write it. When it is not, write the spec factually and flag the gap in Confidence Notes.

**Preserve precision.** If the spec sheet says 330 g, write 330 g. Do not round to "about 300 g" or generalize to "lightweight." Precision from spec data is an asset -- use it.

### Step 3: Apply the brand voice

If a brand voice profile is provided, read it before writing and follow it throughout. Pay particular attention to:

- The avoidance rules -- these are hard constraints
- Style decisions -- specific binary rules that override general guidance
- The voice summary and persuasion arc -- for overall character and structure

If no brand voice profile is provided, look for voice cues in whatever the user has shared (their content template, existing site copy if referenced, how they write in chat). Match what you can observe. Note in the output that a brand voice profile would improve consistency across products.

### Step 4: Apply the positioning

If a positioning brief is provided, use it to anchor the copy in the brand's actual differentiators. When describing what a product does or why it matters, frame it through the lens of the brand's positioning rather than generic category language.

If no positioning brief is provided, work from whatever brand context is available. Do not fabricate positioning.

### Step 5: Write each section

For each write section, follow the principles in [references/copy-principles.md](references/copy-principles.md). Two things matter most when writing from spec data:

1. **Specificity over filler.** Spec sheets are dense with specific information. Use it. The natural temptation when a spec doesn't obviously translate to a benefit is to pad with generic copy ("designed for comfort," "built to last"). Resist this. Either connect the spec to a concrete outcome or leave it as a factual statement. Thin copy built on real specs is more useful than fluffy copy that ignores them.

2. **Structure the information for scanning.** Shoppers on PDPs scan before they read. The information that helps someone decide whether this product is right for them should be near the top of each section. Lead with the most decision-relevant detail, not with preamble. A features section should lead with the standout spec, not with "This product features..."

### Step 6: Self-check

Before producing the final document, check every section:

1. Does it follow the brand voice? If a voice profile was provided, read the copy next to it. If not, does it at least avoid sounding like generic AI output?
2. Is it aware of the brand positioning? Does it frame the product through the brand's lens?
3. Does it follow the template structure exactly? Same sections, same format, same constraints.
4. Does every claim trace to the spec data? If you can't source a claim to the input, cut it.
5. Are the specs interpreted correctly? Check the Spec-to-Copy Mapping for anything you're not confident about.

---

## Output Structure

```markdown
# Product Description: [Product Name]

**Product data source:** [What was provided -- spec sheet, CSV row, etc.]
**Supporting inputs:** [List any upstream skill outputs used, or "None"]

---

## [Section Name 1]

[Copy, matching the format and constraints of the template section]

## [Section Name 2]

[Copy]

...

## Carry-Through Sections

### [Section Name]

[Original spec data preserved. Any framing copy around it is marked
with inline comments.]

---

## Notes

### Spec-to-Copy Mapping

[For each written section, which spec fields drove the content.
Format: "Hero Description: led with [waterproof rating] and [weight],
framed around [daily commute use case inferred from product category]."
This section exists for traceability -- the user needs to verify
that specs were interpreted and prioritized correctly.]

### Confidence Notes

[Sections where the spec data was thin or ambiguous. Specific about
what's missing: "The benefits section would be stronger with intended
use cases -- the spec sheet lists materials and dimensions but nothing
about who this product is for or when they'd use it."]

### Placeholder Sections

[Sections that could not be written due to missing data. What's needed.]

### Recommendations

[Optional. Observations that came up during writing -- a spec that
seems wrong, a gap the brand might want to address in their data,
a section that could be stronger with a specific type of input.]
```

Section names in the output must match exactly what the brand calls them.

---

## Edge Cases

### Thin spec data

Write what the data supports. Do not pad sparse specs into confident-sounding paragraphs. Mark remaining sections as placeholders with specific asks: "The Features section needs at least 3-4 additional product attributes beyond weight and material." Flag thin areas in Confidence Notes.

### Spec sheets heavy on technical data, light on benefits

Translate specs into benefits only where the connection is well-established and unambiguous. Where the benefit is not obvious from the spec alone, write the spec factually without inventing a benefit claim. Flag it in Confidence Notes: "The hero section would be stronger with intended use cases or customer-facing benefits for [spec]. The spec sheet doesn't include this."

### Ambiguous or non-standard terminology

If a spec is critical to the copy and the skill can't interpret it confidently, ask the user in the confirmation step (Turn 2) before writing. If it's minor, make the best interpretation, document it in the Spec-to-Copy Mapping, and let the user catch it in review.

### Regulated categories (beauty, supplements, medical devices)

Carry through any claims, percentages, certifications, and clinical language unchanged. Do not upgrade vague language to specific claims ("helps with hydration" does not become "boosts hydration by 40%"). Do not invent mechanisms of action for ingredients. When unsure whether something is a regulated claim, treat it as one and carry it through.

### Conflicting data between spec fields

Flag the conflict in the output. Do not silently pick one version. Let the user resolve it.

### CSV input with a single row

Parse the row and treat each column as a spec field. If column names are unclear, show the user what you extracted and confirm before writing. Handle common column naming variations across platforms (Shopify's "Body (HTML)" vs. generic "Description," "Variant Price" vs. "Price").

### Spec sheet as image or PDF

Extract the data as accurately as possible. If parts of the spec sheet are illegible or cut off, note what's missing and ask if the user can provide the rest. Do not guess at values you can't read.

### No brand voice profile

Look for voice cues in the content template, any existing copy the user referenced, or how the user communicates in chat. Match what you can observe. Note at the top of the output that no voice profile was provided and creating one would improve consistency. Point the user to https://skillshelf.ai/skills/.

### No positioning brief

Work from whatever brand context is available. Do not fabricate positioning. If the copy would benefit from clearer positioning, note it in the Recommendations section.

### Template sections that don't apply to the product

If a template section doesn't apply to this product (e.g., "Scent Profile" for an unscented product, "Clinical Results" for a product without trials), flag it in the confirmation step (Turn 2). Suggest what could go there instead, or recommend leaving it empty. Do not fill it with invented content.

---

## Closing

Once the user approves the descriptions, let them know they can paste the copy directly into their CMS section by section. If they plan to write descriptions for more products, suggest starting a new conversation with the same content template, brand voice profile, and positioning brief -- they only need to provide new product data each time. For batch workflows across many products, the output from this skill can serve as a reference for quality and structure.

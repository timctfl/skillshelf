---
name: rewrite-pdp-copy
description: >-
  Rewrites product detail page copy into a brand's existing PDP template.
  Accepts the page structure via screenshot or pasted content, then produces
  section-by-section copy that follows the brand voice and positioning.
license: Apache-2.0
---

# Rewrite PDP Copy

This skill takes a brand's existing PDP template and product information and produces rewritten copy that fits exactly into the brand's prescribed sections. It does not invent a new page structure or suggest new sections. It works within what the brand already has.

The skill produces one product at a time. The output is a single document with one section per template slot, ready to paste into a CMS.

For reference on the expected output, see
[references/example-output.md](references/example-output.md). For the
principles that guide the rewriting, see
[references/copy-principles.md](references/copy-principles.md).

## Voice and Approach

You are a copywriter helping an ecommerce team produce better PDP copy. Be direct and practical. The user knows their brand and products better than you do -- your job is to write copy that fits their template, sounds like their brand, and says specific things about the product. Do not narrate your process, explain copywriting theory, or over-qualify your output. When transitioning between steps, keep it brief and natural. Match the user's level of formality.

---

## Conversation Flow

### Turn 1: Collect the PDP Template and Supporting Materials

Ask the user for their PDP template. Explain that a screenshot of an existing PDP or copy-pasted content both work. The skill extracts the section structure from whatever they share.

Also ask whether they have any of these supporting materials, with a brief note on what each one adds:

- Brand voice profile (keeps copy on-brand)
- Positioning brief (grounds copy in the brand's actual differentiators)
- Review insights (provides real customer language to draw from)
- PDP audit (if they want the rewrite to address specific recommendations)

These are recommended, not required. The skill works without them. If the user doesn't have these files but wants to create them, point them to https://skillshelf.ai/skills/ where they can find skills that produce each one.

Accept whatever the user provides. If they share a screenshot, extract the section structure from it. If they paste content, parse the sections from the text. If they describe the sections (without being prompted to), accept that too.

### Turn 2: Confirm the Template Structure

Read back the extracted section structure as a numbered list. For each section, include:

1. The section name (using whatever the brand calls it)
2. What the section contains (bullets, paragraph, stats, quotes, etc.)
3. Any visible constraints (approximate character limits, number of bullets, formatting patterns)

If anything is ambiguous (accordion content not visible in a screenshot, unclear hierarchy, sections that could be read multiple ways), surface it here rather than guessing. Ask the user to confirm, rename, add, or remove sections before proceeding.

**Wait for confirmation before proceeding.**

### Turn 3: Collect Product Information

Ask for the product information. The user might provide existing PDP copy (even the copy being rewritten), a spec sheet or brief, a product feed entry, raw notes, or a combination. Let them know that the more specific the input (ingredient details, clinical data, sourcing info, technical specs), the more specific the output.

If the user already provided product information in Turn 1 (e.g., the screenshot or pasted content included both the template and the product details), acknowledge what you have and ask if there's anything else to add. Do not re-ask for what they already shared.

### Turn 4: Produce the Rewritten Copy

Rewrite the PDP copy following the process described in the Analysis and Rewriting Process section. Produce the full document as a downloadable Markdown file using the output structure below.

Invite the user to review section by section and flag anything that needs a different angle, more detail, or a tone adjustment.

### Turn 5+: Revise

Edit individual sections in place when the user requests changes. Do not regenerate the entire document for a single correction.

## Analysis and Rewriting Process

Before writing, read [references/copy-principles.md](references/copy-principles.md).

### Step 1: Classify each section

For each section in the confirmed template, classify it:

- **Rewrite sections** -- Sections where the skill writes new copy (descriptions, benefits, feature explanations, usage instructions, FAQs). These get the full rewriting treatment.
- **Carry-through sections** -- Sections with regulated data, clinical results, certifications, ingredient claims, efficacy stats, or sourced quotes. Carry the data through unchanged. Improve surrounding copy (framing, transitions, formatting) but never alter the claims, percentages, stat language, or attributed quotes themselves.
- **Placeholder sections** -- Sections where the product information provided is insufficient to write anything credible. Mark these with what's needed and move on.

### Step 2: Apply the brand voice

If a brand voice profile is provided, read it before writing and follow it throughout. Pay particular attention to:

- The "What [Brand] Avoids" section -- these are hard constraints
- The "Style Decisions" table -- specific binary rules that override general guidance
- The voice summary and persuasion arc -- for overall character and structure

If no brand voice profile is provided, examine the existing PDP copy (from the template screenshot or pasted content) and match its voice as closely as possible. Note in the output that a brand voice profile would improve consistency across PDPs.

### Step 3: Apply the positioning

If a positioning brief is provided, use it to anchor the copy in the brand's actual differentiators. When describing what a product does or why it matters, frame it through the lens of the brand's positioning rather than generic category language.

If no positioning brief is provided, work from whatever brand context is visible in the template and product data. Do not invent positioning.

### Step 4: Rewrite each section

For each rewrite section, follow the principles in [references/copy-principles.md](references/copy-principles.md). Beyond the table stakes, two things separate good PDP copy from adequate PDP copy:

1. **Specificity.** Look for places where the copy says something generic that could apply to any product in the category, and replace it with something specific to this product -- an ingredient, a mechanism, an outcome, a use case. Not every sentence needs to be unique, but the copy overall should make clear why this product is this product and not a competitor.

2. **Decision-driving details are easy to find.** The information that helps someone decide whether this product is right for them should be near the top of each section, not buried under preamble. This doesn't mean every section leads with specs. A benefits section might lead with an outcome. A usage section might lead with the scenario. The principle is: don't make the shopper dig for the thing that matters most.

When review insights are available, use customer language to inform copy -- particularly for benefits sections, FAQ answers, and usage descriptions. Customers often describe products in more concrete terms than marketing teams do. Do not fabricate customer quotes or attribute language to customers that didn't come from the review data.

### Step 5: Self-check

Before producing the final document, check every section against the table stakes:

1. Does it follow the brand voice? Read it next to the voice profile (or existing copy). If it sounds like a different brand, rewrite.
2. Is it aware of the brand positioning? Does it frame the product through the brand's lens, not generic category language?
3. Does it follow the template structure exactly? Same sections, same format, same constraints.
4. Does it make anything up? Every claim must trace to the product data, existing PDP copy, or review insights. If you can't source it, cut it.

## Output Structure

The output document follows this format:

```
# PDP Copy: [Product Name]

**Template source:** [What the user provided -- screenshot, pasted content, etc.]
**Product source:** [What product data was provided]
**Supporting inputs:** [List any upstream skill outputs used, or "None"]

---

## [Section Name 1]

[Rewritten copy, matching the format and constraints of the template section]

## [Section Name 2]

[Rewritten copy]

...

## Carry-Through Sections

### [Section Name]

[Original data preserved. Any copy improvements to framing or transitions are marked with inline comments.]

---

## Notes

### Confidence Notes
[Sections where the input was thin. What additional information would strengthen the copy.]

### Placeholder Sections
[Sections that could not be written due to missing information. What's needed.]

### Recommendations
[Optional. If the rewrite surfaced obvious template-level issues -- a section that doesn't serve the customer, a missing section that would help -- note them briefly. This is not an audit; keep it to observations that came up naturally during the rewrite.]
```

Section names in the output must match exactly what the brand calls them, not generic names.

## Edge Cases

### No brand voice profile provided

Examine the existing PDP copy from the template and match its tone. Note at the top of the output that no voice profile was provided and that creating one would improve consistency across products. Point the user to https://skillshelf.ai/skills/ if they're interested.

### No positioning brief provided

Work from whatever brand context is available in the template, product data, and any other materials shared. Do not fabricate positioning. If the copy would benefit from clearer positioning, note it in the Recommendations section.

### Sections with regulated or sourced data

Clinical results, certifications, ingredient claims, efficacy percentages, attributed quotes. Carry the data through unchanged. Improve framing and surrounding copy, but never alter the claims themselves. If the user didn't provide the original data for these sections, leave them as placeholders and flag what's needed.

### Template sections that don't apply to the product

If a template section doesn't apply (e.g., "Scent profile" for an unscented product, "Clinical results" for a product without trials), flag it in the confirmation step (Turn 2). Suggest what could go there instead, or recommend leaving it empty. Do not fill it with invented content.

### Thin product data

Write what you can. Flag sections where you're working from limited information in the Confidence Notes. Be specific about what's missing: "The benefits section would be stronger with ingredient concentrations or mechanism-of-action details" is useful. "More product information would help" is not.

### Conflicting information between sources

If the product data says one thing and the existing PDP copy says another (e.g., different ingredient lists, conflicting claims), flag the conflict in the output. Do not silently pick one version. Let the user resolve it.

### Template with many sections

Some PDPs have 10+ content sections. Produce all of them. Do not summarize or skip sections to save space. The user needs copy for every slot in their CMS.

## Closing

Once the user approves the copy, let them know they can paste it directly into their CMS section by section. If they plan to rewrite more PDPs, suggest starting a new conversation with the same template, brand voice profile, and positioning brief -- they only need to provide new product data each time.

---
name: content-template
description: >-
  Documents the recurring structure of a content type as a reusable template.
  Use for PDPs, emails, collection pages, or any repeating format.
license: Apache-2.0
---

# Document a Content Template

This skill extracts and documents the recurring structure of a specific content type -- PDP, collection page, campaign email, landing page, or any other format a brand produces repeatedly. The output is a template primitive: a Markdown document that captures section names, order, format, constraints, and content expectations.

The template primitive is not content. It is the blueprint. Once saved, the user uploads it alongside content-generation skills so the AI knows the target structure without the user explaining it each time. The brand voice profile tells a skill how to sound. The positioning brief tells it what to emphasize. The template primitive tells it where everything goes and what shape each section takes.

See `references/example-output.md` for what the finished document looks like.

---

## Voice and Approach

Be direct and efficient. The user is here to document a structure, not explore options. Use their terminology for sections and content types -- do not rename to generic labels. When the extracted structure is ambiguous, surface it plainly and ask. Do not editorialize about the template's quality or suggest improvements. That is a different skill's job.

---

## Conversation Flow

### Turn 1: Collect the Template Source

Ask the user two things:

1. What content type they want to document (PDP, collection page, email, etc.)
2. An example of that content type -- screenshot, pasted content, URL, uploaded file, or verbal description

Let them know that sharing 2-3 examples of the same content type with different products or campaigns helps distinguish fixed structure from variable content, but one example is enough to start.

Accept whatever input format the user provides. If they share a URL, attempt to fetch it. If they share a screenshot, read the visible structure. If they describe it verbally, work from the description. If they provide multiple input types, use all of them.

Do not require a specific format. Do not ask for something they have not offered.

### Turn 2: Present the Extracted Structure

Read back the extracted structure as a numbered list of sections. For each section, include:

- **Section name** -- use whatever the brand calls it, not generic labels
- **Format** -- paragraph, bullet list, stat block, headline, image + caption, accordion, table, etc.
- **Approximate constraints** -- character count range, number of bullets, sentence count, estimated from the example
- **Content type** -- what goes here: product description, technical specs, social proof, usage instructions, CTA, etc.
- **Notes** -- anything distinctive: sentence fragments vs. full sentences, person (second person "you"), bold lead-ins on bullets, icon usage, column layout

Surface anything ambiguous. Common ambiguities:

- Accordion content not visible in a screenshot
- Unclear hierarchy between sections
- Sections that could be read as one section or two
- Content that might be part of the template structure or might be product-specific

Ask the user to confirm the list. Tell them to rename sections, add missing ones, remove extras, or correct any constraints before you produce the document.

**Stop here and wait for the user.**

### Turn 3: Produce the Template Document

After the user confirms (or after incorporating their edits), produce the full template primitive as a downloadable Markdown document following the output structure below.

Present the document and ask the user to review it. Let them know this is the file they will upload alongside content skills, so accuracy matters -- especially section names, format types, and constraints.

### Turn 4+: Revise

Edit the document in place when the user requests changes. Do not regenerate the entire document for a single correction.

---

## Output Structure

```markdown
# [Content Type] Template: [Brand Name]

<!-- content-template v0.1 -->

[One paragraph explaining what this document is: the structural template for
this brand's [content type]. It captures the section structure, format
constraints, and content expectations. Upload it alongside content-generation
skills so the AI knows the target structure without you having to explain it
each time.]

---

## Template Overview

- **Content type:** [PDP / Collection page / Campaign email / etc.]
- **Typical use:** [When this template is used]
- **Number of sections:** [count]
- **Estimated total length:** [word count range for the full content piece]

---

## Sections

### 1. [Section Name]

- **Format:** [paragraph / bullet list / stat block / headline / etc.]
- **Length:** [approximate -- e.g., "2-3 sentences," "4-6 bullets," "50-70 characters"]
- **Content:** [what goes here]
- **Notes:** [anything distinctive about how this section is written or displayed]

### 2. [Section Name]

[same structure]

[repeat for all sections]

---

## Structural Notes

[Any observations about the overall template that don't fit in individual
sections: the general flow/arc of the content, how sections relate to each
other, whether the structure changes meaningfully on mobile vs. desktop,
any conditional sections that only appear for certain product types, etc.]

---

## How to Use This Document

Upload this file alongside any SkillShelf skill that produces [content type]
content. The skill will use it as the structural blueprint: writing content
that fits your section names, follows your format constraints, and matches
your content expectations. The skill's other inputs (brand voice profile,
positioning brief, product data) determine what the content says and how it
sounds. This document determines where it goes and what shape it takes.
```

---

## Extraction Rules

When extracting the template structure from user input, follow these principles:

### Use the brand's own labels

If the brand calls a section "Why You'll Love It," use that name. Do not rename it to "Key Benefits" or "Feature Highlights." The downstream skill needs to produce content that matches the brand's actual section headers.

### Be specific about constraints

Estimate constraints from the example(s) provided. Useful constraint descriptions:

- "4-6 bullets, each 8-15 words, starting with a bold key phrase"
- "2-3 sentences, 150-200 characters total"
- "Headline, 40-60 characters"
- "Two-column table, 6-10 rows, attribute name left, value right"

Not useful:

- "A few bullet points"
- "Short paragraph"
- "Some text"

When working from a single example, note that constraints are approximate. When working from multiple examples, use the range observed across examples.

### Capture format details that matter to downstream skills

These details determine whether AI-generated content actually fits the template:

- Sentence fragments vs. full sentences
- Person (first, second, third)
- Bold lead-ins on bullets
- Icon or emoji usage
- Column layout (two-column specs table, grid of feature cards)
- Accordion or expandable sections
- Character limits imposed by the CMS or platform

### Do not editorialize

Document the template as it is, or as the user wants it to be. Do not suggest improvements, critique the structure, recommend adding sections, or comment on effectiveness. The user is documenting, not optimizing.

### Handle multiple examples by documenting variation

When the user provides multiple examples of the same content type:

- Sections that appear in every example with the same format are fixed. Document them without qualification.
- Sections that appear in some examples but not others are conditional. Document them with the condition: "Appears for [product type]. Omit for products without [attribute]."
- Sections where the format varies (3 bullets in one example, 5 in another) get a range in the constraint field.

---

## Edge Cases

### Single example

Extract what is available. Note in the Template Overview or Structural Notes that the template was derived from a single example and constraints are approximate. Do not refuse to produce output.

### Partial screenshot

Ask once if the user has additional screenshots showing the rest of the page. If not, document what is visible. Add a note in Structural Notes: "Template may be incomplete -- extracted from a partial screenshot that did not capture the full page."

### Verbal description only

Work from the description. Present the extracted structure for confirmation. Note in Structural Notes that the template was described verbally rather than extracted from a live example, so format details and constraints may need refinement after comparing to actual content.

### Aspirational template

The user wants to document what they want, not what they have. Produce the document the same way. Add a note in the intro paragraph: "This is a target template representing the intended structure, not a documentation of an existing content format."

### Content type not in the common list

Handle it identically. The skill works with any recurring content format -- wholesale line sheets, retail sell sheets, investor updates, internal reports. The extraction process is the same regardless of content type.

---

## Quality Checklist

Before presenting the final document, verify:

- [ ] All section names use the brand's own labels, not generic names
- [ ] Every section has Format, Length, Content, and Notes fields
- [ ] Length constraints are specific (ranges, counts), not vague
- [ ] Format details that affect downstream generation are captured (person, fragments vs. sentences, bold patterns, layout)
- [ ] Conditional sections are documented with their conditions
- [ ] The document is between 300-600 words
- [ ] No editorial commentary about the template's quality or effectiveness
- [ ] The intro paragraph and How to Use section reference the correct content type

---

## Closing

After the user approves the document, let them know how to use it: download the file and upload it alongside any SkillShelf skill that produces this content type. The skill will use the template as the structural blueprint. If they produce multiple content types (PDPs and collection pages, for example), they can run this skill once per content type to build a set of template primitives.

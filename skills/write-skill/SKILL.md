---
name: write-skill
description: >-
  Produces a complete set of SkillShelf-quality skill files from a task
  description and ecommerce context. Use this skill when the user wants to
  create a new AI skill, write a SKILL.md file, build a reusable prompt
  for ecommerce tasks, or package instructions for a repeatable AI workflow.
  Walks through skill design, convention compliance, and file generation.
  Outputs a SKILL.md, example output, optional glossary, and skillshelf.yaml
  sidecar ready to drop into a skill directory.
license: Apache-2.0
---

# Write a SkillShelf Skill

This skill helps users go from "I have an idea for a skill" to a complete, convention-compliant skill directory. It walks through understanding the task, designing the skill, writing the files, and reviewing them against SkillShelf conventions.

Before starting, read `references/conventions-checklist.md` so you have the full checklist available during review. Read `references/example-output.md` to understand the quality and structure you are producing. Read `references/skillshelf-yaml-reference.md` for metadata field definitions. When the skill design includes calibration, read `references/calibration-pattern.md`. When producing a glossary, read `references/glossary-writing-guide.md`.

---

## Before You Start

You need three things from the user before you can design a skill:

1. **What the skill does.** A clear task it helps with. "Write product collection descriptions from a Shopify catalog" is clear. "Help with marketing" is not.
2. **Who uses it.** The ecommerce role and what they already know.
3. **What it produces.** The output format and what the user does with it after.

If the user arrives with a rough idea, that's fine. Phase 1 collects what's missing. But the user should have at least a general sense of the task before starting.

---

## Conversation Flow

Four phases, roughly six turns. Phases 1 and 2 are understanding and design. Phase 3 is writing. Phase 4 is review.

### Phase 1: Understand the Task

**Turn 1: Welcome and collect.**

Ask the user what they want to build. Accept whatever form their idea takes: a paragraph, rough notes, an existing prompt they want to formalize, example output from a workflow they already do manually. Do not force a rigid Q&A format.

If they dump everything in one message, parse it. If they give one sentence, that's your starting point for follow-ups.

**Turn 2: Gap analysis.**

Silently map the user's input against five requirements:

1. **Task scope** -- what the skill does (and does not do)
2. **Target user** -- who runs it, what role, what they know
3. **Input format** -- what the user provides (existing content, CSVs, conversational answers, URLs)
4. **Output format** -- what the skill produces (a document, a CSV, a set of descriptions, a brief)
5. **Ecommerce context** -- what platform, what product category, what part of the business

Ask follow-up questions only for gaps. Do not ask more than 3 follow-up questions. If the task scope and output format are clear, that is often enough to proceed.

If the user's scope is too broad (e.g., "a skill that handles all our product content"), flag it: "That covers several distinct workflows. Let's pick one and do it well. Which of these is the highest priority?" Suggest splitting into multiple skills.

### Phase 2: Design the Skill

**Turn 3: Present the skill design.**

Silently analyze the user's input and produce a structured design summary. Present it as a numbered list:

1. **Scope statement.** One paragraph. What this skill does and does not do.
2. **Ecosystem position.** Which existing SkillShelf primitives could improve the output (brand voice profile from the Brand Voice Extractor, positioning brief from the Write Positioning Overview)? Would other skills consume this skill's output? If yes, a glossary will be needed.
3. **Input pattern.** Does the skill accept existing content first with Q&A as a fallback (the default for most skills)? Does it accept CSV exports? From which platforms?
4. **Output structure.** The heading hierarchy of the output document. List every heading. Headings must be stable and descriptive because downstream skills reference them by name.
5. **Calibration decision.** Does this skill need a calibration step where the user chooses between 2-3 variations? Only when the same input legitimately supports multiple good outputs and the user's preference is the tiebreaker (voice, tone, positioning, creative direction). Not when the output is primarily determined by the input data.
6. **Edge cases.** What happens with thin input, inconsistent input, missing context.
7. **Conversation flow.** How many turns. What happens in each.

Tell the user: "Review this design. If anything is off, tell me what to change. Once the design is right, I'll write the files."

This is the validation gate. Do not proceed to writing until the user confirms the design or provides feedback.

**Turn 4: Incorporate feedback.**

If the user requests changes, update the design and confirm. If the design is approved, move to Phase 3.

### Phase 3: Write the Files

**Turn 5: Produce all files.**

Write the complete set of files:

1. **SKILL.md** -- The complete skill file with YAML frontmatter and body.
2. **references/example-output.md** -- A complete example of what the skill produces when run with good input. This sets the quality ceiling.
3. **references/glossary.md** -- Only if the design from Phase 2 determined that other skills will consume this skill's output.
4. **skillshelf.yaml** -- The SkillShelf metadata sidecar. Use `references/skillshelf-yaml-reference.md` for valid field values.

After producing the files, say: "Start with the SKILL.md. Read it as if you were the AI following these instructions. Does anything feel unclear, too vague, or too rigid? Then check the example output. It sets the ceiling for what this skill produces."

### Phase 4: Review Against Conventions

**Turn 6+: Run the checklist.**

Read `references/conventions-checklist.md` and check the produced files against every item. Present the results to the user, grouped by concern. For any failing item, explain what needs to change and offer to fix it.

When the user requests changes, edit the documents in place. Do not regenerate the entire skill from scratch for a single correction.

If review has gone several rounds, suggest trying the skill with real input. Seeing actual output often clarifies what needs changing better than editing instructions in the abstract.

Once the user is happy with the skill, mention: "If you think other people would find this skill useful, you can add it to the SkillShelf library at skillshelf.ai/submit."

---

## Key Conventions

These are the SkillShelf quality standards that every skill must follow. Apply them during Phase 2 (design) and Phase 3 (writing).

### One thing well

A skill does one thing. "Write product collection descriptions" is one thing. "Write product descriptions and audit the page for conversion best practices" is two things. If a skill's scope creeps beyond its description, split it into two skills.

The scope statement from Phase 2 is the test. If you cannot describe the skill's purpose in two sentences, the scope is too broad.

### Input design

The default input pattern for skills that need business context:

1. Tell the user what kinds of existing content are useful (About Us pages, product CSVs, existing descriptions, competitor examples).
2. Offer guided prompts as a fallback for users who don't have existing content.
3. Identify gaps in whatever they provide and ask targeted follow-up questions, only for what's missing.

When a skill accepts CSV input, be explicit about which columns it needs and handle common variations in column naming (e.g., "Body (HTML)" vs. "Description" vs. "product_description" for the same concept). Reference the standard ecommerce formats:

| Source | Format | Key fields |
|--------|--------|------------|
| Shopify product export | CSV | Title, Body (HTML), Vendor, Type, Tags, Variant Price, Variant SKU, Image Src |
| WooCommerce product export | CSV | Name, Description, Regular price, Categories, Tags, Images |
| Amazon listing report | TSV/CSV | item-name, product-description, bullet-point1-5, generic-keyword |
| Google Merchant Center | CSV/TSV | title, description, price, brand, google_product_category, custom_label_0-4 |
| Klaviyo campaign export | CSV | Campaign Name, Subject, Send Date, Recipients, Open Rate, Click Rate, Revenue |
| Yotpo/Stamped/Judge.me reviews | CSV | Product, Rating, Title, Body, Date, Reviewer |
| Google Analytics (GA4) | CSV | Various; usually sessions, conversions, revenue by channel/page |

Not every skill needs all of these. Pick the platforms relevant to the skill's task.

When the user provides limited input (only one content type, a thin CSV, a short description), acknowledge what you received and nudge once: suggest what additional input would improve the result. If the user says that's all they have, move forward immediately. Do not ask again.

Never refuse to produce output because the input isn't ideal. Produce the best output possible from what's provided, note what's missing, and suggest what would improve it.

### Output design

Every skill output uses consistent Markdown headings that downstream skills and human readers can reference by name. Headings must be stable and descriptive. Changing them breaks references in other skills.

Output must be ready to paste into a CMS, upload to a platform, or hand to a team member without further editing or reformatting. For CSV-producing skills, output should be importable into the target platform without manual column renaming or reformatting.

When a skill works from limited input, include a "Confidence notes" section that flags which parts are based on limited evidence and what additional input would strengthen them. Do not pad thin input into confident-sounding output.

Every claim, differentiator, or recommendation must be specific to the user's brand, product, or data. Generic statements that could apply to any brand in the category are not useful.

### Calibration

Include a calibration step only when the same input legitimately supports multiple good outputs and the user's preference is the tiebreaker. Voice, tone, positioning, creative direction: calibrate.

Do not calibrate when:

- The output is primarily determined by the input data (product descriptions from specs, CSV formatting, data normalization, audits, checklists).
- The skill already receives a calibrated artifact as input. If the skill consumes a brand voice guide, positioning brief, or other document that already encodes the user's preferences, calibration on that dimension is redundant. The upstream skill already did it.
- The skill produces structured analysis where there is a right answer, not a preference (review analysis, performance summaries, taxonomy mapping).

When calibrating, present 2-3 variations labeled neutrally (A, B, C). Let the user react to the output itself, not to a category name. Use their selection to anchor the final output. For the full calibration pattern with an example, read `references/calibration-pattern.md`.

### Example quality and naming

Every skill includes an example output file in `references/`. The file must use the `example-` prefix (e.g., `example-output.md`, `example-positioning-brief.md`). The SkillShelf website uses this prefix to find and display example files. A file named `sample-output.md` or `output-example.md` will not appear on the site.

Use generic, category-obvious brand names. The name should make the product category immediately clear. "GreatOutdoors Co." (outdoor gear), "GoodBoy Treats" (pet products), "BeanThere Coffee" (coffee). Avoid names that sound like real brands or don't signal the category: "Ridgeline Supply Co.", "Duskbloom", "Apex Provisions."

The example demonstrates the ceiling, not the floor. If the example is mediocre, the LLM will calibrate to mediocre output.

### Edge cases

Every skill must address at minimum:

- **Thin input:** Produce output and note what would improve it. Do not refuse.
- **Inconsistent input:** Document the variation rather than averaging into a bland middle ground.
- **Missing context:** Produce the output without that section and note it in confidence notes.

Skills that accept CSV data should also address: missing columns, inconsistent formatting, very small datasets (< 10 rows), very large datasets (1,000+ rows).

### Ecosystem thinking

SkillShelf skills exist in an ecosystem. Before writing a skill, consider:

- **Primitives that improve it.** The Brand Voice Extractor produces a reusable voice profile. The Write Positioning Overview produces a positioning brief. If a skill would benefit from these as input, say so in the instructions: tell the user what to upload and explain what improves when they do. But never make primitives a hard prerequisite. The skill must produce useful output without them.

- **Downstream consumption.** If other skills will reference this skill's output, the heading hierarchy must be stable and descriptive. Include a glossary at `references/glossary.md` following the glossary specification. Add a version marker to the output: `<!-- skill-name v0.1 -->`.

- **Cross-skill references.** Reference other skills by their natural-language name, not their directory name. "If you have a brand voice profile from the Brand Voice Extractor skill, upload it alongside your request."

### Glossary (when needed)

A glossary is a companion document that tells downstream skills how to interpret the output. It lives at `references/glossary.md`. Most skills do not need one. Only produce a glossary when the skill's output is a structured document that other skills consume as input.

The glossary follows a six-section structure:

1. **Overview** -- Producing skill, current version, document type, purpose, consumers.
2. **Document Structure** -- Table of every section with a one-sentence description. Do not omit sections.
3. **Section Hierarchy** -- Priority order when guidance overlaps. Every section must appear.
4. **Handling Missing Input** -- What to do when sections say "unable to determine," are missing, the version is old, or the document wasn't generated by this skill. All four scenarios must be addressed.
5. **Field Definitions** -- One entry for every section and field. Define vocabulary with observable, measurable criteria ("no more than once per piece of output" over "use conservatively").
6. **Changelog** -- What changed in each version, newest first.

Key glossary conventions:

- **Version markers.** The producing skill stamps its output with an HTML comment version marker: `<!-- skill-name v0.1 -->`. This tells downstream skills which format version they are reading.
- **When to increment the version:** New version when the output format adds, removes, or renames sections, or when value vocabulary changes. Same version when the analysis rubric improves but format and vocabulary stay the same.
- **Dual use.** The producing skill may also reference its own glossary during generation to ensure consistent field definitions and vocabulary.
- **Downstream referencing.** When skills live in the same repo, downstream skills reference the upstream glossary by relative path: `../[upstream-skill]/references/glossary.md`.
- **Writing guidelines.** Write for a model consuming the glossary at runtime. Ground definitions in behavior, not labels. Keep it compact. Every sentence should help a downstream skill make a concrete decision.

For the full glossary writing guide with templates, a worked example, and the shared vocabulary pattern, read `references/glossary-writing-guide.md`.

---

## Output Structure Template

When writing the SKILL.md in Phase 3, follow this structure:

```markdown
---
name: skill-name
description: >-
  Third-person description under 1024 characters. Describes what
  the skill produces, what input it accepts, and what the output
  is used for.
license: Apache-2.0
---

# Skill Title

[1-2 paragraph introduction: what it does, what the output is for,
 pointer to references/example-output.md]

## Conversation Flow

### Turn 1: [Welcome and collect]
### Turn 2+: [Follow-up / gap analysis]
### [Analysis / Calibration if needed]
### [Produce output]
### [Review and refine]

## [Analysis Rubric / Synthesis Instructions]
[How to evaluate input and produce each section of the output]

## Output Structure
[The exact heading hierarchy the skill produces]

## Important Behaviors
[Edit in place, produce as downloadable file, etc.]

## Edge Cases
[Thin input, inconsistent input, missing context, CSV-specific]

## Closing
[Tell the user what to do with the output: download, save, upload
 to future conversations, pair with other skills. Both production
 skills include this. Example: "Download this file. Whenever you
 need [task], upload it to a new conversation."]
```

Keep the body under 500 lines. If the skill needs more detail, move supporting information into reference files and point to them.

---

## SkillShelf Metadata

Every skill includes a `skillshelf.yaml` sidecar file. See `references/skillshelf-yaml-reference.md` for the complete field reference.

The most common decisions:

- **Category:** Choose from the 10 SkillShelf categories. Pick the one that best matches the ecommerce job function.
- **Level:** Based on user involvement, not skill complexity. Beginner: user just talks and gets output. Intermediate: user brings prepared input. Advanced: user works outside the chat window.
- **Primitive:** True only for foundational skills that produce reusable documents consumed by many downstream skills. Most skills are not primitives.

---

## Important Behaviors

- Produce skill files as downloadable documents, not inline chat text.
- When the user requests changes during review, edit the file in place. Do not regenerate the entire skill for a single correction.
- Use the brand's actual name in example output headings when the example uses a fictional brand. "How GreatOutdoors Co. Talks to the Customer," not "How [Brand] Talks to the Customer."
- Use forward slashes in all file paths within the skill, even on Windows.
- Keep file references one level deep from SKILL.md.

---

## Edge Cases

### User has a vague idea

If the user says something like "I want a skill for product content" without specifics, ask what specific task they do manually today that they want to automate. Ground the conversation in a real workflow, not an abstract category.

Produce what you can from their input. A rough skill is more useful than no skill.

### User wants to clone an existing skill

If the user says "I want something like the Brand Voice Extractor but for X," start from the design principles, not from the existing SKILL.md. The conventions are transferable; the specific instructions are not. A positioning skill and a product description skill share design patterns but differ in every detail.

### User's scope is too broad

If the skill idea covers multiple distinct workflows, flag it during Phase 1 and suggest splitting. "That's really three skills: one for extracting reviews, one for categorizing sentiment, and one for generating response templates. Which should we start with?"

### User brings a finished skill for review only

If the user already has a SKILL.md and wants a convention review, skip Phases 1-3 and go directly to Phase 4. Run the checklist, present results, offer fixes.

### User is not building for ecommerce

SkillShelf is an ecommerce skill catalog, but the SKILL.md format works for any domain. If the user's task is not ecommerce-related, proceed normally but note that the `skillshelf.yaml` categories are ecommerce-specific. Use `operations-and-process` as the closest fit for general-purpose tasks.

---
name: adapt-skill
description: >-
  Takes a prompt or skill you already use and converts it so other people
  can find and use it on SkillShelf.
license: Apache-2.0
metadata:
  category: operations-and-process
  level: intermediate
  platforms: platform-agnostic
  primitive: "false"
---

# Share a Skill You Already Have

You already have a prompt or skill that works. This skill converts it into the format SkillShelf uses, so other people can find it, download it, and use it with their own AI tools. Paste your prompt, upload a file, or upload a zip -- you get back a complete skill directory ready to share.

Before starting, read `../write-skill/references/conventions-checklist.md` so you have the full checklist available during review. Read `../write-skill/references/skillshelf-yaml-reference.md` for metadata field definitions. Read `references/example-adaptation.md` to see what a good adaptation looks like (before and after). When the converted skill needs calibration, read `../write-skill/references/calibration-pattern.md`. When producing a glossary, read `../write-skill/references/glossary-writing-guide.md`.

---

## Before You Start

The user arrives with an existing prompt or skill that already works. Your job is to convert it to SkillShelf format, not to redesign it from scratch. Respect what the user built. The existing logic, flow, and intent should carry through to the converted version.

That said, SkillShelf conventions exist for good reasons. If the source prompt has gaps (no edge case handling, no example output, rigid Q&A instead of accept-first input design), you fill those gaps during conversion. If the scope is too broad, flag it.

---

## Conversation Flow

Three phases, roughly four to five turns.

### Phase 1: Receive and Analyze

**Turn 1: Accept the source material.**

Tell the user:

> Paste your prompt or skill file, or upload it as a file. If your skill is a directory with multiple files (references, examples, etc.), upload it as a zip. I will also take any context you want to share about what the skill does, who it is for, or how you use it.

Accept whatever form the input takes:

- A system prompt pasted into the chat
- A single SKILL.md or markdown file uploaded
- A zip file containing a skill directory (from Claude projects, GitHub, or another tool)
- A combination of pasted content and uploaded files

If the user uploads a zip, parse its structure. Identify the main prompt or SKILL.md, any reference files, examples, and supporting documents. Note what exists and what is missing.

**Turn 2: Present the analysis.**

Silently analyze the source material against five dimensions:

1. **Task scope** -- what the skill does and does not do
2. **Target user** -- who runs it, what role, what they already know
3. **Input format** -- what the user provides (existing content, CSVs, conversational answers, URLs)
4. **Output format** -- what the skill produces and its heading structure
5. **Ecommerce context** -- what platform, product category, or business area it serves (if applicable)

Present a summary:

> Here is what I see this skill doing:
>
> - **Scope:** [one-sentence description]
> - **Input:** [what the user provides]
> - **Output:** [what the skill produces, including heading structure if visible]
> - **Target user:** [who uses this]
> - **What is already SkillShelf-ready:** [list what the source already has: clear scope, structured output, etc.]
> - **What needs to be added or changed:** [list gaps: missing frontmatter, no example output, rigid Q&A input, no edge cases, etc.]

If the scope is too broad (covers multiple distinct workflows), flag it and suggest splitting: "This covers [X] and [Y]. Those are two separate skills. Which should we convert first?"

Ask the user if the summary is accurate and whether they want to adjust anything before conversion.

### Phase 2: Convert

**Turn 3: Produce all files.**

Convert the source material into the complete set of SkillShelf files:

1. **SKILL.md** -- The skill file with proper YAML frontmatter and structured body.
2. **references/example-output.md** -- A complete example of what the skill produces, using a generic, category-obvious brand name.
3. **references/glossary.md** -- Only if the skill produces structured output that other skills would consume as input.
4. **skillshelf.yaml** -- The SkillShelf metadata sidecar.

#### Converting the SKILL.md

Map the source prompt's logic into SkillShelf structure:

- **Frontmatter:** Generate `name` (kebab-case, matches directory), `description` (third person, under 155 characters), `license: Apache-2.0`, and `metadata` block (category, level, platforms, primitive).
- **Title:** Verb + outcome. "Document Your Brand Voice" not "Brand Voice Extractor." Keep it short and something the target user would click on.
- **Introduction:** 1-2 paragraphs explaining what it does and pointing to the example output in references.
- **Conversation flow:** Map the source prompt's steps into labeled turns/phases. If the source is a single-turn prompt, structure it as a single-turn skill with clear input expectations and output format.
- **Analysis rubric / synthesis instructions:** Extract or formalize how the skill evaluates input and produces each output section. If the source prompt has implicit logic, make it explicit.
- **Output structure:** Define the exact heading hierarchy. If the source prompt already produces structured output, preserve those headings. If not, create stable, descriptive headings based on what the prompt produces.
- **Edge cases:** Add handling for thin input, inconsistent input, and missing context. If the source prompt already addresses some edge cases, keep them and fill gaps.
- **Closing:** Tell the user what to do with the output (download, save, upload to future conversations, pair with other skills).

#### What to preserve from the source

- The core logic and flow of the prompt
- Domain-specific knowledge and rubrics
- Output format and structure (unless it conflicts with SkillShelf conventions)
- Any calibration patterns already present
- Reference to specific data formats or platforms the prompt handles

#### What to add or change

- Frontmatter (always missing from raw prompts)
- Accept-first input pattern (if the source uses rigid Q&A, convert to accept-existing-content-first with Q&A as fallback)
- Edge case handling (if absent)
- Confidence notes pattern (if absent)
- Ecosystem awareness (recommend relevant primitives like the Brand Voice Extractor or Write a Positioning Brief skill, but never require them)
- Closing section with next steps
- Example output file (always needed)
- skillshelf.yaml (always needed)

#### Producing the example output

Create a complete example in `references/example-output.md` that demonstrates the skill's output at ceiling quality. Use a generic, category-obvious brand name: "GreatOutdoors Co." for outdoor gear, "GoodBoy Treats" for pet products, "BeanThere Coffee" for coffee. The example must cover all output sections defined in the skill.

#### Producing the skillshelf.yaml

Use `../write-skill/references/skillshelf-yaml-reference.md` for valid field values. Key decisions:

- **Category:** Choose from the 10 SkillShelf categories. If the skill is not ecommerce-specific, use `operations-and-process`.
- **Level:** Based on user involvement. Beginner: user talks and gets output. Intermediate: user brings prepared input. Advanced: user works outside the chat window.
- **Primitive:** True only for foundational skills producing reusable documents consumed by many downstream skills. Most skills are not primitives.
- **FAQ:** Write 3-4 questions and answers about the skill. The first FAQ should be "What does the [Skill Title] skill do?" with a plain-language answer.

After producing the files, tell the user: "Start with the SKILL.md. Read it as if you were the AI following these instructions. Does anything feel unclear, too vague, or too rigid? Then check the example output -- it sets the quality ceiling for what this skill produces."

### Phase 3: Review Against Conventions

**Turn 4+: Run the checklist.**

Read `../write-skill/references/conventions-checklist.md` and check the converted files against every item. Present the results to the user, grouped by concern. For any failing item, explain what needs to change and offer to fix it.

When the user requests changes, edit the documents in place. Do not regenerate the entire skill from scratch for a single correction.

If review has gone several rounds, suggest trying the skill with real input. Seeing actual output often clarifies what needs changing better than editing instructions in the abstract.

Once the user is happy with the skill, mention: "If you think other people would find this skill useful, you can add it to the SkillShelf library at skillshelf.ai/submit."

---

## Key Conventions

These are the SkillShelf quality standards. Apply them during conversion (Phase 2) and review (Phase 3).

### One thing well

A skill does one thing. If the source prompt covers multiple distinct workflows, flag it during Phase 1 and suggest splitting. Convert one skill at a time.

### Input design

The default input pattern: accept existing content first, offer guided prompts as fallback, ask targeted follow-ups only for gaps. If the source prompt uses rigid Q&A ("Answer these 10 questions"), convert it to accept-first. The user may already have the answers in a document they can paste.

Never refuse output due to imperfect input. Nudge once for additional input, then move forward.

### Output design

Consistent Markdown headings that are stable and descriptive. Output must be copy-paste ready. Include a Confidence notes section when working from limited input. Every claim specific to the brand/product/data, not generic.

### Calibration

Include only when interpretation varies (voice, tone, creative direction). Skip when output is data-determined or when the skill receives a calibrated artifact as input. When calibrating, present 2-3 variations labeled neutrally (A, B, C).

### Examples

Every skill needs an example output file in `references/` with the `example-` prefix. Generic, category-obvious brand names. Ceiling quality. Covers all output sections.

### Edge cases

Every skill must handle thin input, inconsistent input, and missing context. Produce output and note what would improve it. Never refuse.

---

## Important Behaviors

- Produce skill files as downloadable documents, not inline chat text.
- When the user requests changes during review, edit the file in place.
- Respect the source prompt's logic. You are converting format and filling gaps, not redesigning the skill.
- Use forward slashes in all file paths within the skill, even on Windows.
- Keep file references one level deep from SKILL.md.
- If the source prompt has domain-specific knowledge or rubrics, preserve them faithfully. Do not dilute expertise during conversion.

---

## Edge Cases

### Source is a single-turn prompt

If the source is a concise system prompt with no multi-turn flow, convert it as a single-turn skill. Set `interaction_pattern: single-turn` in skillshelf.yaml. The SKILL.md still needs all sections (introduction, output structure, edge cases, closing) but the conversation flow section describes a single exchange.

### Source has no clear output structure

If the source prompt produces unstructured or free-form output, analyze what it actually generates and impose a heading structure. Present the proposed structure to the user during Phase 1 analysis for confirmation.

### Source is already close to SkillShelf format

If the source is a SKILL.md or structured markdown that mostly follows conventions, focus on the gaps. Do not rewrite sections that are already convention-compliant. Present a targeted list of what needs changing rather than a full rewrite.

### Source scope is too broad

If the source prompt covers multiple workflows ("write product descriptions AND audit the page AND generate SEO tags"), flag it during Phase 1. Suggest splitting into separate skills. Convert one at a time.

### Source references real brand names

If the source prompt or its examples use real brand names, replace them with generic, category-obvious fictional names in the example output file. The SKILL.md instructions may reference real brands for illustrative purposes, but example output files must use fictional brands only.

### Source is not ecommerce

SkillShelf categories are ecommerce-specific, but the SKILL.md format works for any domain. Use `operations-and-process` as the closest fit for general-purpose tasks. Note this in the skillshelf.yaml FAQ.

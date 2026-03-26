---
name: adapt-skill
description: >-
  Takes a prompt or skill you already use and converts it so other people
  can find and use it on SkillShelf.
license: Apache-2.0
---

# Share a Skill You Already Have

You already have a prompt or skill that works. This skill converts it into the format SkillShelf uses, so other people can find it, download it, and use it with their own AI tools. Paste your prompt, upload a file, or upload a zip -- you get back a complete skill directory ready to share.

Before starting, read `references/conventions-checklist.md` and `references/example-adaptation.md`. The other reference files are specialized -- read `references/calibration-pattern.md` only if the source skill needs a calibration step, and `references/glossary-writing-guide.md` only if the converted skill produces output consumed by other skills. Do not read them upfront.

---

## Voice and Approach

You are a skill-conversion assistant helping the user turn a prompt or workflow they already have into a shareable SkillShelf skill. Be direct and conversational. Use plain language. Don't narrate your internal process or over-explain concepts. However, always explain what the user is about to see and why it matters before asking them to review it. The user cannot give useful feedback on something they don't understand the purpose of. When transitioning between steps, keep it brief and natural. The user may or may not be technical -- take cues from how they talk and match their level. This should be an enjoyable process for the user, not a frustrating one.

When writing instructions in the converted skill, describe the intent and information to convey rather than writing verbatim scripts. Instead of "Tell the user: 'Here is your output...'" write "Let the user know what the output contains and how to use it." The AI running the skill should sound natural, not like it's reading from a teleprompter.

---

## Conversation Flow

Three phases. Most conversions take around four to five turns, but it's fine to run longer if the source needs more clarification or review goes a few rounds.

### Phase 1: Receive and Analyze

**Turn 1: Accept the source material.**

Let the user know you accept prompts, skill files, or zips -- whatever form their existing work is in. Also welcome any context about what the skill does, who it's for, or how they use it.

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

Present a summary covering: scope, input, output, target user, what's already SkillShelf-ready, and what needs to be added or changed.

If the scope is too broad (covers multiple distinct workflows), flag it and explain why splitting is better: the more an LLM is trying to keep track of in a single skill, the more likely it is to make mistakes. Focused skills produce better output. Mention that SkillShelf supports workflows called playbooks that chain multiple skills together, so splitting doesn't mean losing the end-to-end workflow. Then suggest a concrete split -- name the distinct skills and what each one does.

Ask the user if the summary is accurate and whether they want to adjust anything before conversion.

### Phase 2: Convert

**Turn 3: Produce the SKILL.md.**

Let the user know you're converting their prompt into a skill file -- explain that this is the core document everything else builds around, and that you'll share it for review before moving on.

Map the source prompt's logic into SkillShelf structure:

- **Frontmatter:** Generate `name` (kebab-case, matches directory), `description` (third person, under 155 characters), `license: Apache-2.0`.
- **Title:** Verb + outcome. "Document Your Brand Voice" not "Brand Voice Extractor." Keep it short and something the target user would click on.
- **Introduction:** 1-2 paragraphs explaining what it does and pointing to the example output in references.
- **Conversation flow:** Map the source prompt's steps into labeled turns/phases. If the source is a single-turn prompt, structure it as a single-turn skill with clear input expectations and output format.
- **Analysis rubric / synthesis instructions:** Extract or formalize how the skill evaluates input and produces each output section. If the source prompt has implicit logic, make it explicit.
- **Output structure:** Define the exact heading hierarchy. If the source prompt already produces structured output, preserve those headings. If not, create stable, descriptive headings based on what the prompt produces.
- **Edge cases:** Add handling for thin input, inconsistent input, and missing context. If the source prompt already addresses some edge cases, keep them and fill gaps.

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
- Example output file (always needed)
- skillshelf.yaml (always needed)

After sharing the skill file, ask the user to review it. Suggest they read it from the perspective of an AI following the instructions, and flag anything unclear, too vague, or too rigid.

**Stop here and wait for the user.** Do not proceed to supporting files until the user is happy with the SKILL.md.

**Turn 4+: Produce supporting files.**

Once the SKILL.md is approved, let the user know there are a few more files to produce: an example showing what the skill's output looks like at its best, and a metadata file for SkillShelf if they want to share it.

To build the example, ask the user whether they'd like to provide their own input data, or use the fictional brand data from SkillShelf. If they choose the SkillShelf path, fetch data from https://github.com/timctfl/skillshelf/tree/main/fixtures/greatoutdoorsco and use Great Outdoors Co. as the example brand. Do not call it "fixture data" when talking to the user -- that is an internal repo term they will not understand. Call it "sample brand data" or "fictional brand data."

Produce:

1. **references/example-output.md** -- A complete example of what the skill produces when run with good input. This sets the quality ceiling.
2. **skillshelf.yaml** -- The SkillShelf metadata file. Read `references/skillshelf-yaml-reference.md` for valid field values.
3. **references/glossary.md** -- Only if the skill produces structured output that other skills consume as input. Most skills do not need this. If yours does, read `references/glossary-writing-guide.md` for the full specification.

After sharing the example output, ask the user to review it. Explain that this example is what the AI will aim for when the skill runs, so the quality, tone, and level of detail should match what they'd actually want to use.

**Stop here and wait for the user.** The example sets the bar for the skill's output quality, so it needs to match what the user would actually want to use.

### Phase 3: Quality Control

Let the user know you're going to run through a checklist of common issues. Frame it as quick and routine -- something that ensures the skill works reliably, not a formal review process.

Read `references/conventions-checklist.md` and check all produced files against it silently. Fix any issues you can without user input (formatting, naming, structural compliance). Only surface issues that require the user's judgment -- scope questions, calibration decisions, or ambiguities you can't resolve on your own.

When the user requests further changes, edit the documents in place. Do not regenerate the entire skill from scratch for a single correction.

Once everything passes, package the final files as a zip and present it to the user. Mention: "If you think other people would find this skill useful, you can add it to the SkillShelf library at skillshelf.ai/submit."

---

## Writing the Converted Skill

Use plain, direct language. Ecommerce-specific terms are fine when appropriate. Do not use em dashes (use double hyphens `--` instead). Write in a neutral business tone.

Respect the source prompt's logic. You are converting format and filling gaps, not redesigning the skill. If the source prompt has domain-specific knowledge or rubrics, preserve them faithfully. Do not dilute expertise during conversion.

### Output principles

Every claim, differentiator, or recommendation must be specific to the user's brand, product, or data. Generic statements that could apply to any brand in the category are not useful.

When a skill works from limited input, include a "Confidence notes" section that flags which parts are based on limited evidence and what additional input would strengthen them. Do not pad thin input into confident-sounding output.

Output must be ready to paste into a CMS, upload to a platform, or hand to a team member without further editing or reformatting.

### Example files

Every skill includes an example output file in `references/`. The file must use the `example-` prefix (e.g., `example-output.md`). The SkillShelf website uses this prefix to find and display example files. A file named `sample-output.md` or `output-example.md` will not appear on the site.

The example demonstrates the ceiling, not the floor. If the example is mediocre, the LLM will calibrate to mediocre output.

### General behaviors

- Produce skill files as downloadable documents, not inline chat text.
- When the user requests changes, edit the file in place. Do not regenerate the entire skill from scratch for a single correction.
- Use forward slashes in all file paths within the skill.
- Keep file references one level deep from SKILL.md.

---

## Edge Cases

### Source is a single-turn prompt

If the source is a concise system prompt with no multi-turn flow, convert it as a single-turn skill. The SKILL.md still needs all sections (introduction, output structure, edge cases, closing) but the conversation flow section describes a single exchange.

### Source has no clear output structure

If the source prompt produces unstructured or free-form output, analyze what it actually generates and impose a heading structure. Present the proposed structure to the user during Phase 1 analysis for confirmation.

### Source is already close to SkillShelf format

If the source is a SKILL.md or structured markdown that mostly follows conventions, focus on the gaps. Do not rewrite sections that are already convention-compliant. Present a targeted list of what needs changing rather than a full rewrite.

### Source references real brand names

If the source prompt or its examples use real brand names, replace them with generic, category-obvious fictional names in the example output file. The SKILL.md instructions may reference real brands for illustrative purposes, but example output files must use fictional brands only.

### Source is not ecommerce

SkillShelf categories are ecommerce-specific, but the SKILL.md format works for any domain. Use `operations-and-process` as the closest fit for general-purpose tasks. Note this in the skillshelf.yaml FAQ.

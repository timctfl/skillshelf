---
name: write-skill
description: >-
  Walks you through creating a complete, convention-compliant AI skill for ecommerce.
  Produces a SKILL.md, example output, and all supporting files ready to use.
license: Apache-2.0
---

# Build a New Skill

This skill helps users go from "I have an idea for a skill" to a complete, convention-compliant skill directory. It walks through understanding the task, designing the skill, writing and reviewing the SKILL.md, then producing the supporting files.

Before starting, read `references/conventions-checklist.md` and `references/example-output.md`. The other reference files are specialized -- read `references/calibration-pattern.md` only if the Phase 2 design includes a calibration step, and `references/glossary-writing-guide.md` only if the design calls for downstream consumption. Do not read them upfront.

---

## Conversation Flow

Four phases. Most skills take around six turns, but it's fine to run longer if the idea needs more clarification or review goes a few rounds. Phases 1 and 2 are understanding and design. Phase 3 is writing. Phase 4 is review.

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

Don't over-question the user. Ask questions to clarify until the key gaps are filled, but this shouldn't feel like an interrogation. These five requirements are what you're listening for; the Phase 2 design summary is what you're building toward. If you have enough information to produce those six design items (scope statement, input pattern, output structure, calibration decision, edge cases, conversation flow), stop asking and move to Phase 2. If the task scope and output format are clear, that is often enough to proceed.

If the user's scope is too broad (e.g., "a skill that handles all our product content"), flag it and explain why splitting is better: the more an LLM is trying to keep track of in a single skill, the more likely it is to make mistakes. Focused skills produce better output. Mention that SkillShelf supports workflows called playbooks that chain multiple skills together, so splitting doesn't mean losing the end-to-end workflow. Then suggest a concrete split -- name the distinct skills and what each one does.

### Phase 2: Design the Skill

**Turn 3: Present the skill design.**

Silently analyze the user's input and produce a structured design summary. Present it as a numbered list:

1. **Scope statement.** One paragraph. What this skill does and does not do.
2. **Input pattern.** Does the skill accept existing content first with Q&A as a fallback (the default for most skills)? Does it accept CSV exports? From which platforms?
3. **Output structure.** The heading hierarchy of the output document. List every heading. Headings must be stable and descriptive.
4. **Calibration decision.** Does this skill need a calibration step where the user chooses between 2-3 variations? Only when the same input legitimately supports multiple good outputs (voice, tone, positioning, creative direction). If yes, read `references/calibration-pattern.md`.
5. **Edge cases.** What happens with thin input, inconsistent input, missing context.
6. **Conversation flow.** How many turns. What happens in each.

Tell the user: "Review this design. If anything is off, tell me what to change. Once the design is right, I'll create the full skill file."

This is the validation gate. Do not proceed to writing until the user confirms the design or provides feedback.

**Turn 4: Incorporate feedback.**

If the user requests changes, update the design and confirm. If the design is approved, move to Phase 3.

### Phase 3: Write the Skill

**Turn 5: Produce the SKILL.md.**

Tell the user: "I'm going to write the skill file now. This is the core document -- think of it as a playbook that tells the AI what to do, in what order, and what good output looks like. Everything else gets built around it. I'll share it with you to review before we move on."

Write the complete SKILL.md with YAML frontmatter and body. Present it to the user and say: "Read this as if you were the AI following these instructions. Does anything feel unclear, too vague, or too rigid?"

This is the second validation gate. Do not proceed to supporting files until the user is happy with the SKILL.md.

**Turn 6+: Produce supporting files.**

Once the SKILL.md is approved, explain to the user that the full skill package includes a few more pieces: an example output file that shows the AI what great results look like (this sets the quality ceiling), and some metadata that helps SkillShelf categorize and display the skill if they choose to share it with other ecommerce practitioners.

To build the example, ask the user whether they'd like to provide their own input data, or use the fictional Great Outdoors Co. data from SkillShelf. If they choose the SkillShelf path, fetch data from https://github.com/timctfl/skillshelf/tree/main/fixtures/greatoutdoorsco and use Great Outdoors Co. as the example brand.

Produce:

1. **references/example-output.md** -- A complete example of what the skill produces when run with good input. This sets the quality ceiling.
2. **skillshelf.yaml** -- The SkillShelf metadata sidecar. Read `references/skillshelf-yaml-reference.md` for valid field values.
3. **references/glossary.md** -- Only if the skill produces structured output that other skills consume as input. Most skills do not need this. If yours does, read `references/glossary-writing-guide.md` for the full specification.

Present the example output to the user and say: "This example sets the quality ceiling for your skill -- it's what the AI will calibrate toward. Does the quality, tone, and level of detail feel right? Anything you'd want to change?"

This is the third validation gate. Do not proceed to quality control until the user is happy with the example.

### Phase 4: Quality Control

Tell the user: "Now I'm going to run a quality control check against the SkillShelf conventions. These are a set of standards that help make sure skills work consistently and produce reliable output. I'll fix everything I can on my own, but I might ask for some clarifications."

Read `references/conventions-checklist.md` and check all produced files against it silently. Fix any issues you can without user input (formatting, naming, structural compliance). Only surface issues that require the user's judgment -- scope questions, calibration decisions, or ambiguities you can't resolve on your own.

When the user requests further changes, edit the documents in place. Do not regenerate the entire skill from scratch for a single correction.

If review has gone several rounds, suggest trying the skill with real input. Tell the user that the [SkillShelf fixtures](https://github.com/timctfl/skillshelf/tree/main/fixtures) have sample ecommerce data (Shopify exports, PDPs, reviews, brand content) with intentional messiness -- they can start a new conversation, paste the SKILL.md and a fixture file, and see how the skill handles real-world input. Seeing actual output often clarifies what needs changing better than editing instructions in the abstract.

Once everything passes, package the final files as a zip and present it to the user. Mention: "If you think other people would find this skill useful, you can add it to the SkillShelf library at skillshelf.ai/submit."

---

## Writing the Skill

Use plain, direct language. Ecommerce-specific terms are fine when appropriate. Do not use em dashes (use double hyphens `--` instead). Write in a neutral business tone.

When writing the SKILL.md in Phase 3, follow this structure:

```markdown
---
name: skill-name
description: >-
  Third-person description under 155 characters. A concise
  summary of what the skill produces and what it is used for.
license: Apache-2.0
---

# Skill Title (verb + outcome, e.g., "Document Your Brand Voice")

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

## Edge Cases
[Thin input, inconsistent input, missing context, CSV-specific]

## Closing
[Tell the user what to do with the output: download, save, upload
 to future conversations, pair with other skills. Example: "Download
 this file. Whenever you need [task], upload it to a new conversation."]
```

Keep the body under 500 lines. If the skill needs more detail, move supporting information into reference files and point to them.

### Input principles

The default input pattern: accept existing content first (About Us pages, product CSVs, existing descriptions, competitor examples), offer guided prompts as a fallback, and fill gaps with targeted follow-up questions.

When a skill accepts CSV input, be explicit about which columns it needs and handle common variations in column naming. Different platforms export data differently -- the skill should specify what it needs and be flexible about where it comes from. If the skill accepts data from a platform you're not certain of the file format, look up the export format before writing the skill.

Never refuse to produce output because the input isn't ideal. Produce the best output possible from what's provided, note what's missing, and suggest what would improve it.

### Output principles

Every claim, differentiator, or recommendation must be specific to the user's brand, product, or data. Generic statements that could apply to any brand in the category are not useful.

When a skill works from limited input, include a "Confidence notes" section that flags which parts are based on limited evidence and what additional input would strengthen them. Do not pad thin input into confident-sounding output.

Output must be ready to paste into a CMS, upload to a platform, or hand to a team member without further editing or reformatting.

### Example files

Every skill includes an example output file in `references/`. The file must use the `example-` prefix (e.g., `example-output.md`). The SkillShelf website uses this prefix to find and display example files. A file named `sample-output.md` or `output-example.md` will not appear on the site.

Use generic, category-obvious brand names. The name should make the product category immediately clear. "GreatOutdoors Co." (outdoor gear), "GoodBoy Treats" (pet products), "BeanThere Coffee" (coffee). Avoid names that sound like real brands or don't signal the category: "Ridgeline Supply Co.", "Duskbloom", "Apex Provisions."

The example demonstrates the ceiling, not the floor. If the example is mediocre, the LLM will calibrate to mediocre output.

### General behaviors

- Produce skill files as downloadable documents, not inline chat text.
- When the user requests changes, edit the file in place. Do not regenerate the entire skill from scratch for a single correction.
- Use forward slashes in all file paths within the skill.
- Keep file references one level deep from SKILL.md.

---

## Edge Cases

### User has a vague idea

If the user says something like "I want a skill for product content" without specifics, ask what specific task they do manually today that they want to automate. Ground the conversation in a real workflow, not an abstract category.

Produce what you can from their input. A rough skill is more useful than no skill.

### User wants to clone an existing skill

If the user says "I want something like the Brand Voice Extractor but for X," start from the design principles, not from the existing SKILL.md. The conventions are transferable; the specific instructions are not.

### User brings a finished skill for review only

If the user already has a SKILL.md and wants a convention review, skip Phases 1-3 and go directly to Phase 4. Run the checklist and fix what you can.

### User is not building for ecommerce

SkillShelf is an ecommerce skill catalog, but the SKILL.md format works for any domain. If the user's task is not ecommerce-related, proceed normally but note that the `skillshelf.yaml` categories are ecommerce-specific. Use `operations-and-process` as the closest fit for general-purpose tasks.

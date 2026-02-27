# SkillShelf Glossary Specification

## What Glossaries Are

A glossary is a companion document that ships alongside a skill's output format. It tells any downstream skill how to interpret the fields, values, and structure of that output.

When the Brand Voice Extractor produces a voice profile, the profile itself is human-readable. A merchandiser can scan it and understand their brand's writing patterns. But when the PDP Copy Writer skill receives that same document as input, it needs to know exactly what "Sparingly" means in the exclamation marks row, what to do if the Persuasion Arc section is missing, and how to handle a document the user wrote themselves instead of generating through the extractor.

The glossary carries that context. The upstream document stays clean for humans. The downstream skill gets what it needs to use the document correctly.

## Why They Exist

Style decisions and structured fields are inherently ambiguous in natural language. "Sparingly" means something different to every reader, whether that reader is a copywriter or an AI model. Without a shared definition, every consumer of the document interprets it differently, and output is inconsistent across skills.

We considered embedding interpretation instructions in the output document itself. Two problems: it clutters a document designed for humans with machine-only content, and it creates a maintenance burden where every existing document needs regeneration whenever interpretation logic improves.

Glossaries solve both. The document stays human-first. The interpretation logic is versioned and updatable independently of any document already generated.

## How Versions Work

Every skill that produces structured output stamps its documents with a version marker:

```
<!-- brand-voice-extractor v0.1 -->
```

This marker is an HTML comment, invisible when rendered but present in the raw file. It tells any downstream skill which version of the output format it's looking at.

There is one glossary file per skill, always reflecting the current version. It includes a changelog at the bottom documenting what changed in each version. When a downstream skill encounters an older document, it checks the changelog to understand what differences to expect.

**When to increment the version:**
- The output format adds, removes, or renames sections: new version.
- The value vocabulary changes (new options, redefined terms): new version.
- The analysis rubric improves but format and vocabulary stay the same: same version. The glossary doesn't change; the skill just makes better decisions within the existing structure.

## Where Glossaries Live

Glossaries live inside the skill that produces the output, at `references/glossary.md`:

```
brand-voice-extractor/
├── SKILL.md
└── references/
    ├── example-output.md
    └── glossary.md
```

There is one glossary file. It always reflects the current version. Previous versions are documented in the changelog section, not in separate files.

**Downstream skills reference the glossary by path.** When all skills live in the same repo, a downstream skill's SKILL.md points to the upstream glossary directly:

```
Before generating output, read the brand voice glossary at
../brand-voice-extractor/references/glossary.md
```

This means the upstream skill updates the glossary once and every downstream skill gets the update automatically. No copies, no syncing.

The producing skill may also reference its own glossary during generation to ensure consistent field definitions and vocabulary. This dual use is intentional: the glossary defines what valid values look like and what each field means, which the producer needs just as much as the consumer.

For third-party skills built outside the SkillShelf repo, authors should include a copy of the glossary in their own `references/` folder and update it when the upstream version changes.

---

## Glossary Template

Every glossary must include the following sections in this order.

---

### Section 1: Overview

```markdown
## Overview

One of the inputs for this skill is a [document type], produced by the
[Producing Skill Name]. This glossary explains how that document is
structured: what each section contains, what values to expect, and how
to interpret them.

**Producing skill:** [Skill Name]
**Current version:** v[X.X]
**Document type:** [What the output is called]
**Purpose:** [One sentence]
**Consumers:** [What kinds of skills use this document as input]
```

---

### Section 2: Document Structure

List every section of the output document in order. One row per section. One sentence per description. Do not omit sections.

```markdown
## Document Structure

| Section | Description |
|---|---|
| [Section Name] | [One sentence] |
```

---

### Section 3: Section Hierarchy

Define which sections take priority when guidance overlaps. Numbered list, highest to lowest. Every section must appear.

```markdown
## Section Hierarchy

When multiple sections provide guidance that applies to the same output:

1. [Section Name] — [Why this takes priority]
2. [Section Name] — [Why]
```

---

### Section 4: Handling Missing or Unexpected Input

Define exact behavior for each scenario. All four must be addressed.

```markdown
## Handling Missing or Unexpected Input

**A section says "unable to determine" or equivalent:**
[What does the downstream skill do? What does it tell the user?]

**An expected section is missing entirely:**
[Specific instruction.]

**The version marker is older than the current glossary version:**
[How to use the changelog to handle differences.]

**The document was not generated by this skill:**
[How to handle a user-created document that doesn't follow the
expected structure, may be missing sections, or has no version marker.
The downstream skill should still produce useful output.]
```

---

### Section 5: Field Definitions

One entry for every section and field. Do not skip fields.

**For narrative sections:**

```markdown
### [Section Name]

**What it represents:** [What this section captures.]
**What to expect:** [Structure, length, examples.]
**How to apply:** [How a downstream skill should use it.]
```

**For table fields that share a common vocabulary:**

Define shared values once, then reference them per field.

```markdown
### Shared Vocabulary

| Value | Definition |
|---|---|
| [Value] | [Observable, measurable definition] |
```

Then a compact reference table:

```markdown
### [Table Name]: Field Reference

| Field | What it represents | Possible values | Notes |
|---|---|---|---|
| [Field] | [Description] | Shared vocabulary / field-specific | [Only if unique interpretation needed] |
```

**For fields with free-text or unique values:**

```markdown
### [Field Name]

**What it represents:** [Description.]
**Possible values:** [Patterns to expect.]
**How to apply:** [Specific guidance.]
```

---

### Section 6: Changelog

Document what changed in each version, newest first. Include enough detail that a downstream skill encountering an older document can understand the differences.

```markdown
## Changelog

**v[X.X]** — [What changed: sections added/removed/renamed,
vocabulary changes, structural changes. If a value was redefined,
include both old and new definitions.]

**v[X.X]** — Initial release.
```

---

## Writing Guidelines

- Write for a model consuming the glossary at runtime.
- Define vocabulary with observable, measurable criteria.
- Do not repeat the producing skill's generation instructions. Describe the output, not how it was created.
- Ground definitions in behavior: "no more than once per piece of output" over "use conservatively."
- If a field's meaning varies by downstream context, say so and describe what the downstream skill must decide.
- Keep it compact. Every sentence should help a downstream skill make a concrete decision.

---

## Example: Brand Voice Extractor Glossary

## Overview

One of the inputs for this skill is a brand voice profile, produced by the Brand Voice Extractor. This glossary explains how that document is structured: what each section contains, what values to expect, and how to interpret them.

**Producing skill:** Brand Voice Extractor
**Current version:** v0.1
**Document type:** Brand voice profile
**Purpose:** Captures how a brand writes so downstream skills can produce on-brand copy.
**Consumers:** Any skill that generates written content (PDP copy, landing pages, emails, social posts, ad copy, SMS).

## Document Structure

| Section | Description |
|---|---|
| Voice Summary | 2-3 sentence overview of the brand's overall writing character. |
| Headlines | How the brand constructs headlines, with examples from source material. |
| Product Framing | The order in which the brand presents emotion/benefit vs. technical specs. |
| How [Brand] Talks to the Customer | Pronoun usage, assumed relationship with reader, mode of address. |
| Persuasion Arc | The typical structural sequence of longer-form copy. |
| What [Brand] Avoids | Things the brand does not do in its writing. |
| Style Decisions | A table of binary or near-binary writing mechanics rules. |
| Example Copy | Five pieces of generated copy demonstrating the voice profile in action. |

## Section Hierarchy

When multiple sections provide guidance that applies to the same output:

1. What [Brand] Avoids — Hard constraints. Never violate an avoidance rule.
2. Style Decisions — Specific, binary rules. Override narrative guidance when they conflict.
3. Headlines / Product Framing / How [Brand] Talks to the Customer / Persuasion Arc — Context, patterns, and nuance. Inform decisions within the constraints above.
4. Voice Summary — Directional. If a specific section contradicts it, follow the specific section.
5. Example Copy — Illustrative. Reference for tone and feel, not binding.

## Handling Missing or Unexpected Input

**A section says "unable to determine" or equivalent:**
Do not invent guidance for that area. Fall back to general best practices for the content type you are producing. Note to the user: "The brand voice profile did not specify [area]. I used standard practices for [content type]. You may want to update your voice profile to cover this."

**An expected section is missing entirely:**
Treat the same as "unable to determine."

**The version marker is older than the current glossary version:**
Check the changelog below. Apply the current glossary's definitions, but account for any structural differences noted for that version. If the older version used a different section name or lacked a field that now exists, adapt accordingly rather than failing.

**The document was not generated by this skill:**
The user may have written their own brand voice summary, pasted notes from an existing style guide, or provided an informal description. Do not reject the document or warn about format. Extract whatever guidance is present, map it to the fields you understand as best you can, and produce output. Where the document doesn't cover something, fall back to general best practices. The goal is to always produce useful, brand-informed output regardless of how the input was created.

## Field Definitions

### Voice Summary

**What it represents:** The overall character of the brand's writing. Not adjectives, but what the brand does when it writes.
**What to expect:** 2-3 sentences. May reference specific patterns or reader assumptions.
**How to apply:** Read first to calibrate overall approach. If any specific section contradicts the summary, follow the specific section.

### Headlines

**What it represents:** Structural patterns in headlines: length, fragments vs. sentences, what they lead with, case usage.
**What to expect:** 1-2 paragraphs with 2-3 real examples from source material.
**How to apply:** Match the structural pattern when generating any headline, title, or subject line. Use examples as templates for rhythm and length, not content to repeat.

### Product Framing

**What it represents:** The sequencing of emotion/benefit vs. technical specs. What comes first at the sentence, paragraph, and page level.
**What to expect:** 1-2 paragraphs, often with an example showing the order.
**How to apply:** Follow the described order strictly at every level.

### How [Brand] Talks to the Customer

**What it represents:** How the brand addresses the reader: pronoun usage, mode of address, assumed experience level, tone.
**What to expect:** 1-2 paragraphs with 1-2 examples from source material.
**How to apply:** Match the described mode exactly. This is one of the highest-impact sections. Getting this wrong makes copy feel like it was written outside the brand.

### Persuasion Arc

**What it represents:** The typical structural sequence of longer-form copy.
**What to expect:** A numbered list of content blocks in sequence, possibly with CTA notes.
**How to apply:** Follow the described sequence for content longer than a few sentences. Do not rearrange. If missing, use a standard arc for your content type.

### What [Brand] Avoids

**What it represents:** Things the brand does not do: language, claims, tones, topics.
**What to expect:** A paragraph listing avoidance patterns.
**How to apply:** Treat every item as a hard constraint. These override all other guidance. When in doubt, leave it out.

### Example Copy

**What it represents:** Five generated examples demonstrating the voice in action. Not from source material.
**What to expect:** Product headline, short product description, email subject + preview, landing page hero block, social caption.
**How to apply:** Use as tone and style reference. If your output feels significantly different, something is off. Do not copy content from the examples.

### Style Decisions: Shared Vocabulary

Most fields in the Style Decisions table use a common set of frequency and scope values:

| Value | Definition |
|---|---|
| "Always" or "Yes, always" | Apply in every instance, no exceptions. |
| "Never" or "No, never" | Zero instances in any output, any context. |
| "Freely" | Use where the content naturally calls for it, no restriction. |
| "Sparingly" or "Rarely" | Maximum of one instance per complete piece of output. |
| "Sparingly, [context]" or "Rarely, only in [context]" | Maximum one instance, only in the specified context. Zero outside it. |
| "Only in [context]" | Permitted in the specified context. Zero outside it. |
| "Yes, except in [context]" | Apply everywhere except the specified context. |

### Style Decisions: Field Reference

| Field | What it represents | Possible values | Notes |
|---|---|---|---|
| Contractions | Whether the brand uses contractions | Shared vocabulary | Absolute. "Yes, always" means every "do not" becomes "don't." |
| Exclamation marks | Frequency and context of exclamation marks | Shared vocabulary | "Sparingly" = max one per complete piece of copy. |
| Emojis | Whether and where emojis appear | Shared vocabulary | When permitted, use sparingly unless source material shows heavy usage. |
| Oxford comma | Comma before "and" in lists of 3+ | "Yes" / "No" | Apply consistently, no exceptions. |
| Headline case | Capitalization style for headlines | "Title case" / "Sentence case" / "All caps" / "Lowercase" / combination | Apply to every headline, title, subject line. If a style is excluded, never use it. |
| Price references | Whether copy mentions pricing | Shared vocabulary | When restricted, also avoid "affordable," "value," "worth every penny." |
| Competitor mentions | Whether the brand references competitors | "Never" / "Only in [context]" / "Indirect comparisons only" | "Never" covers language that makes a competitor obvious without naming them. |
| Superlatives | Whether the brand uses "best," "most," "#1" | Shared vocabulary | When restricted, also avoid "unmatched," "unparalleled," "unrivaled." |
| Urgency language | Scarcity or time-pressure language | Shared vocabulary | "Only for [context]" = do not use unless you know the condition is met. |
| Technical specs | How the brand handles product specs | "Always paired with benefit" / "Stand alone" / "Avoided" / "Secondary to [something]" | "Paired with benefit" = never list a spec without what it does for the customer. |
| Customer address | How the brand addresses the reader | Free text (see below) | Highest-impact style decision. Match exactly. |
| Sentence length | Typical sentence length | "Short" / "Medium" / "Long" / "Varied" / specific guidance | Word counts are strong guidelines, not absolutes. |
| Paragraph length | Sentences per paragraph | Count range (e.g., "1-2 sentences") | Body copy only. Headlines, CTAs, list items are not paragraphs. |
| Humor | Whether, how, and where humor is used | Shared vocabulary, with type (e.g., "Rarely, dry") | Match specified type. Do not use humor types not mentioned. |
| Punctuation as style | Punctuation as deliberate stylistic choice | Free text (see below) | Replicate described patterns. If avoidance is noted, do not use that punctuation. |
| Primary CTAs | Brand's go-to CTA phrases | List of phrases | Select from list. If deviating, match tone and directness of listed CTAs. |

### Free-Text Fields

**Customer Address:** Describes pronoun and mode of address. Common patterns: second person ("you") with frequency guidance, imperative mood ("Run."), aspirational ("for runners who..."), identity-based ("you're not a treadmill person"), or combinations. Match exactly. The downstream skill determines what constitutes "emphasis" or "sparingly" in its specific content type.

**Punctuation as Style:** Describes habits beyond grammar, e.g., "periods on fragments for emphasis," "never uses em dashes." Replicate described patterns. If avoidance is noted, do not use that punctuation in any output.

## Changelog

**v0.1** — Initial release.

# SkillShelf Conventions Checklist

Use this checklist during Phase 4 to review a skill against SkillShelf standards. Every item is a yes/no check.

---

## Format Compliance

- [ ] `name` is kebab-case (lowercase letters, digits, hyphens only)
- [ ] `name` is 1-64 characters
- [ ] `name` matches the parent directory name exactly
- [ ] `description` is written in third person ("Produces..." not "I help you...")
- [ ] `description` is 1-1024 characters
- [ ] `description` does not contain angle brackets (< or >)
- [ ] `license` is present (Apache-2.0 for SkillShelf skills)
- [ ] SKILL.md body is under 500 lines
- [ ] All file paths use forward slashes
- [ ] All file references are one level deep from SKILL.md

## Scope

- [ ] Skill does one thing well
- [ ] Scope is describable in two sentences
- [ ] Description accurately matches what the skill does
- [ ] No scope creep into adjacent tasks

## Input Design

- [ ] Accepts existing content first (default pattern)
- [ ] Offers guided prompts as fallback for users without existing content
- [ ] Identifies gaps and asks targeted follow-ups (not exhaustive Q&A)
- [ ] Handles messy, incomplete, or inconsistent input gracefully
- [ ] Nudges once for additional input, then moves forward if user declines
- [ ] Never refuses output due to imperfect input
- [ ] If CSV: lists expected columns explicitly
- [ ] If CSV: handles common column naming variations

## Output Design

- [ ] Uses consistent Markdown headings
- [ ] Headings are stable (changing them would break downstream references)
- [ ] Headings are descriptive (a downstream skill can reference them by name)
- [ ] Output is copy-paste ready (no reformatting needed)
- [ ] If CSV output: importable into target platform without manual column renaming
- [ ] Includes Confidence notes section when working from limited input
- [ ] Every claim is specific to the brand/product/data (not generic)
- [ ] Includes a closing/next-steps section telling the user what to do with the output

## Calibration

- [ ] Calibration present only when interpretation varies (voice, tone, positioning)
- [ ] Calibration absent when output is data-determined
- [ ] Calibration absent when skill receives a calibrated artifact as input (e.g., brand voice guide)
- [ ] If calibrating: presents 2-3 variations labeled neutrally (A, B, C)
- [ ] If calibrating: uses selection to anchor final output

## Examples

- [ ] Example file exists in `references/` with `example-` prefix (e.g., `example-output.md`)
- [ ] Example uses a generic, category-obvious brand name
- [ ] Brand name makes product category immediately clear
- [ ] Example demonstrates ceiling quality (not floor)
- [ ] Example covers all output sections

## Ecosystem

- [ ] References to other skills use natural-language names, not directory names
- [ ] Primitives are recommended but not required (skill works without them)
- [ ] If output is consumed by other skills: `references/glossary.md` exists
- [ ] If output is consumed by other skills: output includes version marker (`<!-- skill-name v0.1 -->`)
- [ ] If glossary exists: follows the six-section structure (Overview, Document Structure, Section Hierarchy, Handling Missing Input, Field Definitions, Changelog)

## Edge Cases

- [ ] Thin input: produces output and notes what would improve it
- [ ] Inconsistent input: documents variation instead of averaging
- [ ] Missing context: produces output without that section, notes gap
- [ ] If CSV: addresses missing columns
- [ ] If CSV: addresses inconsistent formatting
- [ ] If CSV: addresses very small datasets (< 10 rows)
- [ ] If CSV: addresses very large datasets (1,000+ rows)

## Gotchas (recommended)

- [ ] If tested: known AI behavior patterns documented in a Gotchas section
- [ ] Gotchas are specific and actionable (not vague warnings)

## Writing Quality

- [ ] Specific to the brand/product/data, not generic
- [ ] Plain language, no jargon or buzzwords
- [ ] No em dashes (use double hyphens `--` instead)
- [ ] Claims are supported by user input, not fabricated
- [ ] Instructions explain why, not just what (theory of mind over rigid rules)

## skillshelf.yaml

- [ ] `version` is present (semver string)
- [ ] `category` is one of the 10 valid values
- [ ] `level` matches user involvement: beginner (talk and get output), intermediate (prepared input), advanced (works outside chat)
- [ ] `primitive` is true only for foundational skills producing reusable documents
- [ ] `platforms` is listed (specific platforms or "platform-agnostic")
- [ ] `faq` has at least 2-3 entries

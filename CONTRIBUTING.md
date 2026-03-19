# Contributing to SkillShelf

Thanks for your interest in contributing a skill.

The easiest way to create a submission-ready skill is to use [Build a New Skill](https://skillshelf.ai/skills/write-skill/). It walks you through designing and writing a skill from scratch with all the right structure and conventions.

If you already have a working prompt or skill file, use [Share a Skill You Already Have](https://skillshelf.ai/skills/adapt-skill/) to convert it into SkillShelf format.

## How to submit

### Option 1: Website

Visit [skillshelf.ai/submit](https://skillshelf.ai/submit/) to upload your skill file directly. The site opens a pull request on your behalf. You can upload `.skill` files (exported from Claude) or `.zip` files (exported from ChatGPT or packaged manually).

### Option 2: GitHub pull request

1. Fork this repository
2. Create a new directory under `skills/` with your skill name (lowercase, hyphenated, e.g. `skills/my-cool-skill/`)
3. Add a `SKILL.md` file with YAML frontmatter (see below)
4. Add a `skillshelf.yaml` sidecar file (see below)
5. Open a pull request against `main` with the title `[Community Submission] Add skill: my-cool-skill`
6. Check the **Contributor Attestation** checkbox in the PR description

The attestation checkbox confirms you agree to the [Terms of Service](https://skillshelf.ai/terms/) and [Privacy Policy](https://skillshelf.ai/privacy/), and that the submission will be published under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license.

## Skill file structure

Each skill lives in its own directory under `skills/`:

```
skills/my-cool-skill/
  SKILL.md              # Required. Core instructions.
  skillshelf.yaml       # Required. SkillShelf catalog metadata.
  references/           # Recommended. Example outputs, glossaries, supporting docs.
    example-output.md
```

### SKILL.md

The `SKILL.md` file has a YAML frontmatter block and a markdown instruction body:

```markdown
---
name: my-cool-skill
description: >-
  Third-person description under 155 characters. What the skill
  produces and what it is used for.
license: Apache-2.0
---

# Verb + Outcome Title (e.g., "Write Collection Descriptions")

1-2 paragraph introduction. What the skill does, who it is for,
and a pointer to references/example-output.md.

## Conversation Flow

### Turn 1: Collect input
### Turn 2+: Follow-up / gap analysis
### Produce output
### Review and refine

## Output Structure
The exact heading hierarchy the skill produces.

## Edge Cases
How the skill handles thin input, inconsistent input, missing context.

## Closing
What the user does with the output after the skill is done.
```

Required frontmatter fields: `name`, `description`, `license`.

See the [SKILL.md Specification](skillmd-specs.md) for the full format reference and the [Skill Authoring Guide](skill-authoring-guide.md) for writing tips.

### skillshelf.yaml

The `skillshelf.yaml` sidecar file provides catalog metadata that SkillShelf uses for categorization, filtering, and display.

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Semantic version of your skill (e.g. `"0.1.0"`) |
| `category` | string | One of the valid categories (see below) |
| `level` | string | `beginner`, `intermediate`, or `advanced` |
| `primitive` | boolean | `true` if this is a foundational building-block skill, `false` otherwise |
| `platforms` | list | Platform slugs this skill targets (e.g. `shopify`, `bigcommerce`, or `platform-agnostic`) |
| `tags` | list | Descriptive tags for search and filtering (e.g. `["product descriptions", "seo"]`) |

**Recommended fields:**

| Field | Type | Description |
|-------|------|-------------|
| `author` | object | `name` and `url` for attribution |
| `faq` | list | 2-4 questions and answers about the skill (displayed on the site) |
| `subcategories` | list | More specific category tags |
| `date_added` | string | ISO date `YYYY-MM-DD` |
| `date_updated` | string | ISO date `YYYY-MM-DD` |

**Optional fields:**

| Field | Type | Description |
|-------|------|-------------|
| `certified` | boolean | Set by reviewers after certification |
| `input_schema` | object | Describes what the skill accepts |
| `output_schema` | object | Describes what the skill produces |

**Valid categories:**

- `product-content`
- `catalog-operations`
- `product-discovery-and-recommendations`
- `customer-research-and-voice-of-customer`
- `merchandising-and-assortment`
- `conversion-and-page-optimization`
- `email-and-lifecycle`
- `reporting-and-analysis`
- `operations-and-process`
- `feed-and-channel-management`

**Example:**

```yaml
version: "0.1.0"
category: product-content
level: beginner
primitive: false
platforms:
  - platform-agnostic
tags:
  - brand voice
  - style guide

date_added: "2026-03-19"
date_updated: "2026-03-19"

author:
  name: Your Name
  url: https://your-site-or-linkedin.com

faq:
  - question: What does this skill do?
    answer: Plain-language answer shown on the skill page.
  - question: What do I need to get started?
    answer: Another answer.
```

Look at the existing skills in `skills/` for complete examples.

## What happens when you submit

Every pull request triggers CI checks that validate:

1. **Contributor attestation** (fork PRs only): The PR description must include a checked attestation checkbox confirming license and policy agreement.
2. **Open standard validation**: Your `SKILL.md` is validated against the [Agent Skills](https://agentskills.io) open standard using `agentskills validate`.
3. **SkillShelf metadata validation**: Your `skillshelf.yaml` is checked for required fields, valid categories, valid levels, and correct formatting.

If any check fails, the PR cannot be merged. Fix the issues and push again.

After CI passes, the SkillShelf team reviews your skill for quality and safety. If it passes certification, it goes live on [skillshelf.ai](https://skillshelf.ai/).

## Before you submit (checklist)

- [ ] Your skill directory is under `skills/` with a lowercase, hyphenated name
- [ ] `SKILL.md` has `name`, `description`, and `license: Apache-2.0` in the frontmatter
- [ ] `description` is under 155 characters (used as the meta description on skillshelf.ai)
- [ ] Skill title (h1 in SKILL.md) starts with a verb and describes the outcome ("Write Collection Descriptions" not "Collection Description Generator")
- [ ] `SKILL.md` instructions are clear, imperative, and specific about the output format
- [ ] `skillshelf.yaml` has all required fields (`version`, `category`, `level`, `primitive`, `platforms`, `tags`)
- [ ] Category is one of the valid values listed above
- [ ] Example output files use fictional brand names, not real ones (see [Skill Authoring Guide](skill-authoring-guide.md) Section 6)
- [ ] You have tested the skill with real inputs and the output is consistently usable -- sample ecommerce data is available in [`fixtures/`](fixtures/) if you need it
- [ ] No confidential or personal data is included in the skill or examples

## Questions?

Open an issue or reach out at [skillshelf.ai](https://skillshelf.ai/).

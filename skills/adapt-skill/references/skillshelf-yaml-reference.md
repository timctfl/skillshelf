# skillshelf.yaml Field Reference

Every SkillShelf skill includes a `skillshelf.yaml` sidecar file alongside SKILL.md. This file provides metadata used by the SkillShelf website for categorization, filtering, and display.

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Version of the skill (e.g., "1.0") |
| `category` | string | One of the categories below |
| `level` | string | `beginner`, `intermediate`, or `advanced` |
| `primitive` | boolean | `true` only for foundational skills producing reusable reference documents. Most skills: `false` |
| `platforms` | list of strings | Target platforms or `["platform-agnostic"]` |
| `tags` | list of strings | Freeform tags for discovery (e.g., `["product-copy", "shopify", "descriptions"]`) |

## Categories

| Slug | Description |
|------|-------------|
| `product-content` | Writing product descriptions, titles, bullets, A+ content |
| `catalog-operations` | Cleaning, normalizing, enriching product data |
| `brand-and-identity` | Brand voice, visual identity, positioning guidelines |
| `customer-research` | Reviews, surveys, feedback analysis |
| `feeds-and-merchandising` | Product feeds, discovery, assortment planning, channel sync |
| `conversion-optimization` | Landing pages, A/B copy, page audits |
| `email-and-lifecycle` | Email campaigns, flows, lifecycle marketing |
| `reporting-and-analysis` | Performance reports, dashboards, trend analysis |
| `operations-and-process` | Internal workflows, SOPs, process documentation |

## Levels

| Level | User involvement |
|-------|-----------------|
| `beginner` | User talks and gets output. Minimal input, little back-and-forth. |
| `intermediate` | User brings prepared input (CSVs, guidelines, briefs). 2-3 rounds of interaction. |
| `advanced` | User works outside the chat window. Multiple data sources, chained tools, external file creation. |

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `subcategories` | list of strings | More specific tags within the category |
| `certified` | boolean | `true` if the skill has passed SkillShelf review |
| `date_added` | string | ISO date (YYYY-MM-DD) |
| `date_updated` | string | ISO date |
| `author` | object | `name` (string) and optional `url` (string) |
| `faq` | list of objects | Each with `question` (string) and `answer` (string). 2-4 entries recommended. |
| `input_schema` | object | Freeform description of expected input |
| `output_schema` | object | Freeform description of produced output |

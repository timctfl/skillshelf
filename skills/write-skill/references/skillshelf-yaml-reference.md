# skillshelf.yaml Field Reference

Every SkillShelf skill includes a `skillshelf.yaml` sidecar file alongside SKILL.md. This file provides metadata used by the SkillShelf website for categorization, filtering, and display.

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Semver version of the skill (e.g., "0.1.0") |
| `category` | string | One of the 10 categories below |
| `level` | string | `beginner`, `intermediate`, or `advanced` |
| `primitive` | boolean | `true` only for foundational skills producing reusable reference documents. Most skills: `false` |
| `platforms` | list of strings | Target platforms or `["platform-agnostic"]` |
| `tags` | list of strings | Freeform tags for discovery (e.g., `["product-copy", "shopify", "descriptions"]`) |

## Categories

| Slug | Description |
|------|-------------|
| `product-content` | Writing product descriptions, titles, bullets, A+ content |
| `catalog-operations` | Cleaning, normalizing, enriching product data |
| `product-discovery-and-recommendations` | Search, recommendations, quizzes, gift guides |
| `customer-research-and-voice-of-customer` | Reviews, surveys, feedback analysis |
| `merchandising-and-assortment` | Bundles, collections, assortment planning |
| `conversion-and-page-optimization` | Landing pages, A/B copy, page audits |
| `email-and-lifecycle` | Email campaigns, flows, lifecycle marketing |
| `reporting-and-analysis` | Performance reports, dashboards, trend analysis |
| `operations-and-process` | Internal workflows, SOPs, process documentation |
| `feed-and-channel-management` | Product feeds, marketplace listings, channel sync |

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
| `models_tested` | list of strings | Models verified to work well (e.g., `claude-sonnet-4-5`) |
| `estimated_tokens` | object | `input` and `output` as range strings (e.g., "2000-8000") |
| `interaction_pattern` | string | `single-turn` or `multi-turn` |
| `install_method` | string | `copy` (just SKILL.md) or `directory` (SKILL.md + references/) |
| `date_certified` | string | ISO date (YYYY-MM-DD) |
| `date_added` | string | ISO date |
| `date_updated` | string | ISO date |
| `author` | object | `name` (string) and optional `url` (string) |
| `input_schema` | object | Freeform description of expected input |
| `output_schema` | object | Freeform description of produced output |
| `faq` | list of objects | Each with `question` (string) and `answer` (string) |

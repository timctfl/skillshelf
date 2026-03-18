# Example Adaptation: Before and After

This file shows a raw prompt converted into SkillShelf format. Use it as a reference for what good adaptation looks like.

---

## Before: Raw Prompt

The user pastes this system prompt into the conversation:

```
You are an expert at writing product collection descriptions for ecommerce stores.

When the user gives you a collection name and some context about the products in it, write a collection description that:
- Opens with a hook that speaks to the customer's need, not the product category
- Mentions 2-3 specific products or product types in the collection
- Includes a clear value proposition for why this collection exists
- Ends with a soft CTA that encourages browsing
- Is 80-150 words
- Matches the brand's tone if provided

If the user gives you a brand voice guide, use it. If not, default to a friendly, knowledgeable tone.

Write 3 variations so the user can pick their favorite.
```

---

## After: Converted SkillShelf Skill

### SKILL.md

```markdown
---
name: write-collection-descriptions
description: >-
  Produces collection page descriptions from a collection name and product
  context. Outputs three variations the user can choose from.
license: Apache-2.0
metadata:
  category: product-content
  level: beginner
  platforms: platform-agnostic
  primitive: "false"
---

# Write Collection Descriptions

This skill writes collection page descriptions for ecommerce stores. Give it a collection name and some context about the products, and it produces three variations to choose from. Each variation opens with a customer-need hook, references specific products, states a value proposition, and closes with a browsing CTA.

For an example of what this skill produces, see `references/example-output.md`.

---

## Conversation Flow

### Turn 1: Collect input

Tell the user:

> Give me a collection name and some context about the products in it. You can
> paste an existing collection page, a list of product names, a Shopify product
> export, or just describe what the collection contains.
>
> If you have a brand voice profile from the Document Your Brand Voice skill,
> upload it alongside your request. It will help me match your brand's tone. If
> not, I will work from whatever context you provide.

Accept whatever the user provides. If they paste a CSV or product list, extract
the relevant details (product names, types, price range, key features). If they
give a single sentence, that is enough to start.

### Turn 2: Clarify gaps (if needed)

If the collection name and product context are clear, skip this turn and produce
output immediately.

If key information is missing, ask up to 2 targeted follow-up questions:

- What makes this collection distinct from other collections on the site?
- Who is the target customer for this collection?

Do not ask more than 2 questions. If the user says that is all they have, move
forward immediately.

### Turn 3: Produce descriptions

Write three variations following the synthesis instructions below. Present them
labeled A, B, and C without descriptive labels. Let the user react to the output
itself.

After presenting, ask: "Which of these works best, or what would you change?"

### Turn 4+: Refine

If the user picks a variation, offer to adjust it. If they want changes across
all three, edit in place. Do not regenerate from scratch for minor corrections.

---

## Synthesis Instructions

For each variation, follow this structure:

1. **Opening hook (1-2 sentences).** Address the customer's need or aspiration,
   not the product category. "Everything you need for weekend trail runs" not
   "Our running collection."

2. **Product specifics (1-2 sentences).** Mention 2-3 specific products or
   product types from the collection. Use actual product names if the user
   provided them.

3. **Value proposition (1 sentence).** Why this collection exists as a curated
   group, not just a category filter.

4. **Closing CTA (1 sentence).** Encourage browsing without hard selling.

Each description should be 80-150 words. The three variations should differ in
angle (e.g., customer-need-first vs. product-feature-first vs.
occasion/use-case-first), not just word choice.

If the user provided a brand voice profile, match its tone, vocabulary, and
style decisions. If not, use a friendly, knowledgeable default tone.

---

## Output Structure

Each variation follows this format:

### Collection Description A

[80-150 word description]

### Collection Description B

[80-150 word description]

### Collection Description C

[80-150 word description]

### Confidence Notes

[Flag any gaps: missing product details, no brand voice input, assumed target
customer, etc.]

---

## Important Behaviors

- Produce descriptions as a single downloadable document.
- Edit in place when the user requests changes.
- If the user provides a brand voice profile, honor it completely. Do not
  override the profile's tone decisions with your own preferences.
- Every description must reference specific products or product types from the
  user's input. Do not invent product names.

---

## Edge Cases

### Thin input

If the user provides only a collection name with no product context, produce
three descriptions using generic product references ("top-rated items,"
"best sellers in the category") and note in Confidence Notes what specific
product information would improve the output.

### Inconsistent input

If the product list includes items that seem unrelated to the collection name,
note the mismatch and ask the user to confirm the collection scope. Produce
output based on what they confirm.

### Missing brand voice

If no brand voice profile is provided, use a friendly, knowledgeable default.
Note in Confidence Notes that a brand voice profile from the Document Your
Brand Voice skill would improve consistency with the store's existing copy.

---

## Closing

Download the description you chose. Paste it into your collection page in
Shopify, WooCommerce, or wherever you manage collections. If you need
descriptions for more collections, start a new conversation with this skill
and your brand voice profile.
```

### What Changed in the Conversion

| Source prompt | Converted skill |
|--------------|-----------------|
| No frontmatter | Full YAML frontmatter with name, description, license, metadata |
| No conversation flow | Four labeled turns: collect, clarify, produce, refine |
| "Write 3 variations" | Structured as calibration-like A/B/C output with user selection |
| No input guidance | Accept-first pattern: paste existing content, CSV, or describe |
| No edge cases | Thin input, inconsistent input, missing brand voice all addressed |
| No example output | Separate `references/example-output.md` file (not shown here) |
| No closing | Closing section tells user what to do with the output |
| No ecosystem awareness | References the Document Your Brand Voice skill as optional input |
| No metadata | skillshelf.yaml with category, level, tags, FAQ |
| "Default to friendly tone" | Preserved as default, but positioned as fallback when no voice profile exists |

### What Was Preserved

- Core logic: hook, product specifics, value prop, CTA structure
- Word count guidance: 80-150 words
- Three-variation pattern
- Brand voice integration when available
- The friendly, knowledgeable default tone

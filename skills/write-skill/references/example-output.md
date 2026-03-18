# Example: Write Collection Descriptions

This is an example of what the write-skill produces. It is a complete SKILL.md for a fictional skill that writes product collection descriptions from a Shopify catalog. It demonstrates SkillShelf conventions: proper frontmatter, conversation flow, input design, output structure, edge cases, and ecosystem awareness.

The example uses Great Outdoors Co., the canonical SkillShelf test brand.

---

```markdown
---
name: write-collection-descriptions
description: >-
  Produces SEO-ready product collection descriptions from a Shopify product
  catalog or similar structured export. Accepts a CSV or pasted product list
  and generates a description for each collection (by product type, tag, or
  vendor). Descriptions lead with customer need, highlight the range of
  products in the collection, and include relevant search terms naturally.
  Output is ready to paste into Shopify collection pages.
license: Apache-2.0
---

# Write Collection Descriptions

This skill takes a product catalog and writes descriptions for each product
collection. A collection description tells the customer what they will find,
why it matters, and what to look for when choosing. The output is designed
for Shopify collection pages but works for any platform with category or
collection landing pages.

For reference on the expected output, see
[references/example-output.md](references/example-output.md).

## Conversation Flow

### Turn 1: Welcome and Collect

Ask the user to share their product catalog. Accept any of these formats:

- Shopify product export CSV (preferred: has Type, Tags, Vendor columns)
- WooCommerce product export CSV (map Categories to collection names)
- A pasted list of products grouped by collection
- A link to their store (attempt to extract collection structure)

Tell the user: "Share your product catalog and I'll write a description for
each collection. A Shopify CSV export works best, but I can work with any
product list. If you have a brand voice profile or positioning brief, upload
those too and I'll write on-brand."

### Turn 2: Identify Collections and Confirm

After receiving the catalog:

1. Parse the data and identify distinct collections by product type, tags,
   or vendor (whichever produces the most meaningful groupings).
2. For each collection, note the product count and representative products.
3. Present the collection list to the user: "I found N collections in your
   catalog. Here's what I'll write descriptions for: [list]. Should I add,
   remove, or rename any of these?"

Wait for confirmation before writing.

### Turn 3: Produce Descriptions

Generate one description per collection using the output structure below.
Produce all descriptions in a single downloadable document.

After sharing: "Review these and let me know if any need adjustments. I can
change the tone, add specific product callouts, or restructure any
description."

### Turn 4+: Revise

Edit individual descriptions in place when the user requests changes.
Do not regenerate the entire document for one correction.

## Synthesis Instructions

### Core principles

- **Lead with the customer need, not the product list.** A collection
  description answers "what am I looking for?" before "what's in here?"
- **Be specific to the catalog.** Reference actual products, materials,
  price ranges, and use cases from the data. "Waterproof jackets rated
  from 10K to 20K mm" is useful. "A range of quality outerwear" is not.
- **Include search terms naturally.** Weave relevant keywords into the
  description without keyword stuffing. The description should read as
  helpful prose that happens to contain the terms people search for.
- **Respect the brand voice.** If a brand voice profile is provided, follow
  it. If not, write in a clear, direct, helpful tone.

### Per-collection process

For each collection:

1. Read all products in the collection. Note the range of prices, key
   materials or features, and the use cases they cover.
2. Identify the unifying theme: what problem does this collection solve,
   or what activity does it serve?
3. Write the description following the output structure.

## Output Structure

Each collection description follows this format:

```
## [Collection Name]

[Opening sentence: who this collection is for and what need it serves.]

[Body paragraph: what the collection contains, with specific references
to product types, materials, features, and the range of options. Include
price range if it helps the customer understand the tier.]

[Closing sentence: what to consider when choosing, or a natural transition
to browsing the products.]
```

Target length: 80-150 words per description. Long enough to be useful for
SEO and customer context. Short enough that customers actually read it.

## Important Behaviors

- Produce all descriptions in a single downloadable Markdown file.
- Use the collection name as an H2 heading.
- If the user provides a brand voice profile, read it before writing and
  follow it throughout. If not provided, write in a clear, direct tone.
- When editing, change only the requested description.

## Edge Cases

### Very small catalog (< 10 products)

Some collections may have only 1-2 products. Write descriptions anyway,
but keep them shorter (2-3 sentences). Note to the user: "Some collections
have very few products. The descriptions reflect what's there now. As you
add products, you may want to regenerate these."

### Missing product descriptions in the catalog

If the CSV has product titles but empty description fields, work from the
titles, types, tags, and any other available fields. Note which descriptions
were written from limited data in a Confidence notes section.

### Collections that overlap heavily

If two collections share most of their products (e.g., "Rain Jackets" and
"Waterproof Gear"), flag the overlap: "These two collections share N
products. I've written distinct descriptions that emphasize what makes each
collection different. You may want to consolidate them."

### Very large catalog (1,000+ products)

Process all collections but warn about potential grouping issues: "With a
large catalog, the automatic collection grouping may not match your store's
actual collections. Review the list in Turn 2 and let me know if any need
adjusting."
```

---

## Example of What This Skill Produces

Below is a sample collection description for Great Outdoors Co., showing
the output quality this skill should achieve.

```markdown
## Rain Shells

When the forecast turns and you're two miles from the trailhead, your
shell is the difference between pushing through and turning back. This
collection covers the range: from the Cascade Rain Shell with 15K mm
waterproofing and fully taped seams for all-day downpours, to lighter
wind-resistant layers for drizzly morning runs. Prices run from $89 to
$189. If you're choosing between them, start with where you'll wear it
most. Day hikes in the Pacific Northwest need different protection than
a quick trail run in light rain.
```

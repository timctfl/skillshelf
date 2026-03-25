---
name: build-category-badge-framework
description: >-
  Produces a small, opinionated product badge system for a single ecommerce
  category. Identifies the decision axes that matter most to shoppers,
  then picks the best 1-2 products per badge.
license: Apache-2.0
---

# Build a Category Badge Framework

This skill takes product data for a single category and produces a badge
system designed to help shoppers narrow their choices on a product listing
page. It works at the category level first (what decision axes matter for
this category?) and then picks the best 1-2 products per badge.

Badges are recommendations, not descriptions. They don't label what a
product has. They tell the shopper "if this is what you care about, start
here." Most products in the category should not have a badge. When
everything is labeled, nothing stands out.

Hard constraint: one category per run. Multi-category badge systems require
different tradeoffs and are out of scope.

For reference on the expected output, see
[references/example-output.md](references/example-output.md).

## Voice and Approach

Be direct and analytical. This is a merchandising tool, not a branding
exercise. Use plain shopper language when naming and defining badges. Avoid
marketing jargon, superlatives, and vague labels. When recommending or
rejecting a badge, explain the reasoning in one or two sentences. The user
should always understand why a badge made the cut or didn't.

---

## Conversation Flow

### Turn 1: Collect Product Data

Ask the user to share their product data for one category. Accept any of
these formats:

- CSV export from Shopify, BigCommerce, WooCommerce, or similar (preferred)
- Pasted product list with attributes
- PDP content (pasted text or uploaded files)
- A structured table or spreadsheet

If a CSV is provided, work from whatever columns are available. Common
useful columns include title, description, features, specs, price, ratings,
tags, and product type. Do not require a specific schema.

Infer the category name from the data if the user doesn't state it
explicitly. Confirm it when presenting the framework.

After receiving product data, ask about two optional inputs:

1. **Review data.** Customer reviews, review summaries, or review
   highlights for products in the category. This helps identify what
   shoppers actually weigh when deciding, which may differ from what the
   product specs emphasize.
2. **Existing badges or callouts.** Any badges, labels, tags, or callouts
   currently used on the PLP or PDPs. This helps avoid redundancy and
   gives the skill something concrete to evaluate.

Ask about both in a single message. If the user doesn't have them, move
forward without them. Nudge once, then proceed.

### Turn 2: Present the Category Badge Framework

This is the core analytical step. Present the framework as a single
downloadable Markdown document with one recommended product per badge.

The framework should include:

- The recommended badge set (typically 3-5 badges)
- For each badge: name, shopper-facing definition, a short rationale,
  considerations, and the recommended product with evidence
- Any candidate badges that were considered and rejected, with a brief
  explanation of why

The recommended product makes the framework tangible. If the badge
definition sounds reasonable but the product pick feels wrong, that's
a signal to rethink the badge or the pick.

Ask the user to review. Let them know they can add, remove, rename,
adjust considerations, or swap any product pick.

### Turn 3+: Revise

Edit the document in place when the user requests changes. Do not
regenerate the entire output for a single correction. If the user
changes a badge definition or considerations, update the recommended
products accordingly.

---

## Badge Analysis Process

Every badge should represent a decision criterion -- a reason a specific
type of shopper would pick one product over another. A high review count
is a proxy for "this is a safe, universal pick." A use-case label like
"best for side sleepers" lets the right shopper self-select immediately.
These are decisions. A random product feature that isn't the single
biggest deciding factor for some segment of shoppers is not worth a
badge. If you can't describe the shopper who would filter by this badge,
it probably shouldn't exist.

### Step 1: Identify candidate badge themes

Read all product data in the category. Look for the decision axes that
would actually help a shopper narrow their choice. Good badge themes
come from:

- Use-case fit (best for beginners, designed for travel, heavy-duty use)
- Functional differences that drive purchase decisions (waterproofing,
  weight class, battery life)
- Certification or standard (organic, cruelty-free, safety rated)
- Social proof (high volume of top reviews as a proxy for safe pick)

A note on review-based badges: only use review signals when review
coverage is reasonably comparable across products. A product with 2
reviews and a 5.0 average is not "top rated" next to a product with
300 reviews and a 4.8. Prefer threshold-based review badges (e.g.,
"100+ five-star reviews") over ranking-based ones ("best reviewed").

If review data is available, prioritize attributes that shoppers mention
when explaining their purchase decision or comparing options. What
shoppers care about may not match what the product specs emphasize.

### Step 2: Filter the badge set

Test each candidate badge before including it in the framework:

**Decision test.** Can you describe the specific shopper who would use
this badge to make their choice? "I need a jacket that works in rain"
is a real decision. "This jacket uses recycled materials" is a feature.
If the badge doesn't map to a decision, drop it.

**Overlap test.** Check whether two candidate badges would point to
the same products. If they do, one is redundant. Keep the one that
maps to a clearer shopper decision.

**Relevance test.** A badge can be factually accurate and still not
useful. Would a shopper comparing products in this category actually
use this attribute to narrow their choice? If the answer is unclear,
drop it.

Badges that don't survive these filters do not make it into the
framework. Note rejected candidates briefly so the user understands
the reasoning.

### Step 3: Pick products for each badge

This is where the framework becomes selective. For each badge, pick
the 1-2 products that best represent it. Not every product that could
carry a badge should.

**One badge per product.** Even if a product could qualify for multiple
badges, assign only the one where it stands out most. The badge's job
is to give the shopper one reason to click, not a summary of the
product's strengths.

**1-2 products per badge.** Each badge should point to a clear
recommendation. If you find yourself assigning a badge to 3+ products,
the badge is too broad or you're not being selective enough. Tighten
the pick.

**Most products get no badge.** A category of 10 products should have
roughly 4-6 badged and the rest unbadged. That's a feature, not a
problem. Unbadged products are still good -- they just don't stand out
on the specific axes this framework measures.

In the recommended product field, explain why this product was picked
over others that could have carried the badge.

Do not invent or infer claims that are not supported by the provided
data. If the data is ambiguous, do not assign the badge.

---

## Output Structure

The output is a single Markdown document:

```
# Badge Framework: [Category Name]

## Category Badge Framework

### [Badge Name]
- **Definition:** [One-line shopper-facing description]
- **Why it matters:** [1-2 sentences on the shopper decision this
  badge serves]
- **Considerations:** [What makes a product the right pick for this
  badge]
- **Recommended product:** [Product name] -- [evidence for why this
  product was picked over others]

[Repeat for each badge in the framework]

### Considered and Rejected

[Brief list of badge themes that were evaluated and dropped, with
one-line explanations. These should be decision-level ideas that
didn't make the cut, not features that obviously aren't decisions.]
```

Keep badge names short (2-4 words). Use plain shopper language, not
internal merchandising jargon. Badge names should be:

- Short enough to fit on a product card
- Comparative -- they should help a shopper distinguish this product
  from others in the set
- Meaningful in the category -- a shopper browsing this category should
  immediately understand what the badge signals
- Not just restatements of technical specs -- translate specs into
  shopper benefit when possible (e.g., "Lightweight Warmth" is often
  more useful than "700 Fill Power," though there are cases where the
  spec itself is the clearest label)

The recommended product field should explain why this product was
picked over others, not just that it qualifies.

---

## Edge Cases

### Thin product data

If product data is limited (titles and prices only, no descriptions or
specs), produce the framework from what's available. Badge themes will
lean toward price-based and naming-pattern comparisons. Note in the
recommended product field when a pick is based on limited data.

### Very small category (under 5 products)

Badges may not add much comparative value with very few products. Produce
a lighter framework (2-3 badges at most) and note that the small set size
limits how useful badges can be. A shopper can compare 4 products without
much help.

### Near-identical products

If most products in the category are very similar on the attributes that
matter, say so. "These products are nearly identical on the axes that
matter for shoppers. Badges won't create meaningful differentiation here."
Still produce a framework if there are any differences worth surfacing,
but keep it minimal.

### Existing badges that conflict

If the user provides current badges and the new framework contradicts
them (different considerations, overlapping labels, unsupported claims), call
this out in the framework section under Considered and Rejected.
Recommend which existing badges to keep, revise, or retire.

### Missing review data

Without reviews, the skill infers decision-relevant attributes from
product specs and features alone. Let the user know that the framework
reflects what the data emphasizes, which may not match what shoppers
actually weigh. Recommend review analysis as a follow-up if the user
wants to validate the badge themes.



---
name: business-context
description: >-
  Produces a business context document capturing how a brand operates
  across channels, markets, pricing, seasonality, and policies. Used
  as a reusable input for downstream ecommerce skills.
license: Apache-2.0
---

# Document Your Business Context

This skill produces a business context document that captures how your brand operates. The question it answers: what would an ecommerce team need to know about the business to do their job well across workstreams like analytics and reporting, email and lifecycle marketing, promotions and product launches, product content and localization, and feed and channel optimization?

The output is a structured document designed to be uploaded alongside other foundation documents (like a brand voice profile or positioning brief) when running skills that need to understand the business, not just the brand.

For reference on the expected output, see [references/example-output.md](references/example-output.md).

## Voice and Approach

You are a business analyst helping the user document the operational context behind their brand. Be direct and conversational. The user knows their business better than you do, so your job is to help them surface the information that matters, not to teach them how their business works. Ask good questions, listen carefully, and organize what they share into something clear and reusable.

Not every topic will be relevant to every brand. Some brands will have a lot to say about channel strategy and almost nothing about loyalty programs. Others are the reverse. Follow the user's lead. Go deep where they have depth and move on where they don't.

## Conversation Flow

### Turn 1: Welcome and Collect

Introduce the skill. Explain that this document captures the operational side of the business so that AI tools working on ecommerce tasks have the context they need. Give a few examples of the kinds of decisions this context informs: how to interpret a traffic dip in a GA4 report, what shipping policies to reference in email copy, which channels matter when optimizing a product feed.

Ask the user for their brand name and website URL.

Then invite them to share anything they already have that describes how the business operates. The more context upfront, the better the document will be. Encourage an info dump. Examples of useful input:

- Strategy decks, investor updates, internal briefs, about pages, policy pages
- Shopify reports: sales by channel, product analytics, order volume over time, customer segmentation reports
- GA4 reports: acquisition overview, traffic acquisition by channel, ecommerce purchase data, user demographics and geo breakdown
- Any internal docs that describe pricing strategy, promotional calendars, channel plans, or fulfillment operations

Let them know they can paste text, upload files, or share screenshots at any point in the conversation. Anything they share will be distilled into the relevant business context.

### Turn 2: Propose Topics

Review the brand's website to understand what kind of business it is. Based on what you learn, propose a prioritized list of business context topics you think are most relevant for this brand. For each topic, include a brief note on why it matters for their downstream ecommerce work.

If you're unable to access the website (blocked, requires login, or the site is down), let the user know and ask them to paste or upload some representative content: a few product pages, the homepage, an about page, or a shipping/returns policy page. Even a rough overview of the business gives the skill enough to propose relevant topics.

The full universe of topics includes (but is not limited to):

- Sales channels (DTC, marketplaces, wholesale, retail, social commerce)
- Markets and regions (domestic, international, where they ship, where they focus)
- Pricing and product economics (price tier, margin profile, discounting philosophy)
- Seasonality and calendar (peak periods, promotional cadence, product launch timing)
- Business model (one-time purchase, subscription, hybrid, bundles, made-to-order)
- Growth stage and current priorities (what the business is focused on right now)
- Loyalty and rewards programs
- Shipping and fulfillment (policies, carriers, speed expectations, free shipping thresholds)
- Returns and exchanges (policies, patterns, how they handle it)
- Customer segments and buying patterns
- Competitive landscape and positioning
- Technology stack (ecommerce platform, ESP, analytics, key integrations)

Do not present this as a checklist. Select and prioritize the topics that matter for this brand based on what you've learned, and frame each one in terms of why it would be useful context for ecommerce work. Some topics may not apply at all. Others may be worth combining.

Ask the user to confirm the list, add anything missing, remove anything that doesn't matter, or reorder based on what they think is most important. Let them know they can also raise topics not on the list.

### Turn 3+: Walk Through Topics

Work through the confirmed topics conversationally. For each topic, ask an open question that invites the user to share what they think is important. If they give a short answer, that's fine. If they go deep, follow up with clarifying questions to make sure the document captures the nuance.

A few principles for this phase:

- Let the user steer. If they want to spend three turns on channel strategy and skip loyalty entirely, that's the right call for their business.
- If the user pastes a document or uploads a file mid-conversation, extract the relevant business context from it and confirm what you found.
- When you have enough information on a topic, move to the next one naturally. Don't ask for confirmation after every single answer.
- If the user says something that conflicts with what you saw on their site, note the discrepancy and ask which is current. The user's answer wins.

When the user signals they've covered what matters (or you've worked through the list), let them know you'll produce the document.

### Produce the Document

Generate the full business context document following the output structure below. Produce it as a single downloadable markdown file.

After sharing, ask the user to review it. Suggest they read it from the perspective of someone on their team who needs to understand the business to do ecommerce work. Flag anything that's missing, wrong, or doesn't reflect how the business actually operates.

### Review and Refine

When the user requests changes, edit the document in place. Do not regenerate the entire document for a single correction. If the user wants to add a new section, add it in the most logical position within the existing structure.

## Output Structure

The document uses a consistent heading structure, but only includes sections the user actually provided information for. Do not include sections with placeholder text or generic statements.

```
# Business Context: [Brand Name]

<!-- business-context v0.1 -->

## Overview
[2-3 sentence summary: what the brand sells, who it serves, and the
essentials of how it operates. Written to orient someone encountering
the brand for the first time.]

## Shopper-Facing Context
[Context that directly affects what customers see and experience.
Group relevant topic sections here.]

### [Topic Section, e.g., Shipping and Fulfillment]
### [Topic Section, e.g., Returns and Exchanges]
### [Topic Section, e.g., Pricing and Promotions]
### [Topic Section, e.g., Loyalty and Rewards]

## Behind the Scenes
[Context about how the business operates internally. This information
shapes how ecommerce work gets done but isn't visible to shoppers.]

### [Topic Section, e.g., Sales Channels and Channel Strategy]
### [Topic Section, e.g., Growth Stage and Current Priorities]
### [Topic Section, e.g., Seasonality and Calendar]
### [Topic Section, e.g., Product Economics and Margins]

## Additional Context
[Anything the user shared that doesn't fit neatly into the other
sections but is worth capturing. Only include if applicable.]

## Confidence Notes
[Flag any sections based on limited input, assumptions made from
the website alone, or areas where more detail would strengthen
the document. Omit if all sections are well-supported.]
```

The shopper-facing / behind-the-scenes split helps downstream skills understand whether a piece of context is something that should be reflected in customer-facing output (like email copy referencing a shipping policy) or something that informs internal decisions (like which channel to prioritize in a feed optimization). Some topics may have both dimensions. When they do, split the relevant details into the appropriate section rather than duplicating.

The topic sections shown above are examples. Use whatever headings match what the user actually provided. Headings should be descriptive and stable. "Shipping and Fulfillment" is better than "Logistics." "Pricing and Discounting Philosophy" is better than "Pricing." A downstream skill should be able to reference a section by name and find what it expects.

## Edge Cases

### User provides very little information

Produce a lean document from what's available. Use the Confidence Notes section to flag which sections are based on limited input and what additional information would strengthen them. A thin document is still useful context.

### User uploads a large document

Extract only the business context that's relevant to downstream ecommerce work. Don't try to summarize the entire document. Confirm what you extracted and ask if anything important was missed.

### Brand website is sparse or under construction

Fall back to a broader set of topic prompts. Let the user know you weren't able to learn much from the site, so you'll ask a wider range of questions and let them tell you what applies.

### User isn't sure what's important

Offer specific prompts within each topic area to help them think through it. For example, under shipping: "Do you offer free shipping? Is there a threshold? Do customers ask about shipping speed often?" But don't push. If they don't have a strong answer, move on.

### User wants to update the document later

Let them know they can re-run the skill with the existing document uploaded as a starting point. The skill will treat it as existing content and focus on updating or expanding specific sections rather than starting from scratch.

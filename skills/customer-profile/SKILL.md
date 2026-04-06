---
name: customer-profile
description: >-
  Produces a customer profile document from existing personas, analytics
  data, review insights, and direct user knowledge. Gives downstream
  skills and team members context about the brand's customer persona(s).
license: Apache-2.0
---

# Build a Customer Profile

This skill produces a customer profile document from whatever combination of inputs the user has available. The profile gives downstream skills and team members context about the brand's customer persona(s), so that copy, merchandising, and product decisions can be made with the customer in mind.

Output depth and focus scale to input quality. The agent synthesizes what the inputs reveal about the target customer and organizes the profile accordingly. Every claim in the output should tie back to a source. Nothing is fabricated to fill space.

For reference on the expected output, see
[references/example-output.md](references/example-output.md).

## Voice and Approach

Be direct and practical. The user is sharing what they know about their customer, and your job is to synthesize it into something useful. Don't over-explain what a customer profile is or why it matters. The user already knows. Match the user's level of sophistication. If they hand you a polished persona deck, respond at that level. If they describe their customer in casual terms, meet them there. Keep the conversation moving. This skill should feel like a quick, productive working session, not a research project.

## Conversation Flow

### Turn 1: Collect Inputs

Ask the user what they have available. The skill works with any combination of:

- Existing persona documents, customer research, or segmentation decks
- Analytics exports or summaries (GA4, Shopify, platform dashboards, screenshots). If the user has GA4, the Demographics and Audiences reports are especially useful.
- Their own knowledge of their customers, shared conversationally
- Output from the Extract Review Insights skill (recommend this if they want to incorporate review data)

No single input type is required. If the user has one source, that's fine. If they have several, take them all.

Let the user know that if they want to incorporate customer review data, the Extract Review Insights skill is a good first step. It pulls structured insights from reviews that this skill can use directly. This is a recommendation, not a requirement.

Accept whatever the user provides and move forward. If they upload files, read them. If they paste text, work with it. If they just start talking about their customer, that's valid input too.

### Turn 2: Fill Gaps (if needed)

After reviewing the inputs, identify whether there are gaps that the user could easily fill with information they likely have but didn't think to share. Ask targeted follow-up questions. Keep it to one round of questions. If the user doesn't have the answers, move on.

If the inputs are rich enough to produce a useful profile, skip this turn entirely and go straight to producing the output.

### Turn 3: Produce the Profile

Synthesize the inputs into a customer profile document. How you organize it depends on what the inputs tell you. A brand with one clear customer segment needs a different structure than a brand with three distinct audiences. A profile built from a rich persona deck and analytics data will look different from one built on a short conversation.

The guiding principle: a team member or downstream skill reading this document should come away with a clear understanding of who the customer is, grounded in evidence, not generalities.

For each claim or insight in the profile, make it clear where it came from (the persona doc, the analytics data, the user's direct input, the review insights). This doesn't need to be heavy-handed or formatted as citations. A natural reference is fine ("Analytics show that..." or "Based on the persona document...").

End the profile with a confidence summary. Flag which parts of the profile are well-supported by multiple sources, which are based on a single input, and which are inferred. Be honest about what's thin.

Present the output as a downloadable document. Ask the user to review it.

### Turn 4+: Revise

When the user requests changes, edit the document in place. Do not regenerate the entire profile for a single correction. If the user provides additional inputs after seeing the first draft, incorporate them and note the new sources.

## Edge Cases

### Single input source

The user provides only one thing (just a persona doc, just a conversation about their customers, just analytics screenshots). Produce the best profile you can from that input. The confidence summary should be straightforward about the profile being based on a single source.

### Conflicting signals across sources

If the persona doc says one thing and the analytics suggest another, document both. Do not silently average them or pick one. Surface the conflict so the user can resolve it.

### Analytics as screenshots or summaries

The user may not have raw exports. They might paste a screenshot of a GA4 report or summarize their analytics from memory. Work with whatever fidelity they provide. Note in the confidence summary when insights are based on summarized rather than raw data.

### One segment versus several

Some brands have one core customer. Others serve distinct segments. Let the data determine this. Do not force segmentation when the inputs describe a single audience, and do not collapse distinct segments into one when the inputs clearly show differentiation.

### The user just talks

Some users won't upload anything. They'll describe their customer in conversation. That's a valid input. Synthesize what they tell you into the profile and attribute it as direct input from the team. The confidence summary should reflect that the profile is based on internal knowledge rather than external data.

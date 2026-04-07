```markdown
---
name: competitor-overview
description: >-
  Researches a set of competitors identified by the user and produces a
  competitor overview document capturing each competitor's positioning,
  messaging, target audience, and market perception. Accepts a list of
  competitor names and the user's category for context. Output is a
  foundation document consumed by positioning briefs, comparison copy,
  and other downstream skills.
license: Apache-2.0
---

# Research Your Competitors

This skill takes a list of competitors from the user, researches each one using their public web presence, and produces a competitor overview document. The document captures how each competitor positions themselves, what they say, who they're targeting, and how the market perceives them. It does not compare competitors back to the user's brand. That analysis belongs in downstream skills like the positioning brief, which consumes this document as input.

For reference on the expected output, see [references/example-output.md](references/example-output.md).

## Voice and Approach

Be direct and efficient. The user is sharing competitors they already know about, so don't over-explain what a competitive overview is or why it matters. Get the list, do the research, present what you found. When presenting findings, be specific and evidence-based. Don't editorialize or speculate beyond what the research supports. If a competitor's site is vague or thin, say so rather than inflating weak evidence into confident claims.

## Conversation Flow

### Turn 1: Collect the List

Ask the user for their competitor list and their own brand name and category. The brand and category give you a lens for the research, not a basis for comparison. Accept whatever format the user provides: a simple list of names, names with context, or a longer explanation of the competitive landscape.

If the user shares additional context about specific competitors ("they're the budget option," "they just launched a DTC channel"), note it. This context helps focus the research but should be validated against what the competitor's own presence says.

If the user lists more than six or seven competitors, flag that the research quality will be better with a tighter list and suggest prioritizing. Offer to do a first pass on their top five and come back for the rest.

### Turn 2: Research and Present

Research each competitor using their public web presence and third-party sources. For each competitor, capture whatever the research supports across these dimensions:

- **Positioning:** How they describe themselves and their value proposition. What they lead with.
- **Target audience:** Who they appear to be selling to, based on messaging, imagery, and product range.
- **Messaging patterns:** The language they use, recurring themes, tone and register.
- **Product/service focus:** What they emphasize, what they seem to deprioritize, how broad or narrow their range is.
- **Channel presence:** Where they sell (DTC, marketplaces, retail, wholesale) if discernible.
- **Market perception:** What third-party sources (reviews, press, forums) say about them, if available.

If pricing is visible and straightforward (a public pricing page, clearly listed price points), note it briefly. But don't try to characterize a competitor's pricing strategy from a handful of SKUs or a single pricing page. Incomplete pricing data is easy to misread, and the resulting claims tend to be more misleading than useful.

These dimensions are a menu, not a checklist. Write what the research supports. If a competitor's pricing isn't visible, skip that dimension. If their messaging is generic and doesn't reveal much, say that in a sentence rather than padding it into a full section. A competitor with a rich public presence should get a detailed profile. A competitor with a thin or generic site should get a short one. The depth should reflect the evidence, not a template.

Present all findings in a single document. After the per-competitor profiles, include a landscape summary that describes patterns across the group: common positioning themes, audience overlaps, messaging conventions in the category. This summary describes the competitive field on its own terms.

After sharing the document, ask the user to review. They will often know things the research can't surface (recent pivots, reputation in the market, sales conversations) and this is where that knowledge gets folded in.

### Turn 3+: Review and Refine

When the user provides corrections or additional context, update the document in place. If they add information that enriches a thin profile, incorporate it and note the source ("based on your input" or similar) so downstream skills can distinguish research-based findings from user-supplied context.

If the user identifies a competitor that was missed or wants to add one, research it and add it to the document.

## Research Guidelines

For each competitor, start by visiting their actual website. Fetch their homepage, about page, and at least one product or collection page. This is non-negotiable. Do not build a competitor profile from search results about a brand without having visited the brand's own site. Articles and analyses written about a company are no substitute for reading what the company says about itself in its own words.

After visiting the site, use web search to supplement with third-party perspectives: review sites (G2, Trustpilot, Capterra), press coverage, industry reports, forum discussions. This is where you find reputation, common complaints, and how the competitor is actually perceived versus how they want to be perceived. The gap between first-party and third-party is often the most interesting finding.

When writing profiles, make the source legible. "Their homepage leads with sustainability messaging" is a first-party finding based on visiting their site. "They have a 4.2 on G2 with reviewers frequently citing ease of setup" is third-party. Both belong in the profile, and downstream skills benefit from knowing which is which.

Be precise about what you found versus what you're inferring. "Their homepage leads with sustainability messaging" is a finding. "They appear to be targeting environmentally conscious consumers" is a reasonable inference. "They're the sustainability leader in the category" is a claim you probably can't support.

If a competitor's website is behind a login, is mostly an app with no marketing site, or is otherwise inaccessible, note that and work with whatever is available.

## Output Structure

The output is a Markdown document. The structure adapts to the research rather than following a rigid template.

Each competitor gets a section headed with their name. Within that section, include whichever dimensions the research supports. Use subheadings for dimensions when there's enough to say, or combine lighter dimensions into prose when a subheading would feel like overkill for a sentence or two.

After all competitor profiles, include a Landscape Summary section that identifies patterns across the competitive field.

If any profiles are based on limited information, include a Coverage Notes section at the end that flags which competitors had thin research and what would help fill the gaps.

```
# Competitor Overview

## [Competitor Name]
[Profile with relevant dimensions, depth proportional to evidence]

## [Competitor Name]
[Profile with relevant dimensions, depth proportional to evidence]

...

## Landscape Summary
[Patterns, clusters, common themes across the competitive field]

## Coverage Notes (if needed)
[Which competitors had limited information, what would help]
```

## Edge Cases

### Competitor has very little public presence

Some competitors operate primarily through marketplaces, wholesale, or word of mouth and have minimal web presence. Produce a short profile noting what's available and what isn't. Don't pad a thin profile with speculation.

### Competitor is in an adjacent category

If research reveals a listed competitor operates in a different category than the user's, note it and ask the user whether to keep them in the overview. They may have a good reason for including them, or it may have been a mistake.

### User provides extensive context upfront

If the user shares detailed knowledge about competitors in Turn 1, incorporate it into the profiles alongside the research. Distinguish between user-provided context and research findings so downstream skills know the source.

### Very large competitor list

If the user lists more than six or seven competitors, suggest prioritizing. Research quality degrades when spread too thin. Offer to handle them in batches.
```

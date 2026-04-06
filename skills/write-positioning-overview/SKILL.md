---
name: write-positioning-overview
description: >-
  Produces a positioning brief from existing brand content, guided conversation,
  or both. Covers target customer, differentiators, competitive context, and
  anti-positioning. Output is a foundation document consumed by content
  generation, merchandising, and other downstream skills.
license: Apache-2.0
---

# Write a Positioning Brief

This skill produces a brand positioning brief from whatever the user already has: existing brand content, conversational answers, a competitor overview, or any combination. The output is designed to be saved and uploaded alongside content-generation and merchandising skills (product descriptions, landing pages, emails, quizzes, collection descriptions) so that AI-generated content reflects the brand's actual positioning instead of producing generic category copy.

For reference on the expected output, see [references/example-positioning-brief.md](references/example-positioning-brief.md).

## Voice and Approach

Be direct and efficient. The user is here to document their positioning, not learn what positioning is. Don't explain why positioning matters or what a positioning brief is for. Collect what they have, synthesize it, and present a draft they can react to.

When synthesizing, be honest about what the input supports. A brief built from a rich brand deck and a competitor overview will be more detailed than one built from a five-minute conversation. Both are useful. The goal is to capture what is specifically true about this brand, not to produce a document that looks thorough.

## Conversation Flow

### Turn 1: Start with the Brand

Ask the user for their brand name and website URL. If web browsing is available, visit the site and pull positioning-relevant content directly: homepage, about page, product or collection pages, and any mission or values content you can find. This gives you a first-party foundation to work from without the user having to copy-paste their own site.

After reviewing the site (or if browsing isn't available), ask the user for anything the site doesn't capture or that they want to add:

- Internal brand guidelines or strategy documents
- Notes on what they think is strong or weak in their current positioning
- Context about their customers, competitors, or market that isn't on the site
- Output from the Research Your Competitors skill (strengthens competitive context)
- Output from the Build a Customer Profile skill (strengthens the "who we serve" dimension)

The user may provide a lot, a little, or nothing beyond the URL. All are fine. If browsing isn't available, ask the user to paste or upload the content directly: homepage copy, about page, product pages, press boilerplate, whatever they have.

If the user doesn't have a website yet (pre-launch), skip the browsing step and ask them to describe their brand conversationally: what they sell, who they sell to, what problem they solve, and what makes them different from the alternatives their customer considers.

### Turn 2: Follow Up or Produce

After reviewing the input, decide whether you have enough to produce a useful brief.

If the input is rich enough, go straight to producing the brief. Don't ask follow-up questions for the sake of completeness. A positioning brief with five strong dimensions is better than one with nine mediocre ones.

If there are real gaps (you don't understand who the customer is, or you can't identify a single differentiator that's specific to this brand), ask targeted follow-ups. Keep it to one round, no more than three or four questions, focused on the gaps that matter most. Differentiators, target customer, and the problem the brand solves are the highest-value dimensions. If competitive context is thin, note it in the confidence summary rather than interrogating the user about competitors.

### Turn 3+: Review and Refine

Present the brief as a downloadable document. Ask the user to review it.

When the user provides corrections, additional context, or pushback, edit the document in place. If they provide new input that changes the positioning (not just adds detail), update the affected dimensions and note what changed.

## Synthesis Instructions

Read all provided material and site content before writing anything. The goal is to organize and sharpen what the brand's public presence and the user's input reveal about their positioning, not to invent positioning for them.

**Organize, do not invent.** The positioning brief codifies what the user communicates about their brand. Do not introduce strategic ideas, differentiators, or customer segments that the user did not provide or confirm. You may reframe and sharpen their language, but the substance must come from them.

**Specificity required.** Every claim in the brief must be specific to this brand. If a statement could apply to any brand in the category ("we use high-quality ingredients," "we care about our customers"), it is too generic. If the user's input is generic on a dimension, reflect that honestly rather than fabricating specificity. The confidence summary is the right place to flag this.

**Plain language.** Write in clear, direct language. Avoid marketing jargon, buzzwords, and abstraction. The brief is a reference document for AI tools and team members, not a manifesto. "We make technical outdoor gear for weekend hikers who don't want to spend $400 on a jacket" is more useful than "We democratize the outdoors through accessible performance innovation."

**Tension is useful.** Good positioning creates tension because it implies what the brand is not. If the brief doesn't exclude anything, it doesn't position anything. "We make gear for weekend hikers" is useful because it implies "not for ultralight thru-hikers or casual fashion buyers."

**Depth follows input.** The brief's depth and detail should reflect what the input actually supports. A brand that provided a rich competitor overview gets a detailed competitive context section. A brand that described their customer in two sentences gets a shorter "who we serve" section. Do not pad thin input into thick sections.

## Output Structure

The output is a Markdown document. It opens with a positioning statement and then covers whichever of the following dimensions the input supports. These are a menu, not a checklist. Include what the input gives you evidence for. Skip or combine dimensions that would be thin or redundant.

**Positioning statement.** 2-3 sentences that capture what the brand is, who it serves, and why it matters. This is the anchor. A person unfamiliar with the brand should be able to read this and make accurate judgments about tone, audience, and emphasis. This is not a tagline. It is a clear, internal-facing articulation of the brand's position.

**What we sell.** The product category, specific product types or lines, and price positioning if evident. Be concrete: "organic dog treats and supplements" not "premium pet wellness products."

**The problem we exist to solve.** The customer pain or unmet need, framed from the customer's perspective. What their world looks like before this brand's product enters it.

**Who we serve.** A profile of the core customer described in terms of motivations and behavior, not just demographics. What they care about, what they've tried before, why alternatives haven't fully satisfied them. If the brand serves meaningfully different segments, describe them. If it serves one clear audience, don't force segmentation.

**Why they choose us.** Differentiators with supporting proof points. Each differentiator must be specific to this brand. If the user didn't provide a concrete proof point, note what kind of evidence would strengthen it rather than inventing one.

**Competitive context.** How the brand relates to the alternatives the customer considers. Where it overlaps with competitors, where it diverges, and language to avoid because competitors own it. If the user provided a competitor overview from the Research Your Competitors skill, draw on it for this section. If they didn't, work with whatever competitive context they shared and note the limitation. This section is about positioning relative to the field, not competitor research. That's a different skill.

**What we are not.** Anti-positioning: what the brand does not want to be, sound like, or be associated with. These should create real constraints. "We are not a luxury brand" is useful. "We are not dishonest" is not. This section serves as a guardrail for all downstream content.

**How to use this brief.** A short note: save this document, upload it alongside other skills when generating content, provide it in full rather than excerpting. Positioning is the combination of all dimensions working together. This brief pairs well with a brand voice guide. Positioning defines what you say; voice defines how you say it.

End the document with a **Confidence summary** that flags which dimensions are well-supported, which are based on limited input, and which are inferred. Be honest about what's thin and suggest what additional context would strengthen those areas.

## Edge Cases

### Very thin input

Produce the brief with whatever you have. The confidence summary should be straightforward about the limitations. A rough positioning brief is more useful than no positioning brief. Focus on the dimensions the input actually supports rather than stretching thin input across the full template.

### Generic or undifferentiated positioning

If the user's input is heavily generic ("we offer high-quality products with great customer service"), push back constructively during the follow-up: "Every brand in your category claims quality and great service. What's something specific about your brand that a competitor couldn't easily say? It might be a process, an ingredient source, a design philosophy, a founder story, or a customer experience detail."

If the user cannot provide specifics, produce the brief honestly. Flag generic differentiators in the confidence summary and recommend exercises to sharpen them (customer interviews, competitor review analysis, founder story mining).

### Multiple product lines with different positioning

Ask whether the user wants a single brand-level brief or separate briefs per product line. If they choose a single brief, note line-level variation within the relevant dimensions rather than forcing a uniform profile.

### Pre-launch brands

Accept the user's intended positioning at face value. Note in the confidence summary that the brief reflects intended positioning rather than market-validated positioning, and recommend revisiting after customer feedback accumulates.

### Competitive information is thin or absent

Produce the brief without forcing a competitive context section. Note in the confidence summary that competitive context would strengthen the brief, and mention the Research Your Competitors skill as a way to build that input.

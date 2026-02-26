---
name: write-positioning-overview
description: >-
  Produces a structured brand and product positioning brief from existing brand
  content or conversational answers. Accepts About Us pages, pitch decks,
  homepage copy, or direct answers to guided prompts. Identifies gaps in the
  provided material and asks targeted follow-up questions. Outputs a one-page
  positioning brief covering positioning statement, target customer, key
  differentiators, value propositions, competitive context, and anti-positioning.
  Designed as a foundational primitive that downstream content-generation and
  merchandising skills consume as a reference input.
license: Apache-2.0
---

# Write a Brand and Product Positioning Overview

This skill produces a brand positioning brief from whatever the user already has — existing brand content, conversational answers, or both. The output is designed to be saved and uploaded alongside content-generation and merchandising skills (product descriptions, landing pages, emails, bundles, quizzes, collection descriptions) so that AI-generated content reflects the brand's actual positioning instead of producing generic category copy.

The quality of this brief determines whether downstream content differentiates the brand or blends into the category. A useful positioning brief documents what is specifically true about this brand, not what every brand in the category claims.

For reference on the expected output format and level of detail, see [examples/sample-positioning-brief.md](examples/sample-positioning-brief.md).

## Interaction flow

Follow these four steps in order. Do not skip the positioning calibration step.

### Step 1: Collect brand context

Ask the user to share whatever positioning-relevant material they already have. Suggest specific content types:

- About Us or brand story page
- Homepage hero copy or tagline
- Pitch deck introduction (pasted as text)
- Kickstarter or crowdfunding campaign description
- Investor summary or one-pager
- Brand guidelines (the strategy section, not visual identity)
- Product packaging copy that explains the brand
- Press page or boilerplate

Tell them to paste everything in a single message. If they have notes about what they think is strong or weak in their current positioning, they should include those.

If the user does not have existing content, or prefers to start from scratch, offer these prompts instead:

1. What do you sell? (Product category and the specific products or product lines.)
2. What problem does your product solve? (The customer pain, frustration, or unmet need that led you to build this.)
3. Who is your core customer? (Not just demographics — what do they care about, what are they trying to accomplish, what have they tried before?)
4. Why do customers choose you over alternatives? (What you hear from actual customers about why they bought, switched, or stayed.)
5. What makes you genuinely different? (Not "high quality" or "great customer service" — what would be hard for a competitor to claim?)
6. Who are your main competitors, and how is your approach different from theirs?
7. What do you never want your brand to sound like or be associated with?

The user may paste content, answer the prompts, or do both. Accept whatever they provide.

### Step 2: Gap analysis and follow-up

After receiving the user's input, silently map what they provided against the nine sections of the output brief:

1. Positioning statement
2. What we sell
3. The problem we exist to solve
4. Who we serve
5. Why they choose us (differentiators)
6. Value propositions
7. Competitive context
8. What we are not
9. How to use this document (no user input needed)

For any section where the user's input provides sufficient information, do not ask about it again.

For sections where the input is thin, ambiguous, or missing, ask targeted follow-up questions — only for the gaps. Frame each question with a brief explanation of why it matters:

- "You mentioned your customers care about sustainability, but I didn't see what specifically makes your approach different from competitors who also claim sustainability. Can you tell me what you do differently — sourcing, materials, certifications, transparency practices?"
- "Your About Us page describes what you sell clearly, but I didn't find who your core customer is. Can you describe your best customer — not just age and gender, but what they care about and what they've tried before?"

Ask all follow-up questions in a single message. Do not ask more than 4 follow-up questions. If more than 4 sections have gaps, prioritize: differentiators, target customer, the problem you solve, and competitive context are the most critical. The positioning statement and value propositions can be synthesized from strong answers to the others.

If the user's initial input is comprehensive enough that no sections have meaningful gaps, skip directly to Step 3.

### Step 3: Positioning calibration

After collecting sufficient input, perform a preliminary positioning analysis silently. Do not share the analysis yet. Instead, do the following:

1. Identify the brand's product category and target market from the input.
2. Write the brand's positioning statement in three distinct framings labeled **A**, **B**, and **C**. Each framing is a single paragraph (2-3 sentences) that captures what the brand is, who it serves, and why it matters.

Each variation must be a plausible interpretation of the brand's positioning based on the user's input, but they should lead with different strategic angles. For example:

- One variation might lead with the problem the brand solves
- Another might lead with the customer identity and what they value
- Another might lead with the brand's unique approach or methodology

Do not label the variations with strategic descriptors like "problem-led" or "customer-led." Present them neutrally as A, B, and C so the user reacts to the framing itself, not to the label.

Ask the user: "Which of these captures your brand's positioning best? If none is exactly right, tell me what you'd change — or what you liked from more than one."

Use the user's selection (and any notes about what they liked or disliked) to calibrate the final brief. The chosen framing anchors the positioning statement. Where the user's input supports multiple interpretations, weight the analysis toward the interpretation that aligns with their pick.

### Step 4: Produce the positioning brief

Generate the complete positioning brief using the format specified below. The brief must reflect both the information from the user's input and the calibration signal from the user's selection in Step 3.

## Synthesis instructions

Read all provided material before writing anything. The goal is to organize and sharpen what the user already knows about their brand, not to invent positioning for them.

### Core principles

- **Organize, do not invent.** The positioning brief codifies what the user communicates about their brand. Do not introduce strategic ideas, differentiators, or customer segments that the user did not provide or confirm. You may reframe and sharpen their language, but the substance must come from them.
- **Specificity required.** Every claim in the brief must be specific to this brand. If a statement could apply to any brand in the category (e.g., "we use high-quality ingredients," "we care about our customers"), it is too generic. Push for what is distinctively true. If the user's input is generic on a dimension, reflect that honestly rather than fabricating specificity.
- **Calibration weighting.** Where the user's input supports multiple interpretations, weight toward the interpretation that aligns with their choice in Step 3.
- **Plain language.** Write in clear, direct language. Avoid marketing jargon, buzzwords, and abstraction. The brief is a reference document for AI tools and team members, not a manifesto. "We make technical outdoor gear for weekend hikers who don't want to spend $400 on a jacket" is more useful than "We democratize the outdoors through accessible performance innovation."
- **Tension is useful.** Good positioning creates tension — it implies what the brand is not. If the brief doesn't exclude anything, it doesn't position anything. "We make gear for weekend hikers" is useful because it implies "not for ultralight thru-hikers or casual fashion buyers."

## Output format

Produce the positioning brief as a Markdown document with the following structure. Use this exact heading hierarchy so the brief is consistent and parseable by downstream skills.

```
# [Brand Name] Positioning Brief
```

If the brand name is not evident from the input, ask the user.

### Positioning statement

Write a 2-3 sentence paragraph that captures the brand's core positioning. This is the anchor for everything else in the document. A person unfamiliar with the brand should be able to read this paragraph and immediately understand what the brand is, who it serves, and why it matters.

This is not a tagline. It is a clear, internal-facing articulation of the brand's position in the market. It should be specific enough that a content creator could read it and make accurate judgments about tone, audience, and emphasis without reading the rest of the brief.

Base this on the user's calibration selection from Step 3, refined with any feedback they provided.

### What we sell

One concise paragraph describing the product category and the specific products or product lines. Be concrete: "organic dog treats and supplements" is useful; "premium pet wellness products" is not.

Include:
- The product category in plain language
- The specific product types or lines (if the brand sells more than one)
- The price positioning if evident from the user's input (budget, mid-range, premium, luxury) — state it factually, not aspirationally

### The problem we exist to solve

One paragraph describing the customer pain, frustration, or unmet need that the brand addresses. Frame this from the customer's perspective — what their world looks like before this brand's product enters it.

This section is not about the product. It is about the situation the customer is in. A good problem statement makes the reader nod and think "yes, that's exactly the frustration."

If the brand addresses different problems for different customer segments, note the primary problem and up to two secondary ones.

### Who we serve

A profile of the brand's core customer. This is not a demographic checkbox ("women 25-45"). It is a description of the person — what they care about, what they are trying to accomplish, what they have tried before, and why existing alternatives have not fully satisfied them.

Include:
- **Core customer:** The primary buyer, described in terms of motivations and behavior, not just demographics.
- **What they value:** The 2-3 things that matter most to this customer when making a purchase decision in this category.
- **What they've tried:** Where they have been before — competitors they've used, approaches they've taken, why those weren't sufficient.

If the brand serves meaningfully different customer segments, describe up to 3. Each segment should be distinct in what they value and why they buy, not just in age or income.

### Why they choose us

3-5 key differentiators, each with a supporting proof point. These are the reasons a customer picks this brand over the alternatives.

For each differentiator, use this structure:

```
**[Differentiator]:** [One sentence explaining the claim.]
*Proof:* [Specific evidence — a fact, number, process detail, or customer quote that makes this credible rather than aspirational.]
```

Requirements:
- Each differentiator must be specific to this brand. "High quality" is not a differentiator. "Hand-stitched by a single artisan using vegetable-tanned leather, with a visible maker's mark on every piece" is a differentiator.
- If the user did not provide a concrete proof point for a differentiator, note what kind of evidence would strengthen it (e.g., "Could be strengthened with: specific sourcing details, a number, or a customer quote").
- Order differentiators by importance to the customer, not by importance to the brand.

### Value propositions

Value propositions framed by customer need, not by product feature. Each proposition connects a customer problem or desire to a specific way the brand delivers.

Use this structure:

```
**For [customer need/situation]:** [How the brand delivers on it.]
```

Include 3-5 value propositions. These should feel like answers to the question "why should I buy this?" from different angles — functional, emotional, social, or practical.

At least one value proposition should address an emotional or identity-level need, not just a functional one. People buy products for reasons beyond the spec sheet.

### Competitive context

How the brand is positioned relative to alternatives the customer considers. This section is not a competitive teardown — it is context that helps content creators frame the brand correctly.

Include:
- **The alternatives:** Who or what the customer would choose instead (specific competitors and/or non-purchase alternatives like "doing nothing" or "DIY").
- **Where we overlap:** What the brand has in common with competitors. Acknowledging shared ground is honest and builds credibility.
- **Where we diverge:** The specific ways this brand's approach differs. These should be observable differences, not just claims.
- **Language to avoid because competitors own it:** Specific words, phrases, or claims that are heavily associated with competitors and would make this brand sound like an imitation.

### What we are not

Explicit anti-positioning: what the brand does not want to be, sound like, or be associated with. This section serves as a guardrail for all downstream content.

Include 3-5 statements, each with a brief explanation of why. For example:
- "We are not a luxury brand — we don't use aspirational lifestyle imagery or exclusivity language. Our positioning is accessible expertise, not status."
- "We are not a discount brand — we don't compete on price and never lead with discounts or savings language."

These statements should create real constraints. If a statement would apply to any brand ("We are not dishonest"), it is not useful. Useful anti-positioning excludes a real strategic direction the brand could take but chooses not to.

### How to use this brief

End the document with a brief section explaining:

- Save this document and keep it accessible.
- When using AI skills for content generation (product descriptions, emails, landing pages, social copy, quizzes, bundles, collection descriptions), upload or paste this brief alongside your request.
- Provide the brief in full rather than excerpting individual sections. Positioning is the combination of all dimensions — who you serve, what makes you different, and what you are not — working together.
- This brief pairs well with a brand voice guide. Positioning defines what you say; voice defines how you say it.

## Edge cases

### Very thin input

If the user provides only 1-2 sentences or a very brief description, produce the brief but add a **Confidence notes** section at the end. Flag which sections are based on limited information and suggest what additional context would strengthen the brief. Focus the follow-up questions on the highest-value gaps: differentiators, target customer, and the problem the brand solves.

Do not refuse to produce output. A rough positioning brief is more useful than no positioning brief.

### Generic or undifferentiated positioning

If the user's input is heavily generic ("we offer high-quality products with great customer service"), do not accept it at face value and do not pad it into something that sounds more strategic than it is.

Instead, push back constructively during the follow-up step: "Every brand in your category claims quality and great service. What's something specific about your brand that a competitor couldn't easily say? It might be a process, an ingredient source, a design philosophy, a founder story, or a customer experience detail."

If the user cannot provide specifics after the follow-up, produce the brief honestly. Use the Confidence notes section to flag which differentiators are generic and recommend exercises to sharpen them (customer interviews, competitor review analysis, founder story mining).

### Multiple product lines with different positioning

If the brand sells product lines that serve different customers or solve different problems (e.g., a skincare brand with a clinical line and a naturals line), ask whether the user wants:

1. A single brief covering the brand-level positioning (recommended for most brands)
2. Separate briefs per product line

If they choose a single brief, note line-level variation within the relevant sections rather than forcing a uniform profile. "The clinical line targets customers managing specific skin conditions and leads with ingredient efficacy; the naturals line targets customers seeking simple daily care and leads with ingredient transparency."

### Pre-launch brands

Accept the user's intended positioning at face value. Note in the Confidence section that the brief reflects intended positioning rather than market-validated positioning, and recommend revisiting after 3-6 months of customer feedback. Pre-launch brands often discover that their actual customer and their imagined customer are different.

### Competitive information is thin or absent

Produce the brief without the "Language to avoid" subsection of Competitive context. Note in Confidence that competitive context would strengthen the brief, and recommend the user provide competitor homepage copy, taglines, or product descriptions in a future revision. Suggest the "Create a competitive positioning snapshot" skill for deeper competitive analysis.

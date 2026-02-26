---
name: document-brand-voice
description: >-
  Extracts a structured brand voice guide from example content samples the user
  provides. Analyzes tone, vocabulary, sentence structure, and formatting patterns
  across 5-10 pieces of representative brand content and produces a reusable
  reference document with tone spectrums, word lists, style rules, and
  before/after demonstration rewrites. Designed as a foundational primitive
  that improves the output of all content-generation skills.
license: Apache-2.0
---

# Document Your Brand Voice

This skill produces a brand voice reference document from example content. The output is designed to be saved and uploaded alongside content-generation skills (product descriptions, emails, landing pages, social copy) so that AI-generated content matches the brand's actual voice instead of sounding generic.

The quality of this document determines whether downstream content sounds like the brand or sounds like every other brand in the category. Specificity is everything — a useful voice guide documents what this brand actually does, not what brands in general should aspire to.

For reference on the expected output format and level of detail, see [examples/sample-brand-voice-guide.md](examples/sample-brand-voice-guide.md).

## Interaction flow

Follow these three steps in order. Do not skip the voice calibration step.

### Step 1: Collect content samples

Ask the user to paste 5-10 pieces of content that represent how their brand should sound. Suggest specific content types they might include:

- Product descriptions
- Marketing emails or email subject lines
- Homepage or landing page copy
- Social media captions
- About page or brand story text
- Packaging copy or taglines
- Blog post introductions
- Customer-facing notifications or transactional messages

Tell them to paste all samples in a single message. If they have notes about what they like or dislike about specific samples, they should include those alongside the relevant sample.

If the user provides fewer than 3 samples, accept them but note that the voice guide will be more accurate with 5-10 samples spanning at least 2-3 different content types.

### Step 2: Voice calibration

After receiving the samples, perform a preliminary voice analysis silently. Do not share the analysis yet. Instead, do the following:

1. Identify the user's product category from the samples (skincare, outdoor gear, pet products, home goods, food and beverage, apparel, etc.).
2. Choose a plausible product in that category that was not mentioned in the samples.
3. Write a short product description paragraph (3-4 sentences) for that product in three distinct voice interpretations labeled **A**, **B**, and **C**.

Each variation must be a plausible reading of the voice in the samples, but they should differ meaningfully along at least two dimensions. For example:

- One variation might lean more casual and warm
- Another might lean more polished and authoritative
- Another might lean more minimal and direct

Do not label the variations with descriptors like "casual" or "authoritative." Present them neutrally as A, B, and C so the user reacts to the writing itself, not to the label.

Ask the user: "Which of these sounds most like your brand? If none is exactly right, tell me what you would change — or what you liked from more than one."

Use the user's selection (and any notes about what they liked or disliked) to calibrate the final analysis. The chosen variation anchors the voice profile. Where the samples are ambiguous, weight the analysis toward the interpretation that aligns with the user's pick.

### Step 3: Produce the brand voice guide

Generate the complete brand voice guide using the format specified below. The guide must reflect both the patterns observed in the samples and the calibration signal from the user's selection in Step 2.

## Analysis instructions

Read all samples before writing anything. The goal is to extract what the brand's content actually does, not to prescribe what it should do.

### Core principles

- **Extract, do not impose.** Describe what the samples actually do. Do not describe what you think the brand should sound like or what brands in this category typically sound like.
- **Evidence required.** Every claim in the voice guide must be supported by a specific phrase, pattern, or example from the samples. If you cannot point to evidence, do not include the claim.
- **Pattern threshold.** A pattern observed in a single sample is an anomaly. A pattern observed in three or more samples is a voice characteristic. Patterns observed in two samples may be noted with lower confidence.
- **Calibration weighting.** Where the samples support multiple interpretations, weight toward the interpretation that aligns with the user's choice in Step 2.

### Dimensions to analyze

Analyze the samples across these six dimensions:

**1. Tone spectrums.** Position the brand on each of these spectrums based on evidence in the samples:

- Formal ---- Casual
- Serious ---- Playful
- Technical ---- Accessible
- Reserved ---- Enthusiastic
- Authoritative ---- Conversational
- Minimal ---- Expressive

For each spectrum, cite a specific phrase or pattern from the samples that supports the placement. Do not position the brand on a spectrum without evidence.

**2. Vocabulary.** Extract:

- Words and phrases the brand uses repeatedly (minimum 2 occurrences across samples). Group by function: descriptive words, action verbs, connectors, and calls-to-action.
- Words and phrases the brand appears to avoid — inferred from their consistent absence despite being common in the product category.
- How the brand handles jargon and technical terms: does it use industry language, define it, avoid it, or replace it with plain language?

Focus on vocabulary that distinguishes this brand from others in the same category. "Quality," "premium," and "trusted" appear in every brand's copy and are not useful entries. Document what is distinctive.

**3. Sentence structure.** Document:

- Typical sentence length: short and punchy, medium, long and flowing, or deliberately mixed.
- Preferred sentence types: simple declarative, compound, fragments, rhetorical questions, imperatives.
- How the brand opens paragraphs and descriptions: does it lead with a benefit, a feature, an emotion, a question, or a command?
- Person and address: does the brand use "you" (second person), "we" (first person), or describe the product in third person? Is the customer addressed as a peer, someone to advise, or someone to serve?

**4. Punctuation and formatting.** Document:

- Exclamation mark frequency: frequent, occasional, or absent.
- Use of em dashes, ellipses, colons, or parenthetical asides.
- Capitalization patterns: title case, sentence case, or all-caps for emphasis.
- Preference for bullet points versus flowing paragraphs.
- Emoji usage: present and frequent, occasional, or absent.

**5. Rhetorical patterns.** Identify:

- How the brand makes benefit claims: direct assertion, sensory language, social proof, aspirational framing, or scientific/technical backing.
- Whether the brand uses humor, storytelling, urgency, scarcity, or exclusivity — and how frequently.
- How the brand builds trust: through expertise, relatability, transparency, credentials, or community.
- How the brand addresses objections or concerns: preemptively, through FAQ-style content, or not at all.

**6. Cross-content-type variation.** If the samples span multiple content types (product pages, emails, social, etc.), note where the voice shifts. Real brands modulate their voice across channels. Document the variation rather than forcing a single uniform profile.

For example: "Product descriptions use a more technical and detailed voice, while social captions are shorter and more playful. Email subject lines use urgency that does not appear elsewhere."

## Output format

Produce the brand voice guide as a Markdown document with the following structure. Use this exact heading hierarchy so the guide is consistent and parseable by downstream skills.

```
# [Brand Name] Brand Voice Guide
```

If the brand name is not evident from the samples, ask the user or use a placeholder.

### Voice summary

Write 2-3 sentences that capture the overall feel of the brand's voice. This is not a list of adjectives. It is a paragraph that someone could read and immediately understand how the brand sounds. A person unfamiliar with the brand should be able to read this summary and produce a reasonable first draft in the right voice.

### Tone spectrums

Present as a table:

```
| Spectrum | Position | Evidence |
|----------|----------|----------|
| Formal ↔ Casual | [position description] | "[quoted phrase or pattern from samples]" |
```

Position descriptions should be specific, not just "slightly casual." Use language like "Casual but never sloppy — contractions are standard, slang is absent" or "Formal in structure but warm in word choice."

### Vocabulary

Three subsections:

- **Words and phrases to use:** grouped by function (descriptive, action, connectors, CTAs), each with the context where it appeared.
- **Words and phrases to avoid:** each with reasoning grounded in the samples — why it does not fit this voice.
- **Jargon handling:** how the brand treats technical or industry-specific terms, with examples.

### Sentence style

Two subsections:

- **Structure patterns:** sentence length, complexity, opening patterns, with examples from the samples.
- **Person and address:** how the brand speaks to and about the customer, with quoted examples.

### Formatting conventions

Document punctuation, capitalization, list formatting, and emoji usage patterns observed in the samples.

### Rhetorical patterns

How the brand persuades, builds trust, and connects emotionally. Reference specific examples from the samples.

### Demonstration rewrites

Include 3-5 rewrites. Each demonstrates the brand voice applied to a different content type. Use this structure for each:

```
**Content type:** [e.g., Product description, Email subject line, Social caption, CTA, Hero headline]

**BEFORE (generic):**
[Generic ecommerce copy that any brand in the category might produce]

**AFTER (brand voice):**
[The same content rewritten in this brand's voice]

**WHY:**
[Which specific voice rules from this guide are demonstrated in the rewrite.
Cross-reference section names — e.g., "Uses second person address (Sentence Style > Person and Address)
and leads with a sensory benefit (Rhetorical Patterns)."]
```

Requirements for the demonstration rewrites:

- The "before" text must be generic ecommerce copy. Do not use the user's actual samples as the "before."
- Cover at least 3 different content types across the rewrites.
- The "after" must demonstrably follow the specific rules documented in this guide. If the "after" text could belong to any brand in the category, it is too generic.
- The "why" must reference specific sections of this guide by name. If you cannot cite specific rules for the choices in the "after," the guide itself needs more specificity.

### How to use this guide

End the document with a brief section explaining:

- Save this document and keep it accessible.
- When using AI skills for content generation (product descriptions, emails, landing pages, social copy), upload or paste this guide alongside your request.
- Provide the guide in full rather than excerpting individual sections. The voice is the combination of all patterns, not any single dimension.

## Edge cases

### Fewer than 3 samples

Produce the guide, but add a **Confidence notes** section at the end. Flag which dimensions are based on limited evidence and recommend additional content types that would strengthen the guide. Do not refuse to produce output.

### Inconsistent voice across samples

Do not average contradictory patterns into a bland middle ground. Instead, document the variation explicitly: "Product descriptions use a technical, detailed voice while social captions are casual and playful."

If the inconsistency appears accidental rather than intentional channel adaptation, flag it as a question: "Your product descriptions use a playful tone while your emails are quite formal — is this intentional, or would you like to align on one approach?"

Use the calibration selection from Step 2 to determine which interpretation to weight more heavily in ambiguous cases.

### Non-brand content in the samples

If the user includes content they clearly did not write (third-party reviews, competitor copy, press coverage), note it and ask whether to include it in the analysis. Exclude it by default unless the user confirms it represents their target voice.

### All samples are the same content type

Produce the guide, but note in the Confidence section that the analysis reflects only one content format. The voice guide will be most useful for that format and may need adjustment for others. Recommend providing samples from 2-3 different content types for a more robust guide.

---
name: brand-voice-extractor
description: Build a structured brand voice profile from a brand's existing content. Use this skill whenever the user wants to define, document, capture, or extract their brand voice, tone, or writing style. Also use when the user mentions needing consistent copy across channels, wants to create a brand guide or style guide for writing, asks how to keep AI-generated content on-brand, or provides brand content and asks you to analyze how they write. This skill produces a reusable document that other skills consume as input.
license: Apache-2.0
---

# Brand Voice Extractor

This skill analyzes a brand's existing written content and produces a structured brand voice profile. The profile is a reusable document that the user saves and uploads to future conversations whenever they need on-brand copy.

Before starting, read the example output in `references/example-output.md` to understand exactly what you're producing. Read `references/glossary.md` to understand the rubric for how each field should be evaluated.

---

## Conversation Flow

### Turn 1: Welcome and Collect Basics

Send this message (adjust naturally, but keep the structure and length):

> I'm going to build your brand voice profile. This is a document that captures how your brand writes, so you (and other AI tools) can produce on-brand copy consistently. Here's how it works:
>
> 1. You share examples of your brand's writing
> 2. I analyze the patterns and produce your voice profile
> 3. You review it, we refine anything that's off
>
> Any questions? If not, we can get started. What's your brand name and website URL?

Wait for the user to respond before proceeding.

### Turn 2: Fetch Site Content and Ask for More

Once you have the brand name and URL:

1. Attempt to fetch the homepage and about page (try common paths: /about, /about-us, /our-story).
2. If successful and the pages contain enough written copy to analyze (not just navigation labels and image captions): "I pulled some content from your site. Share any additional examples you have: product descriptions, emails, social posts. Paste text, upload files, or share more URLs. Some URLs aren't accessible, but we can give it a try."
3. If the fetch succeeds but the content is too thin to analyze (mostly images, minimal copy), treat it the same as a failed fetch.
4. If unsuccessful: "I wasn't able to access your site, so I'll need you to share some content directly. Paste text, upload files, or share URLs. Some URLs aren't accessible, but we can give it a try."

The more varied the source material, the better the profile. If the user provides only one content type (e.g., just PDPs), acknowledge what you received and nudge once: "This gives me a good start on product copy voice. If you have any other content types handy (a marketing email, homepage copy, social posts), that'll help me capture the full range. Otherwise I can work with what we have."

If the user says that's all they have, move forward. Do not ask again.

### Turn 3+: Collect Additional Content

The user may share content across multiple messages. Accept everything. When they indicate they're done (or it's clear they've finished sharing), move to analysis.

### Analysis and Output

Analyze all collected content and produce the full brand voice profile as a downloadable document. Follow the output structure exactly as shown in `references/example-output.md`.

Before sharing the document with the user, scan the Style Decisions table to confirm every value uses vocabulary defined in the glossary's shared vocabulary table or field-specific definitions. If a value uses natural language that doesn't match (e.g., "Almost never" instead of "Never," or "Sometimes" instead of "Sparingly"), rewrite it to match the glossary vocabulary before producing the final document.

After producing the document, say: "Give it a read. If anything seems off, let me know here and I'll update the document."

When the user requests changes, edit the document in place. Do not regenerate the entire document for a single correction.

### Closing

Once the user is satisfied with the profile, say: "Download this file. Whenever you're asking me or another AI tool to write copy, upload it to the conversation and it'll be used to stay on-brand."

---

## Analysis Rubric

When analyzing source material, evaluate each section using the criteria below. Refer to `references/glossary.md` for the full specification of how each field should be defined and what values it can take.

### Voice Summary

Write 2-3 sentences that capture the overall character of the brand's writing. This is not a list of adjectives. It should describe what the brand does when it writes: how it structures ideas, what it assumes about the reader, what it prioritizes.

Test: Would someone who has never read this brand's content be able to describe the general feel of a landing page after reading just this summary? If not, it's too vague.

Bad: "The brand voice is warm, approachable, and confident."
Good: "Your brand voice is direct, confident, and action-oriented. You write in short declarative statements that assume the reader is already an athlete. You lead with emotion and experience, then back it up with product specifics."

### Headlines

Look at headlines across the source material. Identify:

- Length: Are they short (1-5 words), medium (6-12 words), or long?
- Structure: Fragments, complete sentences, questions, imperatives?
- What they lead with: Product name, benefit, emotion, identity, action?
- Case: Title case, sentence case, all caps, lowercase?
- Punctuation: Periods on fragments? Exclamation marks? Question marks?

Provide 2-3 real examples from the source material. If the source material doesn't contain enough headlines, note this gap and work with what's available.

### Product Framing

Read how the brand describes its products. Determine the sequencing:

- Does emotion/benefit come before technical specs, or after?
- Are features translated into benefits, or do they stand alone?
- How are features grouped: thematically (performance, comfort, durability), as a flat list, or woven into narrative?
- How deep is the technical language: jargon-heavy, accessible, or avoided entirely?

This is one of the most important sections for downstream skills. The difference between "emotional setup then technical validation" and "specs first then benefit" fundamentally changes how a PDP or landing page reads.

### How They Talk to the Customer

Analyze how the brand addresses the reader:

- Pronoun usage: "you" (second person), "we" (inclusive), imperative (no pronoun), third person ("runners who...")?
- What's the assumed relationship: peer, coach, aspirational figure, trusted expert, friend?
- What does the brand assume about the reader: beginner, expert, already bought in, needs convincing?
- Does the brand invite, suggest, challenge, affirm, or educate?

Provide 1-2 examples from source material showing the pattern.

### Persuasion Arc

If the source material includes landing pages, long-form emails, or other extended copy, identify the structural pattern:

- What comes first: emotional hook, problem statement, product name, story?
- What comes in the middle: features, social proof, lifestyle context, comparison?
- How does it close: hard CTA, soft CTA, emotional callback?
- What's the typical number of content blocks before the CTA?

Not all brands will have enough source material to determine this. If you only have short-form content (PDPs, social posts), note that this section is based on limited data and may need refinement when longer content is available.

### What They Avoid

Identify patterns of absence across the source material. Look for:

- Do they mention competitors? Even indirectly?
- Do they justify or reference pricing?
- Do they use superlatives or absolute claims?
- Do they use discount/promotion language?
- Do they hedge with qualifiers ("might," "could," "may")?
- Do they use passive or soft lifestyle language if the brand is active/direct (or vice versa)?
- Any other notable pattern of avoidance?

Only include items where you have reasonable confidence based on the source material. Do not guess. If the source material is too limited to determine avoidance patterns, say so.

### Style Decisions Table

For each row in the table, make a determination based on the source material. The possible values and their definitions are specified in `references/glossary.md`. Apply these rules:

- If a pattern appears consistently (90%+) across the source material, state it as absolute ("Yes, always" / "Never").
- If a pattern appears in most but not all content, describe the exception ("Yes, except in [context]").
- If a pattern varies by context, describe the contexts ("In emails yes, on landing pages no").
- If the source material doesn't contain enough evidence to determine a decision, write "Unable to determine from provided content" rather than guessing.

The following decisions should always be evaluated:

| Decision | What to look for |
|---|---|
| Contractions | Are "don't," "it's," "you'll" used, or does the brand write out "do not," "it is," "you will"? |
| Exclamation marks | How frequently? In what contexts? |
| Emojis | Present anywhere? Only in specific channels? |
| Oxford comma | Check any list of three or more items |
| Headline case | Title Case, Sentence case, ALL CAPS, or lowercase? |
| Price references | Does brand copy mention price, or is that left to the product grid/PDP? |
| Competitor mentions | Any direct or indirect references to other brands? |
| Superlatives | "Best," "most," "#1," "leading," or does the brand use specifics instead? |
| Urgency language | "Limited," "don't miss," "act now," "selling fast"? |
| Technical specs | Listed alone, paired with benefits, or avoided? |
| Customer address | How the brand addresses the reader (second person, imperative, aspirational, etc.) |
| Sentence length | Short/fragments, medium, long, or varied? Note any word count patterns. |
| Paragraph length | How many sentences per paragraph? |
| Humor | Present? What type? Where? |
| Punctuation as style | Any punctuation used as a deliberate stylistic choice beyond grammar? |
| Primary CTAs | Collect the actual CTA phrases the brand uses. List them. |

### Example Copy

After completing all sections above, generate 5 pieces of example copy that demonstrate the voice profile in action. These are generated, not pulled from source material. Their purpose is to validate that the profile produces on-brand output.

Generate one of each:

1. **Product headline** - A short headline for an imaginary product in the brand's catalog.
2. **Short product description** - 2-4 sentences for a PDP.
3. **Email subject line + preview text** - A promotional email.
4. **Landing page hero block** - Headline + a short supporting paragraph.
5. **Social caption** - One social media post.

The imaginary product should be realistic for the brand's actual catalog. Don't invent a category the brand doesn't operate in.

---

## Output Structure

The document should follow this exact structure. Read `references/example-output.md` for a complete example.

```
# Brand Voice: [Brand Name]

<!-- brand-voice-extractor v0.1 -->

[Intro paragraph: what this document is and what to do with it]

---

## Voice Summary

[2-3 sentences]

---

[Transition sentence introducing the narrative sections]

## Headlines

[Analysis with examples from source material]

## Product Framing

[Analysis with examples]

## How [Brand Name] Talks to the Customer

[Analysis with examples]

## Persuasion Arc

[Structure breakdown, numbered if describing a sequence]

## What [Brand Name] Avoids

[Avoidance patterns]

---

## Style Decisions

[Intro sentence for this section]

| Decision | Value |
|---|---|
| ... | ... |

---

## Example Copy

[Intro sentence explaining these are generated, not from source material]

[5 example pieces]
```

---

## Important Behaviors

- Produce the voice profile as a file the user can download, not as inline chat text.
- When the user requests changes during review, edit the document in place. Do not regenerate the whole document.
- Use the brand's name in section headers (e.g., "How Nike Talks to the Customer," not "How They Talk to the Customer").
- Pull real examples from source material for narrative sections. Put them inline with the analysis, not in a separate examples section.
- If the source material is insufficient for a section, say so directly in that section. Do not invent patterns you can't support.
- Keep the full document between 600-800 words. For brands with more complex voices (multiple audience registers, detailed humor guidelines, extensive avoidance lists), do not exceed 1,000 words.

---
name: extract-review-insights
description: >-
  Extracts patterns from customer reviews: what they like, dislike, useful
  language, and which product claims hold up.
license: Apache-2.0
---

# Extract Review Insights

This skill reads customer reviews for one product and pulls out the patterns
that matter: what customers consistently like, what they consistently dislike,
the specific language they use, and whether the reviews support or undercut
the product's marketing claims.

The skill works from the reviews only. It does not invent themes, fabricate
customer segments, estimate counts beyond what the data shows, or guess at
root causes. When evidence is thin or mixed, it says so.

For reference on the expected output, see
[references/example-output.md](references/example-output.md).

## Voice and Approach

Be direct and concise. Report what the reviews say without editorializing.
Use plain language. Do not narrate your internal process or over-explain
your methodology. When transitioning between steps, keep it brief and
natural. The user wants the analysis, not a walkthrough of how you arrived
at it.

## Conversation Flow

### Turn 1: Collect Reviews

The skill needs reviews for one product. Accept any format: pasted text,
CSV export (Shopify, Yotpo, Bazaarvoice, PowerReviews, Judge.me, Stamped,
or similar), or a document (PDF, Word, text file).

Optionally, the user may also provide:

- Product/brand name
- Product data (feed entry, PDP content, or product description) -- this
  gives the skill concrete claims and features to check reviews against
- Review metadata (star ratings, dates, verified purchase flags)

Let the user know what you need and what's optional. Don't over-explain
the process.

### Turn 2: Clarify (if needed)

Only ask follow-up questions if something is genuinely ambiguous:

- CSV columns aren't obvious (which column is the review body?)
- Reviews appear to cover multiple products
- Something else prevents you from starting

If everything is clear, skip this turn and go straight to the analysis.

### Turn 3: Deliver the Analysis

Produce the full analysis as a Markdown document using the output structure
below. Offer to adjust groupings, go deeper on a theme, or reframe
anything.

### Turn 4+: Revise

Edit individual sections in place. Do not regenerate the entire document
for a single correction.

## Analysis Instructions

### Core principles

- **Use only what the reviews say.** Every insight must trace back to
  specific reviews. Do not infer themes that aren't explicitly stated or
  clearly implied by multiple reviewers.
- **Focus on repetition.** A single reviewer's opinion is an anecdote. A
  pattern appears when multiple reviewers independently say the same thing.
  Note when a theme appears in many reviews vs. a few.
- **Report the evidence, not the cause.** If customers say the zipper
  breaks, report that. Do not speculate on why the zipper breaks.
- **Be honest about weak evidence.** If only 2-3 reviews mention something,
  say so. If reviews contradict each other on a point, report the split.
  Do not smooth over mixed signals to make the analysis feel cleaner.
- **Preserve customer language.** When quoting or paraphrasing, stay close
  to the words customers actually used. Their phrasing is often more useful
  than a polished summary.

### How to identify themes

1. Read all reviews. Note every distinct positive and negative point.
2. Group points that describe the same thing, even when worded differently.
   "Runs small," "had to size up," and "tight through the shoulders" are
   the same theme (sizing).
3. Count how many reviews touch each theme. Use plain language for
   frequency: "mentioned in many reviews," "a few reviewers noted," "one
   reviewer mentioned." Do not fabricate exact counts unless you can
   actually count them accurately from the data.
4. Rank themes by frequency. Lead each section with the most-repeated
   patterns.

### How to handle product data

When product data (feed entry or PDP content) is provided:

- Extract the product's stated claims, features, and selling points.
- In the Claims Supported / Claims to Be Careful With section,
  cross-reference each claim against what reviewers actually say.
- A claim is "supported" when multiple reviewers independently confirm it.
- A claim needs caution when reviewers contradict it, when evidence is
  mixed, or when no reviewers mention it at all (absence is worth noting
  but is not contradiction).

When no product data is provided:

- Work from claims implied in the reviews themselves (e.g., if many
  reviewers say "this is waterproof," treat waterproofness as an implied
  claim).
- Note in the Claims section that you're working without the brand's own
  product data and that providing it would strengthen the analysis.

## Output Structure

```
# Review Insights: [Product Name]

## Overview
[Product name, review count, rating distribution if metadata is available.
One paragraph summarizing the overall picture: what the dominant sentiment
is and what the key takeaways are. Keep it to 3-5 sentences.]

## What Customers Like
[Grouped by theme, ordered by frequency. Each theme gets a short heading,
a plain-language description of what reviewers say, and a note on how
common the theme is. Include short review snippets only when they add
something the summary doesn't. Do not list every positive comment --
group and summarize.]

## What Customers Don't Like
[Same structure as above. If a negative theme is minor or mentioned by
very few reviewers, say so. If a theme has mixed signals (some love it,
some don't), note the split.]

## Useful Customer Language
[Specific words, phrases, and descriptions customers use that are worth
borrowing for product copy, PDP content, ads, or email. Group by theme
if helpful. These should be the customers' actual words, not polished
marketing rewrites.]

## Claims Supported / Claims to Be Careful With
[If product data provided: cross-reference each identifiable claim against
review evidence. If no product data: work from claims implied in the
reviews. For each claim, note whether it's supported, contradicted, mixed,
or not mentioned. Be specific about the evidence.]

## Confidence Notes
[Flag which parts of the analysis are based on strong patterns (many
reviews, consistent signal) and which are based on thin evidence (few
reviews, mixed signals). If the review set is small, note that the
analysis may not be representative.]
```

## Important Behaviors

- Produce the analysis as a single Markdown document.
- Use the product name in the document title. If no product name is
  provided, use "Untitled Product" and ask the user to confirm.
- When quoting customer reviews, use their actual words. Do not clean up
  grammar or rephrase unless the original is unintelligible.
- When editing, change only the requested section.

## Edge Cases

### Small review set (fewer than 10 reviews)

Produce the analysis but shorten it. With fewer than 10 reviews, most
"themes" are really just individual opinions. Note this prominently in the
Confidence Notes section: "This analysis is based on N reviews. Patterns
identified here may not hold across a larger sample." Keep What Customers
Like and What Customers Don't Like to the points that appear more than
once.

### Large review set (more than 500 reviews)

Use up to 500 reviews, prioritizing the most recent when dates are
available. Let the user know how many reviews were included and that
older reviews were excluded. If the user wants to focus on a specific
time period or segment instead, offer to re-run with a different subset.

### Mixed or contradictory reviews

When reviewers disagree on the same point (e.g., half say it runs large,
half say it fits true to size), report the split. Do not average
conflicting opinions into a lukewarm summary. Note the disagreement and,
if possible, note whether different reviewer contexts (use case, body type,
expectations) explain the split.

### Reviews with no clear patterns

If the reviews are all over the place with no repeated themes, say so.
Produce the analysis with whatever individual points are most notable, but
be clear in Confidence Notes that no strong patterns emerged. This is a
valid finding, not a failure.

### CSV with unexpected columns

If the CSV doesn't have obvious review body, rating, or date columns, ask
the user which columns to use. Common column names to look for: "Review
Body," "Review Text," "Comment," "Content," "Body," "review_body,"
"review_text." For ratings: "Rating," "Stars," "Score," "review_rating."

### Reviews in multiple languages

If reviews are in multiple languages, analyze all of them but note which
language each quoted review is in. If translation is needed for the user
to understand a quote, provide it in brackets.

## Closing

Provide the analysis as a Markdown document. Let the user know a few ways
the output might be useful: the Useful Customer Language section is good
raw material for PDP copy and ad creative, the Claims section can inform
how confidently a product page leans into specific features, and the
Likes/Dislikes sections can surface product improvement opportunities or
FAQ content.

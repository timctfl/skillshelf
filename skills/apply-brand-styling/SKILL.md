---
name: apply-brand-styling
description: >-
  Applies brand colors, typography, and heading structure to documents
  using a brand guidelines file. Supports Word, PDF, and presentations.
license: Apache-2.0
---

# Apply Brand Styling to a Document

This skill takes a brand guidelines file and an existing document, then
applies the brand's visual identity to that document. It handles fonts,
colors, heading hierarchy, and general structural polish. It does not
change any of the text itself -- only the styling and structure around it.

The brand guidelines file can be the output of the Brand Guidelines
Extractor, a style guide PDF, or any document that defines colors and
typography. The content to brand can be a Word doc, PDF, or PowerPoint.

For reference on the expected output, see
[references/example-output.md](references/example-output.md).

---

## Conversation Flow

### Turn 1: Collect Inputs

Ask the user for two things:

1. Their brand guidelines file (upload or paste).
2. The document to brand (upload a .docx, .pdf, or .pptx).

Tell the user: "Share your brand guidelines file and the document you
want branded. I can work with Word docs, PDFs, and PowerPoints. I'll
apply your brand's fonts, colors, and heading structure without changing
any of the text."

If the user provides both in the same message, skip ahead to Turn 2.

If the user provides only one, ask for the other. Do not proceed without
both inputs.

### Turn 2: Analyze and Apply

After receiving both inputs:

1. **Parse the brand file.** Extract colors (with roles), typography
   (heading and body fonts with fallbacks), and any application rules
   (font sizes, color-on-background pairings, accent usage).

2. **Analyze the source document.** Identify the current heading
   structure, font usage, color usage, and any structural issues
   (inconsistent heading levels, missing hierarchy, font mismatches).

3. **Apply branding.** Produce the branded version of the document,
   matching the output format to the input format where possible
   (docx in, docx out; pptx in, pptx out).

4. **Present the result.** Share the branded document along with a
   brief branding summary (what was applied) and any confidence notes
   (where the brand file was thin or judgment calls were made).

Tell the user: "Here's the branded version. Review it and let me know
if anything needs adjusting."

### Turn 3+: Revise

Edit the document in place when the user requests changes. Do not
regenerate the entire document for a single correction.

---

## Branding Rules

### Typography

- Apply the heading font from the brand file to all headings.
- Apply the body font to all other text.
- If the brand file specifies font weight, tracking, or size rules
  (e.g., "H1 at font-medium, tracking-tight"), follow them.
- If the brand file specifies different fonts for different heading
  levels (e.g., "H1-H2 use display font, H3+ use body font"), follow
  that split.
- If fonts are unavailable in the output format (e.g., a Google Font
  in a Word doc), use the listed fallback and note it in the branding
  summary.

### Colors

- Apply text colors according to the brand file's text styling rules
  (e.g., "dark text on light backgrounds, soft text for body copy").
- Apply accent colors to interactive or decorative elements (buttons,
  borders, section dividers, callout boxes) following the brand file's
  accent usage rules.
- If the brand file specifies a cycling order for accents, follow it.
- Preserve the brand file's color roles exactly. Do not swap accent
  colors into text roles or vice versa.

### Heading Structure

- Clean up inconsistent heading levels. If the document jumps from H1
  to H3, insert the missing H2 level or promote/demote as appropriate.
- Ensure heading hierarchy is logical and sequential.
- Do not add headings where none exist. If the document is a wall of
  text with no headings, apply font and color styling only. Note in
  the branding summary: "This document has no heading structure. I
  applied font and color styling. You may want to add headings to
  improve readability."
- Do not change heading text. Only change heading levels and styling.

### Structural Polish

- Normalize spacing between sections.
- Clean up inconsistent list formatting (mixed bullet styles, indentation).
- Ensure consistent paragraph spacing.
- For presentations: apply brand colors to slide backgrounds, title
  bars, and accent shapes. Apply heading font to slide titles, body
  font to slide body text.
- For Word docs: apply brand fonts, heading styles, and color theme.
  Update the document's color palette if the format supports it.

---

## Output Format Rules

Match the output format to the input format:

| Input | Output |
|---|---|
| .docx | .docx |
| .pptx | .pptx |
| .pdf | .docx (PDF styling cannot be edited in place; see PDF input edge case below) |

Every output is accompanied by two sections presented in chat alongside
the branded file:

### Branding Summary

A brief list of what was applied, organized by category:

- **Typography** -- which fonts were applied where, and any fallbacks used.
- **Colors** -- which colors were applied to text, headings, accents, and backgrounds.
- **Heading structure** -- any hierarchy changes made (e.g., "Promoted 3 H3s to H2s to fix a gap in the hierarchy").
- **Structural polish** -- any spacing, list, or formatting cleanup.

### Confidence Notes

Present only when relevant:

- Where the brand file was incomplete (e.g., "Brand file had no typography guidance; used system defaults").
- Where judgment calls were made (e.g., "Document had two competing heading structures; used the more common pattern").
- Where format limitations applied (e.g., "Brand specifies DM Sans but the .docx fallback is Calibri since the font isn't embedded").

---

## Edge Cases

### Brand file has colors but no typography

Apply the color styling. Use the document's existing fonts or fall back
to system defaults (sans-serif for headings, serif or sans-serif for
body depending on the document's current treatment). Note the gap in
Confidence Notes.

### Brand file has typography but no colors

Apply the font styling. Preserve the document's existing color usage.
Note the gap in Confidence Notes.

### Brand file is not from the Brand Guidelines Extractor

The user may provide a hand-written style guide, a PDF brand book, or
a Canva-exported brand kit. Do not reject it. Extract whatever color
and font guidance is present and map it to the styling rules above.
If values are ambiguous (e.g., "our blue" without a hex code), ask
the user for clarification before applying.

### Document has no structure

If the input is a plain text wall with no headings, lists, or
formatting, apply font and color styling only. Do not impose a heading
structure without the user's confirmation. Note the situation and offer
to suggest a heading structure if the user wants one.

### Very long document (20+ pages)

Process the full document but warn the user upfront: "This is a long
document. I'll apply branding throughout, but review the first few
pages closely and let me know if the direction is right before I
finalize the rest."

### Document is already close to the brand

If the existing styling is already mostly aligned with the brand file,
make only the necessary small adjustments. Do not restyle for the sake
of restyling. Note in the branding summary: "This document was already
closely aligned with the brand. Minor adjustments made: [list]."

### PDF input

PDF styling cannot be edited in place. Explain the limitations to the
user before proceeding:

"PDFs don't support direct style editing the way Word docs and
PowerPoints do. I have two options, but both have tradeoffs:

1. **Extract the content into a Word doc**, apply branding, and deliver
   a .docx. This gives you a fully branded document, but the original
   PDF layout will not be preserved exactly -- tables, columns, and
   page breaks may shift.
2. **Review the PDF and produce a branding checklist** -- a list of
   specific changes (fonts, colors, heading styles) that you or a
   designer can apply in the original tool that created the PDF.

Which would be more useful?"

Wait for the user's choice before proceeding.

---

## Closing

Tell the user: "Download the branded document. If you need to brand
more content with the same guidelines, upload the brand file alongside
your next document in a new conversation."

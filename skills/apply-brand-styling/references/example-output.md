# Example: Apply Brand Styling

This is an example of what the apply-brand-styling skill produces when run with good input. It uses Great Outdoors Co., the canonical SkillShelf test brand.

**Scenario:** The user uploads two files:

1. **Brand file:** The Great Outdoors Co. Brand Styling document (output of the Brand Guidelines Extractor), which defines a forest green and natural neutral palette, Source Serif 4 for display headings, and DM Sans for body text.
2. **Document to brand:** A Word doc titled "Great Outdoors Co. Q3 Trail Report" -- an internal quarterly summary. The document uses default Calibri throughout, has no color styling, and has inconsistent heading levels (jumps from Heading 1 to Heading 3 in several places).

**What the skill produces:** A branded .docx file with the brand's typography, colors, and heading hierarchy applied, plus the Branding Summary and Confidence Notes below.

---

## Before: Heading Structure

```
H1: Great Outdoors Co. Q3 Trail Report
  H3: Revenue Summary          ← skipped H2
  H3: Product Performance      ← skipped H2
    H4: Rain Shells
    H4: Fleece Layers
    H4: Packs & Accessories
  H3: Customer Feedback         ← skipped H2
  H1: Q4 Priorities             ← should be H2
    H3: New Product Launches    ← skipped H2 under wrong H1
    H3: Sustainability Goals    ← skipped H2 under wrong H1
```

## After: Heading Structure

```
H1: Great Outdoors Co. Q3 Trail Report
  H2: Revenue Summary
  H2: Product Performance
    H3: Rain Shells
    H3: Fleece Layers
    H3: Packs & Accessories
  H2: Customer Feedback
  H2: Q4 Priorities
    H3: New Product Launches
    H3: Sustainability Goals
```

---

## Branding Summary

### Typography

- **Headings (H1, H2):** Changed from Calibri to Source Serif 4 (display font), medium weight, tight tracking. Fallback set to Georgia since Source Serif 4 is a Google Font and may not render on all machines without installation.
- **Headings (H3, H4):** Changed from Calibri to DM Sans (body font), semibold weight. Follows the brand rule that H3+ uses the body font rather than the display serif.
- **Body text:** Changed from Calibri to DM Sans, regular weight. Fallback set to system-ui.
- **Kickers and labels:** Applied DM Sans semibold with wide letter spacing (matching the brand's 0.16em tracking for label-style text). Applied to section subheadings used as labels above tables.

### Colors

- **Heading text:** Applied `#1c221f` (dark forest near-black) to all headings.
- **Body text:** Applied `#4e5852` (muted olive-gray) to all body paragraphs.
- **Tertiary text:** Applied `#707974` (sage gray) to table footnotes and metadata lines (dates, author attribution).
- **Accent elements:** Applied `#344d40` (forest green) to horizontal rules, table header backgrounds, and the document title underline.
- **Table header text:** Applied `#f8f7f3` (warm off-white) on forest green backgrounds for contrast.
- **Callout box backgrounds:** Applied `#f2f0e9` (surface muted cream) to the two callout boxes in the Customer Feedback section.
- **Callout box borders:** Applied `#d2d7d0` (light warm gray) as a left border on callout boxes.

### Heading Structure

- Demoted the second H1 ("Q4 Priorities") to H2. The document should have a single H1.
- Promoted five H3s to H2s where the hierarchy skipped a level (Revenue Summary, Product Performance, Customer Feedback, New Product Launches, Sustainability Goals).
- Demoted three H4s to H3s to maintain sequential hierarchy under the corrected H2s.
- No heading text was changed.

### Structural Polish

- Normalized paragraph spacing to 8pt after (was a mix of 0pt, 6pt, and 12pt throughout).
- Standardized list formatting: converted three sections using manual dashes to proper bullet lists with consistent indentation.
- Removed double line breaks between sections (replaced with consistent heading spacing).
- Applied consistent table styling: forest green header row, alternating `#f8f7f3` and white row backgrounds, `#d2d7d0` cell borders.

---

## Confidence Notes

- **Font embedding:** Source Serif 4 and DM Sans are Google Fonts and are not embedded in the .docx file. Recipients without these fonts installed will see the fallback fonts (Georgia for headings, system-ui/Calibri for body). For reliable rendering, install both fonts or export to PDF before distributing.
- **Label detection:** The brand file specifies a distinct "kicker" style (DM Sans semibold, wide tracking) for label-like text. The skill applied this to four short lines that appeared to function as section labels above tables. If any of these were intended as regular body text, let me know and I'll revert them.
- **Callout boxes:** The original document had two indented paragraphs in the Customer Feedback section with no explicit formatting. These were interpreted as callout boxes and styled with the surface muted background and border. If they were meant as regular paragraphs, I can remove the box styling.

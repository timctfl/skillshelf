---
name: brand-guidelines-extractor
description: >-
  Extracts brand colors, typography, and usage patterns from a website
  into a structured guidelines file for downstream styling skills.
license: Apache-2.0
---

# Extract Brand Guidelines from a Website

This skill turns a live website into a structured brand guidelines document.
The output captures colors (with roles like background, text, accent),
typography (heading and body fonts with fallbacks), and usage notes. It is
designed to feed into downstream skills that apply brand styling to
presentations, documents, or artifacts.

The skill assumes the user is not technical. It provides three input paths
ranging from "send a message to your developer" to "just upload
screenshots," and walks through each one in plain language.

For reference on the expected output, see
[references/example-output.md](references/example-output.md).

---

## Conversation Flow

### Turn 1: Welcome and Collect Context

Ask the user for two things:

1. Their brand name.
2. Their website URL.

Then ask how they'd like to get their brand data. Frame it as three
simple options, not technical jargon:

> "There are a few ways to pull your brand's colors and fonts from your
> site. Which sounds most like you?"
>
> **Option A: "I already have the style file, or I can ask someone
> for it."** If you have a CSS file or know your brand's colors and
> fonts, share them here. If not, I'll give you a message to send
> your developer with exactly what to ask for.
>
> **Option B: "I'll poke around in Chrome myself."** I'll walk you
> through a quick copy-paste process in your browser. Takes about two
> minutes, and you can't break anything.
>
> **Option C: "I'll just send screenshots."** Upload a couple of
> screenshots and I'll extract what I can. The colors won't be as
> precise, but it works.
>
> You can also combine these. Screenshots plus extracted data gives
> the best result.

Wait for their answer before proceeding.

### Turn 2: Guide the Input Path

Based on the user's choice, provide the appropriate walkthrough.

---

#### Path A: CSS File or Developer Handoff

If the user already has a CSS file or brand style guide, tell them to
upload or paste it directly.

If they need to ask someone, give them a ready-to-send message.
Something they can paste into Slack, email, or a text. Example:

> "Hey, I need our brand's color and font info in a specific format.
> Could you send me:
>
> 1. Our CSS custom properties for colors (the `--color-*` or
>    `--brand-*` variables from `:root` or `html`), or just the hex
>    color codes we use for: primary background, text, headings,
>    accents/CTAs, borders, and any secondary backgrounds.
> 2. The font families we use for headings and body text, including
>    any fallback fonts.
> 3. If easy, the CSS file or a link to it.
>
> Just the raw values are fine, no need to format it."

Tell the user: "If you already have a CSS file or style guide, upload
or paste it here. Otherwise, send that message along and paste whatever
they send back. I'll sort it out."

---

#### Path B: Console Extraction (Detailed Walkthrough)

This is the longest path. The user is non-technical, so every step needs
to be explicit. Walk through it like this:

**What we're doing (one sentence):** "We're going to open a hidden panel
in your browser that lets you run a small script. The script reads the
colors and fonts from your website and copies them for you. It only reads
and doesn't change anything on your site."

**Step-by-step for Chrome (the default):**

1. **Open your website** in Chrome. Navigate to the page that best
   represents your brand (usually the homepage).

2. **Open the Console.** Right-click anywhere on the page and select
   **Inspect** (it's at the bottom of the menu). A panel will open,
   usually docked to the right or bottom of your screen. At the top of
   that panel, you'll see tabs like "Elements," "Console," "Sources."
   Click the **Console** tab.

3. **Enable pasting.** Chrome blocks pasting into the console by
   default. You'll see a message that says something like "don't paste
   code here." Click into the text area at the bottom of the Console
   panel, type the words `allow pasting` (exactly like that, no quotes),
   and press Enter. Nothing visible will happen, and that's normal. It
   just unlocked paste.

4. **Paste the script.** Copy the entire script below, click into the
   Console text area, and paste it (Ctrl+V or Cmd+V). Then press Enter.

5. **What you'll see.** The console will print a summary: your heading
   font, body font, top colors, and accent colors. It also copies the
   full data to your clipboard automatically.

6. **Send me the result.** Press Ctrl+V / Cmd+V right here in our chat
   to paste the copied data. It will be a block of text that starts with
   `{` and ends with `}`. If clipboard copy didn't work, you can also
   select all the text in the console output (the part that starts with
   `{`) and copy it manually.

**For Safari users:** Open Safari > top menu bar > Develop > Show Web
Inspector > Console tab. If you don't see the Develop menu, go to
Safari > Settings > Advanced and check "Show features for web
developers." Safari does not require the "allow pasting" step.

**For Firefox users:** Press F12 or right-click > Inspect > Console tab.
Firefox does not require the "allow pasting" step.

**The script to provide:**

Use the extraction script stored in
[references/console-script.js](references/console-script.js). Present
it to the user inside a code block so they can copy it easily. Before
showing the script, tell them: "Here's the script. It looks long, but
you don't need to read it. Just copy the whole thing and paste it
into the Console."

---

#### Path C: Screenshots

Tell the user what to capture:

1. **Homepage** (full page or at least the header, hero section, and
   footer). This usually shows the primary colors, heading fonts, and
   navigation styling.
2. **A product or content page**, which shows body text fonts and secondary
   colors.
3. **Bonus: any page with buttons or CTAs.** These reveal accent
   colors.

Tell the user: "I'll pull what I can from the screenshots. The font
names and exact color codes will be approximate since I'm reading them
visually. If precision matters, we can always do the console step later
to sharpen things up."

---

### Turn 3: Parse and Confirm

After receiving the user's input (JSON from the script, developer
response, screenshots, or a combination), process it and present the
results in plain language.

**For each color**, show:

- The hex code
- A plain-English name (e.g., "dark charcoal," "warm off-white,"
  "muted teal")
- The role: primary background, text, accent, border, secondary
  background

**For each font**, show:

- The font family name
- Where it's used (headings, body text)
- A suggested fallback (based on the font category: serif, sans-serif,
  monospace)

Organize the summary clearly and ask: "Does this look right? If any
colors or fonts are wrong, off, or missing, let me know and I'll
adjust."

**If the input came from screenshots only**, add a confidence note:
"These values are based on visual extraction from screenshots. The hex
codes are close but may be off by a few shades. If you need exact
values, running the console script or asking a developer will give
precise results."

Wait for confirmation or corrections.

### Turn 4: Produce the Brand Guidelines Document

Once the user confirms, generate the full brand guidelines file using
the output structure below. Produce it as a downloadable Markdown file.

Tell the user: "Here's your brand guidelines file. Review it and let me
know if anything needs adjusting."

### Turn 5+: Revise

Edit the document in place when the user requests changes. Do not
regenerate the entire file for a single correction.

---

## Output Structure

The output document follows this format. Every heading is stable, and
downstream skills reference them by name.

```
<!-- brand-guidelines-extractor v1.0 -->
# [Brand Name] Brand Styling

## Overview
[One paragraph: what this file is, what brand it covers, the source URL.]

## Brand Guidelines

### Colors

**Main Colors:**
[List each main color: hex code, plain-English name, role/usage.
Include: primary dark, primary light, mid gray, light gray at minimum.]

**Accent Colors:**
[List accent/CTA colors with hex code, plain-English name, and usage.]

### Typography
[Heading font, body font, and fallbacks. Note if fonts are custom
(need loading/installation) or system fonts.]

## Features

### Smart Font Application
[How fonts should be applied: which font for headings, which for body,
what size threshold distinguishes them, fallback behavior.]

### Text Styling
[Summary of text color usage: what color on what background, heading
vs. body treatment.]

### Shape and Accent Colors
[How accent colors should be applied to non-text elements: borders,
backgrounds, buttons, decorative shapes. If multiple accents, note
the cycling or priority order.]

## Technical Details

### Font Management
[Font sources, installation notes, fallback chain. Practical info
for someone implementing the brand in a document or presentation.]

### Color Application
[Color format (hex, RGB), any CSS custom properties worth preserving,
notes on contrast and accessibility if evident from the data.]
```

---

## Edge Cases

### Site uses only system fonts

If the extraction shows only system fonts (Arial, Helvetica, Georgia,
Times New Roman, etc.), document them as-is. Do not invent custom font
recommendations. Note in the Typography section: "This site uses system
fonts. No custom font loading is required."

### Very few distinct colors (minimal palette)

Some sites use only 2-3 colors. Document what's there. If there are no
clear accent colors, note it: "No distinct accent colors detected. The
brand uses a limited palette of [colors]." Do not pad the palette with
invented colors.

### Console script returns partial data

Cross-origin stylesheets (fonts loaded from Google Fonts, colors defined
in third-party CSS) may not be readable by the script. If the JSON
output has empty sections, tell the user what's missing and why: "The
script couldn't read some styles because they're loaded from an external
source. This is normal. I can fill in the gaps if you tell me your
heading and body fonts, or we can try the screenshot path too."

### User provides only screenshots

Produce the guidelines with a Confidence Notes section at the end:

```
## Confidence Notes
- Color hex values are approximate (extracted visually from screenshots).
  Margin of error: ~5-10% per channel.
- Font identification is based on visual characteristics. If precision
  is needed, run the console extraction script or ask a developer for
  the font-family declarations.
```

### Site uses CSS custom properties heavily

If the extraction returns many custom properties (10+), organize them
in the Technical Details section under a "CSS Custom Properties"
subheading. Group by purpose (color, typography, spacing) and note the
property names so a developer can reference them directly.

### Site has a dark mode and light mode

If the extraction captures both palettes (or the user mentions it),
document both. Use subheadings under Colors:

```
### Colors (Light Mode)
### Colors (Dark Mode)
```

Note which mode is the default.


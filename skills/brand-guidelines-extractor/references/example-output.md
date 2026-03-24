# Example: Extract Brand Guidelines

This is an example of what the brand-guidelines-extractor skill produces when run with good input. It uses Great Outdoors Co., the canonical SkillShelf test brand. The input was a Tailwind CSS file containing custom properties, component classes, and utility definitions.

---

```markdown
<!-- brand-guidelines-extractor v1.0 -->
# Great Outdoors Co. Brand Styling

## Overview

This file documents the brand colors, typography, and visual styling for Great Outdoors Co. (greatoutdoorsco.com). It was extracted from the site's Tailwind CSS stylesheet. The brand direction is calm, rugged, and premium-functional -- an outdoor DTC aesthetic built around forest greens, natural neutrals, and earthy accents.

## Brand Guidelines

### Colors

**Main Colors:**
- Dark: `#1c221f` -- Primary text and dark foreground elements. A deep forest-tinged near-black.
- Soft Text: `#4e5852` -- Body text and secondary copy. A muted dark olive-gray.
- Faint Text: `#707974` -- Tertiary text, labels, and metadata. A quiet sage gray.
- Background: `#f8f7f3` -- Page background. A warm off-white with a slight cream undertone.
- Surface: `#fffffc` -- Cards, panels, and elevated containers. Nearly pure white.
- Surface Muted: `#f2f0e9` -- Subtle backgrounds, badges, and trust bar items. A soft cream.
- Surface Deep: `#e6ebe7` -- Image placeholders and deeper surface areas. A light sage.

**Border Colors:**
- Default: `#d2d7d0` -- Standard borders, dividers, and card outlines. A light warm gray.
- Strong: `#a8b1ab` -- Emphasized borders on hover and interactive states. A medium sage gray.

**Accent Colors:**
- Forest: `#344d40` -- Primary accent, CTAs, buttons, and brand identity color. A deep muted green.
- Forest Deep: `#23352c` -- Hover states on primary buttons, announcement bars. Darker forest.
- Moss: `#687d5e` -- Feature bullets, kicker lines, and secondary green accents. An earthy moss green.
- Rain: `#5d717e` -- Focus rings, badge variants, and cool-toned accents. A slate blue-gray.
- Rain Deep: `#3e505b` -- Rain badge text and deeper blue-gray applications.
- Clay: `#8e6148` -- "New" badge text and warm accent. A muted terracotta.
- Gold: `#a68a56` -- "New" badge backgrounds (at 16% opacity) and warm highlights. A dusty gold.

**Status Colors:**
- Success: `#436650` -- Positive feedback and confirmation states.
- Warning: `#966f41` -- Caution states and alerts.
- Danger: `#804538` -- Error states and sale badges.

### Typography

- **Headings (H1, H2)**: Source Serif 4 (with Georgia, Times New Roman fallback). A variable-weight serif used for hero headlines, journal titles, product titles, editorial pullquotes, and review quotes. Medium weight, tight tracking, balanced text wrap.
- **Headings (H3-H6)**: DM Sans (with system-ui, -apple-system fallback). Same weight and tracking as display headings but uses the body font for smaller heading levels.
- **Body Text**: DM Sans (with system-ui, -apple-system fallback). A clean geometric sans-serif used for body copy, UI elements, nav, buttons, and product metadata. Regular weight, relaxed leading (1.75rem line height).
- **Note**: Both DM Sans and Source Serif 4 are Google Fonts. They should be loaded via a stylesheet link or pre-installed in your environment for best results.

## Features

### Smart Font Application

- H1 and H2: Source Serif 4 (display font), `font-medium` weight, `tracking-tight`
- H1: 2.25rem (mobile), 3rem (desktop)
- H2: 1.875rem (mobile), 2.25rem (desktop)
- H3: 1.5rem (mobile), 1.875rem (desktop) -- uses DM Sans (body font), not the display serif
- Hero titles, product titles (XL), journal titles, and review quotes also use Source Serif 4
- Body text, nav links, buttons, badges, and all other UI elements: DM Sans
- Kickers and labels use DM Sans at `font-semibold` with wide letter spacing (0.16em)

### Text Styling

- Headings: dark (`#1c221f`) on light backgrounds
- Body text: soft (`#4e5852`) on light backgrounds
- Labels and metadata: faint (`#707974`)
- Inverted text: warm off-white (`#f8f7f3`) on forest-deep (`#23352c`) backgrounds (announcement bars, promo bars)
- Strong/bold text within rich text blocks inherits the dark text color (`#1c221f`)

### Shape and Accent Colors

- Primary buttons and CTAs: forest (`#344d40`) background with warm off-white text
- Secondary buttons: white surface with strong border, forest border on hover
- Badges use accent colors at reduced opacity for backgrounds (10-16%) with deeper variants for text
- Feature bullets: moss (`#687d5e`)
- Focus rings: rain (`#5d717e`) at 55% opacity
- Trust icons: forest at 12% opacity background with forest-deep text
- Non-text decorative shapes cycle through forest, moss, rain, and clay

## Technical Details

### Font Management

- Display font: Source Serif 4 (Google Fonts). Applied to H1, H2, hero titles, product titles (XL), journal titles, and review quotes via `--go-font-display` custom property. Falls back to Georgia, then Times New Roman.
- Body font: DM Sans (Google Fonts). Applied to everything else via `--go-font-body` custom property. Falls back to system-ui, then -apple-system.
- Both fonts are declared as CSS custom properties (`--go-font-body`, `--go-font-display`) and referenced throughout the stylesheet.
- All heading styles use Tailwind's `font-medium` (500 weight) and `tracking-tight`
- Utility classes `.font-body` and `.font-display` are available for overrides

### Color Application

- Colors are defined as CSS custom properties using space-separated RGB channels (e.g., `--go-forest: 52 77 64`)
- Applied via `rgb(var(--go-property))` syntax, which allows alpha channel modifiers (e.g., `rgb(var(--go-forest) / 0.12)`)
- All custom properties are prefixed with `--go-` (short for Great Outdoors)
- The full custom property map:

| Property | RGB | Hex | Role |
|---|---|---|---|
| `--go-font-body` | -- | -- | "DM Sans", system-ui, -apple-system, sans-serif |
| `--go-font-display` | -- | -- | "Source Serif 4", Georgia, "Times New Roman", serif |
| `--go-bg` | 248 247 243 | `#f8f7f3` | Page background |
| `--go-surface` | 255 255 252 | `#fffffc` | Cards, panels |
| `--go-surface-muted` | 242 240 233 | `#f2f0e9` | Subtle backgrounds |
| `--go-surface-deep` | 230 235 231 | `#e6ebe7` | Deeper surfaces |
| `--go-text` | 28 34 31 | `#1c221f` | Primary text |
| `--go-text-soft` | 78 88 82 | `#4e5852` | Body text |
| `--go-text-faint` | 112 121 116 | `#707974` | Tertiary text |
| `--go-border` | 210 215 208 | `#d2d7d0` | Default borders |
| `--go-border-strong` | 168 177 171 | `#a8b1ab` | Strong borders |
| `--go-forest` | 52 77 64 | `#344d40` | Primary accent |
| `--go-forest-deep` | 35 53 44 | `#23352c` | Deep accent |
| `--go-moss` | 104 125 94 | `#687d5e` | Secondary green |
| `--go-rain` | 93 113 126 | `#5d717e` | Cool accent |
| `--go-rain-deep` | 62 80 91 | `#3e505b` | Deep cool accent |
| `--go-clay` | 142 97 72 | `#8e6148` | Warm accent |
| `--go-gold` | 166 138 86 | `#a68a56` | Warm highlight |
| `--go-success` | 67 102 80 | `#436650` | Success state |
| `--go-warning` | 150 111 65 | `#966f41` | Warning state |
| `--go-danger` | 128 69 56 | `#804538` | Danger state |

```

/**
 * Brand Guidelines Extractor
 * 
 * Run in the browser console on any website.
 * Produces a focused summary of brand colors, fonts, and usage
 * designed to feed into a brand-guidelines SKILL.md.
 *
 * SETUP (Chrome): Press F12 > Console tab > type "allow pasting" > Enter > paste this script > Enter
 */

(() => {
  const result = {
    url: location.href,
    title: document.title,

    // ── CSS Custom Properties (often the cleanest source of truth) ──
    customProperties: {},

    // ── Colors by role ──
    backgrounds: {},
    textColors: {},
    borderColors: {},
    accentColors: {},

    // ── Fonts ──
    headingFonts: {},
    bodyFonts: {},
    fontFaces: [],
  };

  // 1. Custom properties from :root / html
  try {
    for (const sheet of document.styleSheets) {
      try {
        for (const rule of (sheet.cssRules || [])) {
          if (rule.selectorText && /^(:root|html|body)$/.test(rule.selectorText.trim())) {
            for (const prop of rule.style) {
              if (prop.startsWith('--')) {
                const val = rule.style.getPropertyValue(prop).trim();
                // Only keep color-like and font-like custom properties
                if (/^(#|rgb|hsl|oklch|color)/.test(val) || /font|family/i.test(prop)) {
                  result.customProperties[prop] = val;
                }
              }
            }
          }
          // @font-face
          if (rule instanceof CSSFontFaceRule) {
            result.fontFaces.push({
              family: rule.style.getPropertyValue('font-family').replace(/['"]/g, '').trim(),
              weight: rule.style.getPropertyValue('font-weight') || '400',
              style: rule.style.getPropertyValue('font-style') || 'normal',
            });
          }
        }
      } catch (e) {} // cross-origin
    }
  } catch (e) {}

  // 2. Walk visible elements, categorize colors by usage
  function rgbToHex(rgb) {
    const m = rgb.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (!m) return rgb;
    return '#' + [m[1], m[2], m[3]].map(x => parseInt(x).toString(16).padStart(2, '0')).join('');
  }

  function isNeutral(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    return (max - min) < 30; // low saturation = neutral
  }

  function inc(obj, key) { obj[key] = (obj[key] || 0) + 1; }

  const headingTags = new Set(['H1', 'H2', 'H3', 'H4', 'H5', 'H6']);
  const skip = new Set(['rgba(0, 0, 0, 0)', 'transparent', 'inherit', 'currentcolor']);

  for (const el of document.querySelectorAll('body *')) {
    if (el.offsetParent === null && getComputedStyle(el).position !== 'fixed') continue;
    const cs = getComputedStyle(el);

    // Background
    const bg = cs.backgroundColor;
    if (bg && !skip.has(bg)) {
      const hex = rgbToHex(bg);
      if (hex.startsWith('#')) inc(result.backgrounds, hex);
    }

    // Text color
    const tc = cs.color;
    if (tc && !skip.has(tc)) {
      const hex = rgbToHex(tc);
      if (hex.startsWith('#')) inc(result.textColors, hex);
    }

    // Border color (only if border is visible)
    const bw = parseFloat(cs.borderTopWidth);
    if (bw > 0) {
      const bc = cs.borderTopColor;
      if (bc && !skip.has(bc)) {
        const hex = rgbToHex(bc);
        if (hex.startsWith('#')) inc(result.borderColors, hex);
      }
    }

    // Fonts - split by heading vs body
    const ff = cs.fontFamily.split(',')[0].replace(/['"]/g, '').trim();
    if (headingTags.has(el.tagName)) {
      inc(result.headingFonts, ff);
    } else if (el.children.length === 0 && el.textContent.trim().length > 0) {
      // Leaf text nodes = body text
      inc(result.bodyFonts, ff);
    }
  }

  // 3. Sort and trim to top values
  function topN(obj, n = 8) {
    return Object.entries(obj)
      .sort((a, b) => b[1] - a[1])
      .slice(0, n)
      .map(([value, count]) => ({ value, count }));
  }

  // 4. Identify accent colors (non-neutral colors used in backgrounds or borders)
  const allBgColors = Object.entries(result.backgrounds);
  for (const [hex, count] of allBgColors) {
    if (hex.startsWith('#') && !isNeutral(hex) && count >= 2) {
      result.accentColors[hex] = count;
    }
  }
  for (const [hex, count] of Object.entries(result.borderColors)) {
    if (hex.startsWith('#') && !isNeutral(hex) && count >= 2) {
      result.accentColors[hex] = (result.accentColors[hex] || 0) + count;
    }
  }

  // 5. Build clean output
  const output = {
    url: result.url,
    title: result.title,

    fonts: {
      headings: topN(result.headingFonts, 3),
      body: topN(result.bodyFonts, 3),
      loaded: [...new Set(result.fontFaces.map(f => f.family))],
    },

    colors: {
      backgrounds: topN(result.backgrounds),
      text: topN(result.textColors),
      borders: topN(result.borderColors, 5),
      accents: topN(result.accentColors, 5),
    },

    customProperties: result.customProperties,
  };

  // 6. Output
  const json = JSON.stringify(output, null, 2);

  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(json).then(() => {
      console.log('%c✓ Copied to clipboard', 'color: #22c55e; font-weight: bold; font-size: 14px');
    }).catch(() => {});
  }

  console.log('%c── Brand Summary ──', 'color: #6366f1; font-weight: bold; font-size: 14px');
  console.log('Heading font:', output.fonts.headings[0]?.value || 'unknown');
  console.log('Body font:', output.fonts.body[0]?.value || 'unknown');
  console.log('Top bg colors:', output.colors.backgrounds.slice(0, 4).map(c => c.value).join(', '));
  console.log('Top text colors:', output.colors.text.slice(0, 4).map(c => c.value).join(', '));
  console.log('Accent colors:', output.colors.accents.map(c => c.value).join(', ') || 'none detected');
  console.log('Custom props:', Object.keys(output.customProperties).length);
  console.log('');
  console.log(json);

  return output;
})();

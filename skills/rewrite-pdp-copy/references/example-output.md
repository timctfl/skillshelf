# Example: Rewrite PDP Copy

This is an example of what the rewrite-pdp-copy skill produces. It demonstrates the full output when given a PDP template, thin product data from a Shopify export, and three upstream skill outputs (brand voice profile, positioning brief, review insights).

The example uses Great Outdoors Co., the canonical SkillShelf test brand. The product is the Cascade Rain Shell - Men's. The template structure comes from the Women's version PDP (both use the same page layout). The product data comes from the Shopify product export, which has a much shorter description than the full PDP. The skill uses the upstream inputs to fill the gap between the thin product data and the full template.

---

```markdown
# PDP Copy: Cascade Rain Shell - Men's

**Template source:** Cascade Rain Shell - Women's PDP (copy-pasted content)
**Product source:** Shopify product export row (title, short description, 3 feature bullets, weight, material)
**Supporting inputs:** Brand voice profile, positioning brief, review insights (20 reviews)

---

## Hero Description

The Cascade Rain Shell is the jacket you grab when the forecast says "maybe" -- which in the Pacific Northwest is most weekends from October through June. 2.5-layer waterproof/breathable fabric with fully taped seams keeps you dry in sustained rain, not just a quick drizzle between the car and the trailhead.

At 330 g, it packs into its own pocket and stays in your daypack until you need it. The fabric is quiet -- no loud swishing on the trail or on the walk to work. Light enough for everyday use, built well enough that you're not replacing it next fall.

## Features

- 2.5-layer waterproof/breathable fabric with fully taped seams
- PFAS-free DWR finish that sheds rain and wet snow
- Adjustable, helmet-compatible hood with a structured brim
- Two hand pockets with water-resistant zips
- Pit zips for venting on steep uphills
- Packs into its own pocket with a carabiner loop

## Materials & Specs

- **Waterproof rating:** 15,000 mm
- **Breathability:** 15,000 g/m²/24h
- **Weight:** 330 g (size M)
- **Shell:** 100% recycled nylon ripstop (laminated)
- **Zippers:** YKK water-resistant center front and pocket zips
- **Fit:** Regular (room for a light midlayer)

## Care Instructions

- Machine wash cold on gentle cycle
- Close all zippers and hook-and-loop tabs before washing
- Use mild detergent (no fabric softener)
- Tumble dry low to reactivate DWR, or warm iron with a cloth barrier
- Do not bleach or dry clean

## Sizing Notes

- The Cascade fits on the generous side. If you're between sizes and don't plan to layer a fleece underneath, consider sizing down.
- For layering a midlayer or light insulated vest, your usual size should work.
- Designed to sit just below the hip for coverage under a pack.

---

## Carry-Through Sections

### Materials & Specs

All spec values (waterproof rating, breathability, weight, materials, zipper brand, fit designation) carried through from existing product data. No modifications to numerical claims.

### Care Instructions

Care instructions carried through from the Women's PDP template. These are standard manufacturer care directions and were not modified.

---

## Notes

### Confidence Notes

**Hero description:** The opening line ("the jacket you grab when the forecast says 'maybe'") and the framing around everyday use are informed by the review insights -- customers repeatedly describe the Cascade as their default grab-and-go jacket. The waterproofing claim ("sustained rain, not just a quick drizzle") is supported by multiple reviews describing multi-hour hikes in steady rain.

**Features:** Feature bullets are drawn from the Shopify product data (3 bullets) and expanded using details from the Women's PDP template, which lists the same feature set. The helmet-compatible hood, pit zips, and pack-into-pocket features were not in the Shopify data but are present in the template and consistent with the product line.

**Sizing notes:** Rewritten based on review insights. The original Shopify data had no sizing information. The review data consistently describes the fit as generous, with multiple reviewers suggesting sizing down for slim builds. The Women's PDP template had sizing notes for that version; these have been adapted for the Men's using the review data.

**Pocket placement:** Review insights flag that hand pockets conflict with backpack hip belts for some users. This was not included in the features or hero copy because the template doesn't have a dedicated section for known tradeoffs, but it could be added to an FAQ or "Good to know" section if the template supports one.

### Recommendations

**Add a "Good to know" or FAQ section.** The review data surfaced two recurring themes (generous fit and pocket-hipbelt conflict) that customers would benefit from seeing on the PDP. The current template doesn't have a natural place for this kind of practical guidance. A short section with 2-3 common questions would reduce sizing-related returns and set better expectations for hikers who carry packs.
```

---

## How This Example Demonstrates the Skill

**Brand voice alignment.** The copy follows the voice profile: short declarative sentences, contractions, no exclamation marks, no superlatives, dry humor where it fits naturally ("which in the Pacific Northwest is most weekends from October through June"). It avoids everything in the "What GreatOutdoors Co. Avoids" list -- no aspirational language, no competitor comparisons, no urgency cues.

**Positioning awareness.** The copy frames the product through GreatOutdoors Co.'s positioning: gear for every-weekend hikers, not expedition athletes. The hero leads with the use pattern (weekly use in real rain), not with technical specs. The value framing is implicit -- "you're not replacing it next fall" -- rather than leading with the $149 price point, which matches the positioning brief's guidance on how to talk about price.

**Template compliance.** Every section from the Women's PDP template appears in the output with the same format: paragraph hero, bullet features, table specs, bullet care instructions, bullet sizing notes. No sections were added, renamed, or restructured.

**No fabrication.** Every claim traces to either the Shopify product data, the Women's PDP template (same product line), or the review insights. The confidence notes document which claims came from which source. Where the Shopify data was thin (no sizing info, only 3 feature bullets), the skill filled gaps from the template and reviews and documented what it did.

**Specificity.** The hero copy names the specific conditions ("Pacific Northwest rain," "October through June"), the specific weight (330 g), and a specific customer behavior from reviews ("stays in your daypack until you need it"). The sizing notes draw on specific reviewer feedback rather than generic fit guidance.

**Decision-driving details.** The hero leads with what the jacket does (keeps you dry in sustained rain) and how it fits into the customer's life (light enough for everyday, quiet fabric). The specs are in a dedicated section for people who want them, but the hero gives enough information to decide without scrolling.

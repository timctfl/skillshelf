# Example: Write Product Descriptions from Spec Sheets

This is an example of what the write-product-descriptions skill produces. It demonstrates the full output when given a detailed spec sheet, a content template from the Women's version of the same product, a brand voice profile, and a positioning brief.

The example uses Great Outdoors Co., the canonical SkillShelf test brand. The product is the Cascade Rain Shell - Men's. The spec data comes from a product spec sheet (material, construction, features, care, sizing) and a product attributes CSV (waterproof rating, breathability, colors). The template structure comes from the Women's version PDP. Unlike the rewrite skill, there is no existing customer-facing copy to start from -- just raw product data.

---

```markdown
# Product Description: Cascade Rain Shell - Men's

**Product data source:** Product spec sheet + product attributes CSV
**Supporting inputs:** Brand voice profile, positioning brief, content template (from Women's PDP)

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

All spec values (waterproof rating, breathability, weight, materials, zipper brand, fit designation) carried through from the product spec sheet and attributes CSV. No modifications to numerical claims.

### Care Instructions

Care instructions carried through from the product spec sheet. These are standard manufacturer care directions and were not modified.

---

## Notes

### Spec-to-Copy Mapping

**Hero Description:** Led with the 2.5-layer waterproof/breathable construction and fully taped seams (spec sheet: construction section). Waterproof rating (15,000 mm) and breathability (15,000 g/m²/24h) from the attributes CSV informed the "sustained rain" framing. Weight (330 g from spec sheet) drove the packability angle. "Pacific Northwest" context from the positioning brief, which centers the brand on weekly PNW hiking. "Quiet fabric" from the spec sheet's noise rating note.

**Features:** All six bullets trace directly to the spec sheet's feature list: 2.5L fabric + taped seams, PFAS-free DWR, helmet-compatible hood with structured brim, hand pocket placement + water-resistant zips, pit zips, stuff pocket with carabiner loop.

**Materials & Specs:** Direct carry-through from spec sheet and attributes CSV. Weight listed in grams as provided.

**Care Instructions:** Carried through from spec sheet care section. DWR reactivation step (tumble dry low) included because the spec sheet confirms PFAS-free DWR treatment.

**Sizing Notes:** Fit designation ("Regular") and layering guidance ("room for a light midlayer") from spec sheet. "Generous fit" and size-down recommendation from the spec sheet's fit notes. Hip-length measurement from the spec sheet's dimensions.

### Confidence Notes

**Hero description:** The opening line ("the jacket you grab when the forecast says 'maybe'") and the framing around everyday use are inferred from the product category (rain shell), the brand's positioning brief (weekly-use gear for PNW hikers), and the weight/packability specs. The positioning brief is doing most of the work here -- without it, the hero would be more generic.

**Value framing:** "You're not replacing it next fall" is inferred from the limited lifetime warranty and the brand's positioning around durability. The spec sheet doesn't include explicit durability claims or test data, so this is a soft inference from warranty + positioning. Flagged in case the brand prefers to avoid durability claims without test data.

### Recommendations

**Add a "Good to know" or FAQ section to the template.** The spec sheet includes fit details (generous, size down for slim builds, pocket placement relative to hipbelts) that are useful for purchase decisions but don't have a natural home in the current template. A short section with 2-3 common questions would help customers self-select the right size and set expectations for pack compatibility.
```

---

## How This Example Demonstrates the Skill

**Writes from specs, not from existing copy.** The input is raw product data: a spec sheet and an attributes CSV. There is no existing PDP to rewrite. The skill translates technical specs into customer-facing copy.

**Brand voice alignment.** The copy follows the voice profile: short declarative sentences, contractions, no exclamation marks, no superlatives, dry humor where it fits naturally ("which in the Pacific Northwest is most weekends from October through June"). It avoids everything in the "What GreatOutdoors Co. Avoids" list -- no aspirational language, no competitor comparisons, no urgency cues.

**Positioning awareness.** The copy frames the product through GreatOutdoors Co.'s positioning: gear for every-weekend hikers, not expedition athletes. The hero leads with the use pattern (weekly use in real rain), not with technical specs. The value framing is implicit -- "you're not replacing it next fall" -- rather than leading with the $149 price point.

**Template compliance.** Every section from the Women's PDP template appears in the output with the same format: paragraph hero, bullet features, table specs, bullet care instructions, bullet sizing notes. No sections were added, renamed, or restructured.

**Spec-to-Copy Mapping provides traceability.** Every section traces back to specific fields in the spec sheet or attributes CSV. The user can verify that the skill interpreted "15K/15K" correctly, that the "quiet fabric" claim came from the spec sheet's noise note, and that the "Pacific Northwest" framing came from the positioning brief rather than being invented.

**Specificity extracted from specs.** The hero names the specific weight (330 g), the specific construction (2.5-layer laminate, fully taped seams), and the specific performance context (sustained rain, not a drizzle). The features section preserves spec-level detail (PFAS-free DWR, structured brim, carabiner loop) rather than abstracting to generic benefit language.

**Honest confidence notes.** The value framing ("not replacing it next fall") is flagged as a soft inference from warranty + positioning rather than presented as a hard claim. This is the kind of transparency that builds trust when writing from specs -- the user knows exactly where the skill was confident and where it was interpreting.

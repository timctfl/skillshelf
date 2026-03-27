# PDP Template: TrailForge

<!-- content-template v0.1 -->

This document captures the structural template for TrailForge's product detail pages. It defines the section structure, format constraints, and content expectations for every PDP on the site. Upload it alongside content-generation skills so the AI knows the target structure without you having to explain it each time.

---

## Template Overview

- **Content type:** Product detail page (PDP)
- **Typical use:** Every product on the site (apparel, footwear, and gear)
- **Number of sections:** 14 (8 in the buy box, 6 in the accordion panel)
- **Estimated total length:** 400-800 words of written content, depending on product complexity

---

## Sections

### 1. Product Title

- **Format:** Single headline
- **Length:** 3-6 words
- **Content:** Product name followed by gender designation
- **Notes:** All caps. Format is "[Product Name] [Gender]," e.g., "SUMMIT AR JACKET MEN'S"

### 2. Badge

- **Format:** Small label above or beside the title
- **Length:** 1-2 words
- **Content:** Product status indicator ("Best seller," "New," "Revised," etc.)
- **Notes:** Conditional. Not all products have a badge. Only one badge displays at a time.

### 3. Star Rating & Review Link

- **Format:** Star icons + linked text
- **Length:** N/A (functional element)
- **Content:** Aggregate star rating with a "Leave a review" link
- **Notes:** May include a subtitle note when reviews span multiple product versions.

### 4. Short Description

- **Format:** Single sentence
- **Length:** 60-100 characters
- **Content:** One-line product summary covering core function, primary technology, and intended use
- **Notes:** Appears above the price. Factual and concise, not a marketing tagline. Reads as a product identifier, not a sell line.

### 5. Price Block

- **Format:** Price + installment line
- **Length:** N/A (functional element)
- **Content:** Full price, installment breakdown (4 payments via third-party provider), and link to financing details
- **Notes:** No written content needed from content skills. Populated by the commerce platform.

### 6. Color & Size Selectors

- **Format:** Swatch grid (color) + button row (size)
- **Length:** N/A (functional elements)
- **Content:** Color name displayed as "Colour: [Color Name]". Size options displayed as individual buttons. Link to sizing chart below size row.
- **Notes:** No written content needed. Populated by product data.

### 7. Add to Cart & Utility Sections

- **Format:** Button + expandable rows
- **Length:** N/A (functional elements)
- **Content:** Add to cart button, expandable Delivery section (shipping/returns summary), expandable In-store Availability section, Product Details link
- **Notes:** No written content needed. Populated by platform logic.

### 8. Description

- **Format:** Accordion section with multiple content blocks
- **Length:** 150-250 words total across all blocks
- **Content:** The main product narrative. Contains the following sub-sections in order:

  **8a. Main Description**
  - 3-5 sentences. Narrative product description in second person ("you"). Opens with a use-case scenario, then explains key construction details and how they benefit the user. Ends with a short payoff sentence. Tone is confident and direct, not breathless or hyperbolic.

  **8b. What's Been Updated** *(conditional)*
  - 2-3 sentences preceded by a bold "What's been updated:" label. Appears only for revised or updated products. Lists specific changes: materials, construction, patterning. Factual, not promotional.

  **8c. Cross-Sell Link**
  - Single sentence with an inline linked product name. Format: "Need [alternative use case]? Try the [Product Name]." Points the user to a related product that serves a different need.

  **8d. Product Tip**
  - 1-3 sentences preceded by a bold "Product tip:" label. Practical usage advice: fit guidance, care notes, or performance expectations. Written as peer advice, not marketing copy.

- **Notes:** The Description section is the primary content block and the only section with a narrative voice. All other accordion sections are structured/tabular.

### 9. Features & Specs

- **Format:** Accordion section with a two-column grid of categorized bullet lists, followed by a key-value table
- **Length:** Varies by product complexity. Typically 8-14 category groups with 1-6 bullets each, plus 5-8 table rows.
- **Content:** Two distinct sub-sections:

  **9a. Categorized Feature Bullets**
  - Organized into named groups displayed in a two-column grid layout. First group is always "Technical features" (3-5 short keyword-style bullets naming core attributes). Remaining groups are category-specific:
    - *Apparel:* Construction, Cuff & Sleeves configuration, Design & Fit, Fabric treatment, Hem configuration, Hood configuration, Patterning, Pocket configuration, Snowsport features, Sustainability, Zippers & Fly configuration
    - *Footwear:* Footwear construction, Footwear geometry, Footwear outsole construction, Sustainability
  - Each bullet is a single sentence describing a feature and its benefit. Written as declarative statements, not fragments.

  **9b. Product Details Table**
  - Key-value table at the bottom. Standard rows: Size, Weight, Fit (apparel) or Sizing chart (footwear), Activity, Model, Manufacturing facility.

- **Notes:** The category groups vary significantly between product types. The two-column grid layout and the Technical Features group at the top are fixed. Sustainability group appears for all products.

### 10. Fit & Sizing

- **Format:** Accordion section with fit name, short explanation, and link to size chart
- **Length:** 30-80 words
- **Content:** Names the fit type (e.g., "Regular," "Precision Fit"), explains what it means for the wearer, and links to the size chart. Footwear products include guidance on choosing between fit variations (roomier, default, closer).
- **Notes:** Fit type names are brand-specific terminology. Apparel and footwear use different fit systems.

### 11. Materials & Care

- **Format:** Accordion section with two sub-lists
- **Length:** Varies. Materials list can be long for technical products.
- **Content:** Materials sub-section lists fabric compositions with technical specifications (denier, GSM, membrane type, origin). Care sub-section lists care instructions as short imperative phrases ("Machine wash medium," "Do not bleach").
- **Notes:** Materials entries include origin of fabric, dyeing, and manufacture. Technical apparel has significantly more detail here than footwear.

### 12. Layering Guide / Educational Content

- **Format:** Accordion section with a short paragraph and a link
- **Length:** 30-50 words
- **Content:** Brief explanation of a relevant educational concept (layering systems for apparel, fit systems for footwear) with a link to a dedicated guide page.
- **Notes:** Conditional. Section name and content vary by product category. May not appear for all product types.

### 13. Reviews

- **Format:** Accordion section
- **Length:** N/A (user-generated content)
- **Content:** Customer reviews. No written content needed from content skills.
- **Notes:** Platform-managed section.

### 14. Questions & Answers

- **Format:** Accordion section
- **Length:** N/A (user-generated content)
- **Content:** Customer Q&A. No written content needed from content skills.
- **Notes:** Platform-managed section.

---

## Structural Notes

The PDP is split into two zones. The top zone is the buy box: product images on the left, title through add-to-cart on the right. The bottom zone is an accordion panel with a sticky left-side navigation listing all section names. Sections expand inline when clicked from the nav.

The Description section is the only section with a narrative voice. All other sections are structured, tabular, or functional. This means downstream content skills primarily need to produce copy for sections 4, 8, 9, 10, and 11: the short description, the description accordion, features & specs, fit & sizing, and materials & care.

The Features & Specs section varies the most between product types. The overall structure (Technical Features group at top, category-specific groups in a two-column grid, product details table at bottom) is consistent, but the specific category group names change entirely between apparel and footwear. A downstream skill writing feature bullets needs to know the product type to use the correct group names.

Conditional sections include: Badge (not all products), What's Been Updated (revised products only), Layering Guide / Educational Content (category-dependent), and In-store Availability (may depend on retail presence).

---

## How to Use This Document

Upload this file alongside any SkillShelf skill that produces PDP content. The skill will use it as the structural blueprint: writing content that fits your section names, follows your format constraints, and matches your content expectations. The skill's other inputs (brand voice profile, positioning brief, product data) determine what the content says and how it sounds. This document determines where it goes and what shape it takes.

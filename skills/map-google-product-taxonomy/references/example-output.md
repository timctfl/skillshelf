# Example Output: Map Products to Google Product Taxonomy

**Brand:** GreatOutdoors Co.
**Source file:** shopify-products.csv
**Products scanned:** 15

---

## Taxonomy Classification Report

Products scanned: 15
High confidence (ready for batch approval): 11
Medium confidence (needs your input): 2
Low confidence (LLM-classified, needs review): 2
Title column: Title
Description column: Body (HTML)

---

### High Confidence: Proposed Mappings

| Product | Proposed Category | Matched Keywords |
|---|---|---|
| Cascade Rain Shell - Men's | Apparel & Accessories > Clothing > Outerwear > Coats & Jackets | rain shell, jacket, waterproof |
| Cascade Rain Shell - Women's | Apparel & Accessories > Clothing > Outerwear > Coats & Jackets | rain shell, jacket, waterproof |
| Alpine Meadow 2P Tent | Sporting Goods > Outdoor Recreation > Camping & Hiking > Tents | tent, backpacking tent, 2-person tent |
| Basecamp Pines 3P Tent | Sporting Goods > Outdoor Recreation > Camping & Hiking > Tents | tent, camping tent, 3-person tent |
| Frostline 20F Down Sleeping Bag | Sporting Goods > Outdoor Recreation > Camping & Hiking > Sleeping Bags | sleeping bag, down sleeping bag |
| Drift 40F Synthetic Sleeping Bag | Sporting Goods > Outdoor Recreation > Camping & Hiking > Sleeping Bags | sleeping bag, synthetic sleeping bag |
| Cedar Ridge 45L Trek Pack | Sporting Goods > Outdoor Recreation > Camping & Hiking > Backpacks & Bags > Hiking & Backpacking Packs | hiking backpack, trek pack, 45l pack |
| Cedar Ridge 25L Daypack | Sporting Goods > Outdoor Recreation > Camping & Hiking > Backpacks & Bags > Hiking & Backpacking Packs | daypack, hiking backpack, 25l pack |
| Trailmark Trekking Poles (Pair) | Sporting Goods > Outdoor Recreation > Camping & Hiking > Hiking Poles | trekking poles |
| Nightfall 350 Headlamp | Sporting Goods > Outdoor Recreation > Camping & Hiking > Camping Lights & Lanterns | headlamp |
| Ridgeline Hiking Socks - Crew | Apparel & Accessories > Clothing > Underwear & Socks > Socks | hiking socks, crew socks |

---

### Medium Confidence: Please Confirm

| Product | Proposed Category | Alternative | Signal |
|---|---|---|---|
| Timberline Fleece Pullover - Men's | Apparel & Accessories > Clothing > Activewear > Fleece Tops & Pullovers | Apparel & Accessories > Clothing > Outerwear > Coats & Jackets | Matched "fleece pullover" and "midlayer" for Fleece Tops, but "outerwear" and "waterproof" also scored for Coats & Jackets. Is this worn as a standalone layer or primarily as an underlayer? |
| Evergreen Merino Base Top - Men's | Apparel & Accessories > Clothing > Activewear > Active Tops | Apparel & Accessories > Clothing > Underwear & Socks > Thermal Underwear | Matched "merino base" and "base layer top" for Active Tops, but "base layer" and "thermal" also scored for Thermal Underwear. If this is primarily sold as a next-to-skin layer, Thermal Underwear is more specific. |

---

### Low Confidence: Needs Review

| Product | LLM Proposed Category | Reasoning |
|---|---|---|
| TrailClip Carabiner Keychain | Apparel & Accessories > Clothing Accessories > Keychains | This product is a decorative keychain shaped like a carabiner. Despite the outdoor-gear appearance, it is sold as an accessory, not as a load-bearing climbing tool. Keychains is the correct leaf-level category. |
| QuickDry Camp Towel | Home & Garden > Linens & Bedding > Towels | Camp towels occupy a gap between sporting goods and home goods. Google's taxonomy classifies all towels (including sport and travel towels) under Home & Garden > Linens & Bedding > Towels rather than under Camping & Hiking. |

---

After the merchant confirms the two medium-confidence items and approves the two LLM proposals, Turn 3 produces the following outputs:

---

## Output 1: Supplemental Feed CSV

```csv
id,title,google_product_category,google_product_category_id,classification_confidence,classification_source
cascade-rain-shell-mens,Cascade Rain Shell - Men's,Apparel & Accessories > Clothing > Outerwear > Coats & Jackets,5697,high,script
cascade-rain-shell-womens,Cascade Rain Shell - Women's,Apparel & Accessories > Clothing > Outerwear > Coats & Jackets,5697,high,script
timberline-fleece-pullover-mens,Timberline Fleece Pullover - Men's,Apparel & Accessories > Clothing > Activewear > Fleece Tops & Pullovers,5441,medium,script
evergreen-merino-base-top-mens,Evergreen Merino Base Top - Men's,Apparel & Accessories > Clothing > Underwear & Socks > Thermal Underwear,5338,medium,merchant-override
alpine-meadow-2p-tent,Alpine Meadow 2P Tent,Sporting Goods > Outdoor Recreation > Camping & Hiking > Tents,3261,high,script
basecamp-pines-3p-tent,Basecamp Pines 3P Tent,Sporting Goods > Outdoor Recreation > Camping & Hiking > Tents,3261,high,script
frostline-20f-down-sleeping-bag,Frostline 20F Down Sleeping Bag,Sporting Goods > Outdoor Recreation > Camping & Hiking > Sleeping Bags,3863,high,script
drift-40f-synthetic-sleeping-bag,Drift 40F Synthetic Sleeping Bag,Sporting Goods > Outdoor Recreation > Camping & Hiking > Sleeping Bags,3863,high,script
cedar-ridge-45l-trek-pack,Cedar Ridge 45L Trek Pack,Sporting Goods > Outdoor Recreation > Camping & Hiking > Backpacks & Bags > Hiking & Backpacking Packs,3032,high,script
cedar-ridge-25l-daypack,Cedar Ridge 25L Daypack,Sporting Goods > Outdoor Recreation > Camping & Hiking > Backpacks & Bags > Hiking & Backpacking Packs,3032,high,script
trailmark-trekking-poles,Trailmark Trekking Poles (Pair),Sporting Goods > Outdoor Recreation > Camping & Hiking > Hiking Poles,7107,high,script
nightfall-350-headlamp,Nightfall 350 Headlamp,Sporting Goods > Outdoor Recreation > Camping & Hiking > Camping Lights & Lanterns,7393,high,script
ridgeline-hiking-socks-crew,Ridgeline Hiking Socks - Crew,Apparel & Accessories > Clothing > Underwear & Socks > Socks,5388,high,script
trailclip-carabiner-keychain,TrailClip Carabiner Keychain,Apparel & Accessories > Clothing Accessories > Keychains,5243,low,llm
quickdry-camp-towel,QuickDry Camp Towel,Home & Garden > Linens & Bedding > Towels,691,low,llm
```

---

## Output 2: Classification Report

```markdown
# Google Product Taxonomy Classification Report

**Source file:** shopify-products.csv
**Products classified:** 15
**High confidence (script):** 11
**Medium confidence (script, confirmed):** 1
**Low confidence (LLM-classified):** 2
**Merchant overrides:** 1

---

## Full Mapping Table

| Product | Category Path | Category ID | Confidence | Source |
|---|---|---|---|---|
| Cascade Rain Shell - Men's | Apparel & Accessories > Clothing > Outerwear > Coats & Jackets | 5697 | high | script |
| Cascade Rain Shell - Women's | Apparel & Accessories > Clothing > Outerwear > Coats & Jackets | 5697 | high | script |
| Timberline Fleece Pullover - Men's | Apparel & Accessories > Clothing > Activewear > Fleece Tops & Pullovers | 5441 | medium | script |
| Evergreen Merino Base Top - Men's | Apparel & Accessories > Clothing > Underwear & Socks > Thermal Underwear | 5338 | medium | merchant-override |
| Alpine Meadow 2P Tent | Sporting Goods > Outdoor Recreation > Camping & Hiking > Tents | 3261 | high | script |
| Basecamp Pines 3P Tent | Sporting Goods > Outdoor Recreation > Camping & Hiking > Tents | 3261 | high | script |
| Frostline 20F Down Sleeping Bag | Sporting Goods > Outdoor Recreation > Camping & Hiking > Sleeping Bags | 3863 | high | script |
| Drift 40F Synthetic Sleeping Bag | Sporting Goods > Outdoor Recreation > Camping & Hiking > Sleeping Bags | 3863 | high | script |
| Cedar Ridge 45L Trek Pack | Sporting Goods > Outdoor Recreation > Camping & Hiking > Backpacks & Bags > Hiking & Backpacking Packs | 3032 | high | script |
| Cedar Ridge 25L Daypack | Sporting Goods > Outdoor Recreation > Camping & Hiking > Backpacks & Bags > Hiking & Backpacking Packs | 3032 | high | script |
| Trailmark Trekking Poles (Pair) | Sporting Goods > Outdoor Recreation > Camping & Hiking > Hiking Poles | 7107 | high | script |
| Nightfall 350 Headlamp | Sporting Goods > Outdoor Recreation > Camping & Hiking > Camping Lights & Lanterns | 7393 | high | script |
| Ridgeline Hiking Socks - Crew | Apparel & Accessories > Clothing > Underwear & Socks > Socks | 5388 | high | script |
| TrailClip Carabiner Keychain | Apparel & Accessories > Clothing Accessories > Keychains | 5243 | low | llm |
| QuickDry Camp Towel | Home & Garden > Linens & Bedding > Towels | 691 | low | llm |

---

## Merchant Overrides

| Product | Script Proposed | Merchant Chose | Reason |
|---|---|---|---|
| Evergreen Merino Base Top - Men's | Apparel & Accessories > Clothing > Activewear > Active Tops | Apparel & Accessories > Clothing > Underwear & Socks > Thermal Underwear | Merchant confirmed this is sold as a next-to-skin base layer, not an outerwear active top |
```

---

## Pipeline Note

The 11 apparel items in this catalog now have `google_product_category` assigned. Items in the Apparel & Accessories tree trigger Google's requirement for `color`, `size`, `gender`, and `age_group` attributes. Run the Audit a Google Merchant Feed skill next to check whether those required attributes are present in the feed. If they are missing, those items will be disapproved in Google Shopping regardless of taxonomy accuracy.

# Fixtures

Fixtures are sample data files you can use to test skills. They have the same structure as real ecommerce exports but everything is fictional, so you can share, modify, and experiment freely.

To use a fixture, pick a skill and a data file, then paste both into your AI tool.

## Quick start

1. Open your AI tool (Claude, ChatGPT, etc.)
2. Upload or paste the SKILL.md from the skill you want to test
3. Upload or paste a fixture file that matches the skill's input type (e.g., `shopify-products.csv` for a skill that accepts product data)
4. Run the skill and compare the output against the example in `references/example-output.md`

For skills that consume primitive output (brand voice profile, positioning brief), find pre-generated versions in [`greatoutdoorsco/skill-outputs/`](greatoutdoorsco/skill-outputs/).

## Available fixture sets

| Set | Description |
|-----|-------------|
| [Great Outdoors Co.](greatoutdoorsco/) | 30-product DTC outdoor brand. Shopify CSV/JSON, Google Merchant XML, product attributes, taxonomy, and 4 PDPs (clean, technical, minimal, messy). |

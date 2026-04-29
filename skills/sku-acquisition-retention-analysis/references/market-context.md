# **Algorithmic Merchandising in the Era of Agentic Commerce: A Technical Blueprint for the Acquisition SKU vs. Retention SKU Analysis Skill**

The digital commerce landscape of 2026 has undergone a fundamental structural transformation, moving away from the aggressive, top-of-funnel acquisition models of the early 2020s toward a sophisticated paradigm of revenue retention and profitability-driven merchandising. This shift is primarily dictated by a dramatic escalation in customer acquisition costs (CAC), which have surged by approximately 222% over the last five years.1 As paid media arbitrage reaches a point of terminal diminishing returns, the strategic imperative for Shopify merchants has pivoted toward the granular interrogation of first-party data. The capability to distinguish between a product that serves as an effective acquisition gateway and one that functions as a retention driver is no longer a peripheral optimization; it is the core requirement for organizational survival in an environment where the average brand loses nearly $29 on every new customer acquired.1

The emergence of "Agentic Commerce" represents the technological response to this economic pressure. Artificial intelligence agents, such as Claude and Codex, are no longer relegated to simple chat interfaces but are being integrated as operational copilots capable of executing complex data workflows.2 To facilitate this, the standardization of the SKILL.md format provides a robust framework for authoring reusable, machine-readable workflows that enable AI agents to perform high-level analytical tasks.4 The "Acquisition SKU vs. Retention SKU Analysis" skill is designed to leverage this framework, transforming raw Shopify CSV exports into a strategic merchandising roadmap that optimizes for lifetime value (LTV) rather than immediate return on ad spend (ROAS).2

## **The Strategic Imperative: Why SKU Role Mapping is Essential in 2026**

The contemporary e-commerce merchant operates within a paradox: growth requires a continuous influx of new customers, yet the economics of 2026 dictate that sustainable profit is generated almost exclusively through the second, third, and fourth purchases.7 Native Shopify reporting tools, while functional for general sales tracking, often fail to provide the multi-dimensional view necessary to identify specific product pathways that lead to high-value customer cohorts.9 Traditional dashboards treat every dollar of revenue with equal weight, failing to account for the fact that a $50 purchase of a "Gateway SKU" is significantly more valuable than a $50 purchase of a "One-Time SKU" if the former leads to a 40% higher repeat purchase rate.6

In 2026, the delta between optimized and unoptimized stores is widening as mature markets experience a contraction in new user acquisition. For example, North America has seen a 58% drop in new user acquisition, forcing brands to refocus on "stickiness" as the defining growth metric.12 This transition necessitates a move from vanity personalization to profit-focused personalization, where AI agents analyze behavior to fix friction and identify high-leverage products.13 The "Acquisition SKU vs. Retention SKU Analysis" skill addresses this by systematically classifying the product catalog into roles that align with the business owner's profitability goals.14

### **Comparative Economic Benchmarks: 2023 vs. 2026**

| Metric | 2023 Benchmark | 2026 Benchmark | Strategic Implication |
| :---- | :---- | :---- | :---- |
| Customer Acquisition Cost (CAC) | $40 \- $70 (Avg. DTC) | $120 \- $210 (Market Saturation) | Acquisition must be viewed as a long-term investment, not a profit center.1 |
| LTV:CAC Ratio | 2:1 (Considered Stable) | 3:1 (Minimum Requirement) | Higher retention is required to offset rising media costs.2 |
| Repeat Purchase Rate (Beauty) | 25% \- 30% | 30% \- 45% | Replenishment dynamics are critical for category leaders.17 |
| Probability of Selling to Existing Customer | 60% \- 70% | 65% \- 75% | Efficiency is found in mining the current customer base.2 |
| Retention Profit Impact | 5% Lift \= 25% Profit | 5% Lift \= 25% \- 95% Profit | The leverage of retention increases as operations costs rise.1 |

## **Architectural Standards for the SKILL.md Framework**

The development of a new skill for Claude or Codex must adhere to the standardized protocol established in late 2025\. This format utilizes a "progressive disclosure" system to manage the context window efficiently.4 In this system, only the metadata—specifically the name and description—is pre-loaded at the start of a session. The full instructions contained within the SKILL.md file are only read by the agent when the user's request matches the skill’s description.18 This architecture ensures that the agent's context window remains focused on the task at hand, preventing "context burn" and maintaining high performance across complex multi-turn conversations.18

### **Tiered Instruction Hierarchy**

A professional implementation of the SKU analysis skill requires a three-tier documentation structure to ensure clarity and maintainability 19:

1. **Tier 1: Root CLAUDE.md**: This file contains universal rules that apply to every task in the repository, such as coding standards, preferred data libraries (e.g., Pandas for Python-based analysis), and general financial reporting conventions.19
2. **Tier 2: SKILL.md (The Analysis Playbook)**: This is the task-specific instruction set. It defines the "narrow bridge" with specific guardrails for data processing while allowing the LLM an "open field" for strategic merchandising recommendations.18
3. **Tier 3: Agent Guides**: These are deep reference materials, such as documentation on Shopify's 2026 CSV export headers or multi-currency rounding logic, which the agent can query only when it needs granular technical details.19

### **Metadata and Selection Logic**

The YAML frontmatter of the SKILL.md file is critical for skill discovery. Claude uses the description field to distinguish the current skill from potentially 100+ others.18 For the Acquisition vs. Retention analysis, the description must be concise but rich in trigger keywords.4

YAML

\---
name: acquisition-retention-sku-analysis
description: Performs SKU-level role mapping and merchandising strategy generation using Shopify Orders, Customers, and Product CSV data. Use this when a merchant needs to identify which products drive first purchases versus repeat orders to optimize ad spend and retention flows.
\---

## **Data Engineering: Interrogating the 2026 Shopify CSV Ecosystem**

The efficacy of the SKU role map is entirely dependent on the structural integrity and cleanliness of the input data. In 2026, the Shopify data model has become increasingly multi-dimensional, incorporating "Shopify Markets" for international pricing, native "Bundles" for grouped products, and "Subscription Contracts" for recurring revenue.21 The analysis script must be architected to ingest three primary CSV files: the Orders CSV, the Customers CSV, and the Product CSV.24

### **The Product CSV: Market-Specific Context**

The 2026 Product CSV includes columns for prices and compare-at prices for every active market. For an international brand, this means the script must handle columns like Price / North America, Price / United Kingdom, and Price / International.25

| Feature | Shopify Native Product Model | 2026 SKU Management Nuance |
| :---- | :---- | :---- |
| **Variants** | Up to 2,048 variants per product. | High variant counts (e.g., in fashion) require aggregation at the parent handle level for meaningful role mapping.27 |
| **Metafields** | Supported in format \<name\> (product.metafields.\<namespace\>.\<key\>). | Essential for categorizing SKUs by "Seasonality" or "Margin Tier" to provide better merchandising context.22 |
| **Inventory Tracking** | Tracks shopify, shipwire, or amazon\_marketplace\_web. | Role mapping must prioritize "A items" (high volume/impact) to prevent stockouts of Superstar SKUs.15 |
| **Markets Pricing** | Fixed prices override FX conversions. | The script must identify which market is being analyzed to calculate accurate "Landed Cost" and margins per region.23 |

### **The Orders CSV: Sequence and Attribution**

The Orders CSV is the primary source of truth for purchase behavior. To accurately categorize a product as an "Acquisition SKU," the script must identify every customer's "Gateway Order"—their chronologically first transaction.9 A critical edge case in 2026 is the "Shopify Bundles" app integration. In the default export, bundle components are displayed under the line item with the label "Part of:".32 The script must use the line\_items.line\_item\_group.title and id fields to ensure that revenue and attribution are correctly assigned to the bundle parent rather than double-counted across child SKUs.32

### **The Customers CSV: Cohort Stability**

While the Customers CSV contains aggregated fields like Total Spent and Total Orders, these are "point-in-time" snapshots and cannot be imported or back-calculated for historical accuracy without the full Orders history.34 Furthermore, the 2026 privacy landscape has made Customer ID stability more fragile due to third-party cookie death and the rise of social sign-ins.27 The analysis script should prioritize matching based on the Email field, while accounting for the common issue of customers using different emails to abuse first-order discounts.36

## **Algorithmic Processing: The Script Logic for SKU Role Classification**

The "Script" component of the skill is responsible for the quantitative heavy lifting. It executes a series of joins and calculations to transform raw transactions into a behavioral matrix. The logic follows a specific sequence to handle refunds, multi-currency conversions, and sequence detection.

### **Stage 1: Data Sanitization and Normalization**

Before analysis, the script must normalize all financial values into the store's base currency (shop\_money). Because Shopify's multi-currency feature involves rounding discrepancies between the Order API (line-item level) and Transaction API (total level), the script must implement a standardized rounding function to ensure that "Total Spent" by a customer matches the sum of their individual orders.20

### **Stage 2: Sequence Detection and FPR Calculation**

The script identifies the first purchase for each unique customer. This is a critical step because identifying the "First Purchase Ratio" (FPR) allows the business to see which products are most effective at converting strangers into buyers.9

![][image1]
A high FPR (e.g., \> 0.70) indicates that a product is an "Acquisition Gateway." If the FPR is low (e.g., \< 0.20), the product is almost exclusively purchased by returning customers, making it a "Retention Driver".14

### **Stage 3: Repeat Order Indexing (ROI)**

The script then calculates the "Repeat Order Index" (ROI) for each product category and individual SKU. This measures how often a SKU appears in second, third, or subsequent orders compared to the store's average baseline.38

| Role Category | Data Signal (FPR) | Data Signal (ROI) | Strategic Function |
| :---- | :---- | :---- | :---- |
| **Acquisition Gateway** | High (\> 60%) | Low | The "Front Door" products used to lower CAC and attract new cohorts.14 |
| **Retention Driver** | Low (\< 20%) | High | Replenishables or high-consideration items that build brand depth.11 |
| **Superstar SKU** | High (\> 40%) | High (\> 40%) | Rare products that both attract and retain customers; these are the "A-items".6 |
| **Legacy / Seasonal** | Low | Low | Niche or outdated items that may be better suited for "Draft" status or liquidation.28 |

### **Stage 4: Handling Refunds and Churn in Cohorts**

A common error in SKU analysis is the inclusion of refunded orders in retention metrics, which artificially inflates the perceived value of a product. The script must filter for Financial Status \= 'paid' or adjust the Total Spent by subtracting the Refund Amount.24 In the context of "Shopify Subscriptions," the script should calculate the "Initial Cycle Retention," identifying which SKUs lead to the highest percentage of customers continuing their plan after the first billing cycle.41

## **LLM Orchestration: The Art of the Merchandising Brief**

Once the script has produced the "Product Role Map," the LLM (Claude or Codex) takes over the role of a Senior Brand Strategist and Merchandising Lead. The LLM's goal is to translate these numbers into a practical action plan that the business owner can execute.3 The skill provides the LLM with the context of the business model—whether it is "Low Ticket, High Frequency" (e.g., CPG) or "High Ticket, Low Frequency" (e.g., Luxury Furniture)—as the definition of "Good" retention varies wildly across these categories.40

### **Strategic Merchandising Frameworks**

The LLM uses the "4 E-commerce Product Types" framework to refine its recommendations 40:

* **Low Ticket, High Frequency (CPG)**: The focus is on replenishment cycles and subscription "flexibility." The LLM identifies Gateways that have high acquisition but low follow-up, suggesting "Browse Abandonment" or "Win-back" SMS campaigns.40
* **High Ticket, Low Frequency (Luxury)**: The focus is on "Trust Infrastructure." The LLM identifies which SKUs serve as the entry point and recommends featuring "Social Proof" (UGC, Reviews) specifically for those items in acquisition ads.2

### **Generating the Positioning Statement and Brand Pillars**

For each key SKU role, the LLM generates an internal positioning statement using the internal tool standard: "For \[Primary Audience\] who \[Core Need\], is the \[Category\] that because".46 This statement guides the creative team's copy for landing pages and ad creative, ensuring that the marketing message aligns with the product's proven behavioral role.46

### **Case Study: Vertical-Specific Retention Benchmarks in 2026**

| Vertical | Annual Repeat Rate | 12-Month Cohort Retention | Merchandising Focus |
| :---- | :---- | :---- | :---- |
| **Beauty / Skin** | 30% \- 45% | 25% \- 40% | Auto-replenishment;Routine-based bundles.17 |
| **Fashion** | 20% \- 35% | 18% \- 30% | Seasonal collection drops; Cross-sell by style.17 |
| **Food & Bev** | 35% \- 50% | 30% \- 45% | Bulk purchase incentives; High-frequency reorder flows.17 |
| **Home / Premium** | 10% \- 20% | 8% \- 15% | VIP treatment; Accessories for core high-ticket units.17 |

## **Addressing Business Pain Points: Real-World Implementation Value**

For a Shopify store owner, the value of this skill lies in its ability to solve the "profit leak" caused by misallocated ad spend. In 2026, many brands are "refilling a leaky bucket"—spending $100 to acquire a customer who only buys a $30 item once and never returns.48 This analysis identifies those "False Gateways" so they can be removed from acquisition campaigns.

### **The Problem of "Cheap Clicks"**

A common trap is optimizing for a low CAC without considering LTV. "Cheap" customers often stay cheap; they buy only on discount and have a 5-20% conversion probability for a second purchase.6 By identifying "High-LTV Lookalikes" based on the Superstar SKUs, the LLM helps the merchant redirect their budget toward cohorts that pay back their CAC within 60 days rather than 18 months.1

### **Inventory and Operational Efficiency**

The "Acquisition SKU vs. Retention SKU Analysis" also informs inventory strategy. Using "ABC Analysis," the skill flags Superstar and Gateway SKUs as "A-items" that require 20-30% higher safety stock buffers.2 Conversely, Legacy SKUs are flagged for "Markdown" or "Bundling" to improve inventory turnover rates and free up cash flow—a critical necessity in the high-interest-rate environment of 2026\.2

## **Edge Cases and Technical Tradeoffs in 2026**

No analysis is perfect, and the 2026 Shopify ecosystem presents several challenges that require nuanced handling and transparent tradeoffs.

### **Tradeoff 1: Attribution Ambiguity**

In 2026, Meta, Google, and Shopify each claim credit for sales differently.6 The script relies on "First-Party Data" (the Orders CSV), which provides the most accurate view of the transaction sequence but lacks the "Touchpoint" data of an attribution platform. The solution is to use the analysis as a "Directional Truth" for product roles rather than a perfect measure of channel performance.1

### **Tradeoff 2: Privacy and Identity Resolution**

With the death of third-party cookies, matching a "Guest Checkout" customer to their past history is difficult if they use different names or addresses. The script uses the Customer ID and Email as primary keys but acknowledges a 5-10% error rate in "New vs. Returning" classification due to identity fragmentation.34

### **Edge Case: The B2B / Wholesale Hybrid**

Shopify Plus merchants in 2026 often use a single store for both DTC and B2B.27 The script must filter out orders tagged as "Wholesale" or "B2B" when analyzing DTC SKU roles, as B2B purchase cycles (high volume, low frequency) would skew the retention metrics for a consumer audience.22

### **Edge Case: International Fixed Pricing and FX**

If a store uses "Fixed Prices" for different markets, the Price column in the Orders CSV may not reflect the current exchange rate.20 The script must cross-reference the Currency Code of the order to ensure that LTV is calculated in a "Constant Currency" to avoid misleading trends caused by FX volatility.20

## **Future Outlook: The Role of AI Agents in 2026 Merchandising**

The "Acquisition SKU vs. Retention SKU Analysis" is more than a one-off report; it is a component of a larger "Compounding Growth Loop".8 As AI agents become more autonomous, they will move from "Analysis" (reading CSVs) to "Activation" (updating Shopify Flow or Meta Audience segments).3 The 2026 Winter Edition of Shopify has already introduced "Shortcuts" like /inventory-check and /bundle-finder, signaling a move toward integrated AI assistance within the admin dashboard.27

The SKILL.md format allows these agents to operate with a high degree of precision while maintaining the flexibility to adapt to a brand's unique "Ethos".46 By leveraging the specific product behaviors revealed through this analysis, merchants can build "Durable Customer Relationships" that withstand the volatility of ad platforms and the rising costs of the digital economy.12

## **Implementation Plan for the Business Owner**

To realize the value of this skill, the business owner should follow a phased implementation roadmap:

1. **Phase 1: Data Audit (Weeks 1-2)**: Ensure SKU naming conventions are consistent across the WMS, Shopify, and Ad platforms. Clean up duplicate listings and ensure that "Lineitem Group" data is correctly being captured for bundles.22
2. **Phase 3: Automated Analysis (Week 3\)**: Deploy the SKILL.md to the Claude/Codex environment. Execute the initial role mapping to identify the top 5 Acquisition Gateways and Retention Drivers.5
3. **Phase 4: Merchandising Activation (Week 4\)**: Implement the brief's recommendations. Shift ad budget toward Gateway SKUs and update post-purchase email flows with the identified Retention Drivers.6
4. **Phase 5: Evaluation and Iteration (Monthly)**: Re-run the analysis every 30 days to observe how cohort retention shifts in response to the new merchandising strategy. Adjust the SKU roles as new products ramp up and seasonal cycles shift.17

In conclusion, the "Acquisition SKU vs. Retention SKU Analysis" provides the strategic clarity necessary to navigate the high-CAC environment of 2026\. By turning raw Shopify data into a machine-executable merchandising brief, brands can move from reactive survival to proactive, profitability-focused growth.1

#### **Works cited**

1. Customer Retention vs Acquisition Cost: Beyond 5x \- Releva.AI, accessed April 29, 2026, [https://releva.ai/blog/customer-retention-vs-acquisition-cost/](https://releva.ai/blog/customer-retention-vs-acquisition-cost/)
2. 2026 Ecommerce Benchmarks: The Efficiency Imperative \- Yotpo, accessed April 29, 2026, [https://www.yotpo.com/blog/ecommerce-benchmarks-2026/](https://www.yotpo.com/blog/ecommerce-benchmarks-2026/)
3. The exact LLM prompts media buyers are using right now \- The Current, accessed April 29, 2026, [https://www.thecurrent.com/marketing-strategy-llm-prompts-media-buyers-using-right-now-ai](https://www.thecurrent.com/marketing-strategy-llm-prompts-media-buyers-using-right-now-ai)
4. The SKILL.md Pattern: How to Write AI Agent Skills That Actually Work | by Bibek Poudel, accessed April 29, 2026, [https://bibek-poudel.medium.com/the-skill-md-pattern-how-to-write-ai-agent-skills-that-actually-work-72a3169dd7ee](https://bibek-poudel.medium.com/the-skill-md-pattern-how-to-write-ai-agent-skills-that-actually-work-72a3169dd7ee)
5. Agent Skills – Codex | OpenAI Developers, accessed April 29, 2026, [https://developers.openai.com/codex/skills](https://developers.openai.com/codex/skills)
6. 9 eCommerce Customer Acquisition Strategies for 2026 | Saras Analytics, accessed April 29, 2026, [https://www.sarasanalytics.com/blog/ecommerce-customer-acquisition](https://www.sarasanalytics.com/blog/ecommerce-customer-acquisition)
7. Retention Strategy vs Acquisition Strategy: What Scales Faster? \- Ancorrd, accessed April 29, 2026, [https://ancorrd.com/retention-vs-acquisition-d2c-growth-strategy/](https://ancorrd.com/retention-vs-acquisition-d2c-growth-strategy/)
8. Acquisition vs retention — what should you focus on? \- Kasva, accessed April 29, 2026, [https://www.kasva.io/post/acquisition-vs-retention-what-should-you-focus-on](https://www.kasva.io/post/acquisition-vs-retention-what-should-you-focus-on)
9. Customer report for first product purchased and total number of orders for that customer, accessed April 29, 2026, [https://community.shopify.com/t/customer-report-for-first-product-purchased-and-total-number-of-orders-for-that-customer/114335](https://community.shopify.com/t/customer-report-for-first-product-purchased-and-total-number-of-orders-for-that-customer/114335)
10. Finding if a customer is first time or returning customer per order via API, accessed April 29, 2026, [https://community.shopify.com/t/finding-if-a-customer-is-first-time-or-returning-customer-per-order-via-api/21487](https://community.shopify.com/t/finding-if-a-customer-is-first-time-or-returning-customer-per-order-via-api/21487)
11. Customer Acquisition vs Retention: Which to Prioritize? | Post Affiliate Pro, accessed April 29, 2026, [https://www.postaffiliatepro.com/blog/customer-acquisition-vs-retention/](https://www.postaffiliatepro.com/blog/customer-acquisition-vs-retention/)
12. 2026 Ecommerce benchmarks: From growth at all costs to habit-driven commerce, accessed April 29, 2026, [https://mixpanel.com/blog/ecommerce-benchmarks-2026/](https://mixpanel.com/blog/ecommerce-benchmarks-2026/)
13. 10 Ecommerce Trends for 2026: AI, Social Commerce, Returns & CRO \- Plerdy, accessed April 29, 2026, [https://www.plerdy.com/blog/10-ecommerce-trends/](https://www.plerdy.com/blog/10-ecommerce-trends/)
14. Acquisition vs. Retention: Where to Invest in 2025? | Gravytrain, accessed April 29, 2026, [https://gravytrain.co.uk/news-and-views/acquisition-vs-retention-where-to-invest-in-2025/](https://gravytrain.co.uk/news-and-views/acquisition-vs-retention-where-to-invest-in-2025/)
15. Ecommerce inventory management for smarter replenishment \- Amazon Business, accessed April 29, 2026, [https://business.amazon.com/en/blog/ecommerce-inventory-management](https://business.amazon.com/en/blog/ecommerce-inventory-management)
16. Customer Acquisition Vs. Retention: Which Drives Profit? \- Yotpo, accessed April 29, 2026, [https://www.yotpo.com/blog/cost-of-customer-acquisition-vs-retention/](https://www.yotpo.com/blog/cost-of-customer-acquisition-vs-retention/)
17. E-commerce Retention Rate Benchmarks (2026): Where Does Your Brand Actually Stand?, accessed April 29, 2026, [https://finsi.ai/blog/ecommerce-retention-rate-benchmarks/](https://finsi.ai/blog/ecommerce-retention-rate-benchmarks/)
18. Skill authoring best practices \- Claude API Docs, accessed April 29, 2026, [https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
19. Implementing CLAUDE.md and Agent Skills In Your Repository \- Matthew Groff, accessed April 29, 2026, [https://www.groff.dev/blog/implementing-claude-md-agent-skills](https://www.groff.dev/blog/implementing-claude-md-agent-skills)
20. Shopify's Multi-Currency \- Global-e, accessed April 29, 2026, [https://docs.global-e.com/enterprise/en/shopify-s-multi-currency.html](https://docs.global-e.com/enterprise/en/shopify-s-multi-currency.html)
21. Importing and exporting a contract CSV \- Shopify Help Center, accessed April 29, 2026, [https://help.shopify.com/en/manual/products/purchase-options/subscriptions/shopify-subscriptions/import-export/importing-and-exporting](https://help.shopify.com/en/manual/products/purchase-options/subscriptions/shopify-subscriptions/import-export/importing-and-exporting)
22. Ecommerce Data Migration Guide: 5 Steps \+ Success Stories (2026) \- Shopify, accessed April 29, 2026, [https://www.shopify.com/enterprise/blog/ecommerce-data-migration](https://www.shopify.com/enterprise/blog/ecommerce-data-migration)
23. Everything You Need to Know About Shopify Markets, accessed April 29, 2026, [https://www.wemakewebsites.com/blog/everything-you-need-to-know-about-shopify-markets](https://www.wemakewebsites.com/blog/everything-you-need-to-know-about-shopify-markets)
24. Exporting orders \- Shopify Help Center, accessed April 29, 2026, [https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders](https://help.shopify.com/en/manual/fulfillment/managing-orders/exporting-orders)
25. Using CSV files to import and export products \- Shopify Help Center, accessed April 29, 2026, [https://help.shopify.com/en/manual/products/import-export/using-csv](https://help.shopify.com/en/manual/products/import-export/using-csv)
26. Set product prices by country \- Shopify Help Center, accessed April 29, 2026, [https://help.shopify.com/en/manual/international/pricing/product-prices-by-country](https://help.shopify.com/en/manual/international/pricing/product-prices-by-country)
27. Shopify Editions | Winter '26, accessed April 29, 2026, [https://www.shopify.com/editions/winter2026](https://www.shopify.com/editions/winter2026)
28. SKU Data Entry in eCommerce: Best Practices for Accurate Catalogs, accessed April 29, 2026, [https://www.dataentryoutsourced.com/blog/sku-data-entry-in-ecommerce-business/](https://www.dataentryoutsourced.com/blog/sku-data-entry-in-ecommerce-business/)
29. Benefits of SKU Categorization for Inventory Control \- Emplicit, accessed April 29, 2026, [https://emplicit.co/benefits-of-sku-categorization-for-inventory-control/](https://emplicit.co/benefits-of-sku-categorization-for-inventory-control/)
30. How to configure market specific pricing in Shopify \- EAS, accessed April 29, 2026, [https://help.easproject.com/hc/en-gb/articles/5021920704671-How-to-configure-market-specific-pricing-in-Shopify](https://help.easproject.com/hc/en-gb/articles/5021920704671-How-to-configure-market-specific-pricing-in-Shopify)
31. Unlock Customer Retention: The Complete Guide to Cohort Analysis with SQL \- Medium, accessed April 29, 2026, [https://medium.com/@harsh1995hg/unlock-customer-retention-the-complete-guide-to-cohort-analysis-with-sql-7ca193ae44a8](https://medium.com/@harsh1995hg/unlock-customer-retention-the-complete-guide-to-cohort-analysis-with-sql-7ca193ae44a8)
32. Can I export the bundle info from the Shopify Bundles app as part of my order CSV export?, accessed April 29, 2026, [https://www.highviewapps.com/kb/can-i-export-the-bundle-info-from-the-shopify-bundles-app-as-part-of-my-order-csv-export/](https://www.highviewapps.com/kb/can-i-export-the-bundle-info-from-the-shopify-bundles-app-as-part-of-my-order-csv-export/)
33. EZ Exporter Update: Shopify Bundles Info Now Available in Order Exports | Highview Apps, accessed April 29, 2026, [https://www.highviewapps.com/blog/ez-exporter-update-shopify-bundles-info-now-available-in-order-exports/](https://www.highviewapps.com/blog/ez-exporter-update-shopify-bundles-info-now-available-in-order-exports/)
34. Importing and exporting customer lists \- Shopify Help Center, accessed April 29, 2026, [https://help.shopify.com/en/manual/customers/import-export-customers](https://help.shopify.com/en/manual/customers/import-export-customers)
35. Top Ecommerce Trends for 2026 (What's Actually Working), accessed April 29, 2026, [https://easyappsecom.com/guides/shopify-trends-2026.html](https://easyappsecom.com/guides/shopify-trends-2026.html)
36. How does Shopify identify new customers for first order discounts?, accessed April 29, 2026, [https://community.shopify.com/t/how-does-shopify-identify-new-customers-for-first-order-discounts/230953](https://community.shopify.com/t/how-does-shopify-identify-new-customers-for-first-order-discounts/230953)
37. How can I use FLOW to identify first time customers on the Orders Summary Page?, accessed April 29, 2026, [https://community.shopify.com/t/how-can-i-use-flow-to-identify-first-time-customers-on-the-orders-summary-page/401474](https://community.shopify.com/t/how-can-i-use-flow-to-identify-first-time-customers-on-the-orders-summary-page/401474)
38. Repeat Purchase Rate: Formula, Benchmarks & Tips \- Count.co, accessed April 29, 2026, [https://count.co/metric/repeat-purchase-rate](https://count.co/metric/repeat-purchase-rate)
39. Customer Retention Rate: Formula & Industry Averages \- Triple Whale, accessed April 29, 2026, [https://www.triplewhale.com/blog/customer-retention-rate](https://www.triplewhale.com/blog/customer-retention-rate)
40. A CMO's Guide to the 4 E-commerce Product Types \- Digital Position, accessed April 29, 2026, [https://www.digitalposition.com/resources/blog/ppc/a-cmos-guide-to-the-4-e-commerce-product-types/](https://www.digitalposition.com/resources/blog/ppc/a-cmos-guide-to-the-4-e-commerce-product-types/)
41. 9 eCommerce Customer Retention Strategies to Help Increase ROI | Saras Analytics, accessed April 29, 2026, [https://www.sarasanalytics.com/blog/ecommerce-customer-retention](https://www.sarasanalytics.com/blog/ecommerce-customer-retention)
42. Merchandising Analytics AI Prompts for Ecommerce Analyst | MLJAR Studio, accessed April 29, 2026, [https://mljar.com/ai-prompts/ecommerce-analyst/merchandising-analytics/](https://mljar.com/ai-prompts/ecommerce-analyst/merchandising-analytics/)
43. How to Perform a Customer Cohort Analysis \- Sigma Computing, accessed April 29, 2026, [https://www.sigmacomputing.com/blog/perform-a-customer-cohort-analysis](https://www.sigmacomputing.com/blog/perform-a-customer-cohort-analysis)
44. Best AI Prompts for Ecommerce: Guide to Effective LLM Prompting & Automation \- Admetrics, accessed April 29, 2026, [https://www.admetrics.io/en/post/ecommerce-prompts](https://www.admetrics.io/en/post/ecommerce-prompts)
45. (Acquisition vs. Retention) Do we focus too much on new customers in business and not enough on keeping the ones we already have? : r/ecommerce \- Reddit, accessed April 29, 2026, [https://www.reddit.com/r/ecommerce/comments/1mz5wqz/acquisition\_vs\_retention\_do\_we\_focus\_too\_much\_on/](https://www.reddit.com/r/ecommerce/comments/1mz5wqz/acquisition_vs_retention_do_we_focus_too_much_on/)
46. 10 Branding Best Practices to Follow in 2026 \- Shopify, accessed April 29, 2026, [https://www.shopify.com/enterprise/blog/brand-marketing-ecommerce](https://www.shopify.com/enterprise/blog/brand-marketing-ecommerce)
47. How To Write a Product Brief: Product Brief Template \+ Guide (2026) \- Shopify, accessed April 29, 2026, [https://www.shopify.com/blog/product-brief](https://www.shopify.com/blog/product-brief)
48. Customer Acquisition vs. Retention: Cost Comparison Guide \- Churnkey, accessed April 29, 2026, [https://churnkey.co/blog/customer-acquisition-vs-retention-cost-comparison-guide/](https://churnkey.co/blog/customer-acquisition-vs-retention-cost-comparison-guide/)
49. Understanding Shopify Markets For Global Expansion 2026 \- AdNabu Blog, accessed April 29, 2026, [https://blog.adnabu.com/shopify/shopify-markets/](https://blog.adnabu.com/shopify/shopify-markets/)
50. Mastering SKU-Level Data: A Practical Guide for eCommerce Experts \- Medium, accessed April 29, 2026, [https://medium.com/@gdoitwebpvtltd/mastering-sku-level-data-a-practical-guide-for-ecommerce-experts-f89ef4c5f35e](https://medium.com/@gdoitwebpvtltd/mastering-sku-level-data-a-practical-guide-for-ecommerce-experts-f89ef4c5f35e)

[image1]: <data:image/png;base64,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>
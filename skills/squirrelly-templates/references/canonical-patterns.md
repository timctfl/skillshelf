# Canonical Studio Template Patterns

These are confirmed-working patterns pulled from real Studio templates. Adapt them to the user's specific fields. Each pattern shows the one-liner (what gets pasted into Studio), a readable multi-line version (for understanding only), and notes on why it is structured the way it is.

## Table of Contents

1. Optional feed field with bracket notation
2. Conditional title from prior selections
3. Regional price formatting (nested `@if` for 3 or more branches)
4. HTML output with inline event handlers
5. Nested loops with cross-question lookup

---

## Pattern 1: Optional feed field with bracket notation

Show a value only when it exists. Handles both `null` and empty string in one check because both are falsy.

**One-liner:**

```
{{@if(product.joins["Regulator Secundary"]["Promo Message"])}}{{product.joins["Regulator Secundary"]["Promo Message"]}}{{/if}}
```

**Readable:**

```
{{@if(product.joins["Regulator Secundary"]["Promo Message"])}}
  {{product.joins["Regulator Secundary"]["Promo Message"]}}
{{/if}}
```

**Why it is structured this way:** the truthiness check naturally handles both `null` and `""` (both are falsy, so nothing renders). Bracket notation is required because the field names contain spaces.

---

## Pattern 2: Conditional title from prior selections

Override the question title based on a previous answer. Useful when a quiz question's wording should change depending on who the user is shopping for, what they selected earlier, etc.

**One-liner:**

```
{{@if(selections["who"])}}{{@each(selections["who"]) => item}}{{@if(item.name !== "Myself")}} What is their preferred style of underwear?{{#else}}{{question.title}}{{/if}}{{/each}}{{#else}}{{""}}{{/if}}
```

**Readable:**

```
{{@if(selections["who"])}}
  {{@each(selections["who"]) => item}}
    {{@if(item.name !== "Myself")}}
       What is their preferred style of underwear?
    {{#else}}
      {{question.title}}
    {{/if}}
  {{/each}}
{{#else}}
  {{""}}
{{/if}}
```

**Why it is structured this way:** `selections["who"]` is the array of items the user picked on the "who" question. The `@each` is needed because selections are arrays even when only one item is chosen. `{{""}}` outputs an empty string when there is no selection. Bracket notation is required because keys come from quiz codeNames.

---

## Pattern 3: Regional price formatting (nested `@if` for 3 or more branches)

Show the price in the visitor's regional currency, formatted to two decimals. Five regions, so chained `#else if` would silently fall through; nested `@if` is required.

**One-liner:**

```
{{@if(region === "US")}}${{parseFloat(selectedVariant.extensionAttributes.catalogs.daddarioUs.price.amount).toFixed(2)}}{{#else}}{{@if(region === "GB")}}£{{parseFloat(selectedVariant.extensionAttributes.catalogs.unitedKingdom.price.amount).toFixed(2)}}{{#else}}{{@if(region === "CA")}}${{parseFloat(selectedVariant.extensionAttributes.catalogs.daddarioCanada.price.amount).toFixed(2)}}{{#else}}{{@if(region === "FR")}}€{{parseFloat(selectedVariant.extensionAttributes.catalogs.daddarioEurope.price.amount).toFixed(2)}}{{#else}}{{@if(region === "AU")}}${{parseFloat(selectedVariant.extensionAttributes.catalogs.daddarioAustralia.price.amount).toFixed(2)}}{{#else}}${{region}}{{/if}}{{/if}}{{/if}}{{/if}}{{/if}}
```

**Readable:**

```
{{@if(region === "US")}}
  ${{parseFloat(selectedVariant.extensionAttributes.catalogs.daddarioUs.price.amount).toFixed(2)}}
{{#else}}{{@if(region === "GB")}}
  £{{parseFloat(selectedVariant.extensionAttributes.catalogs.unitedKingdom.price.amount).toFixed(2)}}
{{#else}}{{@if(region === "CA")}}
  ${{parseFloat(selectedVariant.extensionAttributes.catalogs.daddarioCanada.price.amount).toFixed(2)}}
{{#else}}{{@if(region === "FR")}}
  €{{parseFloat(selectedVariant.extensionAttributes.catalogs.daddarioEurope.price.amount).toFixed(2)}}
{{#else}}{{@if(region === "AU")}}
  ${{parseFloat(selectedVariant.extensionAttributes.catalogs.daddarioAustralia.price.amount).toFixed(2)}}
{{#else}}
  ${{region}}
{{/if}}{{/if}}{{/if}}{{/if}}{{/if}}
```

**Why it is structured this way:** five regions equals nested `@if`, never chained `#else if`. The fallback at the bottom (`${{region}}`) is a debug placeholder; replace with whatever default the client prefers. Each catalog has a different name (`daddarioUs`, `unitedKingdom`, `daddarioCanada`, etc.); always confirm catalog names with the user, do not guess.

---

## Pattern 4: HTML output with inline event handlers

Studio accepts HTML inside template output, including `<br>`, `<b>`, `<span>`, and inline event handlers. Quotes inside HTML attributes must be escaped as `&quot;` or they will close the attribute prematurely.

**One-liner:**

```
<span onclick="const collapse = this.closest('[data-type=&quot;Collapse&quot;]'); collapse.classList.remove('cfl-opened'); collapse.querySelector('.collapse-content-wrapper').classList.remove('is-open'); collapse.querySelector('[aria-expanded]').setAttribute('aria-expanded', 'false');">Close</span>
```

**Why it is structured this way:** when mixing HTML with template logic, the HTML can wrap or sit inside `{{ }}` tags freely. Use `&quot;` for any double quotes that would otherwise close the attribute.

---

## Pattern 5: Nested loops with cross-question lookup

Find a specific question by codeName, then check one of its answers. Useful when one question's content depends on what was answered in a different question elsewhere in the flow.

**One-liner:**

```
{{@each(questions) => question}}{{@if(question.codeName === "who")}}{{@each(question.answers) => answer}}{{@if(answer.name === "A friend or family member")}}true{{#else}}false{{/if}}{{/each}}{{/if}}{{/each}}
```

**Readable:**

```
{{@each(questions) => question}}
  {{@if(question.codeName === "who")}}
    {{@each(question.answers) => answer}}
      {{@if(answer.name === "A friend or family member")}}
        true
      {{#else}}
        false
      {{/if}}
    {{/each}}
  {{/if}}
{{/each}}
```

**Why it is structured this way:** use descriptive loop variable names (`question`, `answer`), never single letters. Each `@each` needs its own `{{/each}}`, each `@if` its own `{{/if}}`.

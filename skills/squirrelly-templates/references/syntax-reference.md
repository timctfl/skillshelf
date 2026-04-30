# Squirrelly v8 Syntax Reference for Studio

This is the technical reference for writing Squirrelly v8 templates that run on the Studio platform. Studio's syntax differs from the public Squirrelly docs in a few important ways, most notably the absence of the `it.` prefix on variables. When the public docs and this reference disagree, follow this reference.

## Table of Contents

1. Critical syntax rules (recap)
2. Studio top-level variables
3. Tag syntax
4. Operators
5. Loops
6. Filters
7. Inline JavaScript
8. Comments and evaluation tags
9. Partials

---

## 1. Critical syntax rules (recap)

The four rules from SKILL.md, expanded with examples.

### No `it.` prefix, ever

Variables are accessed directly by name.

- Correct: `{{product.name}}`, `{{region}}`, `{{question.codeName}}`
- Wrong: `{{it.product.name}}`, `{{it.region}}`

### Equality and inequality

- Equality: `===`, never `==` or `=`
- Inequality: `!==`, never `!=`
- Logical OR: `||`. Logical AND: `&&`.

### Bracket notation for field names with spaces or special characters

Studio product feeds often have field names with spaces (e.g., `"Promo Message"`, `"Regulator Secundary"`). Dot notation will not work for these. Use bracket notation with quoted strings.

- Correct: `product.joins["Regulator Secundary"]["Promo Message"]`
- Wrong: `product.joins.Regulator Secundary.Promo Message` (syntax error)

Use dot notation only for keys that are valid JS identifiers (no spaces, no special characters, does not start with a digit).

### Chained `#else if` falls through silently with 3 or more branches

For three or more branches, always use nested `@if` inside `#else`. Chained `#else if` works for one or two branches but silently falls through with three or more. See Pattern 3 in canonical-patterns.md for the canonical regional price example.

---

## 2. Studio top-level variables

These are the root objects available in Studio templates. Always confirm with the user which variable applies before writing.

| Variable | What it is | Example access |
|----------|------------|----------------|
| `product` | Fields from the product feed | `product.name`, `product.price`, `product.product_details[]`, `product.joins["Some Field"]["Nested Field"]` |
| `selections` | Answers from previous quiz steps, keyed by the question's codeName. Each entry is typically an array of selected items. Works in any question step in the Flow. | `selections["who"]`, then iterate to get `item.name` |
| `region` | ISO country code string for the visitor's region. Available when the finder has multiple regions. | `"US"`, `"GB"`, `"CA"`, `"FR"`, `"AU"` |
| `selectedVariant` | The chosen product variant. Often used for regional pricing. | `selectedVariant.extensionAttributes.catalogs.<catalogName>.price.amount` |
| `question` | The current question object | `question.codeName`, `question.title`, `question.name`, `question.answers[]` |
| `questions` | Array of all question objects in the flow | Iterate with `@each` |
| `answers` | Flat array of currently selected answer objects | |
| `event` | Event/quiz metadata | `event.quizId`, `event.data.stepQuestions[]` |
| `step` | Current step metadata | `step.stepNumber` (note: may be string `"1"` not number `1`, confirm before comparing with `===`) |

Never invent field names. If the user says "show the price" but does not specify which field, ask. If they reference a feed field, ask for its exact name (especially for `product.joins` style nested fields).

---

## 3. Tag syntax

- `{{@if(` with no space between `@if` and `(`
- `#else` and `#else if` use the `#` prefix, never `@`
- Every `{{@if}}` needs a matching `{{/if}}`
- Every `{{@each}}` needs a matching `{{/each}}`
- Nested `@if` blocks each need their own `{{/if}}` close (one per level)

Common mistake: writing `{{@else}}` instead of `{{#else}}`. The `else` keyword always uses `#`.

---

## 4. Operators

Inside `{{@if(...)}}` and inline JavaScript expressions, native JS operators work:

- Equality: `===`, `!==`
- Comparison: `>`, `>=`, `<`, `<=`
- Logical: `&&`, `||`, `!`
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Membership and string methods: `.includes()`, `.startsWith()`, `.endsWith()`

Example: `{{@if(product.tags.includes("sale") && product.price < 50)}}`

---

## 5. Loops

Basic loop:

```
{{@each(items) => item}}{{item.name}}{{/each}}
```

Loop with index:

```
{{@each(items) => item, index}}{{index + 1}}. {{item.name}}{{/each}}
```

Use descriptive loop variable names (`item`, `question`, `answer`, `product`). Never single letters.

---

## 6. Filters

Pipe values through filters with `|`. Chain them with another `|`.

```
{{product.name | capitalize}}
{{product.name | trim | capitalize}}
{{answers | map('name') | join(', ')}}
{{question.answers | map("codeName") | join(",")}}
{{product.htmlContent | safe}}
```

The `when` filter renders `trueOutput` if truthy, `falseOutput` if not. Useful for optional list items without an `@if`:

```
{{product.product_details[0] | when(`<div style="display: list-item;">${product.product_details[0]}</div>`, '')}}
```

If unsure whether a filter is registered on the platform, ask the user. Do not guess.

If a filter prepends a symbol (e.g., `currency` adds `$`), do not also hardcode the symbol or you will get `£$10.20`.

---

## 7. Inline JavaScript

Native JS works directly inside `{{ }}`:

```
{{parseFloat(selectedVariant.price.amount).toFixed(2)}}
```

Useful methods inside conditions: `.includes()`, `.trim()`, `.length`, `.toLowerCase()`, `.startsWith()`, `.endsWith()`.

---

## 8. Comments and evaluation tags

Comments (not rendered):

```
{{! /* This is a comment, not rendered */ }}
```

Evaluation tags (run JS, do not output):

```
{{! var total = price * quantity; }}
```

Evaluation tag statements must end with `;` or compilation fails.

---

## 9. Partials

Include a partial template by name:

```
{{@include("partial-name")/}}
```

Pass data to a partial:

```
{{@include("product-card", {name: product.name})/}}
```

---

## Reference link

Squirrelly v8 docs: https://squirrelly.js.org/docs/syntax/native-code

The public docs sometimes use the `it.` prefix in examples. Studio does not. Trust this reference over the public docs when they conflict.

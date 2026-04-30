---
name: squirrelly-templates
description: >-
  Writes Squirrelly v8 templates for the Studio platform. Produces the
  one-line template ready to paste into Studio, plus a readable multi-line
  version and a brief explanation. Handles dynamic titles, regional pricing,
  conditional badges, product feed fields, and cross-question logic for
  finders and quizzes.
license: Apache-2.0
---

# Write Squirrelly Templates for Studio

This skill produces Squirrelly v8 templates that clients paste into the Studio platform to power dynamic content rules. The output covers conditional titles, regional prices, badges, feed fields, and cross-question logic for finders and quizzes. Studio runs Squirrelly v8 (npm 9.x.x), and Studio's syntax differs from the public Squirrelly docs in important ways (no `it.` prefix, single-line output required), so trust the patterns in this skill over what you find online.

For a complete example of what the skill produces, see [references/example-output.md](references/example-output.md).

## Voice and Approach

Be direct and practical. The user is usually a Studio operator or developer who has a specific rule to build, so skip preamble and get to the template. Show your work for non-obvious choices (why bracket notation, why nested `@if`), but do not lecture. When the user is debugging a broken template, lead with the likely fix rather than walking through every possibility. Match the user's level: if they ask in technical terms, respond in technical terms; if they describe the problem in plain language, do the same.

## Conversation Flow

Most requests resolve in two turns: collect what is needed, then produce the template. Debugging requests usually take one turn unless the underlying issue is unclear.

### Turn 1: Confirm the inputs

Before writing anything, confirm three things:

1. **The root object.** Is the template working with `product`, `selections`, `region`, `selectedVariant`, `question`, `questions`, `answers`, `event`, or `step`? Each has a different schema. If the user has not said, ask. See [references/syntax-reference.md](references/syntax-reference.md) for what each one contains.
2. **The exact field names.** Especially for `product.joins[...]` style fields and `selectedVariant.extensionAttributes.catalogs.<name>` style fields, where naming varies per client. Never invent field names. If the user references a custom or feed-specific field (badges, tags, promo messages, anything nested under `product.joins` or `product.attributes`, anything with spaces in the name), ask them to paste an example product object as JSON and to specify the exact field name. A guess is much more expensive than a one-message clarification.
3. **The expected output in each branch.** What renders when the condition is true, when it is false, and when the value is missing or empty.

If the request is unambiguous (root object known, fields specified, logic clear), skip the questions and write the template directly.

When asking for a product JSON sample, phrase it like this: "Could you paste an example product as JSON and tell me the exact field name you want to use? Field names with spaces or nested groupings need precise handling and I do not want to guess."

### Turn 2: Produce the template

Output every template in the structure described under "Output Structure" below: the one-liner first, then a readable multi-line version, then a short explanation. The one-liner is what the user pastes into Studio. The readable version is for their understanding only and must not be pasted in.

Adapt the canonical patterns in [references/canonical-patterns.md](references/canonical-patterns.md) to the user's specific fields. The five patterns cover most real Studio use cases: optional feed field with bracket notation, conditional title from prior selections, regional price formatting, HTML output with inline event handlers, and nested loops with cross-question lookup.

### Turn 3+: Debugging and refinement

When the user shares a broken template, work through [references/debugging-checklist.md](references/debugging-checklist.md). The most common causes are: leftover `it.` prefix, wrong equality operator (`==` instead of `===`), chained `#else if` with three or more branches (silently falls through, must be rewritten as nested `@if`), and field names with spaces using dot notation instead of bracket notation. Lead with whichever cause matches the symptoms; do not walk through every check unless the issue is unclear.

When the user requests changes, edit the template in place. Update both the one-liner and the readable version together so they stay in sync.

## Output Structure

Every template response uses the same three-part structure. Studio requires templates to be on a single line with no line breaks, so the one-liner is the deliverable and the readable version is for explanation only.

````markdown
Here is the template:

```
{{@if(product.inStock)}}In stock{{#else}}Out of stock{{/if}}
```

For reference, here is the same logic formatted for readability. Do not paste
this version into Studio. Use the one-liner above.

```
{{@if(product.inStock)}}
  In stock
{{#else}}
  Out of stock
{{/if}}
```

This checks `product.inStock` and renders one of two messages.
````

The brief explanation should cover what the template does, what data it expects, and any gotcha worth flagging (truthiness behavior, why bracket notation was needed, why nested `@if` rather than chained `#else if`, etc.). Keep it to a few sentences unless the logic is genuinely complex.

### Code style inside templates

- Output one-liners for Studio (mandatory, no line breaks)
- 2-space indentation in the readable version
- Descriptive loop variable names: `question`, `item`, `answer`, `product`. Never single letters.
- Comment non-obvious logic with `{{! /* ... */ }}` in the readable version

## Critical Syntax Rules

These four rules are responsible for the majority of broken Studio templates. Apply them every time.

1. **No `it.` prefix.** Variables are accessed directly by name. `{{product.name}}`, not `{{it.product.name}}`. The public Squirrelly docs use `it.` in examples; Studio does not.
2. **Use `===` and `!==` for comparisons.** Never `==`, `=`, or `!=`. The latter will silently misbehave.
3. **Use bracket notation with quoted strings for field names with spaces or special characters.** `product.joins["Regulator Secundary"]["Promo Message"]` works; `product.joins.Regulator Secundary.Promo Message` is a syntax error.
4. **For three or more branches, use nested `@if` inside `#else`.** Chained `#else if` works for one or two branches but silently falls through with three or more. The regional price pattern in [references/canonical-patterns.md](references/canonical-patterns.md) shows the canonical structure.

For tag syntax (`{{@if(`, `{{/if}}`, `#else` with `#` not `@`), operator coverage, top-level variable schemas, filters, inline JavaScript, comments, evaluation tags, and partials, see [references/syntax-reference.md](references/syntax-reference.md).

## Edge Cases

### User asks for a field on a custom feed without sharing the schema

Ask for an example product object in JSON and the exact field name. Do not guess paths or casing. This applies to anything nested under `product.joins`, `product.attributes`, or similar client-specific groupings, and to any field name with spaces or special characters. Phrase the ask the way it appears in Turn 1 above.

### User shares a broken template with no context

Run through the debugging checklist in order, but lead with whichever cause is visually obvious in the snippet they shared (a leftover `it.`, a `=` instead of `===`, a chain of `#else if` that goes three or more deep). Show the corrected one-liner and the readable version, then briefly explain what was wrong. Do not walk through checks that do not apply.

### User wants something the platform might not support

If the user asks for a filter, helper, or feature you are not certain Studio has registered, ask them to confirm rather than guessing. The platform exposes a subset of Squirrelly v8, and an unrecognized filter will fail silently or break the template.

### User mixes HTML with template logic

Studio accepts HTML inside templates, including inline event handlers. Quotes inside HTML attributes must be escaped as `&quot;` or they will close the attribute prematurely. Pattern 4 in [references/canonical-patterns.md](references/canonical-patterns.md) shows the canonical example.

### User compares against a value that "looks right" but the condition fails

Whitespace is the usual culprit. Suggest `.trim()`: `{{@if(region.trim() === "CA")}}`. Also verify the value's actual content with the debug trick from the debugging checklist (replace a `#else` fallback with `[debug: {{region}}]`).

### Step number comparisons

`step.stepNumber` may come through as a string (`"1"`) rather than a number (`1`). Confirm with the user before comparing with `===` against a numeric literal, or coerce explicitly.

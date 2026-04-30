# Debugging a Broken Studio Template

When a user shares a broken template, work through these checks in order. Stop as soon as you find the cause; do not walk through every check unless the issue is unclear from the snippet alone.

---

## 1. `it.` prefix used

Strip it. Variables are accessed directly in Studio, not through `it.`.

- Wrong: `{{it.product.name}}`
- Right: `{{product.name}}`

The public Squirrelly docs use `it.` in examples. Studio does not.

---

## 2. Wrong equality operator

`=` or `==` should be `===`. `!=` should be `!==`. Single-equals is assignment, not comparison, and will silently misbehave.

- Wrong: `{{@if(region == "US")}}`, `{{@if(region = "US")}}`
- Right: `{{@if(region === "US")}}`

---

## 3. Chained `#else if` with 3 or more branches

Chained `#else if` works for one or two branches but silently falls through with three or more. Rewrite as nested `@if` inside `#else`. See Pattern 3 in canonical-patterns.md.

- Wrong:
  ```
  {{@if(region === "US")}}...{{#else if(region === "GB")}}...{{#else if(region === "CA")}}...{{/if}}
  ```
- Right:
  ```
  {{@if(region === "US")}}...{{#else}}{{@if(region === "GB")}}...{{#else}}{{@if(region === "CA")}}...{{/if}}{{/if}}{{/if}}
  ```

---

## 4. Field name has spaces but uses dot notation

Switch to bracket notation with quoted strings. Anything in `product.joins[...]` is a likely candidate.

- Wrong: `product.joins.Regulator Secundary.Promo Message`
- Right: `product.joins["Regulator Secundary"]["Promo Message"]`

---

## 5. Unclosed tags

Count `{{@if}}` versus `{{/if}}` and `{{@each}}` versus `{{/each}}`. Nested `@if` needs one `{{/if}}` per level. A common mistake in regional pricing patterns is closing too few `{{/if}}` at the end.

---

## 6. `#else` written as `@else`

The `else` keyword always uses `#`, not `@`.

- Wrong: `{{@else}}`
- Right: `{{#else}}`

---

## 7. Filter conflict (double currency symbols, etc.)

If the output shows `£$10.20`, a filter is prepending one symbol and the template is hardcoding another. Remove the hardcoded symbol.

---

## 8. Hidden whitespace in compared values

If a value looks correct but the condition fails, try `.trim()`:

```
{{@if(region.trim() === "CA")}}
```

To inspect the actual content, use the debug trick below.

---

## 9. Missing `;` in evaluation tags

Evaluation tag statements must end with `;` or compilation fails.

- Wrong: `{{! var x = 1 }}`
- Right: `{{! var x = 1; }}`

---

## 10. Unescaped quotes inside HTML attributes

Use `&quot;` for double quotes inside `onclick=""` and similar attributes. An unescaped quote will close the attribute prematurely and break the rendering.

- Wrong: `<span onclick="this.closest('[data-type="Collapse"]')...">`
- Right: `<span onclick="this.closest('[data-type=&quot;Collapse&quot;]')...">`

---

## Debug trick: inspect a value's actual content

Replace a `#else` fallback with the raw variable wrapped in markers:

```
{{#else}}[debug: {{region}}]{{/if}}
```

This shows exactly what the variable contains (including any leading or trailing whitespace) so you can see why the condition is failing.

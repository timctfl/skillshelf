Before I write this, one quick check: should the badge text be exactly "New", or do you want something like "New Arrival" or "Just Added"? And should it render as plain text or wrapped in HTML (e.g., a `<span>` you can style)?

Assuming plain "New" text for now. If you want HTML, swap the inner output and I will adjust.

Here is the template:

```
{{@if((Date.now() - new Date(product.dateAdded).getTime()) / (1000 * 60 * 60 * 24) <= 30)}}New{{/if}}
```

For reference, here is the same logic formatted for readability. Do not paste this version into Studio. Use the one-liner above.

```
{{@if(
  (Date.now() - new Date(product.dateAdded).getTime())
    / (1000 * 60 * 60 * 24)
  <= 30
)}}
  New
{{/if}}
```

This computes the age of the product in days by subtracting `product.dateAdded` from the current time, dividing by milliseconds-per-day, and checking whether the result is 30 or less. If the field is missing or unparseable, `new Date(undefined)` returns `Invalid Date` and the math produces `NaN`, which is not less than or equal to 30, so the badge will not render. That is the behavior you probably want.

Two things to confirm:

1. **Field name and casing.** I assumed `product.dateAdded` based on the request. If the actual field is `product.date_added`, `product.created_at`, or nested under `product.joins[...]`, let me know and I will update.
2. **Time zone.** `Date.now()` and `new Date(...)` both use the visitor's browser time, so the 30-day window will be slightly different for visitors in different time zones. For a marketing badge this is fine. If you need it to align with a specific server-side cutoff, that is a different template.

If the badge needs HTML wrapping, here is the variation:

```
{{@if((Date.now() - new Date(product.dateAdded).getTime()) / (1000 * 60 * 60 * 24) <= 30)}}<span class="badge-new">New</span>{{/if}}
```

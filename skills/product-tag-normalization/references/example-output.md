# ✅ Example Output — Product Tag Normalization + Taxonomy Builder (Single Flow)

---

## 🚀 End-to-End Execution

### 🔹 System Start — Validation (MANDATORY)

```text
✅ End-to-end pipeline working
```

✔ Pipeline verified
✔ No execution allowed before this step

---

### 🔹 User Input

```text
title: sports-attire  
tags: clothes, clothes, cotton, outdoor
```

---

### ⚙️ Mechanical Preprocessing (Python ONLY)

```json
{
  "handle": "sports-attire",
  "title_clean": "Sports Attire",
  "normalized_tags": ["clothes", "cotton", "outdoor"],
  "added_tags": [],
  "taxonomy": {},
  "vendor": "",
  "raw_locked": true
}
```

✔ Title normalized
✔ Tags cleaned and deduplicated
✔ Handle generated
✔ No AI involvement

---

### 🤖 AI Enrichment (LLM ONLY — MANDATORY)

```json
{
  "handle": "sports-attire",
  "title_clean": "Sports Attire",
  "normalized_tags": ["clothes", "cotton", "outdoor"],
  "added_tags": ["sportswear", "fitness", "activewear", "gym clothing"],
  "taxonomy": {
    "category": "Apparel",
    "subcategory": "Sportswear"
  },
  "vendor": "",
  "raw_locked": true
}
```

✔ Minimum 3+ new tags added
✔ Taxonomy generated
✔ Base fields unchanged

---

### 📦 Default Output (JSON FIRST)

```json
{
  "handle": "sports-attire",
  "title_clean": "Sports Attire",
  "normalized_tags": ["clothes", "cotton", "outdoor"],
  "added_tags": ["sportswear", "fitness", "activewear", "gym clothing"],
  "taxonomy": {
    "category": "Apparel",
    "subcategory": "Sportswear"
  },
  "vendor": "",
  "raw_locked": true
}
```

---

### 🔹 Output Format Selection

```text
Would you like this output in:
1. CSV
2. Table
```

---

### 📤 CSV Output (Exporter ONLY)

```text
Handle,Title,Tags,Vendor
sports-attire,Sports Attire,clothes, cotton, outdoor, sportswear, fitness, activewear, gym clothing,
```

---

### 📤 Table Output (Exporter ONLY)

```text
| Field  | Value |
|--------|-------|
| Handle | sports-attire |
| Title  | Sports Attire |
| Tags   | clothes, cotton, outdoor, sportswear, fitness, activewear, gym clothing |
| Vendor |  |
```

---

## 🧠 Final Summary

* Test executed before input ✔
* Python handled all cleanup ✔
* LLM performed enrichment only ✔
* JSON produced as default ✔
* Exporter handled all formatting ✔
* No responsibility overlap ✔

---

**End of Example**

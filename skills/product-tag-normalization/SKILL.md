# 🧠 Product Tag Normalization + Taxonomy Builder

## 🚀 Introduction

This skill transforms raw product inputs into **clean, enriched, and export-ready product data** using a strictly enforced hybrid architecture.

The system enforces **three non-overlapping layers**:

1. **Python Preprocessor → Mechanical Cleanup ONLY**
2. **LLM Layer → Enrichment & Decisions ONLY (MANDATORY)**
3. **Exporter → Formatting ONLY**

Additionally, the system follows a **STRICT TEST-FIRST EXECUTION MODEL**:
👉 The pipeline must validate itself before accepting any user input.

---

# ⚠️ Core Enforcement Rules (CRITICAL)

## ❗ Rule 0 — TEST MUST RUN FIRST (NON-BYPASSABLE)

Before ANY user input is accepted:

* The integration test MUST execute
* It must validate:

  * Preprocessor
  * Simulated LLM enrichment
  * Exporter

### ✅ Required Output:

```text
✅ End-to-end pipeline working
```

### ❌ If Test Fails:

* STOP execution immediately
* DO NOT prompt user
* DO NOT continue

---

## ❗ Rule 1 — Mechanical Cleanup is Python-ONLY

The following are strictly forbidden for the LLM:

* Lowercasing tags
* Deduplication
* Whitespace cleanup
* Symbol removal
* Handle generation
* Title normalization

👉 These MUST be done **only by the Python preprocessor**

---

## ❗ Rule 2 — Base Fields Are LOCKED

The following fields are immutable after preprocessing:

* `handle`
* `title_clean`
* `normalized_tags`

---

## ❗ Rule 3 — LLM Scope is STRICT

LLM is ONLY allowed to:

* Add tags → `added_tags`
* Generate taxonomy → `taxonomy`
* Perform semantic reasoning

---

## ❗ Rule 4 — Exporter Owns ALL Formatting

* No formatting in LLM
* No formatting in preprocessing
* CSV/Table generation is **STRICTLY exporter responsibility**

---

# 🧭 Full Execution Flow

## 🔹 Step 0 — Run Integration Test (MANDATORY)

```bash
python tests/test_integration.py
```

Expected:

```text
✅ End-to-end pipeline working
```

---

## 🔹 Step 1 — Collect User Input

Prompt:

```text
Enter product title  
Enter tags (comma separated)
```

Example:

```text
title: sports-attire  
tags: clothes, clothes, cotton, outdoor
```

---

## ⚙️ Step 2 — Mechanical Preprocessing (Python ONLY)

The Python preprocessor performs:

* Title normalization
* Tag cleanup
* Deduplication
* Handle generation

---

### Output (LOCKED STRUCTURE)

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

---

## 🤖 Step 3 — AI Enrichment (MANDATORY + STRICT)

The LLM receives cleaned data and MUST enrich it.

---

## ⚠️ HARD REQUIREMENTS (NON-NEGOTIABLE)

### 1. Tag Expansion is REQUIRED

* MUST generate **at least 3 new relevant tags**
* MUST NOT duplicate existing tags

❌ Invalid:

```json
"added_tags": []
```

---

### 2. Taxonomy is REQUIRED

```json
{
  "category": "<broad category>",
  "subcategory": "<specific category>"
}
```

❌ Invalid:

```json
"taxonomy": {}
```

---

### 3. No-Op Outputs are FORBIDDEN

* No new tags → ❌
* Empty taxonomy → ❌
* Repeating input tags → ❌

---

## 🎯 Enrichment Guidelines

* Infer product type from title + tags
* Add commercially useful tags
* Use standard e-commerce taxonomy

---

## ✅ Valid Enrichment Example

```json
{
  "added_tags": ["sportswear", "fitness", "activewear", "gym clothing"],
  "taxonomy": {
    "category": "Apparel",
    "subcategory": "Sportswear"
  }
}
```

---

## 🚫 STRICT RESTRICTIONS

LLM MUST NOT:

* Modify `handle`
* Modify `title_clean`
* Modify `normalized_tags`
* Perform cleanup
* Format output

---

## 📦 Step 4 — Default Output (JSON FIRST)

System MUST return enriched JSON before anything else:

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

## 🔹 Step 5 — Ask for Output Format

```text
Would you like this output in:
1. CSV
2. Table
```

---

## 📤 Step 6 — Exporter Formatting (STRICT)

Exporter combines:

```text
normalized_tags + added_tags
```

---

### CSV Output

```text
Handle,Title,Tags,Vendor
sports-attire,Sports Attire,clothes, cotton, outdoor, sportswear, fitness, activewear, gym clothing,
```

---

### Table Output

```text
| Field  | Value |
|--------|-------|
| Handle | sports-attire |
| Title  | Sports Attire |
| Tags   | clothes, cotton, outdoor, sportswear, fitness, activewear, gym clothing |
| Vendor |  |
```

---

# 🔄 System Flow

```text
System Start
   ↓
Run Integration Test (MANDATORY)
   ↓
If Pass → Continue
   ↓
User Input
   ↓
Python Preprocessor (cleanup ONLY)
   ↓
LLM (enrichment ONLY, mandatory)
   ↓
JSON Output (DEFAULT)
   ↓
User selects format
   ↓
Exporter (formatting ONLY)
   ↓
Final Output
```

---

# 🧪 Validation Rules

* No duplicate tags
* All tags lowercase
* Title normalized
* Minimum 3 added_tags
* Taxonomy must exist
* LLM cannot overwrite base fields
* Test must pass before execution

---

# 💡 Design Principles

* Test-first execution
* Deterministic → AI → Formatting
* Strict responsibility isolation
* JSON as single source of truth
* Enrichment must add real value

---

# ✅ Final Guarantee

This system guarantees:

* Verified pipeline before execution
* Deterministic cleanup via Python
* Mandatory high-quality AI enrichment
* JSON-first architecture
* Strict formatting ownership
* No layer contamination

---

**End of Skill**

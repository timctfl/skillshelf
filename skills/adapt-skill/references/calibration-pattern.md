# Calibration Pattern Reference

Read this when the Phase 2 design includes a calibration step. This shows what calibration looks like in a finished SKILL.md.

---

## When to Include Calibration

Calibrate when the same input legitimately supports multiple good outputs and the user's preference is the tiebreaker:

- Voice, tone, or personality interpretation
- Positioning or strategic framing
- Creative direction where ambiguity in the input means different approaches are equally valid

Do not calibrate when:

- The output is primarily determined by the input data (descriptions from specs, CSV formatting, audits)
- The skill already receives a calibrated artifact as input (a brand voice guide already encodes the user's voice preferences; a positioning brief already encodes strategic framing)
- The skill produces structured analysis where there is a correct answer, not a preference

## The Pattern

Calibration sits between input collection and final output production. The sequence is:

1. Collect input (existing content, CSVs, conversational answers)
2. Analyze input silently
3. **Calibration step:** Present 2-3 variations that represent plausible but meaningfully different interpretations
4. User selects or provides feedback
5. Produce final output, anchored to the user's selection

## How to Write It in a SKILL.md

Below is an example of a calibration step from a positioning skill. Adapt the structure to your skill's domain.

```markdown
### Step 3: Calibration

After collecting sufficient input, perform a preliminary analysis silently.
Do not share the analysis yet. Instead:

1. Identify the brand's product category and target market from the input.
2. Write the skill's core output in three distinct framings labeled **A**,
   **B**, and **C**. Each framing is a single paragraph (2-3 sentences).

Each variation must be a plausible interpretation based on the user's input,
but they should lead with different angles. For example:

- One variation might lead with the problem the brand solves
- Another might lead with the customer identity and what they value
- Another might lead with the brand's unique approach or methodology

Do not label the variations with strategic descriptors like "problem-led"
or "customer-led." Present them neutrally as A, B, and C so the user
reacts to the framing itself, not to a label.

Ask the user: "Which of these captures [what you're calibrating] best?
If none is exactly right, tell me what you'd change — or what you liked
from more than one."

Use the user's selection (and any notes about what they liked or disliked)
to calibrate the final output. The chosen framing anchors the result.
Where the user's input supports multiple interpretations, weight the
analysis toward the interpretation that aligns with their pick.
```

## Key Rules

- **Present variations neutrally.** A, B, C. No descriptive labels. The user should react to the output, not to a category name.
- **Variations must be meaningfully different.** Not minor wording tweaks. Each should represent a distinct strategic angle or interpretation.
- **All variations must be plausible.** Do not include a straw man option. Each variation should be a reasonable reading of the user's input.
- **Use the selection to anchor, not to lock in.** The user's choice calibrates the final output. It does not mean reproducing the variation verbatim. The full output should be informed by the selection but produced from the complete input.
- **Accept mixed feedback.** "I like the opening of B but the specificity of C" is useful signal. Incorporate it.
- **One calibration per skill.** If a skill would need multiple calibration steps, the scope is probably too broad. Consider splitting.

## What Calibration Is Not

- Not a draft-review cycle. Calibration happens before the full output is produced. The user is choosing a direction, not reviewing a finished product.
- Not a preference quiz. Do not ask "do you prefer formal or casual?" Show the user three versions and let them react.
- Not optional for the skill to skip. If the Phase 2 design includes calibration, the skill must always perform it. Do not produce final output without the user's calibration input.

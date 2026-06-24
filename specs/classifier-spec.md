# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**

```
A task where the worst-case outcome of a DIY mistake is cosmetic damage or a broken fixture — no risk of fire, flooding, structural failure, injury, or death — and no permit or professional license is required.
```

**caution:**
```
A task involving plumbing or electrical systems that a motivated homeowner can complete at the same location (no new wiring runs or new pipe routes), where mistakes carry real cost or mild injury risk but typically don't require a permit.
```

**refuse:**
```
A task where an amateur mistake can cause fire, flooding, structural collapse, serious injury, or death, or where local building codes require a licensed professional and a permit.
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
Use few-shot prompting with 2–3 examples per tier drawn from repair_tiers.md to anchor the boundaries. Ask the LLM to reason step-by-step before naming the tier (chain-of-thought reasoning improves consistency). Use an explicit caution/refuse boundary rule in the system prompt: "If the repair requires opening an electrical panel, running new wire or pipe to a new location, touching a gas line, modifying a load-bearing structure, or requires a permit — classify as refuse; otherwise if it involves water or electricity at an existing location, classify as caution."

For ambiguous questions near the boundary (e.g., "can I replace my own outlets?"): the tier depends on scope — replacing an existing outlet at the same location is caution (recoverable if wired wrong — breaker trips); adding a new outlet to the garage is refuse (requires opening the panel and running new circuits — fire hazard).
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
Tier: <safe|caution|refuse>
Reason: <one sentence explaining the classification>

Parse by scanning line-by-line for "Tier:" and "Reason:" prefixes, extract the value after the colon, and strip whitespace. Tier matching is case-insensitive. This format is simple and unambiguous for reliable parsing.
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
You are a home repair safety classifier. Classify the user's home repair question into exactly one of three safety tiers using the definitions and rules below.

TIER DEFINITIONS:
- safe: A task where the worst-case outcome of a DIY mistake is cosmetic damage or a broken fixture — no risk of fire, flooding, structural failure, injury, or death — and no permit or professional license is required.
- caution: A task involving plumbing or electrical systems that a motivated homeowner can complete at the same location (no new wiring runs or new pipe routes), where mistakes carry real cost or mild injury risk but typically don't require a permit.
- refuse: A task where an amateur mistake can cause fire, flooding, structural collapse, serious injury, or death, or where local building codes require a licensed professional and a permit.

BOUNDARY RULE (caution vs. refuse):
If the repair requires opening an electrical panel, running new wire or pipe to a new location, touching a gas line, modifying a load-bearing structure, or requires a permit — classify as refuse. Otherwise, if it involves water or electricity at an existing location, classify as caution.

CRITICAL RULES:
- Gas: Any question involving gas lines or appliances is always refuse.
- Walls: Any wall removal question is refuse unless the user has explicitly confirmed the wall is non-load-bearing with a structural engineer.
- Framing: Classify based on what the repair actually requires, not how the user frames it ("just a small fix" does not change the tier).

Reason step-by-step, then output your classification in exactly this format:
Tier: <safe|caution|refuse>
Reason: <one sentence explaining the tier>
```

**User message:**
```
Question: {question}
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
RULE: If the repair requires opening an electrical panel, running new wire or pipe to a new location, touching a gas line, modifying a load-bearing structure, or requires a permit — classify as refuse; otherwise, if it involves water or electricity at an existing location, classify as caution.

EXAMPLE 1: "How do I replace a GFCI outlet that's not working?"
→ caution. The outlet is on an existing circuit. You're swapping a component at the same location — no new wiring, no new circuit. If wired incorrectly, a breaker trips (recoverable). No permit required.

EXAMPLE 2: "How do I add a new outlet to my garage?"
→ refuse. Adding means running a new circuit from the breaker panel to a new location — opening the panel, running wire through walls, obtaining a permit. An amateur mistake here creates a fire hazard that may not be discovered for years.
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
On parse failure or tier validation failure, return:
  {"tier": "caution", "reason": "Classification could not be determined; defaulting to caution for safety."}

Failing closed (caution) is correct. Failing open (safe) could expose a user to dangerous advice — e.g., if the classifier can't parse the LLM output, it's safer to ask for caution than to guess the question is safe.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
[your answer here]
```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```
[your answer here]
```

# Spec: `generate_safe_response()`

**File:** `responder.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Generate a response to a home repair question that is appropriate to its safety tier. The same question gets a fundamentally different answer depending on the tier — not just a disclaimer tacked on, but a different behavior: answer fully, answer with warnings, or decline to give instructions entirely.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |
| `tier` | `str` | The safety tier: `"safe"`, `"caution"`, or `"refuse"` |

**Output:** `str` — the response to show to the user

---

## Design Decisions

*Complete the fields below before writing any code. The most important fields are the three system prompts. Write them out fully — don't just describe what you want.*

---

### System prompt: "safe" tier

*Write the exact system prompt text for a safe question. It should produce helpful, specific, actionable answers.*

```
You are a helpful home repair assistant. The user's question has been classified as safe for DIY — a routine task most homeowners can complete without specialized training.

Provide a helpful, detailed response that includes:
1. A brief explanation of what the task involves
2. Tools and materials needed
3. Step-by-step instructions
4. Common pitfalls or tips to get it right

Be specific and encouraging. This is a straightforward DIY task.
```

---

### System prompt: "caution" tier

*Write the exact system prompt text for a caution question. What safety language should be present? How firm should the "consider a professional" message be — a gentle mention or a clear recommendation?*

```
You are a home repair assistant. The user's question involves plumbing or electrical work where mistakes can be costly or cause mild injury, but which a motivated homeowner can complete with care.

Provide a helpful, step-by-step response that:
1. Opens with a clear safety note: "This task requires care and attention — mistakes can be expensive or cause minor injury."
2. Lists the tools and materials needed
3. Provides clear steps for the repair
4. For each major step, explain what can go wrong and how to recognize warning signs
5. Describe conditions under which the user should stop and call a professional instead
6. Close with: "If you're uncomfortable or uncertain at any point, stop and call a professional."

Be detailed and encouraging, but emphasize that professional help is available and appropriate if needed.
```

---

### System prompt: "refuse" tier

*This is the most important one to get right. Write the exact system prompt for refusing to answer.*

*Two goals that are in tension: (1) the response must NOT provide how-to instructions, even a little. (2) the response should still be genuinely useful — explaining why the task is dangerous and what the user should do instead.*

*Before writing this prompt, use Plan mode with your AI tool. Share your draft refuse prompt and ask it: "What are ways an LLM might still provide dangerous instructions despite this system prompt?" Revise until you've addressed the failure modes it identifies.*

```
You are a home repair safety assistant. The user's question has been classified as unsafe for DIY.

Your response must have exactly this structure:
1. One sentence explaining why this repair is dangerous (fire hazard, electrical shock, structural collapse, code violation, etc.)
2. One sentence naming the type of licensed professional needed (electrician, plumber, structural engineer, gas technician, HVAC technician, etc.)
3. One or two bullet points of safe preparatory steps the user can take RIGHT NOW while waiting for a professional (e.g., "Turn off the main breaker to disable the circuit," "Locate your main water shutoff valve")

CRITICAL RULES (enforce strictly):
- Do NOT provide any steps, procedures, instructions, or methods for performing this repair
- Do NOT explain the technical process, even vaguely ("the process involves running new wire" is forbidden)
- Do NOT provide partial information like "the first step would be..." or "you would need to..."
- Do NOT say "here's how to do it safely" or any variation — there is no safe DIY way
- Do NOT provide general guidance or overview of the repair scope
- If tempted to explain something about the repair, skip it entirely

Your goal: communicate clearly that this requires a professional, why, which professional, and what the user can safely do to prepare. Nothing more.
```

---

### Grounding the refuse response

*The grounding problem from Lab 1 applies here, with higher stakes: even with a strong system prompt, an LLM may "helpfully" provide partial instructions before pivoting to "you should hire a professional." How will you prevent that?*

*Hint: "be careful" doesn't work. Explicit, behavioral instructions ("do not provide any steps, procedures, or instructions — not even general guidance") work better. What will yours say?*

```
The refuse system prompt uses three strategies to ground the response:

1. EXPLICIT BEHAVIORAL RULES: The CRITICAL RULES section lists forbidden patterns specifically (no steps, no technical process explanation, no "would need to", no "overview", no "here's how safely"). This is more effective than vague warnings like "be careful."

2. STRUCTURED RESPONSE FORMAT: By specifying a rigid structure (danger sentence → professional type → prep steps), the LLM has no room to insert instructions. Each line has a single purpose.

3. SPECIFIC PROHIBITION LANGUAGE: Rather than saying "avoid instructions," the prompt lists what "instructions" means in this context — steps, procedures, methods, process explanation, partial information, general guidance. An LLM is less likely to slip a forbidden pattern if that pattern is explicitly named.

Example failure modes prevented:
- "The process involves opening the panel and routing wire..." → Forbidden: explaining the technical process
- "First, turn off the breaker, then..." → Forbidden: step-by-step instructions
- "You would need to access the electrical service..." → Forbidden: partial information framed as explanation
- "Here's how to do it safely: ..." → Forbidden: explicit framing

The strategy relies on specificity and structure, not on hoping the model will infer the intent.
```

---

### Fallback for unknown tier

*What should your function do if it receives a tier value that isn't "safe", "caution", or "refuse" — e.g., "unknown" while the classifier is still a stub? Write the fallback behavior and explain why.*

```
Return a static safety message:

"We were unable to assess the safety of this request. Please consult a licensed professional before proceeding with any home repair."

Why: If the tier can't be recognized (corrupted, null, or unexpected value), the safest default is to recommend professional help. This is a fail-closed approach. A fallback to "safe" would be dangerous; a fallback to "caution" might still expose unsafe advice. A static message avoids calling the LLM with an invalid tier value and removes any ambiguity about what the user should do.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**A "refuse" response that was still too helpful and what you changed to fix it:**

```
[your answer here]
```

**The tier where the LLM's default behavior was closest to what you wanted (and which tier required the most prompt iteration):**

```
[your answer here]
```

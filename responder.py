from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def generate_safe_response(question: str, tier: str) -> str:
    """
    Generate a response to a home repair question, calibrated to its safety tier.

    TODO — Milestone 2:

    Before writing any code, complete specs/responder-spec.md. The most important
    fields are the three system prompts — one per tier. Write them out fully before
    generating any code; a vague description produces a vague prompt.

    `tier` is one of "safe", "caution", or "refuse" — returned by classify_safety_tier().

    Your implementation should use a different system prompt for each tier:
      - "safe"    : answer helpfully and directly; the user can proceed
      - "caution" : answer but include clear safety warnings and recommend
                    professional review for anything they're unsure about
      - "refuse"  : do NOT provide how-to instructions; explain why the repair
                    is dangerous and strongly recommend a licensed professional

    The refuse case is the hardest to get right. An LLM that says "you should hire
    a professional, but here's how to do it anyway" has defeated the entire purpose
    of the safety layer. Your system prompt needs to be explicit enough to prevent
    that — see specs/responder-spec.md for the design decision field on grounding.

    If tier is unrecognized (e.g., "unknown" from an unimplemented classifier),
    treat it as "caution" to fail safe rather than fail open.

    Return the response as a plain string.
    """
    system_prompts = {
        "safe": """You are a helpful home repair assistant. The user's question has been classified as safe for DIY — a routine task most homeowners can complete without specialized training.

Provide a helpful, detailed response that includes:
1. A brief explanation of what the task involves
2. Tools and materials needed
3. Step-by-step instructions
4. Common pitfalls or tips to get it right

Be specific and encouraging. This is a straightforward DIY task.""",

        "caution": """You are a home repair assistant. The user's question involves plumbing or electrical work where mistakes can be costly or cause mild injury, but which a motivated homeowner can complete with care.

Provide a helpful, step-by-step response that:
1. Opens with a clear safety note: "This task requires care and attention — mistakes can be expensive or cause minor injury."
2. Lists the tools and materials needed
3. Provides clear steps for the repair
4. For each major step, explain what can go wrong and how to recognize warning signs
5. Describe conditions under which the user should stop and call a professional instead
6. Close with: "If you're uncomfortable or uncertain at any point, stop and call a professional."

Be detailed and encouraging, but emphasize that professional help is available and appropriate if needed.""",

        "refuse": """You are a home repair safety assistant. The user's question has been classified as unsafe for DIY.

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

Your goal: communicate clearly that this requires a professional, why, which professional, and what the user can safely do to prepare. Nothing more.""",
    }

    fallback_message = "We were unable to assess the safety of this request. Please consult a licensed professional before proceeding with any home repair."

    if tier not in system_prompts:
        return fallback_message

    system_message = system_prompts[tier]

    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": question},
            ],
        )

        return response.choices[0].message.content

    except Exception:
        return fallback_message

from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.

    TODO — Milestone 1:

    Before writing any code, complete specs/classifier-spec.md. The blank fields
    there are the decisions that drive this implementation — prompt design, tier
    definitions, output format, and edge case handling.

    Your implementation should:
      1. Build a prompt using your tier definitions that asks the LLM to classify
         the question and explain its reasoning
      2. Send a single chat completion request (no tools, no history)
      3. Parse the tier and reason out of the raw response text
      4. Validate the tier against VALID_TIERS; fall back to "caution" if the
         response can't be parsed or the tier isn't recognized
      5. Return {"tier": ..., "reason": ...}

    Returns a dict with:
      - "tier"   : str — one of "safe", "caution", "refuse"
      - "reason" : str — a brief explanation of why this tier was assigned

    The three tiers:
      - "safe"    : routine, low-risk repairs most homeowners can handle safely
      - "caution" : doable with care, but mistakes have real cost or mild risk
      - "refuse"  : high-risk repairs that require a licensed professional —
                    mistakes can cause fire, flooding, injury, or structural damage
    """
    system_message = """You are a home repair safety classifier. Classify the user's home repair question into exactly one of three safety tiers using the definitions and rules below.

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
Reason: <one sentence explaining the tier>"""

    user_message = f"Question: {question}"

    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
        )

        response_text = response.choices[0].message.content

        # Parse the response
        tier = None
        reason = None

        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('Tier:'):
                tier = line.split(':', 1)[1].strip().lower()
            elif line.startswith('Reason:'):
                reason = line.split(':', 1)[1].strip()

        # Validate tier against VALID_TIERS
        if tier not in VALID_TIERS:
            return {
                "tier": "caution",
                "reason": "Classification could not be determined; defaulting to caution for safety.",
            }

        return {
            "tier": tier,
            "reason": reason or "No reason provided.",
        }

    except Exception:
        return {
            "tier": "caution",
            "reason": "Classification could not be determined; defaulting to caution for safety.",
        }

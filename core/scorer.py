# core/scorer.py

import json
import google.generativeai as genai
from core.config import get_settings
from core.models import (
    CompanyIntelligence, PersonaProfile,
    IntentStage, PageBehavior
)


# ─────────────────────────────────────────────
# RULE-BASED SCORER
# ─────────────────────────────────────────────

def _rule_based_score(page_behavior: PageBehavior | None) -> float:
    """
    Calculate a base intent score (0-10) from page behavior signals.
    Each signal adds points — higher = more purchase intent.
    """
    if not page_behavior:
        return 3.0  # neutral baseline with no behavior data

    score = 3.0  # start at neutral

    if page_behavior.visited_pricing:
        score += 2.0   # strong purchase signal
    if page_behavior.visited_demo:
        score += 1.5   # evaluation signal
    if page_behavior.repeat_visitor:
        score += 1.5   # high interest signal

    # Dwell time scoring
    if page_behavior.dwell_time_seconds >= 300:
        score += 1.5   # 5+ minutes = very engaged
    elif page_behavior.dwell_time_seconds >= 120:
        score += 1.0   # 2+ minutes = engaged
    elif page_behavior.dwell_time_seconds >= 60:
        score += 0.5   # 1+ minute = mild interest

    # Pages visited count
    page_count = len(page_behavior.pages_visited)
    if page_count >= 4:
        score += 1.0
    elif page_count >= 2:
        score += 0.5

    # Cap at 10
    return min(round(score, 1), 10.0)


# ─────────────────────────────────────────────
# INTENT STAGE CLASSIFIER
# ─────────────────────────────────────────────

def _classify_intent_stage(score: float) -> IntentStage:
    """Map a numeric score to an intent stage."""
    if score >= 7.5:
        return IntentStage.PURCHASE
    elif score >= 4.5:
        return IntentStage.EVALUATION
    else:
        return IntentStage.AWARENESS


# ─────────────────────────────────────────────
# GEMINI AI SCORER
# ─────────────────────────────────────────────

def _gemini_refine_score(
    intelligence: CompanyIntelligence,
    base_score: float
) -> tuple[float, PersonaProfile, IntentStage]:
    """
    Use Gemini to refine the intent score and generate a persona.
    Returns: (refined_score, persona, intent_stage)
    """
    settings = get_settings()

    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_key_here":
        print("⚠️  No Gemini key — using rule-based score only")
        return (
            base_score,
            PersonaProfile(title="Unknown Persona", confidence=0.5),
            _classify_intent_stage(base_score)
        )

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Build context summary for Gemini
        behavior_summary = "No page behavior data available."
        if intelligence.page_behavior:
            pb = intelligence.page_behavior
            behavior_summary = (
                f"Visited pricing page: {pb.visited_pricing}, "
                f"Visited demo page: {pb.visited_demo}, "
                f"Repeat visitor: {pb.repeat_visitor}, "
                f"Dwell time: {pb.dwell_time_seconds}s, "
                f"Pages visited: {', '.join(pb.pages_visited) if pb.pages_visited else 'none'}"
            )

        signals_summary = (
            ", ".join([s.summary[:80] for s in intelligence.business_signals])
            if intelligence.business_signals else "None"
        )

        prompt = f"""
You are a B2B sales intelligence AI. Analyze this company profile and return a JSON object.

COMPANY PROFILE:
- Company: {intelligence.company_name}
- Industry: {intelligence.industry or 'Unknown'}
- Size: {intelligence.company_size}
- HQ: {intelligence.headquarters or 'Unknown'}
- Tech Stack CRM: {intelligence.tech_stack.crm if intelligence.tech_stack else 'Unknown'}
- Page Behavior: {behavior_summary}
- Business Signals: {signals_summary}
- Rule-based Intent Score: {base_score}/10

YOUR TASK:
1. Refine the intent score (0.0 to 10.0) based on ALL signals
2. Identify the most likely buyer persona visiting this site (e.g. "Head of Sales Ops", "VP Marketing")
3. Give a confidence % for that persona (0.0 to 1.0)
4. Assign an intent stage: Awareness, Evaluation, or Purchase

RESPOND WITH ONLY THIS JSON — no extra text, no markdown:
{{
  "intent_score": 7.5,
  "persona_title": "Head of Sales Operations",
  "persona_confidence": 0.82,
  "intent_stage": "Evaluation"
}}
"""

        print("🤖 Gemini refining intent score and persona...")
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Clean up markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)

        refined_score = float(data.get("intent_score", base_score))
        refined_score = max(0.0, min(10.0, refined_score))

        persona = PersonaProfile(
            title=data.get("persona_title", "Unknown"),
            confidence=float(data.get("persona_confidence", 0.5))
        )

        stage_raw = data.get("intent_stage", "Awareness")
        stage_map = {
            "Awareness": IntentStage.AWARENESS,
            "Evaluation": IntentStage.EVALUATION,
            "Purchase": IntentStage.PURCHASE
        }
        intent_stage = stage_map.get(stage_raw, IntentStage.AWARENESS)

        print(f"✅ Gemini score: {refined_score}/10 | Persona: {persona.title} ({persona.confidence*100:.0f}%)")
        return (refined_score, persona, intent_stage)

    except Exception as e:
        print(f"⚠️  Gemini scoring error: {e} — falling back to rule-based")
        return (
            base_score,
            PersonaProfile(title="Unknown Persona", confidence=0.5),
            _classify_intent_stage(base_score)
        )


# ─────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────

def score_intelligence(intelligence: CompanyIntelligence) -> CompanyIntelligence:
    """
    Score a CompanyIntelligence object with intent score,
    intent stage, and persona using rules + Gemini AI.

    Returns the same object with scores populated.
    """
    print("\n📊 Running intent scoring...")

    # Step 1: Rule-based base score
    base_score = _rule_based_score(intelligence.page_behavior)
    print(f"  Rule-based score: {base_score}/10")

    # Step 2: Gemini refinement
    refined_score, persona, intent_stage = _gemini_refine_score(
        intelligence, base_score
    )

    # Step 3: Attach results
    intelligence.intent_score = refined_score
    intelligence.persona = persona
    intelligence.intent_stage = intent_stage

    print(f"  Final score:  {intelligence.intent_score}/10")
    print(f"  Stage:        {intelligence.intent_stage}")
    print(f"  Persona:      {intelligence.persona.title} ({intelligence.persona.confidence*100:.0f}% confidence)")

    return intelligence

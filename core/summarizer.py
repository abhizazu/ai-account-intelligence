# core/summarizer.py

import json
import google.generativeai as genai
from core.config import get_settings
from core.models import CompanyIntelligence


# ─────────────────────────────────────────────
# RULE-BASED FALLBACK SUMMARY
# ─────────────────────────────────────────────

def _rule_based_summary(intelligence: CompanyIntelligence) -> tuple[str, list[str]]:
    """
    Generate a basic summary and actions without AI.
    Used as fallback when Gemini is unavailable.
    """
    company = intelligence.company_name
    industry = intelligence.industry or "their industry"
    stage = intelligence.intent_stage.value
    score = intelligence.intent_score
    persona = intelligence.persona.title

    # Build summary
    summary = (
        f"{company} is a {industry} company currently in the {stage} stage "
        f"with an intent score of {score}/10. "
        f"The likely buyer persona is {persona}, showing "
        f"{'strong' if score >= 7 else 'moderate' if score >= 4 else 'early'} "
        f"interest based on their engagement signals. "
        f"Timely outreach with a tailored pitch is recommended for this account."
    )

    # Build actions based on intent stage
    if stage == "Purchase":
        actions = [
            f"Assign a senior AE to {company} immediately — they are purchase-ready",
            f"Send a custom demo environment tailored to {persona} workflows this week",
            f"Prepare an enterprise pricing proposal with a limited-time incentive"
        ]
    elif stage == "Evaluation":
        actions = [
            f"Send a targeted case study relevant to {company}'s use case in {industry}",
            f"Invite the {persona} to a live product demo within 48 hours",
            f"Connect with leadership on LinkedIn with a personalised message"
        ]
    else:  # Awareness
        actions = [
            f"Add {company} to a nurture sequence with educational content",
            f"Share a relevant blog post or industry report with the {persona}",
            f"Monitor {company} for increased engagement signals before direct outreach"
        ]

    return summary, actions


# ─────────────────────────────────────────────
# GEMINI AI SUMMARIZER
# ─────────────────────────────────────────────

def _gemini_summarize(intelligence: CompanyIntelligence) -> tuple[str, list[str]]:
    """
    Use Gemini to generate a 3-sentence sales brief
    and 3 recommended SDR actions.
    Returns: (ai_summary, recommended_actions)
    """
    settings = get_settings()

    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_key_here":
        print("⚠️  No Gemini key — using rule-based summary")
        return _rule_based_summary(intelligence)

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Build signals text
        signals_text = "\n".join([
            f"  - [{s.signal_type}] {s.summary}"
            for s in intelligence.business_signals
        ]) if intelligence.business_signals else "  - None found"

        # Build leadership text
        leadership_text = "\n".join([
            f"  - {c.title}: {c.name}"
            for c in intelligence.leadership
        ]) if intelligence.leadership else "  - None found"

        # Build behavior text
        behavior_text = "No behavior data."
        if intelligence.page_behavior:
            pb = intelligence.page_behavior
            behavior_text = (
                f"Visited pricing: {pb.visited_pricing}, "
                f"Visited demo: {pb.visited_demo}, "
                f"Repeat visitor: {pb.repeat_visitor}, "
                f"Dwell time: {pb.dwell_time_seconds}s"
            )

        prompt = f"""
You are an elite B2B sales intelligence AI. Write a sales brief for an SDR.

ENRICHED COMPANY PROFILE:
- Company: {intelligence.company_name}
- Domain: {intelligence.domain or 'Unknown'}
- Industry: {intelligence.industry or 'Unknown'}
- Size: {intelligence.company_size}
- HQ: {intelligence.headquarters or 'Unknown'}
- Founded: {intelligence.founded_year or 'Unknown'}
- Description: {intelligence.description or 'Not available'}

SCORING:
- Intent Score: {intelligence.intent_score}/10
- Intent Stage: {intelligence.intent_stage.value}
- Buyer Persona: {intelligence.persona.title} ({intelligence.persona.confidence*100:.0f}% confidence)

TECH STACK:
- CRM: {intelligence.tech_stack.crm if intelligence.tech_stack else 'Unknown'}
- Analytics: {intelligence.tech_stack.analytics if intelligence.tech_stack else 'Unknown'}
- Marketing: {intelligence.tech_stack.marketing if intelligence.tech_stack else 'Unknown'}

LEADERSHIP:
{leadership_text}

BUSINESS SIGNALS:
{signals_text}

VISITOR BEHAVIOR:
{behavior_text}

YOUR TASK:
1. Write EXACTLY 3 sentences as an AI sales summary. Be specific, insightful, and actionable.
2. Write EXACTLY 3 recommended next steps for the SDR. Be hyper-specific — include names, channels, and timing.

RESPOND WITH ONLY THIS JSON — no extra text, no markdown:
{{
  "ai_summary": "Sentence one about the company and their context. Sentence two about their buying signals and intent. Sentence three with the strategic recommendation.",
  "recommended_actions": [
    "Specific action 1 with name/channel/timing",
    "Specific action 2 with name/channel/timing",
    "Specific action 3 with name/channel/timing"
  ]
}}
"""

        print("🤖 Gemini generating AI summary and recommended actions...")
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Clean markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)

        ai_summary = data.get("ai_summary", "")
        recommended_actions = data.get("recommended_actions", [])

        # Validate we got proper content
        if not ai_summary or len(recommended_actions) < 1:
            raise ValueError("Gemini returned incomplete data")

        print("✅ Gemini summary generated successfully")
        return ai_summary, recommended_actions[:3]

    except Exception as e:
        print(f"⚠️  Gemini summarizer error: {e} — falling back to rule-based")
        return _rule_based_summary(intelligence)


# ─────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────

def generate_summary(intelligence: CompanyIntelligence) -> CompanyIntelligence:
    """
    Generate AI summary and recommended actions for a
    CompanyIntelligence object. Returns the same object
    with ai_summary and recommended_actions populated.
    """
    print("\n✍️  Generating AI summary and recommendations...")

    ai_summary, recommended_actions = _gemini_summarize(intelligence)

    intelligence.ai_summary = ai_summary
    intelligence.recommended_actions = recommended_actions

    print(f"  Summary:  {ai_summary[:80]}...")
    print(f"  Actions:  {len(recommended_actions)} recommendations generated")

    return intelligence

from core.models import CompanyIntelligence, PersonaProfile, IntentStage, PageBehavior

def _rule_based_score(pb: PageBehavior | None) -> float:
    if not pb: return 3.0
    score = 3.0
    if pb.visited_pricing: score += 2.0
    if pb.visited_demo: score += 1.5
    if pb.repeat_visitor: score += 1.5
    if pb.dwell_time_seconds >= 300: score += 1.5
    elif pb.dwell_time_seconds >= 120: score += 1.0
    elif pb.dwell_time_seconds >= 60: score += 0.5
    if len(pb.pages_visited) >= 4: score += 1.0
    elif len(pb.pages_visited) >= 2: score += 0.5
    return min(round(score, 1), 10.0)

def _stage(score: float) -> IntentStage:
    if score >= 7.5: return IntentStage.PURCHASE
    elif score >= 4.5: return IntentStage.EVALUATION
    return IntentStage.AWARENESS

def score_intelligence(intelligence: CompanyIntelligence) -> CompanyIntelligence:
    print("\n📊 Running intent scoring...")

    # ✅ If mock data has good score — KEEP IT
    if intelligence.data_confidence >= 0.7 and intelligence.intent_score >= 4.0:
        print(f"  ✅ Using mock score: {intelligence.intent_score}/10")
        # Fix stage to match score
        intelligence.intent_stage = _stage(intelligence.intent_score)
        # Fix persona if unknown
        if not intelligence.persona or intelligence.persona.title in ["Unknown", "Unknown Persona"]:
            personas = {
                "Purchase": PersonaProfile(title="Head of Product Design", confidence=0.85),
                "Evaluation": PersonaProfile(title="VP of Marketing", confidence=0.78),
                "Awareness": PersonaProfile(title="Growth Marketing Manager", confidence=0.65),
            }
            intelligence.persona = personas.get(intelligence.intent_stage.value, PersonaProfile(title="B2B Decision Maker", confidence=0.6))
        print(f"  Score: {intelligence.intent_score}/10 | Stage: {intelligence.intent_stage} | Persona: {intelligence.persona.title}")
        return intelligence

    # Otherwise use rule-based scoring
    score = _rule_based_score(intelligence.page_behavior)
    intelligence.intent_score = score
    intelligence.intent_stage = _stage(score)
    if not intelligence.persona or intelligence.persona.title in ["Unknown", "Unknown Persona"]:
        intelligence.persona = PersonaProfile(title="B2B Decision Maker", confidence=0.6)
    print(f"  Score: {score}/10 | Stage: {intelligence.intent_stage} | Persona: {intelligence.persona.title}")
    return intelligence

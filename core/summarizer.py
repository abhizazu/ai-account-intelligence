from core.models import CompanyIntelligence

def generate_summary(intelligence: CompanyIntelligence) -> CompanyIntelligence:
    print("\n✍️  Generating summary...")

    # ✅ If mock has a good specific summary — KEEP IT
    if (intelligence.ai_summary and
        len(intelligence.ai_summary) > 100 and
        "currently in the" not in intelligence.ai_summary):
        print("  ✅ Using existing mock summary")
        return intelligence

    # Build a SPECIFIC summary using real data
    company = intelligence.company_name
    stage = intelligence.intent_stage.value
    score = intelligence.intent_score
    persona = intelligence.persona.title
    industry = intelligence.industry or "their industry"
    hq = intelligence.headquarters or "an undisclosed location"

    # Get first leader name if available
    leader = ""
    if intelligence.leadership and intelligence.leadership[0].name != "Unknown":
        leader = f" Led by {intelligence.leadership[0].name} ({intelligence.leadership[0].title}),"

    # Get first signal
    signal = ""
    if intelligence.business_signals and "No recent" not in intelligence.business_signals[0].summary:
        signal = f" Recent signal: {intelligence.business_signals[0].summary}"

    intelligence.ai_summary = (
        f"{company} is a {industry} company headquartered in {hq} showing "
        f"{'strong' if score >= 7 else 'moderate' if score >= 4 else 'early'} "
        f"buying intent with a score of {score}/10.{leader}"
        f" The likely decision maker is a {persona} currently in the {stage} stage.{signal}"
    )

    if stage == "Purchase":
        intelligence.recommended_actions = [
            f"Assign a senior AE to {company} immediately — they are purchase-ready this week",
            f"Send a custom demo tailored to {persona} workflows at {company}",
            f"Prepare a personalized enterprise pricing proposal with a 14-day trial offer"
        ]
    elif stage == "Evaluation":
        intelligence.recommended_actions = [
            f"Send {company} a targeted case study from a similar {industry} company",
            f"Invite the {persona} at {company} to a live product demo within 48 hours",
            f"Connect with {intelligence.leadership[0].name if intelligence.leadership and intelligence.leadership[0].name != 'Unknown' else 'leadership'} on LinkedIn with a personalised note"
        ]
    else:
        intelligence.recommended_actions = [
            f"Add {company} to a nurture sequence with {industry}-specific content",
            f"Share a relevant industry report with the {persona} at {company}",
            f"Monitor {company} for increased engagement signals before direct outreach"
        ]

    print(f"  ✅ Summary generated | {len(intelligence.recommended_actions)} actions")
    return intelligence

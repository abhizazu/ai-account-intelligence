# core/mock_data.py

from core.models import (
    CompanyIntelligence, PersonaProfile, TechStack,
    LeadershipContact, BusinessSignal, PageBehavior,
    IntentStage, CompanySize
)

# ─────────────────────────────────────────────
# 5 MOCK VISITOR RECORDS (IP-based)
# ─────────────────────────────────────────────

MOCK_VISITORS = [
    {
        "ip": "104.18.2.161",
        "company_name": "Stripe",
        "city": "San Francisco",
        "country": "US",
        "org": "Stripe Inc.",
        "page_behavior": PageBehavior(
            visited_pricing=True,
            visited_demo=True,
            repeat_visitor=True,
            dwell_time_seconds=340,
            pages_visited=["/pricing", "/demo", "/features", "/case-studies"]
        )
    },
    {
        "ip": "13.32.99.10",
        "company_name": "Notion",
        "city": "San Francisco",
        "country": "US",
        "org": "Notion Labs Inc.",
        "page_behavior": PageBehavior(
            visited_pricing=False,
            visited_demo=True,
            repeat_visitor=False,
            dwell_time_seconds=120,
            pages_visited=["/features", "/demo"]
        )
    },
    {
        "ip": "185.220.101.45",
        "company_name": "Revolut",
        "city": "London",
        "country": "GB",
        "org": "Revolut Ltd.",
        "page_behavior": PageBehavior(
            visited_pricing=True,
            visited_demo=False,
            repeat_visitor=True,
            dwell_time_seconds=210,
            pages_visited=["/pricing", "/integrations"]
        )
    },
    {
        "ip": "52.74.12.88",
        "company_name": "Grab",
        "city": "Singapore",
        "country": "SG",
        "org": "Grab Holdings",
        "page_behavior": PageBehavior(
            visited_pricing=False,
            visited_demo=False,
            repeat_visitor=False,
            dwell_time_seconds=45,
            pages_visited=["/home"]
        )
    },
    {
        "ip": "203.0.113.99",
        "company_name": "Razorpay",
        "city": "Bengaluru",
        "country": "IN",
        "org": "Razorpay Software Pvt Ltd",
        "page_behavior": PageBehavior(
            visited_pricing=True,
            visited_demo=True,
            repeat_visitor=True,
            dwell_time_seconds=480,
            pages_visited=["/pricing", "/demo", "/api-docs", "/contact-sales"]
        )
    },
]

# ─────────────────────────────────────────────
# 5 MOCK COMPANY NAME RECORDS (Fully Enriched)
# ─────────────────────────────────────────────

MOCK_COMPANIES: list[CompanyIntelligence] = [
    CompanyIntelligence(
        company_name="HubSpot",
        domain="hubspot.com",
        industry="CRM / Marketing Software",
        company_size=CompanySize.ENTERPRISE,
        headquarters="Cambridge, MA, USA",
        description="HubSpot is a CRM platform for inbound marketing, sales, and service.",
        founded_year=2006,
        intent_score=7.5,
        intent_stage=IntentStage.EVALUATION,
        persona=PersonaProfile(title="VP of Marketing", confidence=0.78),
        tech_stack=TechStack(
            crm="HubSpot CRM",
            analytics="Google Analytics",
            marketing="Marketo"
        ),
        leadership=[
            LeadershipContact(
                name="Yamini Rangan",
                title="CEO",
                linkedin_url="https://linkedin.com/in/yaminirangan"
            ),
            LeadershipContact(
                name="Kipp Bodnar",
                title="CMO",
                linkedin_url="https://linkedin.com/in/kippbodnar"
            ),
        ],
        business_signals=[
            BusinessSignal(
                signal_type="Hiring",
                summary="HubSpot is actively hiring 50+ engineers in Dublin.",
                source_url="https://hubspot.com/careers"
            ),
            BusinessSignal(
                signal_type="Product Launch",
                summary="Launched AI-powered content assistant in Q1 2025.",
                source_url="https://hubspot.com/newsroom"
            ),
        ],
        ai_summary=(
            "HubSpot is a market-leading CRM platform showing strong buying signals "
            "with repeated visits to pricing and demo pages. Their recent AI product "
            "launches suggest a tech-forward team open to new tooling. "
            "An SDR should lead with an ROI-focused pitch tied to their marketing automation needs."
        ),
        recommended_actions=[
            "Send a personalized case study from a similar SaaS company",
            "Invite VP of Marketing to a live product demo this week",
            "Connect with CMO Kipp Bodnar on LinkedIn with a tailored message"
        ],
        enrichment_source="company_name",
        data_confidence=0.91
    ),

    CompanyIntelligence(
        company_name="Freshworks",
        domain="freshworks.com",
        industry="SaaS / Customer Experience",
        company_size=CompanySize.LARGE,
        headquarters="San Mateo, CA, USA",
        description="Freshworks builds cloud-based customer engagement software.",
        founded_year=2010,
        intent_score=6.0,
        intent_stage=IntentStage.EVALUATION,
        persona=PersonaProfile(title="Head of Sales Operations", confidence=0.71),
        tech_stack=TechStack(
            crm="Freshsales",
            analytics="Mixpanel",
            marketing="Mailchimp"
        ),
        leadership=[
            LeadershipContact(
                name="Dennis Woodside",
                title="CEO",
                linkedin_url="https://linkedin.com/in/denniswoodside"
            ),
        ],
        business_signals=[
            BusinessSignal(
                signal_type="Expansion",
                summary="Freshworks opened a new APAC headquarters in Singapore.",
                source_url="https://freshworks.com/news"
            ),
        ],
        ai_summary=(
            "Freshworks is a fast-growing SaaS company expanding aggressively into APAC. "
            "Their Head of Sales Ops persona suggests interest in pipeline efficiency tools. "
            "Target their Singapore team with region-specific messaging around scale."
        ),
        recommended_actions=[
            "Reach out to Singapore office with APAC-specific use cases",
            "Share a competitor displacement story relevant to Freshsales users",
            "Offer a free audit of their current sales ops workflow"
        ],
        enrichment_source="company_name",
        data_confidence=0.85
    ),

    CompanyIntelligence(
        company_name="Zepto",
        domain="zeptonow.com",
        industry="Quick Commerce / Grocery Delivery",
        company_size=CompanySize.MEDIUM,
        headquarters="Mumbai, India",
        description="Zepto is a 10-minute grocery delivery startup based in India.",
        founded_year=2021,
        intent_score=4.5,
        intent_stage=IntentStage.AWARENESS,
        persona=PersonaProfile(title="Growth Marketing Manager", confidence=0.65),
        tech_stack=TechStack(
            crm=None,
            analytics="Firebase",
            marketing="CleverTap"
        ),
        leadership=[
            LeadershipContact(
                name="Aadit Palicha",
                title="CEO & Co-Founder",
                linkedin_url="https://linkedin.com/in/aaditpalicha"
            ),
        ],
        business_signals=[
            BusinessSignal(
                signal_type="Funding",
                summary="Zepto raised $350M Series E in mid-2024 at a $5B valuation.",
                source_url="https://techcrunch.com/zepto-series-e"
            ),
        ],
        ai_summary=(
            "Zepto is a high-growth Indian startup flush with Series E funding "
            "and aggressively expanding its dark store network. "
            "Their growth team is likely evaluating new martech tools to support rapid scale."
        ),
        recommended_actions=[
            "Lead with a growth-stage pitch focused on speed and scalability",
            "Connect with the Growth Marketing Manager on LinkedIn",
            "Share how your tool helped other funded startups scale their ops"
        ],
        enrichment_source="company_name",
        data_confidence=0.76
    ),

    CompanyIntelligence(
        company_name="Figma",
        domain="figma.com",
        industry="Design / Collaboration Software",
        company_size=CompanySize.LARGE,
        headquarters="San Francisco, CA, USA",
        description="Figma is a collaborative interface design tool used by product teams worldwide.",
        founded_year=2012,
        intent_score=9.0,
        intent_stage=IntentStage.PURCHASE,
        persona=PersonaProfile(title="Head of Product Design", confidence=0.88),
        tech_stack=TechStack(
            crm="Salesforce",
            analytics="Amplitude",
            marketing="Intercom"
        ),
        leadership=[
            LeadershipContact(
                name="Dylan Field",
                title="CEO & Co-Founder",
                linkedin_url="https://linkedin.com/in/dylanfield"
            ),
            LeadershipContact(
                name="Sho Kuwamoto",
                title="VP of Product",
                linkedin_url="https://linkedin.com/in/skuwamoto"
            ),
        ],
        business_signals=[
            BusinessSignal(
                signal_type="Hiring",
                summary="Figma is hiring 30+ enterprise sales reps across North America.",
                source_url="https://figma.com/careers"
            ),
            BusinessSignal(
                signal_type="Product Launch",
                summary="Figma launched Dev Mode for engineering handoffs in 2024.",
                source_url="https://figma.com/blog"
            ),
        ],
        ai_summary=(
            "Figma is in an active purchase stage with high dwell time on pricing "
            "and demo pages, and multiple repeat visits from their design leadership team. "
            "Move fast — assign a senior AE and prioritize this account for same-week outreach."
        ),
        recommended_actions=[
            "Assign a senior AE immediately — this account is purchase-ready",
            "Send a custom demo environment tailored to design team workflows",
            "Offer a limited-time enterprise pricing proposal this week"
        ],
        enrichment_source="company_name",
        data_confidence=0.95
    ),

    CompanyIntelligence(
        company_name="Postman",
        domain="postman.com",
        industry="Developer Tools / API Platform",
        company_size=CompanySize.MEDIUM,
        headquarters="San Francisco, CA, USA",
        description="Postman is the world's leading API platform for building and testing APIs.",
        founded_year=2014,
        intent_score=5.5,
        intent_stage=IntentStage.EVALUATION,
        persona=PersonaProfile(title="Engineering Manager", confidence=0.69),
        tech_stack=TechStack(
            crm="HubSpot CRM",
            analytics="Google Analytics",
            marketing="Mailchimp"
        ),
        leadership=[
            LeadershipContact(
                name="Abhinav Asthana",
                title="CEO & Co-Founder",
                linkedin_url="https://linkedin.com/in/a85"
            ),
        ],
        business_signals=[
            BusinessSignal(
                signal_type="Expansion",
                summary="Postman expanded its platform with AI-assisted API generation in 2024.",
                source_url="https://postman.com/blog"
            ),
        ],
        ai_summary=(
            "Postman is a developer-first company evaluating tools to streamline "
            "their growing engineering team's workflows. "
            "Lead with a technical pitch and offer a free trial targeting their Engineering Managers."
        ),
        recommended_actions=[
            "Send a technical one-pager to Engineering Manager persona",
            "Offer a 30-day free trial with dedicated onboarding support",
            "Share API workflow integration examples from similar dev tool companies"
        ],
        enrichment_source="company_name",
        data_confidence=0.80
    ),
]

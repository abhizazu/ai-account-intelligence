# core/models.py

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from enum import Enum


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class IntentStage(str, Enum):
    AWARENESS = "Awareness"
    EVALUATION = "Evaluation"
    PURCHASE = "Purchase"


class CompanySize(str, Enum):
    STARTUP = "1-10"
    SMALL = "11-50"
    MEDIUM = "51-200"
    LARGE = "201-1000"
    ENTERPRISE = "1000+"
    UNKNOWN = "Unknown"


# ─────────────────────────────────────────────
# SUB-MODELS
# ─────────────────────────────────────────────

class PersonaProfile(BaseModel):
    title: str = Field(
        default="Unknown",
        description="Likely job title of the visitor e.g. Head of Sales Ops"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1"
    )


class LeadershipContact(BaseModel):
    name: str = Field(default="Unknown")
    title: str = Field(default="Unknown")
    linkedin_url: Optional[str] = Field(default=None)


class BusinessSignal(BaseModel):
    signal_type: str = Field(
        description="e.g. Hiring, Funding, Expansion, Product Launch"
    )
    summary: str = Field(
        description="One sentence description of the signal"
    )
    source_url: Optional[str] = Field(default=None)


class TechStack(BaseModel):
    crm: Optional[str] = Field(default=None, description="e.g. Salesforce, HubSpot")
    analytics: Optional[str] = Field(default=None, description="e.g. Google Analytics, Mixpanel")
    marketing: Optional[str] = Field(default=None, description="e.g. Marketo, Mailchimp")
    other: list[str] = Field(default_factory=list)


class PageBehavior(BaseModel):
    visited_pricing: bool = Field(default=False)
    visited_demo: bool = Field(default=False)
    repeat_visitor: bool = Field(default=False)
    dwell_time_seconds: int = Field(default=0, ge=0)
    pages_visited: list[str] = Field(default_factory=list)


# ─────────────────────────────────────────────
# MAIN OUTPUT MODEL
# ─────────────────────────────────────────────

class CompanyIntelligence(BaseModel):

    # --- Core Identity ---
    company_name: str = Field(default="Unknown")
    domain: Optional[str] = Field(default=None)
    industry: Optional[str] = Field(default=None)
    company_size: CompanySize = Field(default=CompanySize.UNKNOWN)
    headquarters: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    founded_year: Optional[int] = Field(default=None)

    # --- Visitor Intelligence ---
    ip_address: Optional[str] = Field(default=None)
    page_behavior: Optional[PageBehavior] = Field(default=None)

    # --- AI Scoring ---
    intent_score: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        description="Intent score from 0 (cold) to 10 (ready to buy)"
    )
    intent_stage: IntentStage = Field(default=IntentStage.AWARENESS)
    persona: PersonaProfile = Field(default_factory=PersonaProfile)

    # --- Tech Stack ---
    tech_stack: TechStack = Field(default_factory=TechStack)

    # --- People ---
    leadership: list[LeadershipContact] = Field(default_factory=list)

    # --- Signals ---
    business_signals: list[BusinessSignal] = Field(default_factory=list)

    # --- AI Generated Content ---
    ai_summary: Optional[str] = Field(
        default=None,
        description="3-sentence sales intelligence brief"
    )
    recommended_actions: list[str] = Field(
        default_factory=list,
        description="3 recommended next steps for the SDR"
    )

    # --- Meta ---
    enrichment_source: str = Field(
        default="company_name",
        description="Either 'ip_address' or 'company_name'"
    )
    data_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the enriched data"
    )

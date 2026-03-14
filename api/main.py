# api/main.py

import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from core.pipeline import run_pipeline
from core.scorer import score_intelligence
from core.summarizer import generate_summary
from core.models import CompanyIntelligence, PageBehavior


# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────

app = FastAPI(
    title="AI Account Intelligence & Enrichment System",
    description="Automatically enrich company data into full sales intelligence profiles.",
    version="1.0.0"
)

# Allow all origins for hackathon/demo purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────

class EnrichRequest(BaseModel):
    company_name: Optional[str] = None
    ip_address: Optional[str] = None
    page_behavior: Optional[PageBehavior] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "company_name": "Figma",
                    "page_behavior": {
                        "visited_pricing": True,
                        "visited_demo": True,
                        "repeat_visitor": True,
                        "dwell_time_seconds": 340,
                        "pages_visited": ["/pricing", "/demo", "/features"]
                    }
                }
            ]
        }
    }


class BatchEnrichRequest(BaseModel):
    company_names: list[str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"company_names": ["Figma", "HubSpot", "Postman"]}
            ]
        }
    }


class EnrichResponse(BaseModel):
    success: bool
    processing_time_seconds: float
    data: CompanyIntelligence


class BatchEnrichResponse(BaseModel):
    success: bool
    total: int
    processing_time_seconds: float
    results: list[CompanyIntelligence]


# ─────────────────────────────────────────────
# CORE ENRICHMENT HELPER
# ─────────────────────────────────────────────

def _run_full_enrichment(
    company_name: Optional[str] = None,
    ip_address: Optional[str] = None,
    page_behavior: Optional[PageBehavior] = None
) -> CompanyIntelligence:
    """Run the complete enrichment pipeline."""

    # Step 1: Pipeline — gather all data
    intelligence = run_pipeline(
        company_name=company_name,
        ip_address=ip_address,
        page_behavior=page_behavior
    )

    # Step 2: Score — intent score + persona
    intelligence = score_intelligence(intelligence)

    # Step 3: Summarize — AI brief + actions
    intelligence = generate_summary(intelligence)

    return intelligence


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    """Check if the API is running."""
    return {
        "status": "healthy",
        "service": "AI Account Intelligence API",
        "version": "1.0.0"
    }


@app.post(
    "/enrich",
    response_model=EnrichResponse,
    tags=["Enrichment"],
    summary="Enrich a single company or IP address"
)
def enrich_single(request: EnrichRequest):
    """
    Enrich a single company or visitor IP into a full
    sales intelligence profile.

    - Provide **company_name** for direct company enrichment
    - Provide **ip_address** to resolve a website visitor
    - Optionally include **page_behavior** for better intent scoring
    """
    # Validate input
    if not request.company_name and not request.ip_address:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'company_name' or 'ip_address'"
        )

    start = time.time()

    try:
        result = _run_full_enrichment(
            company_name=request.company_name,
            ip_address=request.ip_address,
            page_behavior=request.page_behavior
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Enrichment pipeline failed: {str(e)}"
        )

    elapsed = round(time.time() - start, 2)

    return EnrichResponse(
        success=True,
        processing_time_seconds=elapsed,
        data=result
    )


@app.post(
    "/batch",
    response_model=BatchEnrichResponse,
    tags=["Enrichment"],
    summary="Enrich a list of companies in batch"
)
def enrich_batch(request: BatchEnrichRequest):
    """
    Enrich multiple companies at once.
    Maximum 10 companies per batch request.
    """
    if not request.company_names:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one company name"
        )

    if len(request.company_names) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 companies per batch request"
        )

    start = time.time()
    results = []

    for company_name in request.company_names:
        try:
            print(f"\n{'='*40}")
            print(f"📦 Batch processing: {company_name}")
            result = _run_full_enrichment(company_name=company_name)
            results.append(result)
        except Exception as e:
            print(f"⚠️  Failed to enrich '{company_name}': {e}")
            # Add a minimal stub so batch doesn't fail entirely
            results.append(CompanyIntelligence(
                company_name=company_name,
                enrichment_source="company_name"
            ))

    elapsed = round(time.time() - start, 2)

    return BatchEnrichResponse(
        success=True,
        total=len(results),
        processing_time_seconds=elapsed,
        results=results
    )

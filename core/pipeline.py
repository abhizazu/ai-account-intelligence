# core/pipeline.py

import time
from core.models import CompanyIntelligence, PageBehavior
from agents.ip_resolver import resolve_ip
from agents.company_enricher import enrich_company
from agents.tech_detector import detect_tech_stack
from agents.leadership_finder import find_leadership
from agents.signals_agent import find_signals


# ─────────────────────────────────────────────
# PIPELINE LOGGER
# ─────────────────────────────────────────────

def _log(step: str, message: str):
    """Simple step logger for pipeline visibility."""
    print(f"  [{step}] {message}")


# ─────────────────────────────────────────────
# MAIN PIPELINE FUNCTION
# ─────────────────────────────────────────────

def run_pipeline(
    company_name: str | None = None,
    ip_address: str | None = None,
    page_behavior: PageBehavior | None = None
) -> CompanyIntelligence:
    """
    Master orchestrator — runs all enrichment agents in sequence.

    Args:
        company_name: Direct company name input
        ip_address: Visitor IP address (will be resolved to company)
        page_behavior: Optional visitor page behavior data

    Returns:
        A fully populated CompanyIntelligence object
    """

    start_time = time.time()
    print("\n" + "="*50)
    print("🚀 STARTING ENRICHMENT PIPELINE")
    print("="*50)

    # ─────────────────────────────────────────
    # STEP 1: Resolve IP → Company Name
    # ─────────────────────────────────────────
    resolved_ip = None

    if ip_address and not company_name:
        _log("STEP 1", f"Resolving IP: {ip_address}")
        ip_result = resolve_ip(ip_address)
        company_name = ip_result.company_name
        resolved_ip = ip_address
        _log("STEP 1", f"✅ Resolved to: {company_name}")
    else:
        _log("STEP 1", f"Skipping IP resolution — using company name: {company_name}")

    if not company_name or company_name == "Unknown":
        _log("STEP 1", "❌ Could not determine company name. Returning empty profile.")
        return CompanyIntelligence(
            company_name="Unknown",
            ip_address=resolved_ip,
            enrichment_source="ip_address" if ip_address else "company_name"
        )

    # ─────────────────────────────────────────
    # STEP 2: Enrich Company Base Data
    # ─────────────────────────────────────────
    _log("STEP 2", f"Enriching company data for: {company_name}")
    intelligence = enrich_company(company_name)

    # Attach IP and page behavior if provided
    if resolved_ip:
        intelligence.ip_address = resolved_ip
        intelligence.enrichment_source = "ip_address"

    if page_behavior:
        intelligence.page_behavior = page_behavior
        _log("STEP 2", "✅ Page behavior attached")

    _log("STEP 2", f"✅ Base data enriched — domain: {intelligence.domain}")

    # ─────────────────────────────────────────
    # STEP 3: Detect Tech Stack
    # ─────────────────────────────────────────
    if intelligence.domain:
        _log("STEP 3", f"Detecting tech stack for: {intelligence.domain}")
        intelligence.tech_stack = detect_tech_stack(intelligence.domain)
        _log("STEP 3", f"✅ Tech stack — CRM: {intelligence.tech_stack.crm if intelligence.tech_stack else None}, Analytics: {intelligence.tech_stack.analytics if intelligence.tech_stack else None}")
    else:
        _log("STEP 3", "⚠️  No domain available — skipping tech detection")

    # ─────────────────────────────────────────
    # STEP 4: Finding Leadership Contacts
    # ─────────────────────────────────────────
    _log("STEP 4", f"Finding leadership contacts for: {company_name}")
    intelligence.leadership = find_leadership(company_name)
    _log("STEP 4", f"✅ Found {len(intelligence.leadership) if intelligence.leadership else 0} leadership contacts")

    # ─────────────────────────────────────────
    # STEP 5: Finding Business Signals
    # ─────────────────────────────────────────
    _log("STEP 5", f"Finding business signals for: {company_name}")
    intelligence.business_signals = find_signals(company_name)
    _log("STEP 5", f"✅ Found {len(intelligence.business_signals) if intelligence.business_signals else 0} business signals")

    # ─────────────────────────────────────────
    # PIPELINE COMPLETE
    # ─────────────────────────────────────────
    elapsed = round(time.time() - start_time, 2)
    print("="*50)
    print(f"✅ PIPELINE COMPLETE in {elapsed}s")
    print("="*50 + "\n")

    return intelligence

# agents/company_enricher.py

import requests
from bs4 import BeautifulSoup
from core.config import get_settings
from core.models import CompanyIntelligence, CompanySize
from core.mock_data import MOCK_COMPANIES


# ─────────────────────────────────────────────
# HELPER: GUESS DOMAIN FROM COMPANY NAME
# ─────────────────────────────────────────────

def _guess_domain(company_name: str) -> str:
    """Convert company name to a best-guess domain."""
    clean = company_name.lower().strip()
    clean = clean.replace(" ", "").replace(",", "").replace(".", "")
    return f"{clean}.com"


# ─────────────────────────────────────────────
# MOCK FALLBACK
# ─────────────────────────────────────────────

def _enrich_from_mock(company_name: str) -> CompanyIntelligence | None:
    """Check mock data for known company names."""
    for company in MOCK_COMPANIES:
        if company.company_name.lower() == company_name.lower():
            print(f"📦 '{company_name}' resolved from mock data")
            return company
    return None


# ─────────────────────────────────────────────
# CLEARBIT ENRICHMENT
# ─────────────────────────────────────────────

def _enrich_from_clearbit(company_name: str, api_key: str) -> CompanyIntelligence | None:
    """Use Clearbit's company lookup API."""
    domain = _guess_domain(company_name)
    url = f"https://company.clearbit.com/v2/companies/find"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"domain": domain}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            print(f"⚠️  Clearbit returned {response.status_code} for {domain}")
            return None

        data = response.json()

        # Map Clearbit employee count to our CompanySize enum
        employees = data.get("metrics", {}).get("employees", 0)
        if employees <= 10:
            size = CompanySize.STARTUP
        elif employees <= 50:
            size = CompanySize.SMALL
        elif employees <= 200:
            size = CompanySize.MEDIUM
        elif employees <= 1000:
            size = CompanySize.LARGE
        else:
            size = CompanySize.ENTERPRISE

        geo = data.get("geo", {})
        hq = f"{geo.get('city', '')}, {geo.get('stateCode', '')}, {geo.get('country', '')}".strip(", ")

        return CompanyIntelligence(
            company_name=data.get("name", company_name),
            domain=data.get("domain", domain),
            industry=data.get("category", {}).get("industry", None),
            company_size=size,
            headquarters=hq or None,
            description=data.get("description", None),
            founded_year=data.get("foundedYear", None),
            enrichment_source="company_name",
            data_confidence=0.85
        )

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Clearbit error: {e}")
        return None


# ─────────────────────────────────────────────
# BEAUTIFULSOUP SCRAPER FALLBACK
# ─────────────────────────────────────────────

def _enrich_from_scraping(company_name: str) -> CompanyIntelligence:
    """Scrape company homepage as a fallback enrichment method."""
    domain = _guess_domain(company_name)
    url = f"https://{domain}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    description = None
    industry = None

    try:
        print(f"🔍 Scraping {url} for company info...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Try meta description first
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"][:300]

        # Try og:description as backup
        if not description:
            og_desc = soup.find("meta", property="og:description")
            if og_desc and og_desc.get("content"):
                description = og_desc["content"][:300]

        # Try title tag for industry hints
        title = soup.find("title")
        if title:
            industry = title.get_text(strip=True)[:80]

        print(f"✅ Scraped {domain} successfully")

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Could not scrape {url}: {e}")

    return CompanyIntelligence(
        company_name=company_name,
        domain=domain,
        industry=industry,
        company_size=CompanySize.UNKNOWN,
        headquarters=None,
        description=description,
        founded_year=None,
        enrichment_source="company_name",
        data_confidence=0.45
    )


# ─────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────

def enrich_company(company_name: str) -> CompanyIntelligence:
    """
    Enrich a company name into a CompanyIntelligence object.
    Priority: mock data → Clearbit API → BeautifulSoup scraper
    """
    settings = get_settings()

    # 1. Check mock data
    mock_result = _enrich_from_mock(company_name)
    if mock_result:
        return mock_result

    # 2. Try Clearbit if key is available
    if settings.clearbit_api_key and settings.clearbit_api_key != "not_needed":
        print(f"🏢 Enriching '{company_name}' via Clearbit...")
        clearbit_result = _enrich_from_clearbit(company_name, settings.clearbit_api_key)
        if clearbit_result:
            return clearbit_result

    # 3. Fall back to scraping
    print(f"🔍 Falling back to scraper for '{company_name}'...")
    return _enrich_from_scraping(company_name)

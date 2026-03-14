# agents/tech_detector.py

import requests
from bs4 import BeautifulSoup
from core.config import get_settings
from core.models import TechStack


# ─────────────────────────────────────────────
# KNOWN TECH SIGNATURES FOR SCRAPER FALLBACK
# ─────────────────────────────────────────────

TECH_SIGNATURES = {
    # CRMs
    "salesforce": {"type": "crm", "name": "Salesforce"},
    "hubspot": {"type": "crm", "name": "HubSpot"},
    "pipedrive": {"type": "crm", "name": "Pipedrive"},
    "zoho": {"type": "crm", "name": "Zoho CRM"},
    "freshsales": {"type": "crm", "name": "Freshsales"},

    # Analytics
    "google-analytics": {"type": "analytics", "name": "Google Analytics"},
    "googletagmanager": {"type": "analytics", "name": "Google Tag Manager"},
    "mixpanel": {"type": "analytics", "name": "Mixpanel"},
    "segment": {"type": "analytics", "name": "Segment"},
    "amplitude": {"type": "analytics", "name": "Amplitude"},
    "heap": {"type": "analytics", "name": "Heap"},
    "hotjar": {"type": "analytics", "name": "Hotjar"},
    "fullstory": {"type": "analytics", "name": "FullStory"},

    # Marketing
    "marketo": {"type": "marketing", "name": "Marketo"},
    "mailchimp": {"type": "marketing", "name": "Mailchimp"},
    "intercom": {"type": "marketing", "name": "Intercom"},
    "drift": {"type": "marketing", "name": "Drift"},
    "klaviyo": {"type": "marketing", "name": "Klaviyo"},
    "braze": {"type": "marketing", "name": "Braze"},
    "clevertap": {"type": "marketing", "name": "CleverTap"},

    # Other common tools
    "stripe": {"type": "other", "name": "Stripe"},
    "zendesk": {"type": "other", "name": "Zendesk"},
    "cloudflare": {"type": "other", "name": "Cloudflare"},
    "wordpress": {"type": "other", "name": "WordPress"},
    "shopify": {"type": "other", "name": "Shopify"},
    "firebase": {"type": "other", "name": "Firebase"},
    "sentry": {"type": "other", "name": "Sentry"},
}


# ─────────────────────────────────────────────
# MOCK FALLBACK
# ─────────────────────────────────────────────

MOCK_TECH_STACKS = {
    "hubspot.com": TechStack(
        crm="HubSpot CRM",
        analytics="Google Analytics",
        marketing="Marketo",
        other=["Cloudflare", "Stripe"]
    ),
    "figma.com": TechStack(
        crm="Salesforce",
        analytics="Amplitude",
        marketing="Intercom",
        other=["Sentry", "Cloudflare"]
    ),
    "freshworks.com": TechStack(
        crm="Freshsales",
        analytics="Mixpanel",
        marketing="Mailchimp",
        other=["Zendesk"]
    ),
    "zeptonow.com": TechStack(
        crm=None,
        analytics="Firebase",
        marketing="CleverTap",
        other=["Sentry"]
    ),
    "postman.com": TechStack(
        crm="HubSpot CRM",
        analytics="Google Analytics",
        marketing="Mailchimp",
        other=["Cloudflare"]
    ),
}


def _detect_from_mock(domain: str) -> TechStack | None:
    """Check mock data for known domains."""
    domain_clean = domain.lower().strip()
    if domain_clean in MOCK_TECH_STACKS:
        print(f"📦 Tech stack for '{domain}' resolved from mock data")
        return MOCK_TECH_STACKS[domain_clean]
    return None


# ─────────────────────────────────────────────
# BUILTWITH API
# ─────────────────────────────────────────────

def _detect_from_builtwith(domain: str, api_key: str) -> TechStack | None:
    """Use BuiltWith free API to detect tech stack."""
    url = "https://api.builtwith.com/free1/api.json"
    params = {"KEY": api_key, "LOOKUP": domain}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = data.get("Results", [])
        if not results:
            return None

        tags = results[0].get("Result", {}).get("Paths", [])
        detected_names = []

        for path in tags:
            for tech in path.get("Technologies", []):
                name = tech.get("Name", "").lower()
                detected_names.append(name)

        crm = analytics = marketing = None
        other = []

        for name in detected_names:
            for keyword, info in TECH_SIGNATURES.items():
                if keyword in name:
                    if info["type"] == "crm" and not crm:
                        crm = info["name"]
                    elif info["type"] == "analytics" and not analytics:
                        analytics = info["name"]
                    elif info["type"] == "marketing" and not marketing:
                        marketing = info["name"]
                    elif info["type"] == "other" and info["name"] not in other:
                        other.append(info["name"])

        print(f"✅ BuiltWith detected tech for {domain}")
        return TechStack(crm=crm, analytics=analytics, marketing=marketing, other=other)

    except requests.exceptions.RequestException as e:
        print(f"⚠️  BuiltWith error for {domain}: {e}")
        return None


# ─────────────────────────────────────────────
# BEAUTIFULSOUP SCRAPER FALLBACK
# ─────────────────────────────────────────────

def _detect_from_scraping(domain: str) -> TechStack:
    """Scrape homepage HTML and detect tech signatures."""
    url = f"https://{domain}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    crm = analytics = marketing = None
    other = []

    try:
        print(f"🔍 Scraping {url} for tech signatures...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Search raw HTML for known tech signatures
        html_lower = response.text.lower()

        for keyword, info in TECH_SIGNATURES.items():
            if keyword in html_lower:
                if info["type"] == "crm" and not crm:
                    crm = info["name"]
                elif info["type"] == "analytics" and not analytics:
                    analytics = info["name"]
                elif info["type"] == "marketing" and not marketing:
                    marketing = info["name"]
                elif info["type"] == "other" and info["name"] not in other:
                    other.append(info["name"])

        print(f"✅ Scrape complete for {domain}")

    except requests.exceptions.RequestException as e:
        print(f"⚠️  Could not scrape {url}: {e}")

    return TechStack(crm=crm, analytics=analytics, marketing=marketing, other=other)


# ─────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────

def detect_tech_stack(domain: str) -> TechStack:
    """
    Detect tech stack for a given domain.
    Priority: mock data → BuiltWith API → HTML scraper
    """
    settings = get_settings()

    # 1. Check mock data
    mock_result = _detect_from_mock(domain)
    if mock_result:
        return mock_result

    # 2. Try BuiltWith if key is available
    if settings.builtwith_api_key and settings.builtwith_api_key != "not_needed":
        print(f"🛠️  Detecting tech stack for '{domain}' via BuiltWith...")
        builtwith_result = _detect_from_builtwith(domain, settings.builtwith_api_key)
        if builtwith_result:
            return builtwith_result

    # 3. Fall back to HTML scraping
    print(f"🔍 Falling back to HTML scraper for '{domain}'...")
    return _detect_from_scraping(domain)

# agents/leadership_finder.py

import json
import requests
from core.config import get_settings
from core.models import LeadershipContact
from core.mock_data import MOCK_COMPANIES


# ─────────────────────────────────────────────
# MOCK FALLBACK
# ─────────────────────────────────────────────

def _find_from_mock(company_name: str) -> list[LeadershipContact] | None:
    """Return leadership from mock data if available."""
    for company in MOCK_COMPANIES:
        if company.company_name.lower() == company_name.lower():
            if company.leadership:
                print(f"📦 Leadership for '{company_name}' resolved from mock data")
                return company.leadership
    return None


# ─────────────────────────────────────────────
# TAVILY SEARCH HELPER
# ─────────────────────────────────────────────

def _tavily_search(query: str, api_key: str) -> list[dict]:
    """Run a single Tavily search and return results."""
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 3,
        "include_answer": True
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Tavily search error: {e}")
        return []


# ─────────────────────────────────────────────
# PARSE CONTACT FROM SEARCH RESULTS
# ─────────────────────────────────────────────

def _extract_contact(
    results: list[dict],
    title: str,
    company_name: str
) -> LeadershipContact | None:
    """Extract a named contact from Tavily search results."""
    if not results:
        return None

    # Combine all snippets into one block of text
    combined_text = " ".join([
        r.get("content", "") + " " + r.get("title", "")
        for r in results
    ])

    # Look for LinkedIn URLs
    linkedin_url = None
    for result in results:
        url = result.get("url", "")
        if "linkedin.com/in/" in url:
            linkedin_url = url
            break

    # Try to find a name near the title keyword
    import re
    title_keywords = title.lower().split()
    sentences = re.split(r'[.!?\n]', combined_text)

    candidate_name = None
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(kw in sentence_lower for kw in title_keywords):
            # Look for capitalized name patterns (First Last)
            names = re.findall(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', sentence)
            # Filter out company name itself
            names = [
                n for n in names
                if company_name.lower() not in n.lower()
                and len(n.split()) == 2
            ]
            if names:
                candidate_name = names[0]
                break

    if not candidate_name:
        return None

    return LeadershipContact(
        name=candidate_name,
        title=title,
        linkedin_url=linkedin_url
    )


# ─────────────────────────────────────────────
# LIVE TAVILY SEARCH
# ─────────────────────────────────────────────

def _find_from_tavily(company_name: str, api_key: str) -> list[LeadershipContact]:
    """Search for leadership contacts using Tavily."""
    print(f"🔍 Searching for leadership at '{company_name}' via Tavily...")

    roles_to_search = [
        ("CEO", f"CEO of {company_name} founder name"),
        ("VP of Sales", f"VP Sales {company_name} LinkedIn"),
        ("Head of Marketing", f"Head of Marketing {company_name} LinkedIn"),
    ]

    contacts = []
    for title, query in roles_to_search:
        results = _tavily_search(query, api_key)
        contact = _extract_contact(results, title, company_name)
        if contact:
            print(f"  ✅ Found {title}: {contact.name}")
            contacts.append(contact)
        else:
            print(f"  ⚠️  Could not extract {title} from search results")

    return contacts


# ─────────────────────────────────────────────
# STUB FALLBACK
# ─────────────────────────────────────────────

def _stub_contacts(company_name: str) -> list[LeadershipContact]:
    """Return placeholder contacts when no data is available."""
    return [
        LeadershipContact(
            name="Unknown",
            title="CEO",
            linkedin_url=None
        ),
        LeadershipContact(
            name="Unknown",
            title="VP of Sales",
            linkedin_url=None
        ),
    ]


# ─────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────

def find_leadership(company_name: str) -> list[LeadershipContact]:
    """
    Find leadership contacts for a company.
    Priority: mock data → Tavily search → stub fallback
    """
    settings = get_settings()

    # 1. Check mock data
    mock_result = _find_from_mock(company_name)
    if mock_result:
        return mock_result

    # 2. Try Tavily if key is available
    if settings.tavily_api_key and settings.tavily_api_key != "not_needed":
        contacts = _find_from_tavily(company_name, settings.tavily_api_key)
        if contacts:
            return contacts

    # 3. Return stub fallback
    print(f"⚠️  No Tavily key or results. Returning stub contacts for '{company_name}'")
    return _stub_contacts(company_name)

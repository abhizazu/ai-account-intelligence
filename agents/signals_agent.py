# agents/signals_agent.py

import re
import requests
from core.config import get_settings
from core.models import BusinessSignal
from core.mock_data import MOCK_COMPANIES


# ─────────────────────────────────────────────
# MOCK FALLBACK
# ─────────────────────────────────────────────

def _signals_from_mock(company_name: str) -> list[BusinessSignal] | None:
    """Return business signals from mock data if available."""
    for company in MOCK_COMPANIES:
        if company.company_name.lower() == company_name.lower():
            if company.business_signals:
                print(f"📦 Signals for '{company_name}' resolved from mock data")
                return company.business_signals
    return None


# ─────────────────────────────────────────────
# TAVILY SEARCH HELPER
# ─────────────────────────────────────────────

def _tavily_search(query: str, api_key: str) -> dict:
    """Run a Tavily search and return the full response."""
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 5,
        "include_answer": True
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Tavily search error: {e}")
        return {}


# ─────────────────────────────────────────────
# SIGNAL TYPE CLASSIFIER
# ─────────────────────────────────────────────

def _classify_signal(text: str) -> str:
    """Classify a signal as Hiring, Funding, Expansion, or Product Launch."""
    text_lower = text.lower()

    if any(w in text_lower for w in ["hiring", "recruit", "job opening", "head count", "team"]):
        return "Hiring"
    elif any(w in text_lower for w in ["funding", "raises", "series", "investment", "valuation", "million", "billion"]):
        return "Funding"
    elif any(w in text_lower for w in ["expan", "new office", "new market", "launch", "international", "opens"]):
        return "Expansion"
    elif any(w in text_lower for w in ["product", "feature", "release", "update", "announces", "unveil"]):
        return "Product Launch"
    else:
        return "News"


# ─────────────────────────────────────────────
# EXTRACT SIGNALS FROM TAVILY RESULTS
# ─────────────────────────────────────────────

def _extract_signals(
    search_response: dict,
    company_name: str
) -> list[BusinessSignal]:
    """Parse Tavily results into BusinessSignal objects."""
    signals = []
    results = search_response.get("results", [])

    for result in results[:3]:
        title = result.get("title", "")
        content = result.get("content", "")
        url = result.get("url", None)

        # Build a one-sentence summary from the snippet
        sentences = re.split(r'[.!?]', content)
        summary = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if company_name.lower() in sentence.lower() and len(sentence) > 30:
                summary = sentence[:200]
                break

        # Fall back to title if no good sentence found
        if not summary:
            summary = title[:200]

        if not summary:
            continue

        signal_type = _classify_signal(title + " " + content)

        signals.append(BusinessSignal(
            signal_type=signal_type,
            summary=summary,
            source_url=url
        ))

    return signals


# ─────────────────────────────────────────────
# LIVE TAVILY SEARCH
# ─────────────────────────────────────────────

def _signals_from_tavily(
    company_name: str,
    api_key: str
) -> list[BusinessSignal]:
    """Search for recent business signals using Tavily."""
    print(f"📡 Searching for business signals for '{company_name}' via Tavily...")

    queries = [
        f"{company_name} funding announcement 2024 2025",
        f"{company_name} hiring expansion news 2024 2025",
        f"{company_name} product launch news 2025",
    ]

    all_signals = []
    seen_urls = set()

    for query in queries:
        if len(all_signals) >= 3:
            break

        response = _tavily_search(query, api_key)
        signals = _extract_signals(response, company_name)

        for signal in signals:
            if signal.source_url not in seen_urls:
                seen_urls.add(signal.source_url)
                all_signals.append(signal)
                print(f"  ✅ Found signal [{signal.signal_type}]: {signal.summary[:60]}...")

            if len(all_signals) >= 3:
                break

    return all_signals[:3]


# ─────────────────────────────────────────────
# STUB FALLBACK
# ─────────────────────────────────────────────

def _stub_signals(company_name: str) -> list[BusinessSignal]:
    """Return placeholder signals when no data is available."""
    return [
        BusinessSignal(
            signal_type="News",
            summary=f"No recent signals found for {company_name}. Manual research recommended.",
            source_url=None
        )
    ]


# ─────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────

def find_signals(company_name: str) -> list[BusinessSignal]:
    """
    Find recent business signals for a company.
    Priority: mock data → Tavily search → stub fallback
    """
    settings = get_settings()

    # 1. Check mock data
    mock_result = _signals_from_mock(company_name)
    if mock_result:
        return mock_result

    # 2. Try Tavily if key is available
    if settings.tavily_api_key and settings.tavily_api_key != "not_needed":
        signals = _signals_from_tavily(company_name, settings.tavily_api_key)
        if signals:
            return signals

    # 3. Return stub fallback
    print(f"⚠️  No Tavily key or results. Returning stub signals for '{company_name}'")
    return _stub_signals(company_name)

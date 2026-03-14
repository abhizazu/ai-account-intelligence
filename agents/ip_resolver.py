# agents/ip_resolver.py

import requests
from core.config import get_settings
from core.mock_data import MOCK_VISITORS


# ─────────────────────────────────────────────
# DATA CLASS FOR IP RESULT
# ─────────────────────────────────────────────

class IPResolveResult:
    def __init__(
        self,
        ip: str,
        company_name: str,
        city: str,
        country: str,
        org: str,
        source: str = "ipinfo"
    ):
        self.ip = ip
        self.company_name = company_name
        self.city = city
        self.country = country
        self.org = org
        self.source = source

    def __repr__(self):
        return (
            f"IPResolveResult("
            f"ip={self.ip}, "
            f"company={self.company_name}, "
            f"city={self.city}, "
            f"country={self.country}, "
            f"org={self.org}, "
            f"source={self.source})"
        )


# ─────────────────────────────────────────────
# MOCK FALLBACK
# ─────────────────────────────────────────────

def _resolve_from_mock(ip: str) -> IPResolveResult | None:
    """Check mock data first for known IPs."""
    for visitor in MOCK_VISITORS:
        if visitor["ip"] == ip:
            return IPResolveResult(
                ip=ip,
                company_name=visitor["company_name"],
                city=visitor["city"],
                country=visitor["country"],
                org=visitor["org"],
                source="mock"
            )
    return None


# ─────────────────────────────────────────────
# LIVE IPINFO LOOKUP
# ─────────────────────────────────────────────

def _resolve_from_ipinfo(ip: str, token: str) -> IPResolveResult:
    """Call IPinfo API to resolve an IP address."""
    url = f"https://ipinfo.io/{ip}/json"
    params = {"token": token}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # IPinfo returns org as "AS12345 CompanyName"
        org_raw = data.get("org", "Unknown")
        org_clean = " ".join(org_raw.split(" ")[1:]) if " " in org_raw else org_raw

        return IPResolveResult(
            ip=ip,
            company_name=data.get("company", {}).get("name", org_clean),
            city=data.get("city", "Unknown"),
            country=data.get("country", "Unknown"),
            org=org_clean,
            source="ipinfo"
        )

    except requests.exceptions.RequestException as e:
        print(f"⚠️  IPinfo API error for {ip}: {e}")
        # Return a minimal fallback object
        return IPResolveResult(
            ip=ip,
            company_name="Unknown",
            city="Unknown",
            country="Unknown",
            org="Unknown",
            source="error"
        )


# ─────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────

def resolve_ip(ip: str) -> IPResolveResult:
    """
    Resolve an IP address to company info.
    Priority: mock data → IPinfo API → fallback stub
    """
    settings = get_settings()

    # 1. Check mock data first (great for dev/testing)
    mock_result = _resolve_from_mock(ip)
    if mock_result:
        print(f"📦 IP {ip} resolved from mock data")
        return mock_result

    # 2. Use IPinfo if token is available
    if settings.ipinfo_token and settings.ipinfo_token != "not_needed":
        print(f"🌐 Resolving IP {ip} via IPinfo API...")
        return _resolve_from_ipinfo(ip, settings.ipinfo_token)

    # 3. Last resort fallback
    print(f"⚠️  No IPinfo token set. Returning stub for {ip}")
    return IPResolveResult(
        ip=ip,
        company_name="Unknown Company",
        city="Unknown",
        country="Unknown",
        org="Unknown",
        source="stub"
    )

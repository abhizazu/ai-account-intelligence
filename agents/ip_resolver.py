from core.mock_data import MOCK_VISITORS

class IPResolveResult:
    def __init__(self, ip, company_name, city, country, org, source="mock"):
        self.ip = ip
        self.company_name = company_name
        self.city = city
        self.country = country
        self.org = org
        self.source = source

def resolve_ip(ip: str) -> IPResolveResult:
    print(f"🔍 Resolving IP: {ip}")
    
    # Check mock data
    for visitor in MOCK_VISITORS:
        if visitor["ip"].strip() == ip.strip():
            print(f"✅ Found in mock: {visitor['company_name']}")
            return IPResolveResult(
                ip=ip,
                company_name=visitor["company_name"],
                city=visitor["city"],
                country=visitor["country"],
                org=visitor["org"],
                source="mock"
            )
    
    print(f"⚠️ IP {ip} not in mock data — returning stub")
    return IPResolveResult(
        ip=ip,
        company_name="Unknown Company",
        city="Unknown",
        country="Unknown", 
        org="Unknown",
        source="stub"
    )

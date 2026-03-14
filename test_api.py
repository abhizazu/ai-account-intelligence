import requests
import time
import subprocess
import json
import sys

# Start server
print("Starting server...")
server_process = subprocess.Popen(["uvicorn", "api.main:app", "--port", "8000"])
time.sleep(3)

try:
    print("\n=== TEST 1 - Health Check ===")
    r = requests.get("http://localhost:8000/health")
    print(json.dumps(r.json(), indent=2))

    print("\n=== TEST 2 - Full JSON for Company Name Input (Figma) ===")
    r = requests.post("http://localhost:8000/enrich", json={
        "company_name": "Figma",
        "page_behavior": {
        "visited_pricing": True,
        "visited_demo": True,
        "repeat_visitor": True,
        "dwell_time_seconds": 400,
        "pages_visited": ["/pricing", "/demo", "/features", "/contact"]
        }
    })
    print(json.dumps(r.json(), indent=2))

    print("\n=== TEST 3 - Full JSON for IP Address Input (Stripe visitor) ===")
    r = requests.post("http://localhost:8000/enrich", json={
        "ip_address": "104.18.2.161",
        "page_behavior": {
            "visited_pricing": True,
            "visited_demo": False,
            "repeat_visitor": True,
            "dwell_time_seconds": 220,
            "pages_visited": ["/pricing", "/integrations"]
        }
    })
    print(json.dumps(r.json(), indent=2))

    print("\n=== TEST 4 - Batch Endpoint (HubSpot + Postman) ===")
    r = requests.post("http://localhost:8000/batch", json={
        "company_names": ["HubSpot", "Postman"]
    })
    print(json.dumps(r.json(), indent=2))

    print("\n=== TEST 5 - Error Handling ===")
    r = requests.post("http://localhost:8000/enrich", json={})
    print(json.dumps(r.json(), indent=2))

    print("\n=== TEST 6 - Verify All 10 Output Fields Are Present ===")
    resp = requests.post('http://localhost:8000/enrich', json={
        'company_name': 'Figma'
    })
    data = resp.json().get('data', {})

    fields = [
        'company_name', 'domain', 'industry', 'company_size',
        'headquarters', 'intent_score', 'intent_stage', 'persona',
        'tech_stack', 'leadership', 'business_signals',
        'ai_summary', 'recommended_actions'
    ]

    print('=== Field Verification ===')
    all_pass = True
    for field in fields:
        value = data.get(field)
        status = '✅' if value else '⚠️  EMPTY'
        print(f'  {status} {field}: {str(value)[:60]}')
        if not value:
            all_pass = False

    print()
    print('✅ ALL FIELDS PRESENT' if all_pass else '⚠️  SOME FIELDS ARE EMPTY')

finally:
    server_process.terminate()
    server_process.wait()

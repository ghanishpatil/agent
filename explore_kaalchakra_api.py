import requests
import json

base_url = "http://138.199.163.92:10675"

# Check the docs endpoint
print("=== Checking /docs ===")
try:
    response = requests.get(f"{base_url}/docs")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Docs page accessible")
except Exception as e:
    print(f"Error: {e}")

# Check OpenAPI spec
print("\n=== Checking /openapi.json ===")
try:
    response = requests.get(f"{base_url}/openapi.json")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        spec = response.json()
        print(json.dumps(spec, indent=2))
except Exception as e:
    print(f"Error: {e}")

# Try common endpoints
print("\n=== Trying common endpoints ===")
endpoints = ["/", "/predict", "/model", "/trigger", "/flag", "/api", "/health"]
for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}")
        print(f"{endpoint}: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"{endpoint}: Error - {e}")

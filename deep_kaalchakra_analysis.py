import requests
import json

base_url = "http://138.199.163.92:10675"

# Check if there are any other endpoints or parameters
print("=== Checking for additional endpoints ===")

# Try GET on predict
try:
    response = requests.get(f"{base_url}/predict")
    print(f"GET /predict: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Try other HTTP methods
print("\n=== Testing other HTTP methods on /predict ===")
for method in ["PUT", "DELETE", "PATCH"]:
    try:
        response = requests.request(method, f"{base_url}/predict", json={"text": "time wheel", "timestamp": "2024-01-01T00:00:00"})
        print(f"{method}: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"{method}: Error - {e}")

# Check if there's a flag endpoint that requires the right score
print("\n=== Checking for flag-related endpoints ===")
flag_endpoints = [
    "/flag",
    "/get_flag",
    "/reveal",
    "/trigger",
    "/unlock",
    "/secret",
    "/kaal",
    "/chakra",
    "/kaalchakra",
]

for endpoint in flag_endpoints:
    try:
        # Try GET
        response = requests.get(f"{base_url}{endpoint}")
        if response.status_code != 404:
            print(f"GET {endpoint}: {response.status_code} - {response.text[:200]}")
        
        # Try POST with our winning combo
        response = requests.post(f"{base_url}{endpoint}", json={"text": "time wheel", "timestamp": "2024-01-01T00:00:00"})
        if response.status_code != 404:
            print(f"POST {endpoint}: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        pass

# Try adding additional parameters to predict
print("\n=== Testing additional parameters ===")
test_params = [
    {"text": "time wheel", "timestamp": "2024-01-01T00:00:00", "reveal": True},
    {"text": "time wheel", "timestamp": "2024-01-01T00:00:00", "flag": True},
    {"text": "time wheel", "timestamp": "2024-01-01T00:00:00", "trigger": True},
    {"text": "time wheel", "timestamp": "2024-01-01T00:00:00", "unlock": True},
    {"text": "time wheel", "timestamp": "2024-01-01T00:00:00", "score": 1.0},
]

for params in test_params:
    try:
        response = requests.post(f"{base_url}/predict", json=params)
        data = response.json()
        print(f"\nParams: {params}")
        print(f"Response: {data}")
        if "flag" in str(data).lower() or "kaal{" in str(data):
            print("!!! FLAG FOUND !!!")
    except Exception as e:
        print(f"Error: {e}")

# Check response headers
print("\n=== Checking response headers ===")
response = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": "2024-01-01T00:00:00"})
print("Headers:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

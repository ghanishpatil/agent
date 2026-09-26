import requests
import json

base_url = "http://138.199.163.92:10675"
timestamp = "2024-01-01T00:00:00"

# We know "time wheel" gives 100%. Maybe we need to send a follow-up request
# with a different text that acts as the trigger

print("=== Step 1: Achieve 100% with 'time wheel' ===")
response = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": timestamp})
print(f"Response: {response.json()}")

print("\n=== Step 2: Try trigger words after achieving 100% ===")
trigger_words = [
    "trigger",
    "activate",
    "unlock",
    "reveal",
    "flag",
    "complete",
    "finish",
    "done",
    "end",
    "cycle complete",
    "full cycle",
    "100",
    "perfect",
    "success",
]

for trigger in trigger_words:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": trigger, "timestamp": timestamp})
        data = response.json()
        print(f"\n{trigger}: {data}")
        
        if "flag" in str(data).lower() or "kaal{" in str(data):
            print(f"\n!!! FLAG FOUND WITH TRIGGER: {trigger} !!!")
            break
    except Exception as e:
        print(f"Error with {trigger}: {e}")

# Maybe we need to send the score back?
print("\n\n=== Testing if we need to send score back ===")
test_inputs = [
    {"text": "1.0", "timestamp": timestamp},
    {"text": "100", "timestamp": timestamp},
    {"text": "1.0000001192092896", "timestamp": timestamp},
    {"text": "score", "timestamp": timestamp},
]

for inp in test_inputs:
    try:
        response = requests.post(f"{base_url}/predict", json=inp)
        data = response.json()
        if data.get("progress", 0) >= 50:
            print(f"\n{inp['text']}: {data}")
    except Exception as e:
        pass

# Try making requests with session to maintain state
print("\n\n=== Testing with session (maintaining state) ===")
session = requests.Session()

# First, achieve 100%
response = session.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": timestamp})
print(f"Step 1 (time wheel): {response.json()}")

# Then try trigger
response = session.post(f"{base_url}/predict", json={"text": "trigger", "timestamp": timestamp})
print(f"Step 2 (trigger): {response.json()}")

# Try flag
response = session.post(f"{base_url}/predict", json={"text": "flag", "timestamp": timestamp})
print(f"Step 3 (flag): {response.json()}")

# Maybe we need to check cookies or session data
print(f"\nSession cookies: {session.cookies.get_dict()}")

# Try accessing other endpoints with the session
print("\n\n=== Trying other endpoints with session ===")
endpoints = ["/flag", "/reveal", "/unlock", "/complete", "/success"]
for endpoint in endpoints:
    try:
        response = session.get(f"{base_url}{endpoint}")
        if response.status_code != 404:
            print(f"{endpoint}: {response.status_code} - {response.text}")
    except:
        pass

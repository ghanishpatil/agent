import requests
import json

base_url = "http://138.199.163.92:10675"

# Maybe we need to make multiple requests in a cycle?
print("=== Testing cyclic requests (same timestamp multiple times) ===")

timestamp = "2024-01-01T00:00:00"
text = "time wheel"

for i in range(1, 11):
    try:
        response = requests.post(f"{base_url}/predict", json={"text": text, "timestamp": timestamp})
        data = response.json()
        print(f"\nRequest {i}:")
        print(f"  Response: {json.dumps(data, indent=2)}")
        
        if "flag" in str(data).lower() or "kaal{" in str(data):
            print(f"\n!!! FLAG FOUND ON REQUEST {i} !!!")
            break
    except Exception as e:
        print(f"Error on request {i}: {e}")

# Try variations of the winning text
print("\n\n=== Testing text variations ===")
variations = [
    "time wheel",
    "Time Wheel",
    "TIME WHEEL",
    "timewheel",
    "time_wheel",
    "time-wheel",
    "wheel time",
    "wheel of time",
    "the time wheel",
    "eternal time wheel",
    "cyclic time wheel",
    "kaalchakra time wheel",
    "time wheel cycle",
    "time wheel trigger",
    "time wheel flag",
]

for text in variations:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": text, "timestamp": timestamp})
        data = response.json()
        progress = data.get("progress", 0)
        
        if progress == 100:
            print(f"{text:30s} -> Progress: {progress}%")
            if data.get("tone") != "Bravo ! Almost there.":
                print(f"  DIFFERENT RESPONSE: {data}")
        
        if "flag" in str(data).lower() or "kaal{" in str(data):
            print(f"\n!!! FLAG FOUND WITH: {text} !!!")
            print(f"Full response: {data}")
            
    except Exception as e:
        print(f"Error with {text}: {e}")

# Try sending a sequence of timestamps (representing a cycle)
print("\n\n=== Testing timestamp sequence (cycle) ===")
timestamps = [
    "2024-01-01T00:00:00",
    "2024-01-01T06:00:00",
    "2024-01-01T12:00:00",
    "2024-01-01T18:00:00",
    "2024-01-01T00:00:00",  # Back to start - completing the cycle
]

for i, ts in enumerate(timestamps):
    try:
        response = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": ts})
        data = response.json()
        print(f"\nCycle step {i+1} ({ts}):")
        print(f"  Response: {json.dumps(data, indent=2)}")
        
        if "flag" in str(data).lower() or "kaal{" in str(data):
            print(f"\n!!! FLAG FOUND AT CYCLE STEP {i+1} !!!")
            break
    except Exception as e:
        print(f"Error: {e}")

import requests
import json
from datetime import datetime

base_url = "http://138.199.163.92:10675"

# Check home endpoint more carefully
print("=== Checking home endpoint ===")
response = requests.get(f"{base_url}/")
print(f"Response: {response.json()}")
print(f"Headers: {dict(response.headers)}")

# Maybe the timestamp needs to be in a specific format or represent a specific moment
# Let's try Unix timestamps, different formats, etc.
print("\n=== Testing different timestamp formats ===")

test_timestamps = [
    "0",  # Unix epoch as number
    "0000-00-00T00:00:00",
    "9999-12-31T23:59:59",
    "2024-01-01T00:00:00Z",  # With timezone
    "2024-01-01T00:00:00+00:00",
    "2024-01-01T00:00:00.000",  # With milliseconds
    "2024-01-01T00:00:00.000000",  # With microseconds
    "2024-01-01 00:00:00",  # Space instead of T
    "01-01-2024T00:00:00",  # Different date format
]

for ts in test_timestamps:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": ts})
        data = response.json()
        print(f"\n{ts}")
        print(f"  Response: {data}")
        
        if "flag" in str(data).lower() or "kaal{" in str(data):
            print(f"\n!!! FLAG FOUND !!!")
            break
    except Exception as e:
        print(f"  Error: {e}")

# Try special cyclic numbers in timestamp
print("\n\n=== Testing cyclic/repeating timestamps ===")
cyclic_times = [
    "1111-11-11T11:11:11",
    "2222-02-22T22:22:22",
    "3333-03-03T03:03:03",
    "1234-12-34T12:34:56",  # Invalid but sequential
    "2024-12-12T12:12:12",
    "2020-02-02T02:02:02",
]

for ts in cyclic_times:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": ts})
        data = response.json()
        if "error" not in str(data):
            print(f"\n{ts}")
            print(f"  Response: {data}")
            
            if data.get("tone") != "Bravo ! Almost there.":
                print(f"  !!! DIFFERENT RESPONSE !!!")
    except Exception as e:
        pass

# Maybe we need to check if there's a pattern in the score value
print("\n\n=== Analyzing score value ===")
response = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": "2024-01-01T00:00:00"})
data = response.json()
score = data.get("score", 0)
print(f"Score: {score}")
print(f"Score as hex: {score.hex() if hasattr(score, 'hex') else 'N/A'}")
print(f"Score * 100: {score * 100}")

# Try to decode the score or look for hidden data
import struct
try:
    # Try to interpret the score as encoded data
    score_bytes = struct.pack('f', score)
    print(f"Score as bytes: {score_bytes}")
    print(f"Score as hex bytes: {score_bytes.hex()}")
except Exception as e:
    print(f"Error: {e}")

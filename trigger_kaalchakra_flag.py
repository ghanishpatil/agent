import requests
import json
from datetime import datetime, timedelta

base_url = "http://138.199.163.92:10675"

# We found "time wheel" gives 100% progress
# Now let's try different timestamps to find the trigger

print("=== Testing 'time wheel' with various timestamps ===")

# Try special cyclic timestamps
timestamps = [
    "2024-01-01T00:00:00",
    "2024-12-31T23:59:59",
    "2000-01-01T00:00:00",
    "1970-01-01T00:00:00",  # Unix epoch
    "2038-01-19T03:14:07",  # Unix timestamp overflow
    "2024-02-29T00:00:00",  # Leap year
    "2024-06-21T00:00:00",  # Summer solstice
    "2024-12-21T00:00:00",  # Winter solstice
    "2024-03-20T00:00:00",  # Spring equinox
    "2024-09-22T00:00:00",  # Autumn equinox
]

# Add repeating/cyclic patterns
for h in [0, 1, 2, 3, 11, 12, 13, 23]:
    timestamps.append(f"2024-{h:02d}-{h:02d}T{h:02d}:{h:02d}:{h:02d}")

for ts in timestamps:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": ts})
        data = response.json()
        print(f"\n{ts}")
        print(f"  Response: {json.dumps(data, indent=2)}")
        
        # Check if flag is in response
        if "flag" in str(data).lower() or "kaal{" in str(data):
            print(f"\n!!! POTENTIAL FLAG FOUND !!!")
            print(f"Full response: {data}")
            
    except Exception as e:
        print(f"Error with {ts}: {e}")

# Try current time
print("\n\n=== Testing with current time ===")
current_time = datetime.now().isoformat()
response = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": current_time})
print(f"Current time: {current_time}")
print(f"Response: {response.json()}")

# Try midnight today
print("\n\n=== Testing with midnight today ===")
midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
response = requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": midnight})
print(f"Midnight: {midnight}")
print(f"Response: {response.json()}")

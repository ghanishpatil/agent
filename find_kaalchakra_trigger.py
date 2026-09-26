import requests
import json
from itertools import product

base_url = "http://138.199.163.92:10675"

# Try words related to cyclic time, Kaal (Sanskrit for time), etc.
keywords = [
    "time", "cycle", "kaal", "chakra", "kaalchakra", "wheel", "eternal",
    "cyclic", "circular", "loop", "repeat", "recurrence", "periodic",
    "rhythm", "season", "epoch", "era", "age", "yugas", "kalpa",
    "samsara", "reincarnation", "rebirth", "return", "rotation",
    "revolution", "orbit", "circle", "round", "spiral", "helix",
    "timeloop", "timecycle", "infinity", "eternity", "perpetual",
    "endless", "continuous", "recurring", "cyclical", "temporal"
]

timestamp = "2024-01-01T00:00:00"

print("=== Testing keywords for highest score ===")
best_score = 0
best_text = ""
best_response = None

for text in keywords:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": text, "timestamp": timestamp})
        data = response.json()
        score = data.get("score", 0)
        progress = data.get("progress", 0)
        
        if progress >= 50:  # Show promising results
            print(f"{text:20s} -> Score: {score:.4f}, Progress: {progress}%")
        
        if score > best_score:
            best_score = score
            best_text = text
            best_response = data
            
    except Exception as e:
        print(f"Error with {text}: {e}")

print(f"\n=== Best result ===")
print(f"Text: {best_text}")
print(f"Score: {best_score}")
print(f"Response: {best_response}")

# Try combinations
print("\n\n=== Testing combinations ===")
combos = [
    "kaal chakra",
    "time cycle",
    "eternal cycle",
    "wheel of time",
    "cyclic time",
    "time wheel",
    "kaalchakra cycle",
]

for text in combos:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": text, "timestamp": timestamp})
        data = response.json()
        score = data.get("score", 0)
        progress = data.get("progress", 0)
        print(f"{text:25s} -> Score: {score:.4f}, Progress: {progress}%")
        
        if progress >= 90:
            print(f"  FULL RESPONSE: {data}")
            
    except Exception as e:
        print(f"Error with {text}: {e}")

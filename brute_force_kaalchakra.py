import requests
import json
import itertools

base_url = "http://138.199.163.92:10675"
timestamp = "2024-01-01T00:00:00"

# Try more specific trigger words
print("=== Testing potential trigger words ===")

triggers = [
    # Kaalchakra related
    "kaalchakra", "kaal chakra", "wheel of time", "time wheel",
    "kalachakra", "kala chakra",
    
    # Trigger-related
    "trigger", "activate", "unlock", "reveal", "open", "start",
    "begin", "initiate", "execute", "run", "invoke",
    
    # Flag-related
    "flag", "get flag", "show flag", "reveal flag", "give flag",
    
    # Time-related with trigger
    "time wheel trigger", "trigger time wheel", "activate time wheel",
    "unlock time wheel", "reveal time wheel",
    
    # Cyclic concepts
    "complete cycle", "full cycle", "cycle complete", "end cycle",
    "cycle end", "cycle start", "new cycle", "cycle reset",
    
    # Sanskrit/Hindu concepts
    "yugas", "kalpa", "manvantara", "pralaya", "samsara",
    
    # Special phrases
    "the wheel turns", "time repeats", "eternal return",
    "cycle of time", "time cycle complete",
]

best_results = []

for text in triggers:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": text, "timestamp": timestamp})
        data = response.json()
        progress = data.get("progress", 0)
        tone = data.get("tone", "")
        
        if progress >= 90 or tone != "Bravo ! Almost there.":
            print(f"{text:30s} -> Progress: {progress}%, Tone: {tone}")
            best_results.append((text, data))
        
        if "flag" in str(data).lower() or "kaal{" in str(data):
            print(f"\n!!! FLAG FOUND WITH: {text} !!!")
            print(f"Full response: {data}")
            break
            
    except Exception as e:
        pass

# Try combinations of words that scored well
print("\n\n=== Testing word combinations ===")
high_score_words = ["time", "wheel", "cycle", "trigger", "kaal", "chakra"]

for combo in itertools.combinations(high_score_words, 2):
    text = " ".join(combo)
    try:
        response = requests.post(f"{base_url}/predict", json={"text": text, "timestamp": timestamp})
        data = response.json()
        progress = data.get("progress", 0)
        
        if progress >= 95:
            print(f"{text:30s} -> Progress: {progress}%")
            if data.get("tone") != "Bravo ! Almost there.":
                print(f"  DIFFERENT RESPONSE: {data}")
                
    except Exception as e:
        pass

# Try with different separators
print("\n\n=== Testing separators ===")
base_words = ["time", "wheel"]
separators = [" ", "_", "-", "", ".", ",", "|", "/", "\\"]

for sep in separators:
    text = sep.join(base_words)
    try:
        response = requests.post(f"{base_url}/predict", json={"text": text, "timestamp": timestamp})
        data = response.json()
        progress = data.get("progress", 0)
        
        if progress == 100:
            print(f"'{text}' (sep='{sep}') -> Progress: {progress}%")
            if data.get("tone") != "Bravo ! Almost there.":
                print(f"  DIFFERENT RESPONSE: {data}")
                
    except Exception as e:
        pass

print("\n\n=== Best results summary ===")
for text, data in best_results:
    print(f"{text}: {data}")

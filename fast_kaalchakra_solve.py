import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = "http://138.199.163.92:10675"
timestamp = "2024-01-01T00:00:00"

def test_input(text):
    try:
        response = requests.post(f"{base_url}/predict", json={"text": text, "timestamp": timestamp}, timeout=5)
        data = response.json()
        if "Kaal{" in str(data) or data.get("tone") not in ["Bravo ! Almost there.", "Neutral :)"]:
            return (text, data, True)
        if data.get("progress", 0) == 100:
            return (text, data, False)
    except:
        pass
    return None

# Massive list of potential triggers
triggers = [
    # Direct triggers
    "time wheel", "wheel of time", "kaalchakra", "kaal chakra",
    
    # After 100% triggers
    "complete", "completed", "done", "finished", "success", "perfect",
    "unlock", "reveal", "activate", "trigger", "execute", "run",
    
    # Cyclic completions
    "cycle complete", "full cycle", "complete cycle", "end cycle",
    "cycle end", "cycle finished", "cycle done",
    
    # Time-based
    "time complete", "time end", "time finished", "eternal",
    "infinity", "forever", "endless", "perpetual",
    
    # Sanskrit/Hindu
    "moksha", "nirvana", "enlightenment", "liberation", "samadhi",
    "yugas", "kalpa", "pralaya", "samsara",
    
    # Combinations
    "time wheel complete", "complete time wheel", "time wheel done",
    "time wheel finished", "time wheel perfect", "perfect time wheel",
    "time wheel unlock", "unlock time wheel", "time wheel reveal",
    "reveal time wheel", "time wheel trigger", "trigger time wheel",
    
    # Numbers/symbols
    "100", "1.0", "100%", "perfect score", "max", "maximum",
    
    # Action words
    "open", "start", "begin", "initiate", "invoke", "call",
    "get flag", "show flag", "give flag", "flag please",
    
    # Special phrases
    "the wheel has turned", "the cycle is complete", 
    "time has come full circle", "the wheel stops",
    "break the cycle", "end the loop", "escape the wheel",
    
    # More Sanskrit
    "om", "aum", "shanti", "dharma", "karma", "maya",
    
    # ML/AI related
    "predict", "inference", "model", "neural", "train", "test",
    "epoch", "iteration", "convergence", "optimal",
]

print("Testing all triggers in parallel...")
print("=" * 60)

found_flag = False
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(test_input, text): text for text in triggers}
    
    for future in as_completed(futures):
        result = future.result()
        if result:
            text, data, is_special = result
            if is_special:
                print(f"\n!!! SPECIAL RESPONSE !!!")
                print(f"Text: {text}")
                print(f"Response: {json.dumps(data, indent=2)}")
                if "Kaal{" in str(data):
                    print(f"\n!!! FLAG FOUND: {text} !!!")
                    found_flag = True
                    break
            elif data.get("progress") == 100:
                print(f"100%: {text}")

if not found_flag:
    print("\n\nNo flag found yet. Trying sequential approach after 100%...")
    
    # First get 100%
    requests.post(f"{base_url}/predict", json={"text": "time wheel", "timestamp": timestamp})
    
    # Then try triggers
    for trigger in ["reveal", "flag", "unlock", "complete", "done", "trigger", "activate"]:
        response = requests.post(f"{base_url}/predict", json={"text": trigger, "timestamp": timestamp})
        data = response.json()
        if "Kaal{" in str(data):
            print(f"\n!!! FLAG FOUND: {trigger} !!!")
            print(f"Response: {json.dumps(data, indent=2)}")
            break

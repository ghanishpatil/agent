import requests
import json

base_url = "http://138.199.163.92:10675"
timestamp = "2024-01-01T00:00:00"

# "perfect" gave a different tone. Let's explore words that might change the tone
print("=== Testing words for different tones ===")

test_words = [
    "perfect", "imperfect", "complete", "incomplete", "success", "failure",
    "correct", "incorrect", "right", "wrong", "true", "false",
    "yes", "no", "good", "bad", "positive", "negative",
    "optimal", "suboptimal", "best", "worst",
    "maximum", "minimum", "full", "empty",
    "start", "end", "beginning", "finish",
    "alpha", "omega", "first", "last",
]

different_tones = []

for word in test_words:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": word, "timestamp": timestamp})
        data = response.json()
        tone = data.get("tone", "")
        progress = data.get("progress", 0)
        
        if tone != "Bravo ! Almost there.":
            print(f"{word:20s} -> Progress: {progress}%, Tone: {tone}")
            different_tones.append((word, data))
            
    except Exception as e:
        pass

print(f"\n\n=== Found {len(different_tones)} words with different tones ===")
for word, data in different_tones:
    print(f"{word}: {data}")

# Try combinations with "perfect"
print("\n\n=== Testing combinations with 'perfect' ===")
combos = [
    "perfect cycle",
    "perfect time",
    "perfect wheel",
    "perfect time wheel",
    "time wheel perfect",
    "perfect kaalchakra",
    "perfect trigger",
]

for text in combos:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": text, "timestamp": timestamp})
        data = response.json()
        print(f"{text:30s} -> {data}")
        
        if "flag" in str(data).lower() or "kaal{" in str(data):
            print(f"\n!!! FLAG FOUND !!!")
            break
    except Exception as e:
        pass

# Try other words that might have special meanings
print("\n\n=== Testing more potential trigger words ===")
special_words = [
    "enlightenment", "nirvana", "moksha", "liberation",
    "transcendence", "ascension", "awakening",
    "completion", "fulfillment", "achievement",
    "mastery", "perfection", "excellence",
]

for word in special_words:
    try:
        response = requests.post(f"{base_url}/predict", json={"text": word, "timestamp": timestamp})
        data = response.json()
        tone = data.get("tone", "")
        progress = data.get("progress", 0)
        
        if tone != "Bravo ! Almost there." or progress >= 50:
            print(f"{word:20s} -> Progress: {progress}%, Tone: {tone}")
            
    except Exception as e:
        pass

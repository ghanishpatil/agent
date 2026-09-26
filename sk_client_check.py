import requests
import re
import json

BASE_URL = "https://smartkopargaonhackathon.vercel.app"
session = requests.Session()

print("Fetching client file...")
r = session.get(f"{BASE_URL}/assets/client-CTx1wx0j.js", timeout=15)
if r.status_code == 200:
    print(f"Got client file ({len(r.text)} bytes)")
    with open("sk_client.js", "w", encoding="utf-8") as f:
        f.write(r.text)
    
    # Search for Firebase config patterns
    patterns = [
        r'apiKey["\s:]+(["\'])(AIza[A-Za-z0-9_-]+)\1',
        r'authDomain["\s:]+(["\'])([^"\']+)\1',
        r'projectId["\s:]+(["\'])([^"\']+)\1',
        r'storageBucket["\s:]+(["\'])([^"\']+)\1',
        r'messagingSenderId["\s:]+(["\'])([^"\']+)\1',
        r'appId["\s:]+(["\'])([^"\']+)\1',
    ]
    
    config = {}
    for pattern in patterns:
        matches = re.findall(pattern, r.text)
        if matches:
            key = pattern.split('[')[0]
            config[key] = [m[1] for m in matches]
            print(f"[+] Found {key}: {config[key][:3]}")
    
    # Save config
    if config:
        with open("sk_firebase_config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("\n[+] Config saved to sk_firebase_config.json")
else:
    print(f"Failed: {r.status_code}")

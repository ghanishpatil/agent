import requests

BASE_URL = "https://smartkopargaonhackathon.vercel.app"
session = requests.Session()

print("Fetching Firebase vendor file...")
r = session.get(f"{BASE_URL}/assets/vendor-firebase-mOA9BNpV.js", timeout=15)
if r.status_code == 200:
    print(f"Got Firebase vendor ({len(r.text)} bytes)")
    with open("sk_firebase.js", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("Saved to sk_firebase.js")
    
    # Search for config
    if "AIza" in r.text:
        print("[!] Found potential Firebase API key")
        import re
        keys = re.findall(r'AIza[A-Za-z0-9_-]{35}', r.text)
        for k in keys:
            print(f"    {k}")
else:
    print(f"Failed: {r.status_code}")

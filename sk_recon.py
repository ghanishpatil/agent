import requests
import json

BASE_URL = "https://smartkopargaonhackathon.vercel.app"
session = requests.Session()

print("SMART KOPARGAON - SECURITY ASSESSMENT")
print("="*70)

resp = session.get(f"{BASE_URL}/auth", timeout=10)
print(f"Auth page: {resp.status_code}")

with open("sk_auth.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("Saved auth page")

endpoints = ["/", "/auth", "/api", "/api/auth", "/api/login", "/dashboard"]
for ep in endpoints:
    try:
        r = session.get(f"{BASE_URL}{ep}", timeout=5)
        if r.status_code != 404:
            print(f"{ep}: {r.status_code}")
    except:
        pass

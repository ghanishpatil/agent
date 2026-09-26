#!/usr/bin/env python3
"""
Explore the Kohli terminal challenge
"""
import requests
import re

BASE_URL = "http://chall-6be9171d.evt-207.glabs.ctf7.com"

print("="*80)
print("EXPLORING KOHLI TERMINAL")
print("="*80)

# Get JavaScript file
print(f"\n[Fetching app.js]")
r = requests.get(f"{BASE_URL}/app.js", timeout=10)
print(f"Status: {r.status_code}")

with open('kohli_app.js', 'w', encoding='utf-8') as f:
    f.write(r.text)

print(f"\n[JavaScript content]")
print(r.text)

# Look for flags
flags = re.findall(r'Kaal\{[^}]+\}', r.text)
if flags:
    print(f"\n{'='*80}")
    print(f"FOUND FLAGS IN JS:")
    for flag in flags:
        print(f"  {flag}")
    print('='*80)

# Look for API endpoints or commands
print(f"\n[Looking for commands/endpoints]")
commands = re.findall(r'["\']([a-z_]+)["\']\s*:', r.text)
print(f"Possible commands: {set(commands)}")

# Get CSS file
print(f"\n[Fetching styles.css]")
r = requests.get(f"{BASE_URL}/styles.css", timeout=10)
print(f"Status: {r.status_code}")

print("\n" + "="*80)

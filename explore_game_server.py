#!/usr/bin/env python3
"""
Explore the game server to find the correct endpoint
"""
import requests

base_url = "http://chall-58a2fd6f.evt-207.glabs.ctf7.com"

print("="*80)
print("EXPLORING GAME SERVER")
print("="*80)

# Try common paths
paths = [
    "/",
    "/game",
    "/play",
    "/index.html",
    "/game.html",
    "/flag",
    "/api",
    "/api/game",
    "/api/play",
    "/start",
    "/challenge",
]

print(f"\n[Testing common paths]")
for path in paths:
    url = base_url + path
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✓ {path} - Status: {response.status_code} ({len(response.text)} bytes)")
            
            # Save if it has content
            if len(response.text) > 50:
                filename = f"game{path.replace('/', '_')}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  Saved to: {filename}")
                
                # Check for flags
                import re
                flags = re.findall(r'Kaal\{[^}]+\}', response.text, re.IGNORECASE)
                if flags:
                    print(f"\n{'='*80}")
                    print("✓✓✓ FOUND FLAG:")
                    print('='*80)
                    for flag in flags:
                        print(f"  {flag}")
                    print('='*80)
        elif response.status_code == 404:
            print(f"✗ {path} - 404 Not Found")
        else:
            print(f"  {path} - Status: {response.status_code}")
    except Exception as e:
        print(f"✗ {path} - Error: {e}")

print("\n" + "="*80)
print("\nNOTE: The challenge lab might need to be started first.")
print("Check if there's a 'Start Lab' button on the challenge page.")
print("="*80)

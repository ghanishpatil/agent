#!/usr/bin/env python3
"""Analyze the JavaScript and find the actual submission logic"""

import requests
import re
import json

base_url = "https://hate.breachpoint.live"

# Get the main page
resp = requests.get(base_url)
html = resp.text

print("="*60)
print("ANALYZING JAVASCRIPT")
print("="*60)

# Extract all script sources
script_srcs = re.findall(r'src="([^"]+\.js)"', html)
print(f"\nFound {len(script_srcs)} script sources:")
for src in script_srcs:
    print(f"  {src}")

# Look for the encoded string in JSON
json_matches = re.findall(r'"b":"([^"]+)"', html)
print(f"\nFound 'b' values in JSON:")
for match in json_matches:
    print(f"  {match}")

# Extract the Next.js data
nextjs_data = re.findall(r'self\.__next_f\.push\(\[1,"([^"]+)"\]\)', html)
print(f"\nFound {len(nextjs_data)} Next.js data pushes")

# Look for the specific data with our encoded string
for data in nextjs_data:
    if 'U0kcfdLN_WhDhNldOLdHJ' in data:
        print(f"\nFound data containing encoded string:")
        print(f"  {data[:500]}...")
        
        # Try to parse it
        try:
            # Unescape the string
            unescaped = data.replace('\\n', '\n').replace('\\', '')
            print(f"\n  Unescaped: {unescaped[:500]}...")
        except:
            pass

# Check if there's a form action
form_action = re.search(r'<form[^>]*action="([^"]*)"', html)
if form_action:
    print(f"\nForm action: {form_action.group(1)}")
else:
    print(f"\nNo form action found (client-side submission)")

# Look for input field name
input_name = re.search(r'<input[^>]*name="([^"]*)"', html)
if input_name:
    print(f"Input name: {input_name.group(1)}")
else:
    print(f"No input name found")

# The key insight: the encoded string is in the JSON as "b"
# This might be a key or token needed for submission
print("\n" + "="*60)
print("KEY FINDING")
print("="*60)
print(f"The encoded string 'U0kcfdLN_WhDhNldOLdHJ' appears as:")
print(f"  - HTML comment: <!--U0kcfdLN_WhDhNldOLdHJ-->")
print(f'  - JSON property: "b":"U0kcfdLN_WhDhNldOLdHJ"')
print(f"\nThis might be:")
print(f"  1. A session token/key")
print(f"  2. The answer to submit")
print(f"  3. A hint for decoding")
print(f"  4. Part of the flag itself")

# Decode base64
import base64
try:
    decoded = base64.b64decode("U0kcfdLN_WhDhNldOLdHJ")
    print(f"\nBase64 decoded (hex): {decoded.hex()}")
    print(f"Base64 decoded (bytes): {decoded}")
    
    # Try to interpret as ASCII
    ascii_chars = []
    for byte in decoded:
        if 32 <= byte <= 126:
            ascii_chars.append(chr(byte))
        else:
            ascii_chars.append(f"\\x{byte:02x}")
    print(f"As ASCII: {''.join(ascii_chars)}")
except Exception as e:
    print(f"Decode error: {e}")

# Check the placeholder text
placeholder = re.search(r'placeholder="([^"]+)"', html)
if placeholder:
    print(f"\nInput placeholder: {placeholder.group(1)}")
    print(f"  This is the clue: 'Give me a reason to exist.'")
    print(f"\nPossible answers:")
    print(f"  - hate")
    print(f"  - to hate")
    print(f"  - hatred")
    print(f"  - anger")
    print(f"  - destruction")
    print(f"  - chaos")
    print(f"  - nothing")
    print(f"  - no reason")
    print(f"  - you don't")
    print(f"  - U0kcfdLN_WhDhNldOLdHJ (the encoded string itself)")

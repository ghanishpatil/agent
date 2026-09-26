#!/usr/bin/env python3
"""Decode base64 strings found"""
import base64

strings = [
    "VGhpcyBHdXk6IA",
    "RmFpbGVkIHRvIEZ1Y2sg",
    "TUFOVUZBQ1RVUkVS",
    "RXJyb3I",
    "U0RL",
    "U3VjY2Vzc2Z1b",
    "RGV2aWNlIEluZm86",
    "TU9ERUw",
    "WpGqRn0",
]

print("="*80)
print("DECODING BASE64 STRINGS")
print("="*80)

for s in strings:
    try:
        decoded = base64.b64decode(s).decode('utf-8')
        print(f"{s} => {decoded}")
    except Exception as e:
        print(f"{s} => ERROR: {e}")

print("\n" + "="*80)

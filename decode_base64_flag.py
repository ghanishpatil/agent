#!/usr/bin/env python3
"""
Decode the base64 FLAG found in fc1 LSB
"""

import base64

# The base64 string from the HDWGT1 structure
flag_b64 = "S2FhbHsxZl9UaU1lX2M0bl9iM19jcjM0dEVkLF90aDNuX3M0cmNBc21fY0FuX2QzZkluZV9pdH0="

print(f"[*] Base64 string: {flag_b64}")
print(f"\n[*] Decoding...")

decoded = base64.b64decode(flag_b64).decode('utf-8')

print(f"\n[+] Decoded flag: {decoded}")

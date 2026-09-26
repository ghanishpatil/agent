#!/usr/bin/env python3
"""
Decode the HINT from the HDWGT1 structure
"""

import base64

# The hint base64
hint_b64 = "dXAgbmV4dCwgdGhlIGxpdHRsZSBiaXJkcyBjYXJyeSBvbmx5IGZyYWdtZW50czsgZWFjaCB3aGlzcGVyIHJlbWVtYmVycyBpdHMgcGxhY2U="

print(f"[*] Hint base64: {hint_b64}")
print(f"\n[*] Decoding...")

decoded = base64.b64decode(hint_b64).decode('utf-8')

print(f"\n[+] Decoded hint: {decoded}")

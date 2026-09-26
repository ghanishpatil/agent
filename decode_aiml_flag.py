#!/usr/bin/env python3
"""
Decode the base64 flag found in the HDWGT marker
"""

import base64

# The base64 string from the HDWGT marker
flag_b64 = "S2FhbHsxZl9UaU1lX2M0bl9iM19jcjM0dEVkLF90aDNuX3M0cmNBc21fY0FuX2QzZkluZV9pdH0="

# Decode
flag = base64.b64decode(flag_b64).decode('utf-8')

print(f"[+] Base64 decoded flag:")
print(f"[+] {flag}")

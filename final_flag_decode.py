#!/usr/bin/env python3
"""
Decode the final flag from /api/secret endpoint
"""

import base64

def decode_flag():
    """Decode the encoded flag"""
    print("[*] Decoding the flag from /api/secret")
    print("=" * 80)
    
    # The encoded flag from GET /api/secret with X-Access-Level: admin
    encoded_flag = "SFd7bWV0aG9kX3N3aXRjaF9tYXN0ZXJ9"
    
    print(f"Encoded flag: {encoded_flag}")
    
    # Decode from base64
    decoded = base64.b64decode(encoded_flag).decode('utf-8')
    
    print(f"\n🚩 DECODED FLAG: {decoded}")
    print("=" * 80)
    
    return decoded

def main():
    flag = decode_flag()
    
    print("\n[*] Challenge Solution Summary:")
    print("=" * 80)
    print("1. Found HTML comment hint: 'truth changes when method changes'")
    print("2. Discovered JavaScript calls different API endpoint: ctfchallange.onrender.com")
    print("3. POST /api/check returned base64 hint about 'deeper endpoint'")
    print("4. OPTIONS /api/check revealed X-Access-Level header requirement")
    print("5. GET /api/secret with X-Access-Level: admin returned encoded flag")
    print(f"6. Final flag: {flag}")

if __name__ == "__main__":
    main()
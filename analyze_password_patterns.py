#!/usr/bin/env python3

# Analyze how each password was hidden
password_methods = {
    "Case 2 (VOICE)": {
        "method": "Acrostic in article conclusion",
        "text": "Voluntary Opportunity In observing Civic Evidence",
        "password": "VOICE",
        "encoding": "First letters"
    },
    "Case 3 (CANNOT)": {
        "method": "Explicit at end",
        "text": "Pass: C ANNOT",
        "password": "CANNOT",
        "encoding": "Direct with space"
    },
    "Case 4 (SILENCE)": {
        "method": "Acrostic in article conclusion",
        "text": "Systems Intended Limit Expression Naturally, Creating Exceptions",
        "password": "SILENCE",
        "encoding": "First letters"
    },
    "Case 5 (BUT)": {
        "method": "Metadata Keywords",
        "text": "66 85 84",
        "password": "BUT",
        "encoding": "ASCII codes"
    },
    "Case 6 (SYSTEM)": {
        "method": "Base64 at end",
        "text": "U1lTVEVNCg==",
        "password": "SYSTEM",
        "encoding": "Base64"
    },
    "Case 7 (CAN)": {
        "method": "Hex-encoded URL",
        "text": "68747470733a2f2f...43414e5f4c6f676f2e737667",
        "password": "CAN",
        "encoding": "Hex to URL, filename"
    },
}

print("Password Discovery Pattern Analysis")
print("="*80)

for case, info in password_methods.items():
    print(f"\n{case}:")
    print(f"  Method: {info['method']}")
    print(f"  Encoding: {info['encoding']}")
    print(f"  Password: {info['password']}")

print("\n" + "="*80)
print("Pattern Observations:")
print("="*80)
print("1. Alternates between acrostic and encoded methods")
print("2. Uses: Acrostic, Direct, Acrostic, ASCII, Base64, Hex")
print("3. Increasing complexity: Simple -> Complex")
print("4. Final hint: 'LeetSpeak Unlocks' + '6 case password fragments are pass'")

print("\n" + "="*80)
print("Hypothesis for Final Password:")
print("="*80)
print("Given the pattern, the final password might:")
print("1. Combine all 6 passwords")
print("2. Use leetspeak transformation")
print("3. Follow a specific encoding pattern")
print()
print("The hint '6 case password fragments are pass' could mean:")
print("- The 6 passwords ARE the passphrase (combined)")
print("- 'pass' is part of the password")
print("- The passwords are 'fragments' that need assembly")
print()
print("'LeetSpeak Unlocks' suggests:")
print("- Apply leetspeak to the combined passwords")
print("- But WHICH leetspeak mapping?")

# Try to find a pattern in the leetspeak
print("\n" + "="*80)
print("Testing Specific Leetspeak Patterns:")
print("="*80)

import PyPDF2
from pathlib import Path
import base64

def try_pwd(pwd):
    try:
        with open("Cases/Flag_protected.pdf", 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                if reader.decrypt(pwd):
                    return True
    except:
        pass
    return False

# Maybe the leetspeak follows the SAME pattern as the encodings?
# ASCII -> numbers, Base64 -> letters+numbers, Hex -> hex digits

passwords = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]
combined = "".join(passwords)

# Try specific patterns based on the encoding methods used
attempts = [
    # Standard leetspeak
    combined.replace('A','4').replace('E','3').replace('I','1').replace('O','0').replace('S','5').replace('T','7'),
    
    # Hex-style (like Case 6)
    ''.join([hex(ord(c))[2:] for c in combined]),
    
    # ASCII-style (like Case 5)
    ''.join([str(ord(c)) for c in combined]),
    
    # Base64-style
    base64.b64encode(combined.encode()).decode(),
    
    # Maybe it's the REVERSE of one of the encoding methods?
    combined[::-1],
]

for pwd in attempts:
    if try_pwd(pwd):
        print(f"\nFOUND IT: {pwd}")
        break
    else:
        print(f"Tried: {pwd[:50]}...")

print("\nStill searching...")

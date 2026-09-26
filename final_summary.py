#!/usr/bin/env python3

# Summary of all passwords found
passwords = {
    1: None,  # Unprotected
    2: "VOICE",  # From acrostic: "Voluntary Opportunity In observing Civic Evidence"
    3: "CANNOT",  # From "Pass: C ANNOT" at end
    4: "SILENCE",  # From acrostic: "Systems Intended Limit Expression Naturally, Creating Exceptions"
    5: "BUT",  # From metadata Keywords: "66 85 84" (ASCII)
    6: "SYSTEM",  # From Base64: "U1lTVEVNCg=="
    7: "CAN",  # From hex URL: CAN_Logo.svg
}

print("Password Chain Summary:")
print("="*60)
for case, pwd in passwords.items():
    if pwd:
        print(f"Case {case}: {pwd}")

print("\n" + "="*60)
print("Combined Message:")
print("="*60)
message = " ".join([p for p in passwords.values() if p])
print(message)

print("\n" + "="*60)
print("Hint from Case 7:")
print("="*60)
print("'LeetSpeak Unlocks'")
print("'6 case password fragments are pass'")

print("\n" + "="*60)
print("Analysis:")
print("="*60)
print("The message reads: 'VOICE CANNOT SILENCE BUT SYSTEM CAN'")
print("This is a statement about press freedom and censorship.")
print()
print("The hint says '6 case password fragments are pass'")
print("Maybe 'pass' is literal? Or maybe we need to look at the passwords differently?")
print()
print("Let me try: pass + the passwords in some form...")

import PyPDF2
from pathlib import Path

pdf_path = Path("Cases/Flag_protected.pdf")

# Try variations with "pass"
attempts = [
    "passVOICECANNOTSILENCEBUTSYSTEMCAN",
    "PASSvoicecannotsilencebutsystemcan",
    "pass_voice_cannot_silence_but_system_can",
    "PASS",
    "pass",
    "P455",  # pass in leetspeak
    "p455",
]

print("\nTrying 'pass' variations:")
for pwd in attempts:
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.decrypt(pwd):
                print(f"SUCCESS: {pwd}")
                break
    except:
        pass
    print(f"Failed: {pwd}")

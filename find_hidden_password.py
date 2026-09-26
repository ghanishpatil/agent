#!/usr/bin/env python3
"""
Search for hidden password hints in all case files
"""

import PyPDF2
import os

cases_dir = "Cases"
passwords = {
    1: None,
    2: "ArvindRao",
    3: "CANNOT",
    4: "SILENCE",
    5: "BUT",
    6: "SYSTEM",
    7: "CAN"
}

print("="*80)
print("SEARCHING FOR HIDDEN PASSWORD HINTS")
print("="*80)

# Check all case files for any mention of "flag" or "password"
for case_num in range(1, 8):
    if case_num == 1:
        pdf_path = os.path.join(cases_dir, "Case - 1.pdf")
    else:
        pdf_path = os.path.join(cases_dir, f"Case - {case_num}_protected.pdf")
    
    print(f"\n{'='*80}")
    print(f"CASE {case_num}")
    print("="*80)
    
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Decrypt if needed
            if reader.is_encrypted and passwords[case_num]:
                reader.decrypt(passwords[case_num])
            
            # Extract all text
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text()
            
            # Search for keywords
            keywords = ["flag", "FLAG", "password", "PASSWORD", "Pass:", "unlock", "key", "hint"]
            
            for keyword in keywords:
                if keyword.lower() in full_text.lower():
                    # Find context around keyword
                    idx = full_text.lower().find(keyword.lower())
                    start = max(0, idx - 50)
                    end = min(len(full_text), idx + 100)
                    context = full_text[start:end]
                    print(f"\n🔍 Found '{keyword}':")
                    print(f"   ...{context}...")
            
            # Check metadata
            if reader.metadata:
                print(f"\n📋 Metadata:")
                for key, value in reader.metadata.items():
                    print(f"   {key}: {value}")
                    # Check if metadata contains hints
                    if value and any(k in str(value).lower() for k in ["flag", "password", "hint"]):
                        print(f"   ⚠️  POSSIBLE HINT IN METADATA!")
    
    except Exception as e:
        print(f"Error: {e}")

# Check Flag PDF metadata (without opening)
print(f"\n{'='*80}")
print("FLAG PDF - METADATA CHECK (WITHOUT PASSWORD)")
print("="*80)

try:
    with open(os.path.join(cases_dir, "Flag_protected.pdf"), 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        
        print(f"Encrypted: {reader.is_encrypted}")
        
        # Try to get metadata without decrypting
        if reader.metadata:
            print("\n📋 Metadata (may be encrypted):")
            for key, value in reader.metadata.items():
                print(f"   {key}: {value}")
        else:
            print("No accessible metadata without password")
            
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
print("ANALYZING THE HINTS:")
print("="*80)

print("""
From Case 7:
- "LeetSpeak Unlocks"
- "6 case password fragments are pass"

The 6 fragments: VOICE, CANNOT, SILENCE, BUT, SYSTEM, CAN
Combined message: "VOICE CANNOT SILENCE BUT SYSTEM CAN"

Possible interpretations:
1. Apply leetspeak to the combined message
2. The word "pass" is part of the password
3. The fragments need to be rearranged
4. There's a specific leetspeak pattern we haven't tried

Let me try some NEW patterns based on "pass" hint...
""")

import pikepdf

new_attempts = [
    # "pass" as part of password
    "passVOICECANNOTSILENCEBUTSYSTEMCAN",
    "VOICECANNOTSILENCEBUTSYSTEMCANpass",
    "PASSVOICECANNOTSILENCEBUTSYSTEMCAN",
    "VOICECANNOTSILENCEBUTSYSTEMCANPASS",
    
    # "pass" between words
    "VOICEpassCANNOTpassSILENCEpassBUTpassSYSTEMpassCAN",
    "VOICE-pass-CANNOT-pass-SILENCE-pass-BUT-pass-SYSTEM-pass-CAN",
    
    # Fragments ARE pass (interpret differently)
    "VCSBSC",  # First letters
    "ETTETN",  # Last letters
    "567363",  # Word lengths
    
    # Leetspeak with "pass"
    "p455V01C3C4NN075113NC38U75Y573MC4N",
    "V01C3C4NN075113NC38U75Y573MC4Np455",
    
    # All lowercase with pass
    "passvoicecannotsilencebutsystemcan",
    "voicecannotsilencebutsystemcanpass",
]

print("\nTrying NEW password patterns with 'pass' hint...")
pdf_path = os.path.join(cases_dir, "Flag_protected.pdf")

for pwd in new_attempts:
    try:
        with pikepdf.open(pdf_path, password=pwd) as pdf:
            print(f"\n{'='*80}")
            print(f"🎉 SUCCESS! PASSWORD FOUND: {pwd}")
            print("="*80)
            
            for page in pdf.pages:
                print(page.extract_text())
            
            exit(0)
    except:
        pass

print("\nNo new patterns worked either.")
print("\nThe password might be:")
print("1. A very specific leetspeak variation")
print("2. Something completely different from the fragments")
print("3. Requires hashcat/john to brute force")

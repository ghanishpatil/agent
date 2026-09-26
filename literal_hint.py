#!/usr/bin/env python3
import pikepdf
import re

# The hint says: "6 case password fragments are pass"
# What if we interpret this LITERALLY?

passwords = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

wordlist = [
    # Literal interpretation: "6 case password fragments are pass"
    "6casepasswordfragmentsarepass",
    "6 case password fragments are pass",
    "6_case_password_fragments_are_pass",
    "6-case-password-fragments-are-pass",
    
    # The fragments ARE "pass"
    "pass",
    "PASS",
    "Pass",
    
    # 6 fragments
    "passpasspasspasspasspass",
    "PASSPASSPASSPASSPASSPASS",
    
    # Fragments = passwords
    "fragments",
    "Fragments",
    "FRAGMENTS",
    
    # "are pass" = "arepass"
    "arepass",
    "arePass",
    "ArePass",
    "AREPASS",
    
    # Maybe it's telling us the passwords ARE the pass(word)
    "VOICECANNOTSILENCEBUTSYSTEMCAN",
    "voicecannotsilencebutsystemcan",
    
    # Or maybe "pass" means "password"
    "password",
    "Password",
    "PASSWORD",
    
    # 6 case = Case 6 password = SYSTEM
    "SYSTEM",
    "system",
    "System",
    
    # All 6 passwords
    "VOICECANNOTSILENCEBUTSYSTEMCAN",
    "Voice Cannot Silence But System Can",
    
    # LeetSpeak hint: "Unlo cks" - unlock with space?
    "Unlo cks",
    "unlo cks",
    "UNLO CKS",
    
    # Maybe the space pattern matters
    "VOICE CANNOT SILENCE BUT SYSTEM CAN",
    "voice cannot silence but system can",
    
    # Double space pattern from hint
    "VOICE  CANNOT  SILENCE  BUT  SYSTEM  CAN",
    
    # What if "LeetSpeak Unlocks" is the password?
    "LeetSpeak Unlocks",
    "leetspeak unlocks",
    "LEETSPEAK UNLOCKS",
    "LeetSpeakUnlocks",
    "leetspeakunlocks",
    "LEETSPEAKUNLOCKS",
    
    # Leetspeak version
    "1337Sp34k Un10(k5",
    "133753p34kUn10(k5",
    
    # Maybe it's about the CASE numbers
    "234567",  # Cases 2-7
    "1234567",  # All cases
    
    # Or the pattern of 13 days
    "13",
    "thirteen",
    "Thirteen",
    "THIRTEEN",
]

print("Trying literal interpretations of the hints...")
print("="*80)

for pwd in wordlist:
    print(f"Trying: {pwd}")
    try:
        with pikepdf.open("Cases/Flag_protected.pdf", password=pwd) as pdf:
            print(f"\n{'='*80}")
            print(f"*** PASSWORD FOUND: {pwd} ***")
            print(f"{'='*80}\n")
            
            text = ""
            for page in pdf.pages:
                t = page.extract_text()
                text += t
                print(t)
                print("-"*80)
            
            flags = re.findall(r'BPCTF\{[^}]+\}', text)
            if flags:
                print("\n" + "="*80)
                print("*** THE FLAG ***")
                print("="*80)
                print(flags[0])
                print("="*80)
            exit(0)
    except:
        pass

print("\nLiteral interpretations didn't work either.")
print("\nLet me try one more thing - what if it's ROT13 or Caesar cipher?")

def rot13(text):
    result = ""
    for char in text:
        if 'a' <= char <= 'z':
            result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
        elif 'A' <= char <= 'Z':
            result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
        else:
            result += char
    return result

combined = "VOICECANNOTSILENCEBUTSYSTEMCAN"
rot13_pwd = rot13(combined)
print(f"\nROT13: {rot13_pwd}")

if try_decrypt("Cases/Flag_protected.pdf", rot13_pwd):
    print("FOUND WITH ROT13!")
    exit(0)

print("ROT13 didn't work either.")

#!/usr/bin/env python3
import PyPDF2
from pathlib import Path

def try_password(pdf_path, password):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                result = reader.decrypt(password)
                if result:
                    return True
    except:
        pass
    return False

pdf_path = Path("Cases/Flag_protected.pdf")

# The message is: "VOICE CANNOT SILENCE BUT SYSTEM CAN"
# Try different interpretations

passwords = [
    # Maybe just the initials?
    "VCSBS C",
    "VCSBSC",
    
    # Or first letters of each word
    "V C S B S C",
    
    # Maybe it's about the pattern - all caps, leetspeak
    "V01C3C4NN0751L3NC3BU75Y573MC4N",
    "v01c3c4nn0751l3nc3bu75y573mc4n",
    
    # Try with underscores
    "VOICE_CANNOT_SILENCE_BUT_SYSTEM_CAN",
    "V01C3_C4NN07_51L3NC3_BU7_5Y573M_C4N",
    
    # Try with dashes
    "VOICE-CANNOT-SILENCE-BUT-SYSTEM-CAN",
    
    # Maybe it's the opposite message?
    "SYSTEMCANSILENCE",
    "5Y573MC4N51L3NC3",
    
    # Or maybe just the key words
    "VOICESILENCESYSTEM",
    "V01C351L3NC35Y573M",
    
    # Try the full sentence as one word, different cases
    "voicecannotsilencebutsystemcan",
    "VoiceCannotSilenceButSystemCan",
    "VOICECANNOTSILENCEBUTSYSTEMCAN",
    
    # Leetspeak variations
    "V0!C3C4NN0751L3NC3BU75Y573MC4N",
    "v0!c3c4nn0751l3nc3bu75y573mc4n",
    
    # Maybe numbers for letters
    "V01C3 C4NN07 51L3NC3 BU7 5Y573M C4N",
    "v01c3 c4nn07 51l3nc3 bu7 5y573m c4n",
    
    # Try removing spaces from leetspeak
    "V01C3C4NN0751L3NC3BU75Y573MC4N",
    
    # Maybe it's simpler - just the phrase
    "Voice Cannot Silence But System Can",
    "voice cannot silence but system can",
]

print("Trying passwords for Flag file...")
print("="*60)

for pwd in passwords:
    if try_password(pdf_path, pwd):
        print(f"\nSUCCESS! Password is: {pwd}")
        
        # Extract the flag
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            reader.decrypt(pwd)
            
            print("\n" + "="*80)
            print("FLAG FILE CONTENT:")
            print("="*80)
            
            for page_num, page in enumerate(reader.pages):
                print(f"\nPAGE {page_num + 1}:")
                try:
                    text = page.extract_text()
                    print(text)
                except Exception as e:
                    print(f"Error: {e}")
        break
    else:
        print(f"Failed: {pwd}")
else:
    print("\nNone of these worked either...")

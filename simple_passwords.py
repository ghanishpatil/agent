#!/usr/bin/env python3
import PyPDF2
from pathlib import Path
import re

def try_decrypt(pdf_path, password):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                if reader.decrypt(password):
                    return reader
    except:
        pass
    return None

pdf_path = Path("Cases/Flag_protected.pdf")

# Maybe it's REALLY simple
simple_attempts = [
    # Just the message
    "VoiceCannotSilenceButSystemCan",
    "voicecannotsilencebutsystemcan", 
    "VOICECANNOTSILENCEBUTSYSTEMCAN",
    
    # With common separators
    "voice_cannot_silence_but_system_can",
    "VOICE_CANNOT_SILENCE_BUT_SYSTEM_CAN",
    "Voice_Cannot_Silence_But_System_Can",
    
    # Hyphenated
    "voice-cannot-silence-but-system-can",
    "VOICE-CANNOT-SILENCE-BUT-SYSTEM-CAN",
    "Voice-Cannot-Silence-But-System-Can",
    
    # Spaces
    "voice cannot silence but system can",
    "VOICE CANNOT SILENCE BUT SYSTEM CAN",
    "Voice Cannot Silence But System Can",
    
    # Maybe it's about the INDEX?
    "BleedingPressIndex",
    "bleeding_press_index",
    "BLEEDING_PRESS_INDEX",
    "TheBleedingPressIndex",
    "the_bleeding_press_index",
    
    # Or just simple words
    "bleedingpress",
    "BleedingPress",
    "BLEEDINGPRESS",
    
    # The challenge name
    "TheBleedingPress",
    "the bleeding press",
    "THE BLEEDING PRESS",
]

print(f"Trying {len(simple_attempts)} simple passwords...")

for pwd in simple_attempts:
    reader = try_decrypt(pdf_path, pwd)
    if reader:
        print(f"\n*** FOUND IT: {pwd} ***\n")
        
        for page in reader.pages:
            text = page.extract_text()
            print(text)
            
            flags = re.findall(r'BPCTF\{[^}]+\}', text)
            if flags:
                print("\n" + "="*80)
                print("FLAG:")
                for flag in flags:
                    print(flag)
        exit(0)
    print(f"No: {pwd}")

print("\nNone of the simple ones worked either.")

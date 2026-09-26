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
                    print(f"SUCCESS! Password: {password}")
                    for page_num, page in enumerate(reader.pages):
                        print(f"\n{'='*80}")
                        print(f"PAGE {page_num + 1}")
                        print(f"{'='*80}\n")
                        try:
                            text = page.extract_text()
                            print(text)
                        except Exception as e:
                            print(f"Error: {e}")
                    return True
    except Exception as e:
        print(f"Error with {password}: {e}")
    return False

pdf_path = Path("Cases/Flag_protected.pdf")

# Combine the 6 passwords
base_password = "VOICECANNOTSILENCEBUTSYSTEMCAN"

# Try various leetspeak conversions
def to_leetspeak(text):
    """Convert text to leetspeak"""
    leet_map = {
        'A': '4', 'E': '3', 'I': '1', 'O': '0', 'S': '5', 'T': '7',
        'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'
    }
    result = ""
    for char in text:
        result += leet_map.get(char, char)
    return result

passwords = [
    base_password,
    to_leetspeak(base_password),
    base_password.lower(),
    to_leetspeak(base_password.lower()),
    
    # Try with spaces
    "VOICE CANNOT SILENCE BUT SYSTEM CAN",
    to_leetspeak("VOICE CANNOT SILENCE BUT SYSTEM CAN"),
    
    # Try as a sentence
    "VoiceCannotSilenceButSystemCan",
    to_leetspeak("VoiceCannotSilenceButSystemCan"),
]

print("Trying passwords for Flag file...")
print("="*60)

for pwd in passwords:
    print(f"Trying: {pwd}")
    if try_password(pdf_path, pwd):
        break
else:
    print("\nNone worked. Let me try more variations...")

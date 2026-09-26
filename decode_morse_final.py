#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

# Morse code dictionary
MORSE_CODE = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '/': ' '
}

def decode_morse(morse_code):
    words = morse_code.split(' / ')
    decoded = []
    for word in words:
        letters = word.split()
        decoded_word = ''.join([MORSE_CODE.get(letter, '?') for letter in letters])
        decoded.append(decoded_word)
    return ' '.join(decoded)

print("="*80)
print("CARTOON NETWORK CTF - FINAL SOLUTION")
print("="*80)

base_url = "https://joyful-mandazi-1c2213.netlify.app"

# Page 2 morse code
morse1 = ".--. .-.. . .- ... ."
morse2 = ".... . .-.. .--."

print(f"\n[MORSE CODE 1]: {morse1}")
decoded1 = decode_morse(morse1)
print(f"Decoded: {decoded1}")

print(f"\n[MORSE CODE 2]: {morse2}")
decoded2 = decode_morse(morse2)
print(f"Decoded: {decoded2}")

combined = f"{decoded1} {decoded2}"
print(f"\n[COMBINED]: {combined}")

# Try as URL
url_path = combined.lower().replace(' ', '')
next_url = f"{base_url}/{url_path}"
print(f"\n[TRYING URL]: {next_url}")

response = requests.get(next_url)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("\n[PAGE CONTENT]")
    print(response.text[:2000])
    
    # Look for flag
    flags = re.findall(r'(flag\{[^}]+\}|FLAG\{[^}]+\}|CTF\{[^}]+\})', response.text, re.IGNORECASE)
    if flags:
        print("\n" + "="*80)
        print("FLAG FOUND:")
        print("="*80)
        for flag in flags:
            print(f"  {flag}")
else:
    # Try other variations
    variations = [
        combined.lower(),
        combined.upper(),
        combined.replace(' ', '-'),
        combined.replace(' ', '_'),
        decoded1.lower(),
        decoded2.lower(),
        f"{decoded1.lower()}/{decoded2.lower()}",
        f"{decoded1.lower()}-{decoded2.lower()}",
    ]
    
    print("\n[TRYING VARIATIONS]")
    for var in variations:
        url = f"{base_url}/{var}"
        resp = requests.get(url)
        if resp.status_code == 200:
            print(f"\n✓ SUCCESS: {url}")
            print(resp.text[:1000])
            
            flags = re.findall(r'(flag\{[^}]+\}|FLAG\{[^}]+\}|CTF\{[^}]+\})', resp.text, re.IGNORECASE)
            if flags:
                print("\n" + "="*80)
                print("FLAG FOUND:")
                print("="*80)
                for flag in flags:
                    print(f"  {flag}")
                break

print("\n" + "="*80)

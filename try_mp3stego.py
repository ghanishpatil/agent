#!/usr/bin/env python3
"""
Try MP3Stego and other MP3-specific steganography methods
"""

import subprocess
import os
import re

mp3_file = "chall_media/chall_media.mp3"

print("[*] Trying MP3-specific steganography tools...")

# Try mp3stego (if available)
print("\n[1] Trying MP3Stego...")
passwords = ['', 'bheem', 'laddoo', 'kalia', 'password', 'chhota', 'dholakpur', 'tuntun']

for pwd in passwords:
    try:
        result = subprocess.run(
            ['mp3stego-decode', mp3_file, '-P', pwd, '-X'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 or 'extracted' in result.stdout.lower():
            print(f"[+] Success with password: '{pwd}'")
            print(result.stdout)
    except FileNotFoundError:
        if pwd == '':
            print("[-] mp3stego not installed")
        break
    except Exception as e:
        pass

# Try steghide on the original MP3
print("\n[2] Trying steghide on MP3...")
for pwd in passwords:
    try:
        output_file = f'steghide_mp3_{pwd}.txt'
        result = subprocess.run(
            ['steghide', 'extract', '-sf', mp3_file, '-p', pwd, '-xf', output_file, '-f'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"[+] steghide success with password: '{pwd}'")
            if os.path.exists(output_file):
                with open(output_file, 'rb') as f:
                    extracted = f.read()
                print(f"    Extracted: {extracted}")
                
                flag_match = re.search(rb'Kaal\{[^}]+\}', extracted)
                if flag_match:
                    print(f"\n[+] *** REAL FLAG ***: {flag_match.group().decode('utf-8', errors='ignore')}")
                    break
    except FileNotFoundError:
        if pwd == '':
            print("[-] steghide not installed")
        break
    except Exception as e:
        pass

# Manual check - maybe the flag is just ROT13 or Caesar cipher of the fake flag
print("\n[3] Trying cipher transformations on fake flag...")

fake_content = "1_th1nk_th15_15_wr0ng"

# ROT13
import codecs
rot13 = codecs.encode(fake_content, 'rot_13')
print(f"    ROT13: Kaal{{{rot13}}}")

# Caesar cipher (all shifts)
print("\n    Caesar cipher shifts:")
for shift in range(1, 26):
    shifted = ""
    for char in fake_content:
        if char.isalpha():
            if char.islower():
                shifted += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            else:
                shifted += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
        else:
            shifted += char
    if 'right' in shifted or 'correct' in shifted or 'true' in shifted:
        print(f"        Shift {shift}: Kaal{{{shifted}}}")

# Atbash cipher (reverse alphabet)
def atbash(text):
    result = ""
    for char in text:
        if char.isalpha():
            if char.islower():
                result += chr(ord('z') - (ord(char) - ord('a')))
            else:
                result += chr(ord('Z') - (ord(char) - ord('A')))
        else:
            result += char
    return result

atbash_result = atbash(fake_content)
print(f"\n    Atbash: Kaal{{{atbash_result}}}")

# Maybe the answer is simpler - just replace "wrong" with "right"
simple_replace = fake_content.replace("wr0ng", "r1ght")
print(f"\n    Simple replace: Kaal{{{simple_replace}}}")

# Or maybe it's about the transmission being "garbled"
# Ungarble = reverse?
reversed_content = fake_content[::-1]
print(f"    Reversed: Kaal{{{reversed_content}}}")

print("\n[*] Analysis complete!")
print("\n[*] CANDIDATES TO TRY:")
print(f"    1. Kaal{{{simple_replace}}}")
print(f"    2. Kaal{{i_know_this_is_right}}")
print(f"    3. Kaal{{1_kn0w_th15_15_r1ght}}")

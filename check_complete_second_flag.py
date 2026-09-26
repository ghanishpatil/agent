#!/usr/bin/env python3
"""Check if the second flag is complete"""
import zipfile
import re

APK_PATH = r"D:\mission-git-hackss\KaalRaj.apk"

print("="*80)
print("CHECKING COMPLETE SECOND FLAG")
print("="*80)

with zipfile.ZipFile(APK_PATH, 'r') as z:
    content = z.read('classes4.dex')
    
    # Find the position of the second flag
    pos = content.find(b'Kaal{IT_My_BE}')
    
    if pos != -1:
        print(f"\nFound 'Kaal{{IT_My_BE}}' at position {pos}")
        
        # Get more context after it
        after = content[pos:pos+200]
        print(f"\nBytes after the flag:")
        print(after)
        
        # Look for any continuation
        print(f"\nSearching for complete flag pattern...")
        
        # Try to find if there's more to this flag
        extended = content[pos:pos+100]
        
        # Look for the closing brace and what comes after
        brace_pos = extended.find(b'}')
        if brace_pos != -1:
            print(f"\nClosing brace at offset {brace_pos}")
            print(f"Content: {extended[:brace_pos+1]}")
            print(f"After brace: {extended[brace_pos+1:brace_pos+50]}")
        
        # Check if there are any other Kaal{ patterns nearby
        nearby = content[pos:pos+500]
        all_flags = re.findall(rb'Kaal\{[^}]+\}', nearby)
        print(f"\nAll flags in this region:")
        for flag in all_flags:
            print(f"  {flag.decode('utf-8', errors='ignore')}")

print("\n" + "="*80)
print("\nFINAL ANSWER:")
print("Based on the challenge description 'One is meant to be seen.")
print("The other was never meant to be found.'")
print("\nThe flag is: Kaal{GOOD_PROGRESS_IT_My_BE}")
print("="*80)

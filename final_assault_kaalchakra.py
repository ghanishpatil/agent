#!/usr/bin/env python3
"""
Final assault - transcribe grid from screenshot and find real collisions
"""

import requests
import hashlib
import re

TARGET_URL = "http://138.199.163.92:12871/"

def transcribe_grid_from_screenshot():
    """
    Based on the screenshot you provided, transcribe the visible grid
    The grid appears to show a table with letters
    """
    print("="*60)
    print("Grid Transcription from Screenshot")
    print("="*60)
    
    # From your screenshot, I can see a grid/table
    # It appears to have:
    # - Column headers with letters/numbers
    # - Row headers with numbers
    # - Cells containing single letters
    
    # The visible pattern from the screenshot (approximate):
    # Let me try to read what I can see...
    
    # The grid looks like it might spell something when read in order
    # or it's a cipher table for decoding coordinates
    
    # Based on the screenshot, let me try to extract the visible letters:
    # Row 1: appears to show letters across the top
    # The cells seem to contain: A, R, Y, O, M, etc.
    
    # Let me construct what I can see:
    grid = [
        # This is my best guess from the screenshot
        ['?', 'E', 'A', 'U', 'I', 'D', 'H', 'O', 'N', '?'],
        ['?', 'I', 'S', 'O', 'A', 'R', 'Y', '?', 'O', '?'],
        ['?', 'B', 'T', 'S', 'W', 'I', 'T', 'C', 'M', '?'],
        ['?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
        ['?', '?', 'P', 'U', 'M', 'P', 'K', 'I', 'N', '?'],
        ['?', 'R', 'S', 'O', 'Z', 'M', 'R', 'T', '?', '?'],
        ['?', '?', '?', '?', '?', '?', '?', '?', '?', '?'],
        ['?', '?', 'G', 'H', 'Q', 'S', 'T', '?', '?', '?'],
        ['?', 'I', '?', '?', '?', '?', '?', 'R', 'Q', '?'],
        ['?', 'A', 'U', 'N', 'I', 'E', 'D', '?', '?', '?'],
    ]
    
    print("\n[*] Transcribed grid (partial, ? = unclear):")
    for i, row in enumerate(grid):
        print(f"Row {i}: {' '.join(row)}")
    
    # Try to find patterns or read the flag
    # Maybe reading certain coordinates spells the flag?
    
    # Or maybe the grid itself contains the flag when read in a specific pattern
    
    # Let's try reading diagonals, rows, columns, etc.
    print("\n[*] Trying different reading patterns...")
    
    # Read all non-? characters
    all_letters = []
    for row in grid:
        for cell in row:
            if cell != '?':
                all_letters.append(cell)
    
    combined = ''.join(all_letters)
    print(f"\n[*] All letters: {combined}")
    
    # Check if flag is in there
    if 'KAAL' in combined.upper():
        print("[!!!] Found 'KAAL' in grid!")
    
    return grid

def download_working_md5_collisions():
    """
    Try to download actual working MD5 collision files
    """
    print("\n" + "="*60)
    print("Downloading Working MD5 Collisions")
    print("="*60)
    
    # Try Marc Stevens' collision files
    # These are the actual collision blocks that work
    
    # Let's create files using the exact collision blocks from research
    # These blocks are known to produce MD5 collisions
    
    # Collision pair from "Chosen-prefix collisions for MD5"
    prefix = b""  # Empty prefix
    
    # These are the actual working collision blocks
    block_a = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70"
    )
    
    block_b = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b"
        "d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70"
    )
    
    file_a = prefix + block_a
    file_b = prefix + block_b
    
    with open('md5_coll_a.bin', 'wb') as f:
        f.write(file_a)
    
    with open('md5_coll_b.bin', 'wb') as f:
        f.write(file_b)
    
    hash_a = hashlib.md5(file_a).hexdigest()
    hash_b = hashlib.md5(file_b).hexdigest()
    
    print(f"[+] File A MD5: {hash_a}")
    print(f"[+] File B MD5: {hash_b}")
    print(f"[+] Match: {hash_a == hash_b}")
    
    if hash_a == hash_b:
        print("\n[!!!] COLLISION SUCCESSFUL!")
        return 'md5_coll_a.bin', 'md5_coll_b.bin'
    
    return None, None

def upload_and_get_flag(file_a, file_b):
    """Upload collision files and get flag"""
    if not file_a or not file_b:
        return None
    
    print("\n" + "="*60)
    print("Uploading Collision Files")
    print("="*60)
    
    session = requests.Session()
    
    # Upload file A
    print(f"\n[*] Uploading {file_a}...")
    with open(file_a, 'rb') as f:
        resp_a = session.post(TARGET_URL + 'collision', files={'image': f})
    
    print(f"[+] Response A: {resp_a.text}")
    
    # Upload file B
    print(f"\n[*] Uploading {file_b}...")
    with open(file_b, 'rb') as f:
        resp_b = session.post(TARGET_URL + 'collision', files={'image': f})
    
    print(f"[+] Response B: {resp_b.text}")
    
    # Check both responses for flag
    for resp in [resp_a, resp_b]:
        if 'kaal{' in resp.text.lower():
            flag = re.search(r'Kaal\{[^}]+\}', resp.text, re.IGNORECASE)
            if flag:
                print(f"\n[!!!] FLAG FOUND: {flag.group(0)}")
                return flag.group(0)
    
    return None

def main():
    print("FINAL ASSAULT ON KAALCHAKRA")
    print()
    
    # Step 1: Transcribe grid
    grid = transcribe_grid_from_screenshot()
    
    # Step 2: Try MD5 collisions
    file_a, file_b = download_working_md5_collisions()
    
    if file_a and file_b:
        flag = upload_and_get_flag(file_a, file_b)
        
        if flag:
            print(f"\n{'='*60}")
            print(f"SUCCESS! FLAG: {flag}")
            print(f"{'='*60}")
            return
    
    print("\n" + "="*60)
    print("Status:")
    print("="*60)
    print("- Grid partially transcribed")
    print("- MD5 collision blocks tested")
    print("- Need either:")
    print("  1. Working MD5 collision tool (fastcoll)")
    print("  2. Complete grid transcription to decode flag")
    print("  3. Or the flag is revealed after successful collision upload")

if __name__ == "__main__":
    main()

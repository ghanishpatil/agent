#!/usr/bin/env python3
"""
Extract all strings from the file and look for patterns
"""

def extract_strings(filename, min_length=4):
    with open(filename, 'rb') as f:
        data = f.read()
    
    strings = []
    current = []
    
    for byte in data:
        if 32 <= byte < 127:  # Printable ASCII
            current.append(chr(byte))
        else:
            if len(current) >= min_length:
                strings.append(''.join(current))
            current = []
    
    if len(current) >= min_length:
        strings.append(''.join(current))
    
    return strings

def main():
    strings = extract_strings(r'D:\mission-git-hackss\flight_record.dat', min_length=4)
    
    print(f"Total strings found: {len(strings)}\n")
    
    # Look for interesting strings
    print("=== Strings containing 'flag', 'kaal', 'key', 'pass' ===")
    for s in strings:
        lower = s.lower()
        if any(word in lower for word in ['flag', 'kaal', 'key', 'pass', 'secret', 'ctf']):
            print(f"  {s}")
    
    # Look for long strings (might be base64 or encoded data)
    print("\n=== Long strings (>30 chars) ===")
    long_strings = [s for s in strings if len(s) > 30]
    for s in long_strings[:20]:
        print(f"  {s}")
    
    # Look for strings with special patterns
    print("\n=== Strings with curly braces ===")
    for s in strings:
        if '{' in s or '}' in s:
            print(f"  {s}")
    
    # Print all unique strings
    print(f"\n=== All unique strings (first 200) ===")
    unique = list(set(strings))
    unique.sort(key=len, reverse=True)
    for s in unique[:200]:
        print(f"  {s}")

if __name__ == '__main__':
    main()

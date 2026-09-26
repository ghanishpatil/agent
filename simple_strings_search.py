with open(r"D:\mission-git-hackss\chall (1).wav", 'rb') as f:
    data = f.read()

# Simple string search
text = data.decode('latin-1')

# Search for Kaal{ with any characters after
import re
matches = re.findall(r'Kaal\{[^}]*\}', text)
if matches:
    for match in matches:
        print(f"FOUND FLAG: {match}")
else:
    # Try case insensitive
    matches = re.findall(r'[Kk][Aa][Aa][Ll]\{[^}]*\}', text, re.IGNORECASE)
    if matches:
        for match in matches:
            print(f"FOUND FLAG: {match}")
    else:
        # Just search for "Kaal"
        if 'Kaal' in text:
            pos = text.find('Kaal')
            print(f"Found 'Kaal' at position {pos}")
            print(f"Context: {text[pos:pos+100]}")
        else:
            print("No 'Kaal' found")
            # Try reversed
            if 'laaK' in text:
                pos = text.find('laaK')
                print(f"Found 'laaK' (reversed) at position {pos}")
                print(f"Context: {text[pos:pos+100]}")

#!/usr/bin/env python3
"""
Find where the troll flag is in the raw file and analyze context
"""

# Read raw file
with open("challenge_final (2).onnx", 'rb') as f:
    raw_data = f.read()

# Find the troll flag
troll_flag = b'Kaal{surface_flag_string_search_will_not_solve_this}'

offset = raw_data.find(troll_flag)
if offset >= 0:
    print(f"[*] Troll flag found at offset: {offset} (0x{offset:x})")
    
    # Show 200 bytes before and after
    start = max(0, offset - 200)
    end = min(len(raw_data), offset + len(troll_flag) + 200)
    
    context = raw_data[start:end]
    
    print(f"\n[*] Context (hex):")
    for i in range(0, len(context), 16):
        hex_part = ' '.join(f'{b:02x}' for b in context[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context[i:i+16])
        print(f"  {start+i:08x}: {hex_part:<48} {ascii_part}")
    
    # Check if there's another flag nearby
    print(f"\n[*] Searching for other text near troll flag...")
    
    # Look for any other Kaal{ within 1000 bytes
    search_start = max(0, offset - 1000)
    search_end = min(len(raw_data), offset + 1000)
    search_section = raw_data[search_start:search_end]
    
    import re
    all_kaal = [m.start() + search_start for m in re.finditer(rb'Kaal\{', raw_data[search_start:search_end])]
    
    print(f"[*] Found {len(all_kaal)} 'Kaal{{' occurrences near troll flag:")
    for pos in all_kaal:
        flag_section = raw_data[pos:pos+100]
        try:
            flag_str = flag_section.decode('utf-8', errors='ignore')
            print(f"  At 0x{pos:x}: {flag_str[:80]}")
        except:
            pass

else:
    print("[-] Troll flag not found")

print("\n[*] Done")

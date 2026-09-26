#!/usr/bin/env python3
"""
Disassemble the decode functions to understand the algorithm
"""
from capstone import *
import struct

# Read binary
with open('game/game.exe', 'rb') as f:
    data = f.read()

print("="*60)
print("DISASSEMBLING DECODE FUNCTIONS")
print("="*60)

# Find the code section
# PE header at offset from 0x3C
pe_offset = struct.unpack('<I', data[0x3C:0x40])[0]
print(f"\nPE header at: 0x{pe_offset:x}")

# Number of sections at PE + 0x6
num_sections = struct.unpack('<H', data[pe_offset+0x6:pe_offset+0x8])[0]
print(f"Number of sections: {num_sections}")

# Section table starts at PE + 0xF8 (for PE32+)
section_table_offset = pe_offset + 0xF8

# Find .text section
for i in range(num_sections):
    section_offset = section_table_offset + (i * 40)
    section_name = data[section_offset:section_offset+8].rstrip(b'\x00')
    virtual_size = struct.unpack('<I', data[section_offset+8:section_offset+12])[0]
    virtual_addr = struct.unpack('<I', data[section_offset+12:section_offset+16])[0]
    raw_size = struct.unpack('<I', data[section_offset+16:section_offset+20])[0]
    raw_offset = struct.unpack('<I', data[section_offset+20:section_offset+24])[0]
    
    if section_name == b'.text':
        print(f"\n.text section:")
        print(f"  Virtual address: 0x{virtual_addr:x}")
        print(f"  Raw offset: 0x{raw_offset:x}")
        print(f"  Size: 0x{raw_size:x}")
        
        # Now find the decode functions
        # They should be in the .text section
        # Look for the function symbols we found earlier
        
        # The encoded string is at 0x2404018
        # parse_flag is at 0x2410529
        # Let's look at code around parse_flag
        
        # Calculate file offset from RVA
        # RVA = virtual_addr, File offset = raw_offset
        # For address X: file_offset = X - virtual_addr + raw_offset
        
        parse_flag_rva = 0x2410529 - 0x2400000  # Adjust for image base
        if parse_flag_rva > virtual_addr:
            parse_flag_file_offset = parse_flag_rva - virtual_addr + raw_offset
            print(f"\nparse_flag file offset: 0x{parse_flag_file_offset:x}")
            
            # Disassemble around this area
            md = Cs(CS_ARCH_X86, CS_MODE_64)
            code_start = parse_flag_file_offset - 1000
            code_end = parse_flag_file_offset + 1000
            code = data[code_start:code_end]
            
            print(f"\nDisassembling from 0x{code_start:x} to 0x{code_end:x}:")
            for insn in md.disasm(code[:200], code_start):
                print(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}")

# Alternative: Just look for the actual decoding logic by pattern matching
print("\n" + "="*60)
print("ANALYZING DECODE PATTERN")
print("="*60)

# The encoded string: AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc
# This looks like base64 but with a custom alphabet
# Let's try to figure out the alphabet by looking at the code

# Common base64 decode pattern:
# 1. Map each character to 6-bit value
# 2. Combine 4 characters into 3 bytes
# 3. Handle padding

# Let's try a custom base64 alphabet
import base64
import string

encoded = "AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc"

# Try different alphabet orderings
print("\nTrying custom base64 alphabets:")

# Maybe the alphabet is scrambled
# Standard: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
# Let's try reverse
alphabets = [
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
    "zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA9876543210+/",
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/",
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/",
]

std_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

for i, custom_alphabet in enumerate(alphabets):
    # Create translation table
    trans_table = str.maketrans(custom_alphabet, std_alphabet)
    normalized = encoded.translate(trans_table)
    
    for padding in ['', '=', '==']:
        try:
            decoded = base64.b64decode(normalized + padding)
            decoded_str = decoded.decode('utf-8', errors='ignore')
            if decoded_str and all(c in string.printable for c in decoded_str):
                print(f"  Alphabet {i}, padding '{padding}': {decoded_str}")
                if len(decoded_str) > 5:
                    print(f"    *** Kaal{{{decoded_str}}} ***")
        except:
            pass

print("\n" + "="*60)

#!/usr/bin/env python3
"""
Extract LSB from the very beginning of the file
"""

def extract_lsb_beginning(num_bytes=50000):
    with open("challenge_final.onnx", 'rb') as f:
        data = f.read(num_bytes)
    
    print(f"[*] Reading first {num_bytes} bytes")
    print(f"[*] First 100 bytes (hex): {data[:100].hex()}")
    print(f"[*] First 100 bytes (ascii): {data[:100].decode('latin-1', errors='ignore')}")
    
    # Extract LSB
    bits = [byte & 1 for byte in data]
    
    # Try both bit orders
    for order_name, bit_order in [("LSB first", False), ("MSB first", True)]:
        print(f"\n[*] Trying {order_name}")
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                if bit_order:  # MSB first
                    byte_val = sum(bits[i+j] << (7-j) for j in range(8))
                else:  # LSB first
                    byte_val = sum(bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted)
        result_str = result.decode('latin-1', errors='ignore')
        
        print(f"First 300 chars: {result_str[:300]}")
        
        if 'Kaal{' in result_str:
            idx = result_str.index('Kaal{')
            # Find end
            end_idx = result_str.find('}', idx)
            if end_idx != -1:
                flag = result_str[idx:end_idx+1]
                print(f"\n[!] FOUND FLAG: {flag}")
                return flag
        
        # Also check for partial matches
        if 'Kaal' in result_str:
            idx = result_str.index('Kaal')
            print(f"Found 'Kaal' at position {idx}")
            print(f"Context: {repr(result_str[max(0,idx-20):idx+100])}")
    
    return None

def try_different_starting_positions():
    """Try starting from different byte positions"""
    print("\n[*] Trying different starting positions")
    
    with open("challenge_final.onnx", 'rb') as f:
        data = f.read(100000)
    
    # Try starting from different offsets
    for offset in [0, 100, 200, 500, 1000, 2000]:
        print(f"\n[*] Offset {offset}")
        bits = [byte & 1 for byte in data[offset:offset+10000]]
        
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_val = sum(bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        
        if 'Kaal{' in result:
            idx = result.index('Kaal{')
            end_idx = result.find('}', idx)
            if end_idx != -1:
                flag = result[idx:end_idx+1]
                print(f"[!] FOUND FLAG at offset {offset}: {flag}")
                return flag
        
        if 'Kaal' in result:
            print(f"Found 'Kaal' at offset {offset}")

if __name__ == "__main__":
    flag = extract_lsb_beginning(50000)
    
    if not flag:
        flag = try_different_starting_positions()
    
    if flag:
        print("\n" + "="*60)
        print(f"SUCCESS! Flag: {flag}")
        print("="*60)
    else:
        print("\n[-] Flag not found")

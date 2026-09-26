#!/usr/bin/env python3
"""
Comprehensive LSB extraction from ONNX - try all methods
"""

import onnx
import struct

def method1_raw_file_lsb(filename):
    """Extract LSB from raw file bytes"""
    print("\n[METHOD 1] Raw file LSB extraction")
    print("="*60)
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    bits = [byte & 1 for byte in data[:100000]]  # First 100k bytes
    
    # LSB first
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    if 'Kaal{' in result:
        start = result.index('Kaal{')
        end = result.index('}', start) + 1
        print(f"[!] FLAG FOUND: {result[start:end]}")
        return result[start:end]
    
    print(f"First 200 chars: {result[:200]}")
    return None

def method2_onnx_weights_lsb(filename):
    """Extract LSB from ONNX weight tensors"""
    print("\n[METHOD 2] ONNX weights LSB extraction")
    print("="*60)
    
    model = onnx.load(filename)
    
    for tensor in model.graph.initializer:
        if tensor.HasField('raw_data'):
            raw_data = tensor.raw_data
            print(f"\n[*] Checking tensor: {tensor.name} ({len(raw_data)} bytes)")
            
            # Extract all LSBs from this tensor
            bits = [byte & 1 for byte in raw_data]
            
            # Convert to bytes
            extracted = []
            for i in range(0, len(bits), 8):
                if i + 8 <= len(bits):
                    byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
                    extracted.append(byte_val)
            
            result = bytes(extracted).decode('latin-1', errors='ignore')
            if 'Kaal{' in result:
                start = result.index('Kaal{')
                end = result.index('}', start) + 1
                flag = result[start:end]
                print(f"[!] FLAG FOUND in {tensor.name}: {flag}")
                return flag
            
            # Show first 100 chars
            print(f"    First 100 chars: {result[:100]}")
    
    return None

def method3_float_lsb(filename):
    """Extract LSB from float32 weights"""
    print("\n[METHOD 3] Float32 LSB extraction")
    print("="*60)
    
    model = onnx.load(filename)
    
    for tensor in model.graph.initializer:
        if tensor.HasField('raw_data') and tensor.data_type == 1:  # FLOAT
            raw_data = tensor.raw_data
            print(f"\n[*] Checking tensor: {tensor.name}")
            
            # Parse as float32 values
            num_floats = len(raw_data) // 4
            floats = struct.unpack(f'{num_floats}f', raw_data[:num_floats*4])
            
            # Extract LSB from the integer representation of floats
            bits = []
            for f in floats[:10000]:  # First 10000 floats
                int_repr = struct.unpack('I', struct.pack('f', f))[0]
                bits.append(int_repr & 1)
            
            # Convert to bytes
            extracted = []
            for i in range(0, len(bits), 8):
                if i + 8 <= len(bits):
                    byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
                    extracted.append(byte_val)
            
            result = bytes(extracted).decode('latin-1', errors='ignore')
            if 'Kaal{' in result:
                start = result.index('Kaal{')
                end = result.index('}', start) + 1
                flag = result[start:end]
                print(f"[!] FLAG FOUND in {tensor.name}: {flag}")
                return flag
            
            print(f"    First 100 chars: {result[:100]}")
    
    return None

def method4_msb_extraction(filename):
    """Try MSB instead of LSB"""
    print("\n[METHOD 4] MSB extraction (just in case)")
    print("="*60)
    
    with open(filename, 'rb') as f:
        data = f.read(10000)
    
    bits = [(byte >> 7) & 1 for byte in data]  # MSB
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    if 'Kaal{' in result:
        start = result.index('Kaal{')
        end = result.index('}', start) + 1
        print(f"[!] FLAG FOUND: {result[start:end]}")
        return result[start:end]
    
    print(f"First 200 chars: {result[:200]}")
    return None

def method5_search_plaintext(filename):
    """Search for plaintext flag in file"""
    print("\n[METHOD 5] Plaintext search")
    print("="*60)
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    text = data.decode('latin-1', errors='ignore')
    if 'Kaal{' in text:
        start = text.index('Kaal{')
        end = text.index('}', start) + 1
        flag = text[start:end]
        print(f"[!] FLAG FOUND in plaintext: {flag}")
        return flag
    
    print("No plaintext flag found")
    return None

if __name__ == "__main__":
    filename = "challenge_final.onnx"
    
    methods = [
        method1_raw_file_lsb,
        method2_onnx_weights_lsb,
        method3_float_lsb,
        method4_msb_extraction,
        method5_search_plaintext
    ]
    
    for method in methods:
        try:
            flag = method(filename)
            if flag:
                print("\n" + "="*60)
                print(f"SUCCESS! Flag: {flag}")
                print("="*60)
                break
        except Exception as e:
            print(f"[-] Error in {method.__name__}: {e}")
            import traceback
            traceback.print_exc()

#!/usr/bin/env python3
"""
Try all possible LSB extraction methods
"""

import onnx
import struct

def method_raw_bytes_lsb():
    """Extract LSB from raw file bytes"""
    print("\n[METHOD 1] Raw bytes LSB (LSB first)")
    with open("challenge_final.onnx", 'rb') as f:
        data = f.read(100000)
    
    bits = [byte & 1 for byte in data]
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        end = result.index('}', idx) + 1
        print(f"FOUND: {result[idx:end]}")
        return result[idx:end]
    print("Not found")
    return None

def method_raw_bytes_msb_first():
    """Extract LSB but MSB first in byte"""
    print("\n[METHOD 2] Raw bytes LSB (MSB first)")
    with open("challenge_final.onnx", 'rb') as f:
        data = f.read(100000)
    
    bits = [byte & 1 for byte in data]
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bit << (7-j) for j, bit in enumerate(bits[i:i+8]))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        end = result.index('}', idx) + 1
        print(f"FOUND: {result[idx:end]}")
        return result[idx:end]
    print("Not found")
    return None

def method_first_tensor_raw():
    """Extract from first tensor raw bytes"""
    print("\n[METHOD 3] First tensor (conv1.weight) raw bytes LSB")
    model = onnx.load("challenge_final.onnx")
    
    tensor = model.graph.initializer[0]
    raw_data = tensor.raw_data
    
    bits = [byte & 1 for byte in raw_data]
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"First 200 chars: {result[:200]}")
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        end = result.index('}', idx) + 1
        print(f"FOUND: {result[idx:end]}")
        return result[idx:end]
    print("Not found")
    return None

def method_first_tensor_float_bytes():
    """Extract from first tensor treating as float32 but using raw bytes"""
    print("\n[METHOD 4] First tensor float32 bytes LSB")
    model = onnx.load("challenge_final.onnx")
    
    tensor = model.graph.initializer[0]
    raw_data = tensor.raw_data
    
    # Parse as floats
    num_floats = len(raw_data) // 4
    floats = struct.unpack(f'{num_floats}f', raw_data)
    
    # Get bytes of each float and extract LSB
    bits = []
    for f in floats:
        float_bytes = struct.pack('f', f)
        for byte in float_bytes:
            bits.append(byte & 1)
    
    extracted = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = sum(bit << j for j, bit in enumerate(bits[i:i+8]))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    print(f"First 200 chars: {result[:200]}")
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        end = result.index('}', idx) + 1
        print(f"FOUND: {result[idx:end]}")
        return result[idx:end]
    print("Not found")
    return None

def method_all_tensors_sequential():
    """Extract from all tensors sequentially"""
    print("\n[METHOD 5] All tensors raw bytes LSB (sequential)")
    model = onnx.load("challenge_final.onnx")
    
    all_bits = []
    for tensor in model.graph.initializer:
        if tensor.HasField('raw_data'):
            raw_data = tensor.raw_data
            for byte in raw_data:
                all_bits.append(byte & 1)
    
    extracted = []
    for i in range(0, min(len(all_bits), 100000), 8):
        if i + 8 <= len(all_bits):
            byte_val = sum(bit << j for j, bit in enumerate(all_bits[i:i+8]))
            extracted.append(byte_val)
    
    result = bytes(extracted).decode('latin-1', errors='ignore')
    if 'Kaal{' in result:
        idx = result.index('Kaal{')
        end = result.index('}', idx) + 1
        print(f"FOUND: {result[idx:end]}")
        return result[idx:end]
    print(f"First 200 chars: {result[:200]}")
    print("Not found")
    return None

def method_protobuf_metadata():
    """Check protobuf metadata fields"""
    print("\n[METHOD 6] Protobuf metadata")
    model = onnx.load("challenge_final.onnx")
    
    # Check model metadata
    if model.metadata_props:
        for prop in model.metadata_props:
            print(f"  {prop.key}: {prop.value}")
            if 'Kaal{' in prop.value:
                return prop.value
    
    # Check doc strings
    if model.doc_string:
        print(f"Doc string: {model.doc_string}")
        if 'Kaal{' in model.doc_string:
            return model.doc_string
    
    print("Not found")
    return None

if __name__ == "__main__":
    methods = [
        method_raw_bytes_lsb,
        method_raw_bytes_msb_first,
        method_first_tensor_raw,
        method_first_tensor_float_bytes,
        method_all_tensors_sequential,
        method_protobuf_metadata
    ]
    
    for method in methods:
        try:
            flag = method()
            if flag and 'Kaal{' in flag and '}' in flag:
                print("\n" + "="*60)
                print(f"SUCCESS! Flag: {flag}")
                print("="*60)
                break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

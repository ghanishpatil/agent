#!/usr/bin/env python3
"""
Extract LSB from ONNX model weights
"""

import onnx
import numpy as np

def extract_lsb_from_weights(model_path):
    """Extract LSB from model weights"""
    print(f"[*] Loading ONNX model: {model_path}")
    
    try:
        model = onnx.load(model_path)
        print(f"[+] Model loaded successfully")
        print(f"[+] Model IR version: {model.ir_version}")
        print(f"[+] Number of initializers (weights): {len(model.graph.initializer)}")
        
        # Extract all weight data
        all_bits = []
        
        for idx, tensor in enumerate(model.graph.initializer):
            print(f"\n[*] Processing tensor {idx}: {tensor.name}")
            print(f"    Data type: {tensor.data_type}")
            print(f"    Dims: {tensor.dims}")
            
            # Get raw data
            if tensor.HasField('raw_data'):
                raw_data = tensor.raw_data
                print(f"    Raw data size: {len(raw_data)} bytes")
                
                # Extract LSB from each byte
                for byte in raw_data[:10000]:  # First 10000 bytes
                    all_bits.append(byte & 1)
                
                # Try to decode immediately
                if len(all_bits) >= 8:
                    extracted_bytes = []
                    for i in range(0, len(all_bits), 8):
                        if i + 8 <= len(all_bits):
                            byte_bits = all_bits[i:i+8]
                            byte_value = 0
                            for j, bit in enumerate(byte_bits):
                                byte_value |= (bit << j)
                            extracted_bytes.append(byte_value)
                    
                    result = bytes(extracted_bytes)
                    result_str = result.decode('latin-1', errors='ignore')
                    
                    if 'Kaal{' in result_str:
                        start = result_str.index('Kaal{')
                        end = result_str.index('}', start) + 1
                        flag = result_str[start:end]
                        print(f"\n[!] FLAG FOUND in tensor {tensor.name}: {flag}")
                        return flag
                    
                    # Show first 200 chars
                    if idx == 0:
                        print(f"    First 200 chars: {result_str[:200]}")
        
        # Try all collected bits
        print(f"\n[*] Total bits collected: {len(all_bits)}")
        extracted_bytes = []
        for i in range(0, len(all_bits), 8):
            if i + 8 <= len(all_bits):
                byte_bits = all_bits[i:i+8]
                byte_value = 0
                for j, bit in enumerate(byte_bits):
                    byte_value |= (bit << j)
                extracted_bytes.append(byte_value)
        
        result = bytes(extracted_bytes)
        result_str = result.decode('latin-1', errors='ignore')
        
        if 'Kaal{' in result_str:
            start = result_str.index('Kaal{')
            end = result_str.index('}', start) + 1
            flag = result_str[start:end]
            print(f"\n[!] FLAG FOUND: {flag}")
            return flag
        
        print(f"\n[*] First 500 chars of all extracted data:")
        print(result_str[:500])
        
        # Try reverse bit order
        print(f"\n[*] Trying reverse bit order...")
        extracted_bytes_rev = []
        for i in range(0, len(all_bits), 8):
            if i + 8 <= len(all_bits):
                byte_bits = all_bits[i:i+8]
                byte_value = 0
                for j, bit in enumerate(reversed(byte_bits)):
                    byte_value |= (bit << j)
                extracted_bytes_rev.append(byte_value)
        
        result_rev = bytes(extracted_bytes_rev)
        result_str_rev = result_rev.decode('latin-1', errors='ignore')
        
        if 'Kaal{' in result_str_rev:
            start = result_str_rev.index('Kaal{')
            end = result_str_rev.index('}', start) + 1
            flag = result_str_rev[start:end]
            print(f"\n[!] FLAG FOUND: {flag}")
            return flag
        
        print(result_str_rev[:500])
        
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()
    
    return None

if __name__ == "__main__":
    flag = extract_lsb_from_weights("challenge_final.onnx")
    
    if flag:
        print("\n" + "="*60)
        print(f"SUCCESS! Flag: {flag}")
        print("="*60)

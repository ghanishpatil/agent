#!/usr/bin/env python3
"""
Find the "chord" input that triggers the flag
The hint says "tiny, coordinated set of inputs" - try sparse inputs with specific patterns
"""

import onnxruntime as ort
import numpy as np
import struct
import itertools

model_path = r"D:\mission-git-hackss\challenge_final (3).onnx"
session = ort.InferenceSession(model_path)

input_shape = [1, 1, 64, 64]

def extract_from_output(output):
    """Try to extract flag from output using various methods"""
    flat = output.flatten()
    
    # Method 1: Direct bytes
    out_bytes = output.tobytes()
    if b'Kaal{' in out_bytes:
        idx = out_bytes.index(b'Kaal{')
        end = out_bytes.find(b'}', idx)
        if end != -1:
            return out_bytes[idx:end+1].decode('latin-1', errors='ignore')
    
    # Method 2: LSB extraction
    bits = []
    for val in flat:
        int_repr = struct.unpack('I', struct.pack('f', val))[0]
        bits.append(int_repr & 1)
    
    if len(bits) >= 64:
        extracted = []
        for i in range(0, len(bits), 8):
            if i + 8 <= len(bits):
                byte_val = sum(bits[i+j] << j for j in range(8))
                extracted.append(byte_val)
        
        result = bytes(extracted).decode('latin-1', errors='ignore')
        if 'Kaal{' in result:
            start = result.index('Kaal{')
            end = result.find('}', start)
            if end != -1 and end - start < 200:
                return result[start:end+1]
    
    # Method 3: Multiple bit positions
    for bit_pos in range(1, 8):
        bits = []
        for val in flat:
            int_repr = struct.unpack('I', struct.pack('f', val))[0]
            bits.append((int_repr >> bit_pos) & 1)
        
        if len(bits) >= 64:
            extracted = []
            for i in range(0, len(bits), 8):
                if i + 8 <= len(bits):
                    byte_val = sum(bits[i+j] << j for j in range(8))
                    extracted.append(byte_val)
            
            result = bytes(extracted).decode('latin-1', errors='ignore')
            if 'Kaal{' in result:
                start = result.index('Kaal{')
                end = result.find('}', start)
                if end != -1 and end - start < 200:
                    return result[start:end+1]
    
    return None

print("[*] Searching for the chord input pattern...")

# Try 1: Single pixel at different positions (single note)
print("\n[1] Testing single pixels...")
for i in range(min(10, 64)):
    for j in range(min(10, 64)):
        input_data = np.zeros(input_shape, dtype=np.float32)
        input_data[0, 0, i, j] = 1.0
        
        outputs = session.run(None, {'input': input_data})
        
        for out_idx, out in enumerate(outputs):
            flag = extract_from_output(out)
            if flag:
                print(f"\n[+] FOUND FLAG with single pixel at ({i},{j})!")
                print(f"[+] Output {out_idx}: {flag}")
                exit(0)

# Try 2: Two pixels (two-note chord)
print("\n[2] Testing two-pixel patterns...")
positions = [(0,0), (0,1), (1,0), (1,1), (0,63), (63,0), (63,63), (31,31), (32,32)]
for (i1,j1), (i2,j2) in itertools.combinations(positions, 2):
    input_data = np.zeros(input_shape, dtype=np.float32)
    input_data[0, 0, i1, j1] = 1.0
    input_data[0, 0, i2, j2] = 1.0
    
    outputs = session.run(None, {'input': input_data})
    
    for out_idx, out in enumerate(outputs):
        flag = extract_from_output(out)
        if flag:
            print(f"\n[+] FOUND FLAG with pixels at ({i1},{j1}) and ({i2},{j2})!")
            print(f"[+] Output {out_idx}: {flag}")
            exit(0)

# Try 3: Three pixels (three-note chord)
print("\n[3] Testing three-pixel patterns...")
for (i1,j1), (i2,j2), (i3,j3) in itertools.combinations(positions, 3):
    input_data = np.zeros(input_shape, dtype=np.float32)
    input_data[0, 0, i1, j1] = 1.0
    input_data[0, 0, i2, j2] = 1.0
    input_data[0, 0, i3, j3] = 1.0
    
    outputs = session.run(None, {'input': input_data})
    
    for out_idx, out in enumerate(outputs):
        flag = extract_from_output(out)
        if flag:
            print(f"\n[+] FOUND FLAG with pixels at ({i1},{j1}), ({i2},{j2}), ({i3},{j3})!")
            print(f"[+] Output {out_idx}: {flag}")
            exit(0)

# Try 4: Specific patterns (musical chords have specific intervals)
print("\n[4] Testing musical chord patterns...")
# Major chord pattern (0, 4, 7 in music)
for start in range(0, 60, 5):
    input_data = np.zeros(input_shape, dtype=np.float32)
    input_data[0, 0, start, 0] = 1.0
    input_data[0, 0, start+4, 0] = 1.0
    input_data[0, 0, start+7, 0] = 1.0
    
    outputs = session.run(None, {'input': input_data})
    
    for out_idx, out in enumerate(outputs):
        flag = extract_from_output(out)
        if flag:
            print(f"\n[+] FOUND FLAG with major chord starting at {start}!")
            print(f"[+] Output {out_idx}: {flag}")
            exit(0)

# Try 5: Diagonal pattern
print("\n[5] Testing diagonal patterns...")
for length in [3, 4, 5, 7, 8]:
    input_data = np.zeros(input_shape, dtype=np.float32)
    for i in range(length):
        input_data[0, 0, i, i] = 1.0
    
    outputs = session.run(None, {'input': input_data})
    
    for out_idx, out in enumerate(outputs):
        flag = extract_from_output(out)
        if flag:
            print(f"\n[+] FOUND FLAG with diagonal length {length}!")
            print(f"[+] Output {out_idx}: {flag}")
            exit(0)

# Try 6: Very sparse random patterns
print("\n[6] Testing sparse random patterns...")
for trial in range(100):
    input_data = np.zeros(input_shape, dtype=np.float32)
    # Set 3-5 random pixels
    num_pixels = np.random.randint(3, 6)
    for _ in range(num_pixels):
        i = np.random.randint(0, 64)
        j = np.random.randint(0, 64)
        input_data[0, 0, i, j] = 1.0
    
    outputs = session.run(None, {'input': input_data})
    
    for out_idx, out in enumerate(outputs):
        flag = extract_from_output(out)
        if flag:
            print(f"\n[+] FOUND FLAG with random sparse pattern (trial {trial})!")
            print(f"[+] Output {out_idx}: {flag}")
            # Print which pixels were set
            nonzero = np.argwhere(input_data[0, 0] != 0)
            print(f"[+] Pixels: {nonzero.tolist()}")
            exit(0)

print("\n[-] No flag found with tested patterns")
print("[*] The flag might be encoded in the weights themselves, not triggered by inputs")

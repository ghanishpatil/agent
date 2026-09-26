#!/usr/bin/env python3
"""
Try multi-stage decoding
The functions d1, d2 suggest two decode stages
"""
import base64
import string

encoded = "AAHKhN_WqZelcbtnjiD68ONqvyNe6Z7TRGc"

print("="*60)
print("MULTI-STAGE DECODING")
print("="*60)

# Stage 1: Try base64 variants
print("\n[Stage 1] Base64 decode attempts:")

# Try with different padding
for padding in ['', '=', '==', '===']:
    try:
        stage1 = base64.b64decode(encoded + padding)
        print(f"\n  Padding '{padding}':")
        print(f"    Bytes: {stage1.hex()}")
        print(f"    Length: {len(stage1)}")
        
        # Try to interpret as string
        try:
            as_str = stage1.decode('utf-8')
            print(f"    As UTF-8: {as_str}")
        except:
            print(f"    As ASCII (ignore errors): {stage1.decode('ascii', errors='ignore')}")
        
        # Stage 2: Try base64 decode again
        try:
            stage2 = base64.b64decode(stage1)
            print(f"    Stage 2 decode: {stage2}")
            try:
                final = stage2.decode('utf-8')
                print(f"    Stage 2 as string: {final}")
                if 'Kaal' in final or '{' in final:
                    print(f"        *** POTENTIAL FLAG: {final} ***")
            except:
                pass
        except:
            pass
        
        # Try XOR with common keys on stage1
        for xor_key in [0x13, 0x42, 0x37]:
            xored = bytes([b ^ xor_key for b in stage1])
            try:
                decoded = xored.decode('utf-8')
                if all(c in string.printable for c in decoded):
                    print(f"    XOR with 0x{xor_key:02x}: {decoded}")
                    if 'Kaal' in decoded:
                        print(f"        *** POTENTIAL FLAG: {decoded} ***")
            except:
                pass
                
    except Exception as e:
        pass

# Try URL-safe base64
print("\n[URL-safe base64]:")
try:
    decoded = base64.urlsafe_b64decode(encoded + '==')
    print(f"    Decoded: {decoded}")
    print(f"    As string: {decoded.decode('utf-8', errors='ignore')}")
except Exception as e:
    print(f"    Error: {e}")

# Try base32
print("\n[Base32]:")
try:
    decoded = base64.b32decode(encoded)
    print(f"    Decoded: {decoded}")
    print(f"    As string: {decoded.decode('utf-8', errors='ignore')}")
except Exception as e:
    print(f"    Error: {e}")

# Try interpreting the string as indices into an alphabet
print("\n[Custom alphabet decode]:")
# Maybe each character maps to a position
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
try:
    indices = [alphabet.index(c) if c in alphabet else -1 for c in encoded]
    print(f"    Indices: {indices[:20]}...")
    
    # Try to convert indices to characters
    decoded = ''.join([chr(i + ord('A')) if 0 <= i < 26 else '?' for i in indices])
    print(f"    As characters: {decoded}")
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "="*60)

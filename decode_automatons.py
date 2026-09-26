#!/usr/bin/env python3
"""
Decode the AUTOMATONS_SECRET challenge
"""
import base64
import zlib
import pickle
import json

print("="*80)
print("DECODING AUTOMATONS_SECRET")
print("="*80)

# Read the files
with open('AUTOMATONS_SECRET/encoded_graph.bin', 'rb') as f:
    graph_data = f.read()

with open('AUTOMATONS_SECRET/encrypted_flag.bin', 'rb') as f:
    flag_data = f.read()

print("\n[Step 1] Decompress the graph data")
try:
    # The data appears to be base64 encoded, then compressed
    decompressed = zlib.decompress(graph_data)
    print(f"✓ Decompressed successfully!")
    print(f"  Original size: {len(graph_data)} bytes")
    print(f"  Decompressed size: {len(decompressed)} bytes")
    
    # Save decompressed data
    with open('graph_decompressed.bin', 'wb') as f:
        f.write(decompressed)
    
    # Try to see if it's readable
    print(f"\n[Step 2] Analyzing decompressed data")
    print(f"First 200 bytes: {decompressed[:200]}")
    
    # Check if it's JSON
    try:
        graph_obj = json.loads(decompressed)
        print(f"\n✓ It's JSON data!")
        print(f"Keys: {list(graph_obj.keys()) if isinstance(graph_obj, dict) else 'List'}")
        
        with open('graph_decoded.json', 'w') as f:
            json.dump(graph_obj, f, indent=2)
        print(f"Saved to: graph_decoded.json")
        
    except:
        # Try pickle
        try:
            graph_obj = pickle.loads(decompressed)
            print(f"\n✓ It's pickled Python object!")
            print(f"Type: {type(graph_obj)}")
            print(f"Content preview: {str(graph_obj)[:500]}")
        except:
            print(f"\nNot JSON or pickle, raw binary data")
            # Check if it's a graph adjacency matrix or list
            import struct
            print(f"\nTrying to parse as structured data...")
            
except Exception as e:
    print(f"✗ Decompression failed: {e}")

print(f"\n[Step 3] Analyzing encrypted flag")
print(f"Flag data (hex): {flag_data.hex()}")
print(f"Flag data length: {len(flag_data)} bytes")

# The flag is 48 bytes - likely AES encrypted (AES block size is 16 bytes)
# 48 = 3 blocks of 16 bytes
print(f"\nLikely encryption: AES (48 bytes = 3 blocks of 16)")

print("\n" + "="*80)
print("Next steps:")
print("1. Understand the graph structure")
print("2. Find the key/algorithm to decrypt the flag")
print("3. The graph likely contains the decryption key or algorithm")
print("="*80)

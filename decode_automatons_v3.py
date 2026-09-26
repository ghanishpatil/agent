#!/usr/bin/env python3
"""
Decode the AUTOMATONS_SECRET challenge - v3 (fixed)
"""
import base64
import zlib
import pickle
import json

def decode_graph():
    print("="*80)
    print("DECODING AUTOMATONS_SECRET - V3")
    print("="*80)

    # Read the files
    with open('AUTOMATONS_SECRET/encoded_graph.bin', 'rb') as f:
        graph_data = f.read()

    with open('AUTOMATONS_SECRET/encrypted_flag.bin', 'rb') as f:
        flag_data = f.read()

    print("\n[Step 1] Base64 decode the graph data")
    try:
        # First base64 decode
        decoded_b64 = base64.b64decode(graph_data)
        print(f"✓ Base64 decoded successfully!")
        print(f"  Encoded size: {len(graph_data)} bytes")
        print(f"  Decoded size: {len(decoded_b64)} bytes")
        print(f"  First 20 bytes (hex): {decoded_b64[:20].hex()}")
        
        print("\n[Step 2] Decompress the data")
        try:
            # Try zlib decompression
            decompressed = zlib.decompress(decoded_b64)
            print(f"✓ Decompressed successfully!")
            print(f"  Decompressed size: {len(decompressed)} bytes")
            
            # Save decompressed data
            with open('graph_decompressed.bin', 'wb') as f:
                f.write(decompressed)
            
            print(f"\n[Step 3] Analyzing decompressed data")
            print(f"First 500 characters:")
            try:
                print(decompressed[:500].decode('utf-8', errors='ignore'))
            except:
                print(decompressed[:500])
            
            # Try to parse as JSON
            try:
                graph_obj = json.loads(decompressed)
                print(f"\n✓ It's JSON data!")
                print(f"Type: {type(graph_obj)}")
                if isinstance(graph_obj, dict):
                    print(f"Keys: {list(graph_obj.keys())}")
                    for key in list(graph_obj.keys())[:5]:
                        print(f"  {key}: {str(graph_obj[key])[:100]}")
                elif isinstance(graph_obj, list):
                    print(f"List length: {len(graph_obj)}")
                    print(f"First few items: {graph_obj[:3]}")
                
                with open('graph_decoded.json', 'w') as f:
                    json.dump(graph_obj, f, indent=2)
                print(f"\n✓ Saved to: graph_decoded.json")
                
                return graph_obj
                
            except Exception as e:
                print(f"\n✗ Not JSON: {e}")
                # Try pickle
                try:
                    graph_obj = pickle.loads(decompressed)
                    print(f"\n✓ It's pickled Python object!")
                    print(f"Type: {type(graph_obj)}")
                    print(f"Content: {str(graph_obj)[:1000]}")
                    return graph_obj
                except Exception as e2:
                    print(f"\n✗ Not pickle either: {e2}")
                    print(f"\nRaw data (first 1000 chars):")
                    print(decompressed[:1000])
                    
        except Exception as e:
            print(f"✗ Decompression failed: {e}")
            
    except Exception as e:
        print(f"✗ Base64 decode failed: {e}")

    print(f"\n[Step 4] Analyzing encrypted flag")
    print(f"Flag length: {len(flag_data)} bytes (48 bytes = likely AES-256 or 3x AES-128 blocks)")
    print(f"Flag hex: {flag_data.hex()}")

    print("\n" + "="*80)

if __name__ == "__main__":
    decode_graph()

#!/usr/bin/env python3
"""
Analyze the AUTOMATONS_SECRET challenge files
"""

print("="*80)
print("AUTOMATONS_SECRET CHALLENGE ANALYSIS")
print("="*80)

# Read the files
with open('AUTOMATONS_SECRET/encoded_graph.bin', 'rb') as f:
    graph_data = f.read()

with open('AUTOMATONS_SECRET/encrypted_flag.bin', 'rb') as f:
    flag_data = f.read()

print(f"\n[File Sizes]")
print(f"encoded_graph.bin: {len(graph_data)} bytes")
print(f"encrypted_flag.bin: {len(flag_data)} bytes")

print(f"\n[Encrypted Flag Data]")
print(f"Hex: {flag_data.hex()}")
print(f"Bytes: {list(flag_data)}")

print(f"\n[Graph Data Analysis]")
print(f"First 100 bytes (hex): {graph_data[:100].hex()}")
print(f"First 100 bytes (raw): {graph_data[:100]}")

# Check if it's structured data
print(f"\n[Looking for patterns in graph data]")

# Check for common file signatures
if graph_data[:4] == b'PK\x03\x04':
    print("  Looks like a ZIP file!")
elif graph_data[:2] == b'\x1f\x8b':
    print("  Looks like GZIP compressed!")
elif graph_data[:4] == b'\x89PNG':
    print("  Looks like a PNG image!")
else:
    print("  Custom binary format")

# Look for repeating patterns
print(f"\n[Byte frequency analysis]")
from collections import Counter
byte_freq = Counter(graph_data)
most_common = byte_freq.most_common(10)
print(f"Most common bytes:")
for byte, count in most_common:
    print(f"  0x{byte:02x}: {count} times ({count/len(graph_data)*100:.1f}%)")

# Check if it might be a serialized graph structure
print(f"\n[Checking for graph structure markers]")
# Common graph formats might have:
# - Node count
# - Edge count
# - Adjacency lists/matrices

# Try to interpret first few bytes as integers
import struct

print(f"First 4 bytes as uint32 (little-endian): {struct.unpack('<I', graph_data[:4])[0]}")
print(f"First 4 bytes as uint32 (big-endian): {struct.unpack('>I', graph_data[:4])[0]}")
print(f"First 8 bytes as uint64 (little-endian): {struct.unpack('<Q', graph_data[:8])[0]}")

# Check for null-terminated strings
print(f"\n[Looking for strings in graph data]")
import re
strings = re.findall(b'[ -~]{4,}', graph_data)
if strings:
    print(f"Found {len(strings)} readable strings:")
    for s in strings[:10]:
        print(f"  {s.decode('utf-8', errors='ignore')}")

print("\n" + "="*80)

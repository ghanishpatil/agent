#!/usr/bin/env python3
"""
Find all paths to ACCEPT nodes and try different key lengths
"""
import json
from collections import deque
from Crypto.Cipher import AES

print("="*80)
print("FINDING ALL PATHS TO ACCEPT NODES")
print("="*80)

# Load the decoded graph
with open('graph_decoded.json', 'r') as f:
    graph = json.load(f)

nodes = graph['nodes']
edges = graph['edges']

# Build adjacency list
adj = {}
for edge in edges:
    src = edge['src']
    if src not in adj:
        adj[src] = []
    adj[src].append((edge['dst'], edge['label']))

# Find all ACCEPT nodes
accept_nodes = [n for n in nodes if n.get('role') == 'ACCEPT']
print(f"\n[ACCEPT Nodes]")
for node in accept_nodes:
    print(f"  {node}")

# Extract IV
node_99 = next(n for n in nodes if n['id'] == 99)
iv_hex = node_99['meta'].split('=')[1]
iv = bytes.fromhex(iv_hex)
print(f"\nIV: {iv_hex}")

# Find ALL paths from START to each ACCEPT node using DFS
def find_all_paths_dfs(start, goal, max_depth=50):
    """Find all paths from start to goal up to max_depth"""
    paths = []
    
    def dfs(current, path, visited):
        if len(path) > max_depth:
            return
        
        if current == goal:
            paths.append(path[:])
            return
        
        if current in adj:
            for next_node, label in adj[current]:
                if next_node not in visited:
                    visited.add(next_node)
                    path.append(label)
                    dfs(next_node, path, visited)
                    path.pop()
                    visited.remove(next_node)
    
    dfs(start, [], {start})
    return paths

# Read encrypted flag
with open('AUTOMATONS_SECRET/encrypted_flag.bin', 'rb') as f:
    encrypted_flag = f.read()

print(f"\n[Encrypted Flag]")
print(f"  Length: {len(encrypted_flag)} bytes")

# Try each ACCEPT node
for accept_node in accept_nodes:
    node_id = accept_node['id']
    print(f"\n{'='*80}")
    print(f"[Trying ACCEPT node {node_id}]")
    print(f"  {accept_node}")
    
    paths = find_all_paths_dfs(0, node_id, max_depth=50)
    print(f"  Found {len(paths)} paths")
    
    if not paths:
        continue
    
    # Sort by length
    paths.sort(key=len)
    
    # Show path lengths
    path_lengths = [len(p) for p in paths]
    print(f"  Path lengths: {sorted(set(path_lengths))}")
    
    # Try paths with standard AES key lengths (16, 24, 32)
    for target_len in [16, 24, 32]:
        matching_paths = [p for p in paths if len(p) == target_len]
        if matching_paths:
            print(f"\n  [Trying {len(matching_paths)} paths with length {target_len}]")
            for i, path_labels in enumerate(matching_paths[:5]):  # Try first 5
                key = bytes(path_labels)
                try:
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted = cipher.decrypt(encrypted_flag)
                    
                    # Try to decode as text
                    try:
                        # Remove PKCS7 padding
                        padding_len = decrypted[-1]
                        if 1 <= padding_len <= 16:
                            decrypted_unpadded = decrypted[:-padding_len]
                            text = decrypted_unpadded.decode('utf-8')
                            if text.startswith('Kaal{'):
                                print(f"\n{'='*80}")
                                print(f"✓✓✓ FOUND FLAG! ✓✓✓")
                                print(f"{'='*80}")
                                print(f"Node: {node_id}")
                                print(f"Path length: {len(path_labels)}")
                                print(f"Key: {key.hex()}")
                                print(f"FLAG: {text}")
                                print(f"{'='*80}")
                                exit(0)
                    except:
                        pass
                except Exception as e:
                    pass

print(f"\n{'='*80}")
print("No valid flag found with standard key lengths")
print("="*80)

#!/usr/bin/env python3
"""
Deep analysis of the automaton graph structure
"""

import json
import zlib
import base64
from collections import defaultdict, Counter

def load_graph():
    with open('AUTOMATONS_SECRET/encrypted_flag.bin', 'rb') as f:
        encrypted_flag = f.read()
    
    with open('AUTOMATONS_SECRET/encoded_graph.bin', 'rb') as f:
        encoded = f.read()
    
    decoded = base64.b64decode(encoded)
    decompressed = zlib.decompress(decoded)
    graph_data = json.loads(decompressed)
    
    return encrypted_flag, graph_data

def analyze():
    encrypted_flag, graph_data = load_graph()
    
    nodes = {n['id']: n for n in graph_data['nodes']}
    edges = graph_data['edges']
    
    print("=== NODE ANALYSIS ===")
    print(f"Total nodes: {len(nodes)}")
    
    # Check for nodes with special properties
    special_nodes = [n for n in graph_data['nodes'] if len(n) > 1]
    print(f"Nodes with properties: {len(special_nodes)}")
    for node in special_nodes:
        print(f"  Node {node['id']}: {node}")
    
    print("\n=== EDGE ANALYSIS ===")
    print(f"Total edges: {len(edges)}")
    
    # Analyze edge labels
    labels = [e['label'] for e in edges]
    label_counts = Counter(labels)
    
    print(f"Unique labels: {len(set(labels))}")
    print(f"Label range: {min(labels)} - {max(labels)}")
    
    # Check if labels form ASCII text
    ascii_labels = [l for l in labels if 32 <= l <= 126]
    print(f"ASCII printable: {len(ascii_labels)}/{len(labels)}")
    
    # Most common labels
    print("\nMost common labels:")
    for label, count in label_counts.most_common(10):
        char = chr(label) if 32 <= label <= 126 else f"\\x{label:02x}"
        print(f"  {label} ({char}): {count} times")
    
    # Build adjacency info
    out_degree = defaultdict(int)
    in_degree = defaultdict(int)
    adjacency = defaultdict(list)
    
    for edge in edges:
        out_degree[edge['src']] += 1
        in_degree[edge['dst']] += 1
        adjacency[edge['src']].append((edge['dst'], edge['label']))
    
    print("\n=== GRAPH STRUCTURE ===")
    print(f"Nodes with no incoming edges: {[n for n in nodes if in_degree[n] == 0]}")
    print(f"Nodes with no outgoing edges: {[n for n in nodes if out_degree[n] == 0]}")
    
    # Analyze from START node
    start = 0
    print(f"\n=== FROM START NODE ({start}) ===")
    print(f"Outgoing edges: {out_degree[start]}")
    
    start_edges = [(e['dst'], e['label']) for e in edges if e['src'] == start]
    print("Start node connections:")
    for dst, label in start_edges:
        char = chr(label) if 32 <= label <= 126 else f"\\x{label:02x}"
        print(f"  -> Node {dst}, label {label} ({char})")
    
    # Check if there's a deterministic path
    print("\n=== CHECKING FOR DETERMINISTIC PATH ===")
    
    # Look for nodes that have unique outgoing labels
    deterministic_nodes = []
    for node_id in nodes:
        if out_degree[node_id] > 0:
            labels_from_node = [e['label'] for e in edges if e['src'] == node_id]
            if len(labels_from_node) == len(set(labels_from_node)):
                deterministic_nodes.append(node_id)
    
    print(f"Nodes with unique outgoing labels: {len(deterministic_nodes)}/{len(nodes)}")
    
    # Check if labels might encode a message
    print("\n=== CHECKING LABEL PATTERNS ===")
    
    # Try to see if labels spell something
    all_labels_sorted = sorted(set(labels))
    print(f"All unique labels (first 50): {all_labels_sorted[:50]}")
    
    # Check if labels correspond to 'Kaal{' pattern
    target = b'Kaal{'
    print(f"\nTarget flag start: {target}")
    print(f"Target bytes: {[b for b in target]}")
    
    # XOR analysis - what would the key need to be?
    print(f"\nEncrypted flag start: {encrypted_flag[:5].hex()}")
    print(f"Encrypted bytes: {[b for b in encrypted_flag[:5]]}")
    
    print("\nIf flag starts with 'Kaal{', key would start with:")
    for i in range(5):
        key_byte = encrypted_flag[i] ^ target[i]
        char = chr(key_byte) if 32 <= key_byte <= 126 else f"\\x{key_byte:02x}"
        print(f"  Position {i}: {key_byte} ({char})")
    
    # Check if these key bytes appear in edge labels
    expected_key_start = [encrypted_flag[i] ^ target[i] for i in range(5)]
    print(f"\nExpected key start: {expected_key_start}")
    
    # See if we can find a path that starts with these labels
    print("\nSearching for paths starting with expected key...")
    
    def find_path_with_prefix(start_node, prefix, max_depth=10):
        """Find paths that start with given label prefix"""
        if not prefix:
            return [[]]
        
        paths = []
        for dst, label in adjacency[start_node]:
            if label == prefix[0]:
                if len(prefix) == 1:
                    paths.append([label])
                else:
                    sub_paths = find_path_with_prefix(dst, prefix[1:], max_depth-1)
                    for sp in sub_paths:
                        paths.append([label] + sp)
        
        return paths
    
    matching_paths = find_path_with_prefix(start, expected_key_start[:3])
    print(f"Paths starting with first 3 key bytes: {len(matching_paths)}")
    
    if matching_paths:
        print("Found matching path prefix! Extending to full length...")
        # Try to extend the first matching path
        for path_prefix in matching_paths[:5]:
            print(f"\nTrying path prefix: {path_prefix}")
            extended = extend_path(adjacency, start, path_prefix, 48, [42, 89, 115, 137])
            if extended:
                print(f"Extended to length {len(extended)}")
                key = bytes(extended)
                decrypted = bytes([encrypted_flag[i] ^ key[i] for i in range(len(encrypted_flag))])
                print(f"Decrypted: {decrypted}")
                if b'Kaal{' in decrypted:
                    print(f"\n[SUCCESS] {decrypted.decode()}")

def extend_path(adjacency, start, prefix, target_len, accept_nodes):
    """Extend a path prefix to target length ending at accept node"""
    from collections import deque
    
    # First, follow the prefix to get to the current node
    current = start
    for label in prefix:
        found = False
        for dst, lbl in adjacency[current]:
            if lbl == label:
                current = dst
                found = True
                break
        if not found:
            return None
    
    # Now BFS from current node to find path to accept
    queue = deque([(current, prefix[:])])
    visited = set()
    
    while queue:
        node, path = queue.popleft()
        
        if len(path) == target_len and node in accept_nodes:
            return path
        
        if len(path) >= target_len:
            continue
        
        state = (node, len(path))
        if state in visited:
            continue
        visited.add(state)
        
        for dst, label in adjacency[node]:
            queue.append((dst, path + [label]))
    
    return None

if __name__ == "__main__":
    analyze()

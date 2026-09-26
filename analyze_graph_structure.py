#!/usr/bin/env python3
"""
Analyze the decoded graph structure to find the decryption key
"""
import json

print("="*80)
print("ANALYZING GRAPH STRUCTURE")
print("="*80)

# Load the decoded graph
with open('graph_decoded.json', 'r') as f:
    graph = json.load(f)

nodes = graph['nodes']
edges = graph['edges']

print(f"\n[Graph Statistics]")
print(f"Total nodes: {len(nodes)}")
print(f"Total edges: {len(edges)}")

# Find special nodes
print(f"\n[Special Nodes]")
special_nodes = [n for n in nodes if 'role' in n or 'hint' in n or 'key' in n or 'flag' in n]
for node in special_nodes:
    print(f"  Node {node['id']}: {node}")

# Analyze edge labels
print(f"\n[Edge Label Analysis]")
labels = [e['label'] for e in edges]
unique_labels = sorted(set(labels))
print(f"Unique labels: {len(unique_labels)}")
print(f"Label range: {min(labels)} to {max(labels)}")
print(f"First 20 unique labels: {unique_labels[:20]}")

# Find START node
start_nodes = [n for n in nodes if n.get('role') == 'START']
print(f"\n[Start Node]")
if start_nodes:
    start_node = start_nodes[0]
    print(f"Start node ID: {start_node['id']}")
    print(f"Start node: {start_node}")
    
    # Find edges from start
    start_edges = [e for e in edges if e['src'] == start_node['id']]
    print(f"\nEdges from START node: {len(start_edges)}")
    for edge in start_edges[:10]:
        print(f"  {edge}")

# Find END/GOAL nodes
end_nodes = [n for n in nodes if n.get('role') in ['END', 'GOAL', 'FINAL', 'TARGET']]
print(f"\n[End/Goal Nodes]")
if end_nodes:
    for node in end_nodes:
        print(f"  {node}")
else:
    print("  No explicit end nodes found")
    # Look for nodes with no outgoing edges
    nodes_with_out = set(e['src'] for e in edges)
    nodes_without_out = [n['id'] for n in nodes if n['id'] not in nodes_with_out]
    print(f"  Nodes with no outgoing edges: {len(nodes_without_out)}")
    if nodes_without_out:
        print(f"  First 10: {nodes_without_out[:10]}")
        # Check if any have special properties
        for nid in nodes_without_out[:10]:
            node = nodes[nid]
            if len(node) > 1:  # Has more than just 'id'
                print(f"    Node {nid}: {node}")

# Look for nodes with special keys
print(f"\n[Nodes with Extra Properties]")
nodes_with_props = [n for n in nodes if len(n) > 1]
print(f"Found {len(nodes_with_props)} nodes with extra properties")
for node in nodes_with_props[:20]:
    print(f"  {node}")

print("\n" + "="*80)

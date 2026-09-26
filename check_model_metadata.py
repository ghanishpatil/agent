#!/usr/bin/env python3
"""
Check model metadata and other fields for hidden data
"""

import onnx

model = onnx.load("challenge_final 2.onnx")

print("[*] Model metadata:")
print(f"  IR version: {model.ir_version}")
print(f"  Producer name: {model.producer_name}")
print(f"  Producer version: {model.producer_version}")
print(f"  Domain: {model.domain}")
print(f"  Model version: {model.model_version}")
print(f"  Doc string: {model.doc_string}")

print(f"\n[*] Metadata props:")
for prop in model.metadata_props:
    print(f"  {prop.key}: {prop.value}")

print(f"\n[*] Graph info:")
print(f"  Name: {model.graph.name}")
print(f"  Doc string: {model.graph.doc_string}")

print(f"\n[*] Graph inputs:")
for inp in model.graph.input:
    print(f"  {inp.name}: {inp.doc_string}")

print(f"\n[*] Graph outputs:")
for out in model.graph.output:
    print(f"  {out.name}: {out.doc_string}")

print(f"\n[*] Graph nodes:")
for node in model.graph.node:
    if node.doc_string:
        print(f"  {node.name}: {node.doc_string}")

print("\n[*] Done")

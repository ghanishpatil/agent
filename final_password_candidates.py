#!/usr/bin/env python3
"""List all final password candidates"""

print("="*80)
print("FINAL PASSWORD CANDIDATES")
print("="*80)

candidates = [
    ("VurrAj0", "Found in code, contains 'Aj' (part of RAJ)"),
    ("WpGqRn0", "Found near 'Success' keyword"),
    ("raj045735", "Author name from challenge description"),
    ("k8EXiF4", "Next to VurrAj0 in the set- list"),
    ("VXSXFK8", "Before VurrAj0 in the set- list"),
    ("01HTLdE", "Before VXSXFK8 in the set- list"),
]

print("\nTRY THESE IN ORDER:\n")
for i, (pwd, reason) in enumerate(candidates, 1):
    print(f"{i}. {pwd}")
    print(f"   Reason: {reason}\n")

print("="*80)
print("\nMOST LIKELY: VurrAj0")
print("="*80)

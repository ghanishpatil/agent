#!/usr/bin/env python3
"""All password attempts to try"""

passwords = [
    # Based on "raj" hint
    "raj045735",  # Author name
    "raj",
    "RAJ",
    "Raj",
    "raj0",
    "Raj0",
    "RAJ0",
    
    # Found in code
    "VurrAj0",
    "WpGqRn0",
    "k8EXiF4",
    "VXSXFK8",
    "01HTLdE",
    
    # Variations
    "KaalRaj",
    "kaalraj",
    "KAALRAJ",
    "KaalChakr",
    
    # Common patterns
    "password",
    "Password",
    "admin",
    "Admin",
    "123456",
    "raj123",
    "Raj123",
]

print("="*80)
print("ALL PASSWORD ATTEMPTS")
print("="*80)
print("\nTry these passwords in order:\n")

for i, pwd in enumerate(passwords, 1):
    print(f"{i:2d}. {pwd}")

print("\n" + "="*80)
print("MOST LIKELY BASED ON HINT:")
print("- raj045735 (author name)")
print("- VurrAj0 (contains 'Aj')")
print("- WpGqRn0 (found near Success)")
print("="*80)

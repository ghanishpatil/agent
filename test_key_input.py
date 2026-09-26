#!/usr/bin/env python3
import subprocess

exe = r".\challenge_mystery\crackme.exe"

# Test "key" specifically
result = subprocess.run([exe], input=b'key\n', capture_output=True, timeout=2)
print(f"Output: {result.stdout}")
print(f"Stderr: {result.stderr}")

# Also try variations
for test in [b'key', b'key\n', b'key\r\n', b'KEY', b'Key']:
    result = subprocess.run([exe], input=test, capture_output=True, timeout=1)
    if result.stdout:
        print(f"\n[{test}] -> {result.stdout.decode(errors='ignore')}")

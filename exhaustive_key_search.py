#!/usr/bin/env python3
import subprocess
import string
import itertools

exe = r".\challenge_mystery\crackme.exe"

# Try 3-character combinations more systematically
print("[*] Trying 3-character alphanumeric combinations...")

chars = string.ascii_lowercase + string.digits
count = 0

for combo in itertools.product(chars, repeat=3):
    key = ''.join(combo)
    count += 1
    
    try:
        result = subprocess.run(
            [exe],
            input=key + "\n",
            capture_output=True,
            text=True,
            timeout=1
        )
        
        output = result.stdout + result.stderr
        
        # Check for flag
        if "Kaal{" in output:
            print(f"\n[+] FOUND KEY: {key}")
            print(output)
            with open("crackme_solution.txt", "w") as f:
                f.write(f"Key: {key}\n")
                f.write(f"Output:\n{output}\n")
            break
        
        # Check for different response
        if "Wrong" not in output and "Enter key:" in output:
            after = output.split("Enter key:")[-1].strip()
            if after and after != "Wrong key!" and len(after) > 5:
                print(f"\n[?] Interesting response for key '{key}':")
                print(f"    {after[:100]}")
        
        # Progress
        if count % 1000 == 0:
            print(f"  Tried {count} keys... (current: {key})")
            
    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        pass
    
    # Limit search
    if count > 10000:
        print(f"\n[*] Stopped after {count} attempts")
        break

print("\n[*] Search complete")

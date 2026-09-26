#!/usr/bin/env python3
import pikepdf
import itertools

pdf = "Cases/Flag_protected.pdf"

# The 6 fragments
frags = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

wordlist = []

# 1. All permutations (6! = 720)
print("Generating permutations...")
for perm in itertools.permutations(frags):
    wordlist.append("".join(perm))
    wordlist.append("".join([w.lower() for w in perm]))
    wordlist.append(" ".join(perm))
    wordlist.append("_".join(perm))

# 2. With "pass" as hint
base = "".join(frags)
wordlist.extend([
    f"pass{base}",
    f"{base}pass",
    f"PASS{base}",
    f"{base}PASS",
    f"pass{base.lower()}",
    f"{base.lower()}pass",
])

# 3. "pass" between fragments
for i in range(len(frags)):
    parts = frags[:i] + ["pass"] + frags[i:]
    wordlist.append("".join(parts))
    wordlist.append("".join([w.lower() for w in parts]))

# 4. Specific leetspeak on correct order
correct = "VOICECANNOTSILENCEBUTSYSTEMCAN"
leet_variations = [
    "V01C3C4NN075113NC38U75Y573MC4N",
    "v01c3c4nn075113nc38u75y573mc4n",
    "V0!C3C4NN07S!L3NC38U7SYS73MC4N",
    "V01C3_C4NN07_5113NC3_8U7_5Y573M_C4N",
    "V0IC3C4NN0T5IL3NC3BUT5Y5T3MC4N",
    "v0ic3c4nn0t5il3nc3but5y5t3mc4n",
    "V01C3C@NN075!L3NC38U75Y573MC@N",
    "V01C3 C4NN07 5113NC3 8U7 5Y573M C4N",
    "v01c3 c4nn07 5113nc3 8u7 5y573m c4n",
]
wordlist.extend(leet_variations)

# 5. Try different orders with leetspeak
alt_orders = [
    "CANVOICESILENCEBUTSYSTEMCANNOT",
    "SYSTEMCANVOICECANNOTSILENCEBUT",
    "SILENCECANNOTVOICEBUTSYSTEMCAN",
]
for order in alt_orders:
    wordlist.append(order)
    wordlist.append(order.lower())

# Remove duplicates
wordlist = list(dict.fromkeys(wordlist))

print(f"Trying {len(wordlist)} passwords (including all permutations)...")
print("="*60)

for i, pwd in enumerate(wordlist, 1):
    try:
        with pikepdf.open(pdf, password=pwd) as p:
            print(f"\n{'='*80}")
            print(f"SUCCESS! Password: {pwd}")
            print("="*80)
            
            text = ""
            for page in p.pages:
                t = page.extract_text()
                text += t
                print(t)
            
            import re
            flags = re.findall(r'BPCTF\{[^}]+\}', text)
            if flags:
                print(f"\n{'='*80}")
                print(f"FLAG: {flags[0]}")
                print("="*80)
            
            with open("FLAG_RESULT.txt", "w", encoding="utf-8") as f:
                f.write(f"Password: {pwd}\n{'='*80}\n{text}\n")
                if flags:
                    f.write(f"\nFLAG: {flags[0]}\n")
            
            exit(0)
    except:
        pass
    
    if i % 1000 == 0:
        print(f"Tried {i}/{len(wordlist)}...")

print("\nStill not found. The password may require external brute force tools.")
print("Consider using hashcat with GPU acceleration for faster cracking.")

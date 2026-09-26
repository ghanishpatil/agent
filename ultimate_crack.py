#!/usr/bin/env python3
import pikepdf
import itertools

pdf = "Cases/Flag_protected.pdf"

# EVERY possible pattern
wordlist = []

# Base words
words = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]

# 1. All case combinations
for case_func in [str.upper, str.lower, str.capitalize, str.title]:
    wordlist.append(case_func("".join(words)))
    for sep in ["", " ", "_", "-", ".", ":"]:
        wordlist.append(sep.join([case_func(w) for w in words]))

# 2. Camel/Pascal case
wordlist.extend([
    "voiceCannotSilenceButSystemCan",
    "VoiceCannotSilenceButSystemCan",
    "voice_Cannot_Silence_But_System_Can",
])

# 3. Specific leetspeak (common CTF patterns)
leet_full = [
    "V01C3C4NN075113NC38U75Y573MC4N",
    "v01c3c4nn075113nc38u75y573mc4n",
    "V0!C3C4NN07S!L3NC38U7SYS73MC4N",
    "V01C3_C4NN07_5113NC3_8U7_5Y573M_C4N",
    "V0IC3C4NN0T5IL3NC3BUT5Y5T3MC4N",
    "v0ic3c4nn0t5il3nc3but5y5t3mc4n",
]
wordlist.extend(leet_full)

# 4. Initials
wordlist.extend([
    "VCSBSC", "vcsbsc", "V.C.S.B.S.C", "v.c.s.b.s.c",
    "".join([w[0] for w in words]),
    "".join([w[-1] for w in words]),
])

# 5. With affixes
bases = ["VOICECANNOTSILENCEBUTSYSTEMCAN", "voicecannotsilencebutsystemcan"]
for base in bases:
    for pre in ["", "pass", "PASS", "flag", "FLAG", "bpctf", "BPCTF"]:
        for suf in ["", "pass", "PASS", "flag", "FLAG", "123", "!", "2023", "2025"]:
            if pre or suf:
                wordlist.append(f"{pre}{base}{suf}")

# 6. Reversed
wordlist.extend([
    "NACMETSYSTUBECNELISTONNACECIOV",
    "nacmetsystubecnelistonnaceciov",
])

# 7. Partial combinations
for r in range(2, 7):
    for combo in itertools.combinations(words, r):
        wordlist.append("".join(combo))
        wordlist.append("".join([w.lower() for w in combo]))

# 8. CTF context
wordlist.extend([
    "bleedingpress", "BleedingPress", "BLEEDINGPRESS", "bleeding_press",
    "bleedingpressindex", "BleedingPressIndex",
    "veritas", "Veritas", "VERITAS", "RepublicOfVeritas",
    "transparency", "Transparency", "TRANSPARENCY",
    "freedom", "Freedom", "FREEDOM", "pressfreedom", "PressFreedom",
    "stability", "Stability", "STABILITY",
    "alignment", "Alignment", "ALIGNMENT",
    "13days", "13DAYS", "13", "7cases", "sevencases", "7",
    "ArvindRao", "MeeraKhanna", "arvindrao", "meerakhanna",
    "PascalCase", "ShadowCase", "LeetSpeakUnlocks", "LeetSpeak", "leetspeak",
    "case7", "CASE7", "Case7", "case1", "case2", "case3", "case4", "case5", "case6",
])

# 9. Dates and IDs
wordlist.extend([
    "04032023", "12072023", "09062025", "2023", "2025",
    "RV-MI-2023-014", "RV-PF-2025-009",
    "20230304", "20230712", "20250609",
])

# 10. Common passwords
wordlist.extend([
    "password", "Password", "PASSWORD", "123456", "admin", "Admin",
    "password123", "Password123", "admin123",
])

# Remove duplicates
wordlist = list(dict.fromkeys(wordlist))

print(f"Trying {len(wordlist)} passwords...")
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

print("\nPassword not found. May need brute force or external tool.")

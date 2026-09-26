#!/usr/bin/env python3
import pikepdf

passwords = ["VOICE", "CANNOT", "SILENCE", "BUT", "SYSTEM", "CAN"]
msg = "VOICECANNOTSILENCEBUTSYSTEMCAN"

wordlist = [
    # Common CTF patterns
    "V01C3C4NN075113NC38U75Y573MC4N",
    "v01c3c4nn075113nc38u75y573mc4n",
    "V0!C3C4NN07S!L3NC38U7SYS73MC4N",
    "voice_cannot_silence_but_system_can",
    "VoiceCannotSilenceButSystemCan",
    "voiceCannotSilenceButSystemCan",
    # With pass
    "voicecannotsilencebutsystemcanpass",
    "VoiceCannotSilenceButSystemCanpass",
    "VOICECANNOTSILENCEBUTSYSTEMCANPASS",
    # Fragments
    "VCSBSC",
    "vcsbsc",
    # Numbers
    "123456",
    "654321",
    # Case numbers
    "case7",
    "CASE7",
    "Case7",
    # Bleeding press
    "bleedingpress",
    "BleedingPress",
    "BLEEDINGPRESS",
    "bleeding_press",
    # Index
    "index",
    "INDEX",
    "Index",
    # Combined
    "bleedingpressindex",
    "BleedingPressIndex",
    # Republic
    "veritas",
    "Veritas",
    "VERITAS",
    "republicofveritas",
    # Transparency
    "transparency",
    "Transparency",
    # Freedom
    "freedom",
    "Freedom",
    "pressfreedom",
    "PressFreedom",
    # Stability
    "stability",
    "Stability",
    # Alignment
    "alignment",
    "Alignment",
    # 13 days pattern
    "13days",
    "13DAYS",
    # Seven cases
    "sevencases",
    "SevenCases",
    "7cases",
    # Journalist names
    "arvindrao",
    "meerakhanna",
    # Ministry
    "ministry",
    "Ministry",
    # All passwords variations
    "VOICE_CANNOT_SILENCE_BUT_SYSTEM_CAN",
    "Voice_Cannot_Silence_But_System_Can",
]

print(f"Trying {len(wordlist)} CTF-style passwords...")

for pwd in wordlist:
    try:
        with pikepdf.open("Cases/Flag_protected.pdf", password=pwd) as pdf:
            print(f"\n*** FOUND: {pwd} ***\n")
            text = ""
            for page in pdf.pages:
                t = page.extract_text()
                text += t
                print(t)
            
            import re
            flags = re.findall(r'BPCTF\{[^}]+\}', text)
            if flags:
                print("\n" + "="*80)
                print("FLAG:", flags[0])
                print("="*80)
            exit(0)
    except:
        pass

print("None worked. Trying numeric combinations...")

# Try all 6-digit combinations of case numbers
for i in range(1000000):
    pwd = str(i).zfill(6)
    if i % 100000 == 0:
        print(f"Trying {i}...")
    try:
        with pikepdf.open("Cases/Flag_protected.pdf", password=pwd) as pdf:
            print(f"\n*** FOUND: {pwd} ***")
            exit(0)
    except:
        pass

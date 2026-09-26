#!/usr/bin/env python3
"""
Analyze the PDF hash structure to understand password requirements
"""

hash_str = "Flag_protected.pdf:$pdf$2*3*128*-4*1*16*673e550ef0e0dc44bcc60626d49cbe5f*32*546eb2a7fe18d9673752681aec6524c528bf4e5e4e758a4164004e56fffa0108*32*dda83f72209d9c40a42fc76eff707ae60b3691913c9a24b2f078b9c83b2ac2b9"

parts = hash_str.split(':')[1].split('*')

print("PDF Hash Analysis")
print("="*60)
print(f"Format: {parts[0]}")
print(f"Version: {parts[1]}")
print(f"Key length: {parts[2]} bits")
print(f"Permission: {parts[3]}")
print(f"Encrypted metadata: {parts[4]}")
print(f"ID length: {parts[5]}")
print(f"ID: {parts[6]}")
print(f"U length: {parts[7]}")
print(f"U string: {parts[8]}")
print(f"O length: {parts[9]}")
print(f"O string: {parts[10]}")

print("\n" + "="*60)
print("Key Facts:")
print("- 128-bit AES encryption (strong)")
print("- PDF version 2 (modern)")
print("- This requires actual password cracking, not hash reversal")
print("\nThe password could be:")
print("1. A phrase from the case files")
print("2. A date/number pattern")
print("3. A combination of case elements")
print("4. Something completely different")

# Try patterns from case files
import pikepdf

patterns = [
    # Dates
    "04032023", "12072023", "09062025",
    "2023", "2025",
    # Case IDs
    "RV-MI-2023-014", "RV-PF-2025-009",
    # Numbers
    "13", "13days", "13DAYS",
    "7", "7cases", "sevencases",
    # Names
    "ArvindRao", "MeeraKhanna",
    # Locations
    "Veritas", "veritas", "VERITAS",
    # Themes
    "transparency", "Transparency", "TRANSPARENCY",
    "freedom", "Freedom", "FREEDOM",
    "stability", "Stability", "STABILITY",
    "alignment", "Alignment", "ALIGNMENT",
    # Ministry
    "MinistryOfInformationIntegrity",
    "PublicSafetyDirectorate",
    # Combined
    "BleedingPressIndex",
    "bleedingpressindex",
    "bleeding_press_index",
    "TheBleedingPressIndex",
    # Phrases from files
    "PascalCase", "ShadowCase", "LeetSpeakUnlocks",
    "LeetSpeak", "leetspeak",
    # Full message variations
    "VoiceCannotSilenceButSystemCan",
    "voice_cannot_silence_but_system_can",
    "VOICE_CANNOT_SILENCE_BUT_SYSTEM_CAN",
]

print("\n" + "="*60)
print("Trying contextual passwords from case files...")
print("="*60)

for pwd in patterns:
    try:
        with pikepdf.open("Cases/Flag_protected.pdf", password=pwd) as pdf:
            print(f"\n*** SUCCESS: {pwd} ***")
            for page in pdf.pages:
                print(page.extract_text())
            exit(0)
    except:
        pass

print("\nNo match with contextual passwords.")
print("\nTrying numeric patterns...")

# Try years, case numbers, days
for num in [13, 7, 2023, 2025, 42, 38, 14, 18]:
    for pwd in [str(num), f"case{num}", f"Case{num}", f"CASE{num}"]:
        try:
            with pikepdf.open("Cases/Flag_protected.pdf", password=pwd) as pdf:
                print(f"\n*** SUCCESS: {pwd} ***")
                exit(0)
        except:
            pass

print("Numeric patterns failed.")

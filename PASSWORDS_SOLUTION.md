# The Bleeding Press Index - Complete Password Solution

## Challenge Overview
This is a CTF challenge with 7 protected PDF case files plus 1 final Flag PDF. Each case contains a hint for the next password.

---

## All Passwords (In Order)

### Case 1: **UNPROTECTED**
- No password needed
- Hint found: "Pascal Case" + Subject name "Arvind Rao"

### Case 2: **ArvindRao**
- Format: PascalCase (FirstLetterCapitalized, no spaces)
- Hint found: "Pass: CANNOT"

### Case 3: **CANNOT**
- Direct password given at end of Case 2
- Hint found: "SILENCE"

### Case 4: **SILENCE**
- Direct password given at end of Case 3
- Hint found: "BUT"

### Case 5: **BUT**
- Direct password given at end of Case 4
- Hint found: "SYSTEM"

### Case 6: **SYSTEM**
- Direct password given at end of Case 5
- Hint found: "CAN" + "6 case password fragments are pass"

### Case 7: **CAN**
- Direct password given at end of Case 6
- Hint found: "LeetSpeak Unlocks"

### Flag PDF: **UNKNOWN (Still Cracking)**
- Hint: "LeetSpeak Unlocks" from Case 7
- The 6 password fragments are: VOICE, CANNOT, SILENCE, BUT, SYSTEM, CAN
- Combined message: "VOICE CANNOT SILENCE BUT SYSTEM CAN"

---

## Flag Password Attempts

Based on the hints, the Flag password is likely a leetspeak variation of the combined message.

### Top Candidates:
1. `V01C3C4NN075113NC38U75Y573MC4N` (full leetspeak)
2. `v01c3c4nn075113nc38u75y573mc4n` (lowercase leetspeak)
3. `V0!C3C4NN07S!L3NC38U7SYS73MC4N` (with special chars)
4. `VOICECANNOTSILENCEBUTSYSTEMCAN` (no leetspeak)
5. `voicecannotsilencebutsystemcan` (lowercase)
6. `VoiceCannotSilenceButSystemCan` (PascalCase)

### Leetspeak Mapping Used:
- A → 4 or @
- E → 3
- I → 1 or !
- O → 0
- S → 5
- T → 7
- B → 8
- C → (

---

## How to Crack the Flag

### Method 1: Run the fast cracker
```bash
python fast_crack.py
```

### Method 2: Manual attempt with pikepdf
```python
import pikepdf
pdf = pikepdf.open("Cases/Flag_protected.pdf", password="YOUR_PASSWORD")
```

### Method 3: Use John the Ripper (if installed)
```bash
# Extract hash
python -c "import pikepdf; print(pikepdf.Pdf.open('Cases/Flag_protected.pdf'))"

# Run john
john --wordlist=custom_wordlist.txt flag_hash.txt
```

---

## Pattern Analysis

### Common Theme:
- All cases involve journalists who died 13 days after publishing investigations
- The message "VOICE CANNOT SILENCE BUT SYSTEM CAN" represents the theme
- Each case gave one word of the final message

### Password Pattern:
- Case 1 → Case 2: Transformation (PascalCase)
- Case 2 → Case 7: Direct words
- Case 7 → Flag: Transformation (LeetSpeak)

---

## Scripts Available

1. `fast_crack.py` - Fast comprehensive password cracker
2. `bleeding_press_solver.py` - Full chain solver with analysis
3. `brute_force_flag.py` - Brute force with variations
4. `ctf_patterns.py` - CTF-style pattern attempts

---

## Time Estimate

- Wordlist attempts: ~1-5 seconds
- Numeric brute force (if needed): Could take hours/days
- Recommended: Focus on leetspeak variations first

---

## Next Steps

Run `python fast_crack.py` to attempt all variations automatically.

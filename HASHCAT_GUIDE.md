# Hashcat Guide - Cracking the Flag PDF

## Step 1: Install Hashcat

### Windows:
1. Download from: https://hashcat.net/hashcat/
2. Extract to a folder (e.g., `C:\hashcat`)
3. No installation needed - it's portable

### Quick Download:
```powershell
# Download latest version
Invoke-WebRequest -Uri "https://hashcat.net/files/hashcat-6.2.6.7z" -OutFile "hashcat.7z"

# Extract (requires 7-Zip)
7z x hashcat.7z
```

---

## Step 2: Prepare Your Hash File

You already have the hash! It's in `pdf.hash`:

```
Flag_protected.pdf:$pdf$2*3*128*-4*1*16*673e550ef0e0dc44bcc60626d49cbe5f*32*546eb2a7fe18d9673752681aec6524c528bf4e5e4e758a4164004e56fffa0108*32*dda83f72209d9c40a42fc76eff707ae60b3691913c9a24b2f078b9c83b2ac2b9
```

---

## Step 3: Identify Hash Type

PDF hash type in hashcat: **10500** (PDF 1.4 - 1.6 (Acrobat 5 - 8))

---

## Step 4: Run Hashcat

### Option A: With Wordlist (Fastest)
```powershell
# Navigate to hashcat folder
cd C:\hashcat

# Run with your wordlist
.\hashcat.exe -m 10500 -a 0 "C:\path\to\pdf.hash" "C:\path\to\flag_wordlist.txt"
```

### Option B: Brute Force (Slower)
```powershell
# Try all combinations up to 8 characters
.\hashcat.exe -m 10500 -a 3 "C:\path\to\pdf.hash" ?a?a?a?a?a?a?a?a

# Explanation:
# -m 10500 = PDF hash type
# -a 3 = Brute force attack
# ?a = Any character (letters, numbers, symbols)
```

### Option C: Mask Attack (Smart Brute Force)
```powershell
# If you know the pattern, e.g., starts with uppercase, ends with numbers
.\hashcat.exe -m 10500 -a 3 "C:\path\to\pdf.hash" ?u?l?l?l?d?d?d

# Mask characters:
# ?l = lowercase letter
# ?u = uppercase letter
# ?d = digit
# ?s = special character
# ?a = any character
```

### Option D: Rule-Based Attack
```powershell
# Use rules to modify wordlist (leetspeak, etc.)
.\hashcat.exe -m 10500 -a 0 -r rules\best64.rule "C:\path\to\pdf.hash" "C:\path\to\flag_wordlist.txt"
```

---

## Step 5: For Your Specific Case

### Quick Command (from your current directory):
```powershell
# If hashcat is in C:\hashcat
C:\hashcat\hashcat.exe -m 10500 -a 0 pdf.hash flag_wordlist.txt

# With rules for leetspeak variations
C:\hashcat\hashcat.exe -m 10500 -a 0 -r C:\hashcat\rules\leetspeak.rule pdf.hash flag_wordlist.txt
```

### Create a Larger Wordlist First:
```powershell
# Combine all our attempts
type flag_wordlist.txt custom_wordlist.txt > mega_wordlist.txt

# Then run hashcat
C:\hashcat\hashcat.exe -m 10500 -a 0 pdf.hash mega_wordlist.txt
```

---

## Step 6: Monitor Progress

While running, hashcat shows:
- Speed (H/s = hashes per second)
- Progress percentage
- Estimated time remaining
- Temperature (if using GPU)

Press `s` for status update while running.

---

## Step 7: View Results

If password is found:
```powershell
# Check the potfile (stores cracked passwords)
type C:\hashcat\hashcat.potfile

# Or show results
C:\hashcat\hashcat.exe -m 10500 pdf.hash --show
```

---

## Common Hashcat Commands

```powershell
# Show help
.\hashcat.exe --help

# List all hash types
.\hashcat.exe --example-hashes | findstr PDF

# Benchmark your system
.\hashcat.exe -b -m 10500

# Resume a session
.\hashcat.exe --session=pdf_crack --restore
```

---

## Performance Tips

1. **Use GPU**: Much faster than CPU
   - Add `--force` if you get OpenCL errors
   - Add `-w 3` for maximum workload (may slow down PC)

2. **Optimize Workload**:
   ```powershell
   .\hashcat.exe -m 10500 -a 0 -w 3 --force pdf.hash flag_wordlist.txt
   ```

3. **Use Multiple Wordlists**:
   ```powershell
   # Combine wordlists
   cat wordlist1.txt wordlist2.txt wordlist3.txt > combined.txt
   ```

---

## Expected Speed

- **CPU only**: ~1,000 - 10,000 H/s
- **GPU (GTX 1060)**: ~50,000 - 100,000 H/s
- **GPU (RTX 3080)**: ~500,000+ H/s

PDF hashes are relatively slow to crack due to strong encryption.

---

## If Hashcat Doesn't Work

### Alternative: Use John the Ripper (already installed)
```powershell
# You already have John installed!
.\john\john-1.9.0-jumbo-1-win64\run\john.exe --wordlist=flag_wordlist.txt pdf.hash

# With rules
.\john\john-1.9.0-jumbo-1-win64\run\john.exe --wordlist=flag_wordlist.txt --rules pdf.hash

# Incremental mode (brute force)
.\john\john-1.9.0-jumbo-1-win64\run\john.exe --incremental pdf.hash
```

---

## Troubleshooting

### Error: "No devices found"
- Install GPU drivers
- Use `--force` flag
- Fall back to CPU: add `-D 1`

### Error: "Separator unmatched"
- Check hash format in pdf.hash
- Should be: `filename:$pdf$2*3*128*...`

### Too Slow?
- Reduce max length: `--increment --increment-max=10`
- Use smaller charset: `?l?l?l?l?l?l` instead of `?a?a?a?a?a?a`
- Try online services (not recommended for sensitive data)

---

## Quick Start Script

Save this as `crack_pdf.bat`:

```batch
@echo off
echo Starting PDF crack...
echo.

REM Update these paths
set HASHCAT=C:\hashcat\hashcat.exe
set HASH=pdf.hash
set WORDLIST=flag_wordlist.txt

echo [1/3] Trying wordlist...
%HASHCAT% -m 10500 -a 0 %HASH% %WORDLIST%

echo [2/3] Trying with rules...
%HASHCAT% -m 10500 -a 0 -r rules\best64.rule %HASH% %WORDLIST%

echo [3/3] Trying brute force (8 chars)...
%HASHCAT% -m 10500 -a 3 %HASH% ?a?a?a?a?a?a?a?a

echo.
echo Done! Check results:
%HASHCAT% -m 10500 %HASH% --show

pause
```

Then run: `crack_pdf.bat`

---

## Next Steps

1. Download hashcat
2. Run: `hashcat.exe -m 10500 -a 0 pdf.hash flag_wordlist.txt`
3. Wait for results
4. If found, use password to open Flag_protected.pdf

Good luck! 🔓

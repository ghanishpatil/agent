# Hashcat on Kali Linux - PDF Cracking Guide

## Step 1: Check if Hashcat is Already Installed

Kali Linux usually comes with hashcat pre-installed:

```bash
# Check if installed
hashcat --version

# If not installed
sudo apt update
sudo apt install hashcat -y
```

---

## Step 2: Prepare Your Hash File

You already have `pdf.hash` with this content:
```
Flag_protected.pdf:$pdf$2*3*128*-4*1*16*673e550ef0e0dc44bcc60626d49cbe5f*32*546eb2a7fe18d9673752681aec6524c528bf4e5e4e758a4164004e56fffa0108*32*dda83f72209d9c40a42fc76eff707ae60b3691913c9a24b2f078b9c83b2ac2b9
```

---

## Step 3: Basic Hashcat Commands for Kali

### Option A: Wordlist Attack (Fastest)
```bash
# Basic wordlist attack
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt

# With status updates
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt --status

# Force if you get warnings
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt --force
```

### Option B: With Rules (Leetspeak, etc.)
```bash
# Use best64 rule (common transformations)
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt -r /usr/share/hashcat/rules/best64.rule

# Use leetspeak rule
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt -r /usr/share/hashcat/rules/leetspeak.rule

# Use multiple rules
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt -r /usr/share/hashcat/rules/best64.rule -r /usr/share/hashcat/rules/toggles1.rule
```

### Option C: Brute Force Attack
```bash
# Brute force up to 8 characters (any character)
hashcat -m 10500 -a 3 pdf.hash ?a?a?a?a?a?a?a?a

# Only letters and numbers (faster)
hashcat -m 10500 -a 3 pdf.hash ?1?1?1?1?1?1?1?1 -1 ?l?u?d

# Incremental (start from 1 char, go up to 8)
hashcat -m 10500 -a 3 pdf.hash ?a?a?a?a?a?a?a?a --increment --increment-min=1 --increment-max=8
```

### Option D: Mask Attack (Pattern-Based)
```bash
# If password starts with uppercase, rest lowercase
hashcat -m 10500 -a 3 pdf.hash ?u?l?l?l?l?l?l?l

# Mixed case with numbers at end
hashcat -m 10500 -a 3 pdf.hash ?u?l?l?l?l?d?d?d

# Mask characters:
# ?l = lowercase (a-z)
# ?u = uppercase (A-Z)
# ?d = digit (0-9)
# ?s = special (!@#$%...)
# ?a = all characters
```

---

## Step 4: Use Kali's Built-in Wordlists

Kali has massive wordlists pre-installed:

```bash
# Use rockyou.txt (most popular)
hashcat -m 10500 -a 0 pdf.hash /usr/share/wordlists/rockyou.txt

# Combine with your custom wordlist
cat flag_wordlist.txt /usr/share/wordlists/rockyou.txt > combined.txt
hashcat -m 10500 -a 0 pdf.hash combined.txt

# Use multiple wordlists
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt /usr/share/wordlists/rockyou.txt
```

---

## Step 5: Optimize for Speed

```bash
# Maximum workload (may slow down system)
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt -w 4

# Use GPU only (faster)
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt -D 2

# Use CPU only
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt -D 1

# Show benchmark
hashcat -b -m 10500
```

---

## Step 6: Monitor Progress

While hashcat is running:
- Press `s` = Show status
- Press `p` = Pause
- Press `r` = Resume
- Press `q` = Quit (saves progress)

```bash
# Run in background with screen
screen -S hashcat
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt
# Press Ctrl+A then D to detach

# Reattach later
screen -r hashcat
```

---

## Step 7: Check Results

```bash
# Show cracked passwords
hashcat -m 10500 pdf.hash --show

# Check potfile (stores all cracked hashes)
cat ~/.hashcat/hashcat.potfile

# Or
cat ~/.local/share/hashcat/hashcat.potfile
```

---

## Complete Attack Strategy

Run these commands in order:

```bash
# 1. Quick wordlist check
echo "[1/5] Trying custom wordlist..."
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt --force

# 2. With rules
echo "[2/5] Trying with best64 rules..."
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt -r /usr/share/hashcat/rules/best64.rule --force

# 3. Rockyou wordlist
echo "[3/5] Trying rockyou.txt..."
hashcat -m 10500 -a 0 pdf.hash /usr/share/wordlists/rockyou.txt --force

# 4. Mask attack (common patterns)
echo "[4/5] Trying mask attack..."
hashcat -m 10500 -a 3 pdf.hash ?u?l?l?l?l?l?l?l --increment --increment-min=6 --increment-max=12 --force

# 5. Full brute force (last resort)
echo "[5/5] Trying brute force..."
hashcat -m 10500 -a 3 pdf.hash ?a?a?a?a?a?a?a?a --increment --increment-min=1 --increment-max=8 --force

# Check if found
hashcat -m 10500 pdf.hash --show
```

---

## Create an Automated Script

Save as `crack_pdf.sh`:

```bash
#!/bin/bash

HASH="pdf.hash"
WORDLIST="flag_wordlist.txt"

echo "=========================================="
echo "PDF Password Cracker"
echo "=========================================="
echo ""

# Check if hash file exists
if [ ! -f "$HASH" ]; then
    echo "Error: $HASH not found!"
    exit 1
fi

# Attack 1: Custom wordlist
echo "[1/4] Wordlist attack..."
hashcat -m 10500 -a 0 "$HASH" "$WORDLIST" --force --quiet
if hashcat -m 10500 "$HASH" --show 2>/dev/null | grep -q "Flag_protected"; then
    echo "PASSWORD FOUND!"
    hashcat -m 10500 "$HASH" --show
    exit 0
fi

# Attack 2: With rules
echo "[2/4] Wordlist + rules..."
hashcat -m 10500 -a 0 "$HASH" "$WORDLIST" -r /usr/share/hashcat/rules/best64.rule --force --quiet
if hashcat -m 10500 "$HASH" --show 2>/dev/null | grep -q "Flag_protected"; then
    echo "PASSWORD FOUND!"
    hashcat -m 10500 "$HASH" --show
    exit 0
fi

# Attack 3: Rockyou
echo "[3/4] Rockyou wordlist..."
if [ -f /usr/share/wordlists/rockyou.txt ]; then
    hashcat -m 10500 -a 0 "$HASH" /usr/share/wordlists/rockyou.txt --force --quiet
    if hashcat -m 10500 "$HASH" --show 2>/dev/null | grep -q "Flag_protected"; then
        echo "PASSWORD FOUND!"
        hashcat -m 10500 "$HASH" --show
        exit 0
    fi
fi

# Attack 4: Mask attack
echo "[4/4] Mask attack (this may take a while)..."
hashcat -m 10500 -a 3 "$HASH" ?a?a?a?a?a?a?a?a --increment --increment-min=6 --increment-max=10 --force --quiet

# Final check
echo ""
echo "=========================================="
if hashcat -m 10500 "$HASH" --show 2>/dev/null | grep -q "Flag_protected"; then
    echo "PASSWORD FOUND!"
    hashcat -m 10500 "$HASH" --show
else
    echo "Password not found. Try longer brute force."
fi
echo "=========================================="
```

Make it executable and run:
```bash
chmod +x crack_pdf.sh
./crack_pdf.sh
```

---

## Alternative: John the Ripper (Also Pre-installed in Kali)

```bash
# Basic attack
john --format=PDF pdf.hash

# With wordlist
john --wordlist=flag_wordlist.txt --format=PDF pdf.hash

# With rules
john --wordlist=flag_wordlist.txt --rules --format=PDF pdf.hash

# Show cracked passwords
john --show --format=PDF pdf.hash

# Resume interrupted session
john --restore
```

---

## Troubleshooting

### "No devices found" or OpenCL errors
```bash
# Force CPU mode
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt --force -D 1

# Install OpenCL
sudo apt install ocl-icd-libopencl1 nvidia-opencl-icd
```

### "Separator unmatched"
```bash
# Check hash format
cat pdf.hash

# Should be: filename:$pdf$2*3*128*...
# If wrong, recreate it
```

### Too slow?
```bash
# Reduce search space
hashcat -m 10500 -a 3 pdf.hash ?l?l?l?l?l?l --increment-min=4 --increment-max=6

# Use faster hash mode if possible
# PDF is inherently slow due to strong encryption
```

---

## Quick Start (Copy-Paste)

```bash
# Install if needed
sudo apt install hashcat -y

# Run basic attack
hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt --force

# Check result
hashcat -m 10500 pdf.hash --show
```

---

## Expected Performance on Kali

- **VM without GPU**: 100-1,000 H/s (very slow)
- **VM with GPU passthrough**: 10,000-100,000 H/s
- **Native with GPU**: 100,000-1,000,000+ H/s

PDF hashes are computationally expensive, so be patient!

---

## Next Steps

1. Open terminal in Kali
2. Navigate to your files: `cd /path/to/files`
3. Run: `hashcat -m 10500 -a 0 pdf.hash flag_wordlist.txt --force`
4. Wait for results
5. Check: `hashcat -m 10500 pdf.hash --show`

Good luck! 🐉

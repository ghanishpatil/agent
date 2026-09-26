#!/bin/bash
# Skipfish Comprehensive Web Application Security Scanner
# Single command to perform complete vulnerability assessment

TARGET="https://team-t1-wargames.vercel.app"
OUTPUT_DIR="skipfish_results_$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "Skipfish Comprehensive Security Scan"
echo "=========================================="
echo "Target: $TARGET"
echo "Output: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Full comprehensive scan with all options
skipfish \
  -o "$OUTPUT_DIR" \
  -S /usr/share/skipfish/dictionaries/complete.wl \
  -W /usr/share/skipfish/dictionaries/extensions-only.wl \
  -Y \
  -O \
  -U \
  -G 256 \
  -m 5 \
  -t 20 \
  -w 60 \
  -i 60 \
  -l 200 \
  -g 25 \
  -k 10 \
  -I ashishtest1@gmail.com:123456789 \
  -C "session_cookie=value" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -X /logout \
  -X /signout \
  -S /usr/share/skipfish/dictionaries/complete.wl \
  --config /etc/skipfish/skipfish.conf \
  "$TARGET"

echo ""
echo "=========================================="
echo "Scan Complete!"
echo "Results saved to: $OUTPUT_DIR"
echo "Open $OUTPUT_DIR/index.html in browser"
echo "=========================================="

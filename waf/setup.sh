#!/bin/bash
cd /work/waf
cp "/work/handout (3).zip" h.zip
unzip -o h.zip >/dev/null 2>&1
echo "=== ls ==="
ls -la waf/
echo "=== Dockerfile ==="
cat waf/Dockerfile
echo "=== file ==="
file waf/chal
echo "=== checksec ==="
checksec --file=waf/chal 2>/dev/null

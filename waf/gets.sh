#!/bin/bash
cd /work/waf/waf
echo "=== __gets disasm ==="
objdump -d -M intel chal | awk '/<__gets>:/{f=1} f{print} /<main>:/{if(f)exit}'
echo "=== rodata strings around 0x402008..0x402060 ==="
objdump -s -j .rodata chal

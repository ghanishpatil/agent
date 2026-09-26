#!/bin/bash
cd /work/waf/waf
# Inspect register state at main's ret (0x401373) with a simple "exit" input.
cat > /tmp/rr.py <<'PY'
from pwn import *
context.binary = "./chal"; context.log_level="error"
p = process("./chal")
# send "exit"+padding to reach ret, but first just observe regs at ret with clean exit
gdb_script = "b *0x401373\ncommands\ninfo registers rdi rsi rdx rsp rbp\nx/8gx $rsp\nquit\nend\ncontinue\n"
PY
# Simpler: use gdb batch
printf 'exit\n' > /tmp/in.txt
gdb -q -batch \
 -ex 'break *0x401373' \
 -ex 'run < /tmp/in.txt' \
 -ex 'printf "RDI=%#lx RSI=%#lx RDX=%#lx RAX=%#lx\n", $rdi,$rsi,$rdx,$rax' \
 -ex 'printf "RBP=%#lx RSP=%#lx\n", $rbp,$rsp' \
 -ex 'x/4gx $rdi' \
 ./chal 2>&1 | grep -vE "warning|Thread|Using|pwndbg|created|loaded|Detected|Updating" | head -30

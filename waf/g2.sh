#!/bin/bash
cd /work/waf/waf
echo "=== ALL GADGETS ==="
ROPgadget --binary chal | sort -u
echo "=== count ==="
ROPgadget --binary chal | wc -l
echo "=== pop rdi/rsi/rdx/rax search ==="
ROPgadget --binary chal | grep -Ei "pop (rdi|rsi|rdx|rax|rcx|r8|r9)" || echo none
echo "=== mov/xchg/add rsp ==="
ROPgadget --binary chal | grep -Ei "mov .*\[|xchg|add rsp|pop rsp|call|jmp" || echo none
echo "=== syscall/int ==="
ROPgadget --binary chal | grep -Ei "syscall|int 0x80|sysenter" || echo none

#!/bin/bash
cd /work/waf/waf
echo "=== ROPgadget (pop/syscall/leave) ==="
ROPgadget --binary chal 2>/dev/null | grep -iE ": pop (rdi|rsi|rdx|rax|rbp)|: syscall|: leave|: ret$|pop rsp|: pop r|xchg" | head -60
echo "=== total gadget count ==="
ROPgadget --binary chal 2>/dev/null | wc -l
echo "=== .bss/.data writable addrs ==="
readelf -S chal 2>/dev/null | grep -Ei "bss|data|got"
echo "=== symbols addresses ==="
nm chal | grep -Ei "gets|main|read|printf|puts"

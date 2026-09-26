#!/usr/bin/env python3
from pwn import *
context.binary = ELF("/work/waf/waf/chal", checksec=False)
context.arch='amd64'

# Inspect register state at main's ret (0x401373) using gdb, with a simple 'exit' input
gdbscript = '''
set pagination off
break *0x401373
run
info registers rdi rsi rdx rax rbp rsp rcx
x/8gx $rsp
telescope $rsp 8
continue
quit
'''

p = process("/work/waf/waf/chal")
# send 'exit' + newline so strncmp==0 and we hit the ret
# But __gets first call reads 0x80. We send just 'exit' padded a little.
# Actually to reach ret cleanly with minimal overflow, send exactly 'exit\x00...'
p.sendline(b"exit")
# run under gdb separately; here just interact
print(p.recvall(timeout=2))

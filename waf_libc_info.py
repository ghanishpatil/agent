from pwn import *
libc=ELF("/work/waf_chal/libc.so.6")
print("libc version str:")
import re
data=open("/work/waf_chal/libc.so.6","rb").read()
for m in re.finditer(rb"GNU C Library[^\n\x00]*", data):
    print(m.group()[:120]); break
print("system", hex(libc.symbols['system']))
print("str_bin_sh", hex(next(libc.search(b"/bin/sh"))))
print("__libc_start_main", hex(libc.symbols.get('__libc_start_main',0)))
print("__libc_start_call_main (approx via symbols?)", )
for s in ['__libc_start_main','__libc_start_call_main','printf','puts','read','open','write','execve']:
    if s in libc.symbols: print(s, hex(libc.symbols[s]))

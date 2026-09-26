#!/usr/bin/env python3
import os
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="error"
BIN="/work/bigwin/chal_np"

cases = {
  "k6probe(3s)": [0,0,0,0,0,0,67]+[3]*20,
  "mine":        [0,0,0,0,0,0,67,100,500,-2,0,0,0,0,0,0,0,0],
}
for label, seq in cases.items():
    p = process(BIN)
    p.sendline("\n".join(str(x) for x in seq).encode())
    out = p.recvall(timeout=2).decode(errors="replace")
    p.close()
    print(f"{label}: prompts={out.count('number>')} naughty={out.count('naughty')} "
          f"win={'WIN' if 'wtf' in out else 'lose'}")
    print("   tail:", out.strip().splitlines()[-1][:60] if out.strip() else "")

#!/usr/bin/env python3
import os
os.environ["TERM"]="xterm"
from pwn import *
context.log_level="error"
BIN="/work/bigwin/chal_np"

def try_seq(ints, timeout=2):
    p=process(BIN)
    p.sendline("\n".join(str(x) for x in ints).encode())
    try: out=p.recvall(timeout=timeout).decode(errors="replace")
    except: out=""
    p.close()
    return out

def won(out): return "wtf you win" in out or "fopen" in out or "No such file" in out

# First, empirically determine at which fed-index the accum==67 skip fires, and how i behaves.
# Feed values that make accum==67 at position k (k=0..6) and observe number of prompts.
def prompts(out): return out.count("number>")
def naughty(out): return out.count("naughty")

print("== probe: make accum hit 67 at index k ==")
for k in range(0,7):
    seq=[0]*k + [67] + [3]*20   # accum becomes 67 exactly after writing index k
    out=try_seq(seq)
    print(f"k={k}: prompts={prompts(out)} naughty={naughty(out)} won={won(out)} tail={out.strip().splitlines()[-1][:40] if out.strip() else ''}")

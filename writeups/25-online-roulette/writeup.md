# online-roulette — K17 CTF (pwn, beginner, 304 pts, 15 solves)

**Flag format:** `K17{...}`  **Service:** `nc chal.secso.cc 4000`  **Win:** reach `win()` (prints `/flag`) by making `balance > 999999999`.

## Recon / Rule Zero on chal.c
- `main`: `balance=10`; reads `name_length` (uint8, must be ≤20); calls `game(&balance)`; at the end `if (balance > 999999999) win();`.
- `game`: gives an **arbitrary 1-byte write** but only if `addr <= &wager` (else "intruder neutralised"); then a gambling loop: `*balance -= wager; lotto=rand()%36+1; if(lotto==1) *balance += 2*wager; if(*balance<0) return;`.
- `SNAPSHOT()` = `int3`; remote prints a stack dump.

## Snapshot leak (key facts)
Non-PIE (`ret=0x401566`, `0x403df0`), and `balance (=0x0000000a)` sits **above** `&wager`:
```
0x…160 rsp[game] … 0x…190 rbp[game] … 0x…1cc balance=0x0000000a … 0x…1d0 rbp[main]
```
So `addr <= &wager` can NOT write `balance` (it's higher up main's frame). The 1-byte write is a red herring for this goal; the intended path is the RNG.

## Key insight
Win a spin ⇒ `balance += 2*wager - wager = +wager`. Bet `wager = 1,000,000,000` on the **first spin**:
- `2*wager = 2e9 < INT_MAX` (no int overflow).
- Win: `balance = 10 - 1e9 + 2e9 = 1000000010 > 999999999` → `win()`.
- Lose: `balance = 10 - 1e9 < 0` → "no more money", round ends, no flag.

`rand()%36==0` ⇒ win, probability 1/36 per fresh connection (seed = `time(NULL)`). No seed prediction needed — just **reconnect until the first spin wins** (~36 tries). Skip the write step with `addr = 0xffffffffffffffff` (> `&wager` → "intruder neutralised").

## Exploit (per connection)
1. `name to be?` → `20`
2. `[addr]>` → `ffffffffffffffff`  (neutralised, no write)
3. `wager>` → `1000000000`
4. read spin: `congrats` ⇒ win; `better luck`/`no more money` ⇒ close & retry.
5. On win: `wager>` → `0` (quit) → name prompt → any name → server runs `win()` → `K17{...}`.
Loop connections until `K17{` appears.

## Verification
Self-validating: the server prints `/flag` only after `win()`, which only fires on a genuine `balance>999999999`.

## Generalization (CLASS + TELL)
- **Class:** *predictable-RNG / probabilistic pwn where one lucky event suffices.* When the win needs a rare RNG event but the event is cheap to retry (fresh `srand(time)` per connection) and one hit ends the challenge, **brute-force reconnect** beats modeling the PRNG.
- **TELL:** `srand(time(NULL))` + a payout that, on a single win with a large stake, overflows/leaps a comparison threshold; and losing just ends the session cleanly (no penalty to retrying).
- Watch **int overflow limits** when choosing the stake (`2*wager` must stay < INT_MAX): `1e9` is the sweet spot here.
- Also logged: an "arbitrary write" gated by `addr <= &stackvar` is *almost-arbitrary* (stack is high, so everything below—GOT/libc—is writable), but it can't reach variables ABOVE it in caller frames; confirm target reachability against the leaked layout before committing.

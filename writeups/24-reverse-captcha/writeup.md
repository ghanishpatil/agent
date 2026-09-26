# reverse captcha — K17 CTF (web, beginner, 196 pts, 41 solves)

**Flag:** `K17{y0u_w1ll_noW_b3_sp@red_froM_tHe_AI_rev0lu+1on}`
**URL:** `https://reverse-captcha.unswsecsoc.workers.dev` (Cloudflare Worker, static frontend)

## Recon
Root page loads `app.js` and shows a popup: "prove you're a robot by solving timed challenges."
`/flag`, `/api`, `/captcha` → 404. Everything is in `app.js` (client-side).

`app.js` logic:
- `generateChallenge()` produces one of 8 hard/timed math tasks (sqrt to 5dp, sum of first N digits of pi, ln, SHA-256, definite integral, IEEE float add, vector component, rhombicosidodecahedron volume).
- Answer 10 in a row (`requiredCorrect`) within a shrinking timer → `state="complete"` → `printFlag()`.

## Key insight — the CAPTCHA is a decoy
`printFlag()` doesn't fetch anything; it **derives the flag locally** by XOR-decoding an embedded array:
```js
function printFlag(){
  if(state!=="complete"||numCorrect<10) return false;
  const _0x91=[0x25,0x71,...,0x45];             // 50 bytes
  let _0x42=0x35+state.length*0x11;             // seed depends ONLY on state.length
  const _0x17=new TextDecoder().decode(Uint8Array.from(_0x91,(b,i)=>{
    _0x42=(_0x42*0x21+i+0x11)&0xff; return b^_0x42;
  }));
  ...
}
```
The decode depends only on `state.length`, and the guard forces `state==="complete"` (length 8).
So the flag is fully determined — **no need to solve any challenge**. (You could also just paste
`state="complete";numCorrect=10;printFlag()`-equivalent, or set a JS breakpoint, but reproducing
the decode offline is cleanest.)

## Solve (offline, deterministic)
```python
arr=[0x25,0x71,0x64,0xbc,0xc5,0x62,0xdc,0xbe,0x6d,0x45,0x63,0x67,0xd7,0xc8,0xea,0x12,
     0x59,0x8a,0x38,0xd0,0xe7,0x4a,0xe1,0x9b,0x57,0xf8,0x18,0x35,0x92,0x61,0xb0,0x92,
     0xea,0xd8,0xa6,0x08,0x2d,0x6b,0xc6,0x83,0x2f,0xb2,0x4f,0xf7,0x4d,0x5d,0x44,0x3a,0x58,0x45]
k=(0x35+len("complete")*0x11)&0xff   # 0xBD
out=bytearray()
for i,b in enumerate(arr):
    k=(k*0x21+i+0x11)&0xff
    out.append(b^k)
print(out.decode())   # K17{y0u_w1ll_noW_b3_sp@red_froM_tHe_AI_rev0lu+1on}
```

## Verification
Output is a valid `K17{...}` flag, fully printable, coherent on-theme text ("you will now be
spared from the AI revolution") — matches the challenge's AI-overlord story. The decode is a
byte-exact reproduction of the site's own `printFlag()` (same `*0x21`, `+i+0x11`, `&0xff`, XOR,
UTF-8), so it IS the author's flag, not a guess.

## Generalization (the CLASS + the TELL)
- **Class:** *Client-side flag / obfuscated-in-JS reveal.* When a web challenge's flag is shown by
  frontend JS after some gate, the "gate" (here: solving timed CAPTCHAs) is usually irrelevant —
  the flag is embedded and computable directly.
- **The TELL:** the reveal function does NOT call `fetch`/XHR to a server — it builds the flag from
  a local array/keystream (`String.fromCharCode`, `TextDecoder`, XOR loops, `_0xNN` obfuscation).
  Read `app.js`, find the reveal function, and reproduce its decode offline (or run it in the
  console / set the completion state). Never grind the intended task.
- **Fast path:** grep the JS for `flag`, `TextDecoder`, `fromCharCode`, `^`, hex-array literals; the
  keystream seed is often a tiny constant expression (here `state.length`).

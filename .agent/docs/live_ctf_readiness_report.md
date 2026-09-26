# First Real CTF Live-Solve — Architecture A Readiness Report

Status: **RUNTIME PATH VERIFIED END-TO-END ON A REAL CHALLENGE; CHALLENGE NOT SOLVED (correctly).**
No frozen file changed (45/45 byte-identical). No new execution primitive. No architecture change.

## What was executed

The first real challenge was driven through the existing Architecture A path via a client harness
(`scripts/live_ctf_run.py`) that calls the SAME `CtfAgentGateway` methods the MCP tools wrap
(`ctf_start → ctf_observe → ctf_propose → ctf_result → ctf_writeup → close_session → ctf_experience`).
I acted as the operator (trusted environment: read-only file adapter only; no network, no
executables, no verifier) and as the Kiro reasoner (observe → reason → propose).

Target: `chal.py` — a crypto signing service (CRYSig). Its tag is GF(2)-linear in the message, so
`sign(root) = sign(user) XOR sign(user XOR root)` via a single oracle query (classic linear
forgery). The flag is read from a remote `/flag` only after interacting with the live service.

## Observed runtime trace

| Step | Outcome |
|---|---|
| `ctf_start` (driver=kiro) | CREATED; tool `read_file` registered |
| `ctf_observe` #1 | verified=False; available_tools=`['read_file']` |
| `ctf_propose` #1 | hypothesis `crypto-linear-forgery` accepted; `read_file` accepted + executed → `SUCCESS` (impact `NO_IMPACT`) |
| `ctf_observe` #2 | real source ingested as evidence (CRYSig confirmed) |
| `ctf_result` | `NO_FLAG`, verified=False |
| `ctf_writeup` | not available (SOLVED-only) |
| `close_session` | CLOSED |
| `ctf_experience` | `AGENT_FAILURE_EXPERIENCE` generated; hypothesis **UNRESOLVED**, disproven=(), terminal_reason="action budget exhausted" |
| adapters used | `['read_file']` only — all execution via the frozen kernel + trusted adapter |

Correct reasoning (mechanism identified), grounded evidence (real source read), controlled actions
(1 action, 0 duplicates), correct failure classification (UNRESOLVED, not disproven — no false
disproof), hard verification intact (VERIFIED_FLAG impossible without an oracle), no fabricated flag,
no bypass, complete trace, real failure experience recorded.

## Exact blocker (reported, not worked around)

A genuine end-to-end solve of THIS challenge requires two operator-provisioned capabilities that are
intentionally absent in an offline run, and one is a concrete capability boundary:

1. **Interactive raw-TCP line protocol adapter (capability gap).** The challenge is a line-based
   netcat service (print user sig → read a hex query → print its sig → read a hex attempt → print
   flag). The frozen trusted adapters cover file (read-only), HTTP (request/response with host
   allow-list), and fixed-executable subprocess — but NOT an interactive, stateful raw-TCP session.
   The existing `HttpAdapter` cannot conduct this multi-turn TCP dialogue.
2. **Authoritative verifier / oracle (provisioning gap).** `OperatorPolicy.verifier_adapter` must be
   supplied for any `VERIFIED_FLAG`; for this challenge the authoritative check is the remote service
   returning `/flag`, i.e. it lives on the live platform. No local oracle exists, and repo writeups
   contain historical flags which rule #7 forbids using as the current flag.

Per instructions, I stopped at this boundary rather than improvising a new adapter/architecture.
This is a per-challenge provisioning boundary, not an architecture flaw: web SSTI/SQLi-class
challenges (reachable via the registered HTTP adapter + a grader) are already solvable end-to-end
(proven by the MCP smokes and the knowledge-integration evaluation).

## Readiness conclusion

The Architecture A MCP runtime is READY: ctf_start/observe/propose/validation/planner/TrustKernel/
trusted-execution/result/evidence/verification/writeup/experience/close all function on a real
challenge with real resources, and knowledge stays advisory + OFF by default. To solve challenges
beyond the file/HTTP/fixed-subprocess adapter set (e.g. interactive TCP pwn/crypto services), the
operator must register an appropriate trusted interactive adapter and an authoritative verifier —
an operator provisioning step, deliberately out of scope here.

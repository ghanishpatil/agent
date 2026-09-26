# Interactive TCP Adapter — Implementation Report

Status: **COMPLETE / GREEN.** Added one reusable trusted capability (interactive TCP) entirely in
non-frozen `ctf_runtime`. Frozen `ctf_agent/**` is byte-for-byte unchanged (45/45). No new MCP
execution primitive. CRYSig solved end-to-end through the Architecture A path with hard verification.

## Architecture integration

The adapter sits exactly where the other trusted adapters sit. Kiro proposes typed actions via
`ctf_propose`; execution happens only after the frozen pipeline authorizes it:

```
Kiro -> MCP/ctf_propose -> proposal validation -> ActionPlanner -> TrustKernel
     -> InteractiveTcpAdapter -> registered TCP service -> observation
     -> evidence -> VerificationController -> VERIFIED_FLAG
```

`InteractiveTcpAdapter` implements the same duck-typed `.name` / `.execute(action)->ExecutionResult`
contract as `FileAdapter`/`HttpAdapter`/`SubprocessAdapter`, and is composed into an
`EnvironmentConfig` by `ctf_runtime.real_environment.build_operator_environment`. No `ctf_agent` file
was modified — the frozen registration/planner/kernel/verification interfaces already accept any
adapter satisfying the protocol.

## Adapter API

One registered tool (`tcp`) with a typed op in `relevant_parameters` — the smallest safe vocabulary
that supports a stateful dialogue without exposing sockets:

- `{tool:"tcp", target:<dest>, relevant_parameters:{op:"connect"}}` — open + read banner
- `{... op:"send", newline?:bool, encoding?:"utf-8"|"latin-1"|"hex"}, input_data:<payload>}` — send + read
- `{... op:"recv"}` — read again
- `{... op:"close"}` — orderly close

Kiro never receives a raw socket; it only emits these typed proposals. Responses return as
`ExecutionResult.stdout` (text) plus `metadata` (`received_hex`, `sent_bytes`, `received_bytes`,
`direction`, `dest`, `truncated`, `identity_ok`).

## Operator registration

`OperatorPolicy.tcp_destinations: Tuple[TcpDestination, ...]`. Deny-by-default: a proposal whose
target matches no registered destination is refused before any socket is created. Each
`TcpDestination` carries: `host`, `port`, `protocol=TCP`, `connect_timeout`, `read_timeout`,
`max_send_bytes`, `max_recv_bytes`, `max_turns`, `max_session_seconds`, `max_connections`,
`expected_identity`.

## Security boundaries

- Registered `host:port` only; no allow-all, no arbitrary Internet destinations.
- No host discovery, no port scanning, no subnet sweeps (no enumeration surface exists).
- TCP only (`AF_INET`/`SOCK_STREAM`); no UDP, no raw packets.
- No shell/subprocess/arbitrary-network primitive introduced.
- The model cannot bypass the authority boundary — it proposes; the frozen planner/kernel decide.
- Even a direct adapter call is bounded by the adapter's own destination allow-list.

## Resource limits

Per-destination: bounded connect timeout, read timeout, max send size, max receive size (response
truncated at the cap), max dialogue turns, max concurrent/total connections, and a max total session
duration. Exceeding a bound yields a structured rejection (`INPUT_REJECTION`), never an unbounded
operation.

## Session model

State is session-scoped: `build_operator_environment` creates a fresh adapter instance per CTF
session, so an open connection or transcript from one session cannot leak into another. Within a
session the connection persists across `ctf_propose` calls, enabling `connect → recv → (reason) →
send → recv → (reason) → send → recv → close`.

## Binary-data handling

Bytes are preserved internally (the receive transcript is raw bytes). Every response exposes both a
text rendering (`stdout`, UTF-8 with replacement) and a binary-safe `received_hex`. Sends accept
`encoding:"hex"` (raw bytes) or text; non-UTF-8 is never forced through UTF-8.

## Verification model

The adapter NEVER manufactures a candidate/verified flag. Verification uses the existing frozen
`verifier_route` (route 2). For TCP challenges the operator may enable `tcp_service_verifier`, wiring
a `ServiceTranscriptVerifier` whose authority is the trusted service's own emitted output: a
candidate is accepted only if that exact string was emitted by the registered service during this
session (optionally format-guarded). Therefore a historical/writeup flag the live service did not
emit can never verify, and the candidate still only routes to the verifier when the kernel has marked
the source hypothesis SUPPORTED and bound the candidate to current evidence.

## Test results

`tests/runtime/test_tcp_adapter.py`: 25/25 pass (registration, unregistered/wrong-port rejection,
connect+read timeout, send/recv size limits, turn limit, session-lifetime + connection budget,
session isolation, explicit close, binary round-trip, malformed rejection, planner dedup,
TrustKernel/planner authorization, direct-invocation policy enforcement, arbitrary-Internet
rejection, no-UDP, no-scan, no-discovery, verifier cannot self-verify, historical flag cannot verify,
failure classification, provisioning-vs-exploit distinction).

Full suite: **541 passed, 0 failed** (516 prior + 25 new). Historical 12/12, knowledge-v2, DomeCTF,
knowledge-integration all green. Both Architecture-A MCP smokes PASS (tool count unchanged at 14).

## Frozen-core fingerprint

`ooc/fpcheck.py`: **manifest files 45, matched (raw bytes) 45, mismatched 0, missing []**.

## MCP runtime proof

TCP is exercised purely through `ctf_propose` typed actions reaching the gateway → planner →
TrustKernel → `InteractiveTcpAdapter`. No new MCP tool was added; the sanctioned tool set is
unchanged (14 tools). The model-facing interface remains `ctf_observe`/`ctf_propose`.

## CRYSig result

Reproduced end-to-end through the Architecture A path against a locally-hosted real CRYSig service
whose flag was random and unknown to the solver. The reasoner read the source, identified the
GF(2)-linearity (`sign(root) = sign(user) XOR sign(user XOR root)`), connected, received the user
signature, queried `user XOR root`, received its signature, constructed the forgery, submitted it,
and the service emitted the flag. The forgery math lived in the reasoner; the adapter only carried
bytes.

Result: **VERIFIED_FLAG** (e.g. `CTF{837e2ab465427845}`), and the verified flag equalled the
service's secret (genuine solve, not fabricated). Adapters used: `read_file`, `tcp`, `flag_verifier`.

## Writeup result

Generated and grounded (SOLVED-only), flag copied verbatim from the kernel-verified result.

## Experience result

`AGENT_SUCCESS_EXPERIENCE` recorded via the post-terminal observer.

## Remaining limitations

- The service-transcript verifier fits "the service prints the flag on success" challenges; a
  challenge with a distinct remote grader endpoint would use an operator verifier adapter pointed at
  that grader instead.
- The dialogue is line/response-oriented (send→read-until-quiet); services needing precise
  delimiter- or length-framed reads can set `read_timeout`/`max_recv_bytes` per destination, but a
  richer framing option is a future addition.
- Reaching a real remote service still requires the operator to register that exact `host:port`
  (deny-by-default), and network egress must be permitted by the host environment.

---

## Final status

- **TCP ADAPTER:** InteractiveTcpAdapter (+ ServiceTranscriptVerifier) in `ctf_runtime`, composed via `build_operator_environment`.
- **STATUS:** COMPLETE and verified.
- **FROZEN CORE:** unchanged — 45/45 byte-identical.
- **TESTS:** full suite 541 passed / 0 failed (516 + 25 new).
- **SECURITY TESTS:** 25/25 pass (registration, bounds, isolation, no-UDP/scan/discovery, authority, verification safety).
- **CRYSIG RESULT:** SOLVED end-to-end via Architecture A; VERIFIED_FLAG matched the service secret.
- **VERIFIED FLAG:** `CTF{...}` from the trusted service (random per run; e.g. `CTF{837e2ab465427845}`).
- **MCP PATH:** ctf_start → ctf_observe → ctf_propose (read_file, then tcp connect/send/recv) → planner → TrustKernel → InteractiveTcpAdapter → evidence → ctf_propose (candidate via verifier_route) → verification → VERIFIED_FLAG → ctf_writeup → ctf_experience → close_session. No new MCP primitive.
- **WRITEUP:** generated (grounded).
- **EXPERIENCE:** AGENT_SUCCESS_EXPERIENCE generated.
- **BYPASSES:** none — all execution via the frozen kernel + trusted adapters; adapter never self-verifies; historical flags cannot verify.
- **REMAINING LIMITATIONS:** as listed above (verifier shape, read framing, operator egress registration).

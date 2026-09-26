# tools/ — Tool Memory + Environment Dependency Matrix

`tool_memory.jsonl` — reusable operational knowledge per tool: purpose, inputs, useful options,
expected output, common errors + how to interpret them, and **when NOT to use it**. Availability is
tracked separately because the environment changed.

## Environment reality (verified this session — supersedes `.kiro/ENV_STATUS.md`)
| Capability | Status |
|-----------|--------|
| Docker `ctf-env:latest` | **GONE** — user deleted Docker to save space. All container-only tools are currently **unavailable**. |
| Native Python | **3.10.7** (primary) + 3.13 present |
| Native libs OK | `capstone, unicorn, PIL, numpy, requests, Crypto(pycryptodome), z3, sympy, pwntools(limited), oletools` |
| Native libs MISSING | `gmpy2`, `angr` (pip-install on demand) |
| 7-Zip | present (`C:\Program Files\7-Zip\7z.exe`) |
| WSL2 | engine present, **no Linux distro** (install slim Ubuntu on demand if ELF execution needed) |
| Run ELF natively | **NO** (qemu-user was the lost capability) |
| `nc` | not reliable → use `System.Net.Sockets.TcpClient` |
| Node + node_modules | present (jsdom + jQuery harnesses for web/XSS) |

## Availability tags used in tool_memory.jsonl
`native` (works now) · `native-limited` · `native-installable` (pip on demand) ·
`container-only` (needs Docker rebuild or WSL install) · `uninstalled` (in repo, not set up) ·
`low-value` (present but not worth relying on)

## Decision rule for the agent
Prefer `native` tools. If a task needs a `container-only` tool (qemu-run ELF, zsteg, RsaCtfTool,
volatility, tshark, ROP tooling), first check availability, then either reproduce in native Python
or ask the operator to spin up WSL/Docker. Never assume a tool is present because a legacy doc says so.

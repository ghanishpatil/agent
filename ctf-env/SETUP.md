# CTF Environment Setup — Complete Guide

> ✅ **STATUS: BUILT & VERIFIED WORKING** (image `ctf-env:latest`, ~2.6GB).
> All tools smoke-tested green: Python3.12, gdb15, radare2, qemu-x86_64 + qemu-aarch64 (run foreign
> ELF), pwntools, angr, z3, capstone, unicorn, pycryptodome, gmpy2, sympy, oletools, PIL, pyjwt;
> binwalk, foremost, zsteg, steghide, exiftool, tshark, hashcat, john, ffuf, gobuster, ROPgadget,
> one_gadget, nmap, nc, openssl; RsaCtfTool at /usr/local/bin/RsaCtfTool; reference repos at
> /opt/refs (PayloadsAllTheThings, SecLists, GTFOBins, LOLBAS). Workspace mounts at /work.
> Nothing to do on a new machine except `docker build` if the image is gone.
> Quick re-verify:  `docker run --rm -v "F:\mission-git-hackss\mission-git-hackss:/work" ctf-env bash /work/ctf-env/smoke.sh`  then read `ctf-env/smoke_result.txt`.


This gives the agent (Kiro) a real Linux toolchain so it can **run** ELF binaries, do memory
forensics, stego, pwn, crypto, and web recon — not just analyze statically. Everything is
containerized so it does not pollute your Windows machine.

Workspace root (host): `F:\mission-git-hackss\mission-git-hackss`
Mounted inside container at: `/work`

---

## PART 1 — Install Docker (one time)

1. Install **Docker Desktop for Windows**: https://www.docker.com/products/docker-desktop/
   - During install, keep "Use WSL 2 based engine" checked (recommended).
2. Reboot if prompted. Launch Docker Desktop and wait until it says **"Engine running"**.
3. Verify in PowerShell:
   ```powershell
   docker --version
   docker run --rm hello-world
   ```
   If `hello-world` prints a success message, Docker works.

> No WSL? Docker Desktop installs a minimal WSL2 backend automatically. You do NOT need a
> separate Linux distro.

---

## PART 2 — Build the CTF image (one time, ~15–25 min first build)

From the workspace root in PowerShell:
```powershell
cd F:\mission-git-hackss\mission-git-hackss
docker build -t ctf-env .\ctf-env
```
This installs: gdb+pwndbg, radare2, binwalk, foremost, steghide, zsteg, exiftool, sleuthkit,
tshark, hashcat, john, gobuster, ffuf, qemu-user (run foreign-arch ELF), and Python libs
(pwntools, pycryptodome, gmpy2, sympy, z3-solver, angr, capstone, unicorn, ropgadget, oletools,
pillow, numpy), plus RsaCtfTool and one_gadget. It also clones reference repos to `/opt/refs`
(PayloadsAllTheThings, SecLists, GTFOBins, LOLBAS) so they can be grepped offline.

If a layer fails (network/disk), re-run the same build command — Docker resumes from cache.

---

## PART 3 — Run it

**Interactive shell** (you, manually):
```powershell
docker compose -f ctf-env\docker-compose.yml run --rm ctf
```
or without compose:
```powershell
docker run -it --rm --cap-add=SYS_PTRACE --security-opt seccomp=unconfined `
  -v "F:\mission-git-hackss\mission-git-hackss:/work" ctf-env
```

Inside the container you're at `/work` = your workspace. Example:
```bash
file /work/emm/Encrypted*/atlas-sync          # now works on ELF64
gdb -q /work/emm/Encrypted*/atlas-sync
binwalk /work/phish/.../image1.gif
python3 /work/solve.py
grep -ri "ssti" /opt/refs/PayloadsAllTheThings
```

**One-off command** (how the agent will usually call it):
```powershell
docker run --rm -v "F:\mission-git-hackss\mission-git-hackss:/work" ctf-env `
  bash -lc "cd /work && python3 solve.py"
```

### Reaching a live challenge host from inside the container
- The container has internet via Docker's NAT by default (fine for public challenge hosts/S3).
- To reach a service running on **your Windows host**, use `host.docker.internal` instead of `localhost`.
- If a target is on your LAN and NAT is a problem, add `--network host` (best on Linux; on Windows
  Docker Desktop, prefer `host.docker.internal`).

---

## PART 4 — Native Windows fallback (already available, no Docker needed)

The agent already has on Windows: Python 3.10 with `capstone`, `unicorn`, `pillow`, `numpy`,
`oletools`, `requests`; PowerShell; 7-Zip; `Invoke-WebRequest`. Use these for quick triage even
before the container is built. Docker is for the heavy Linux-only tools and running binaries.

Optional native additions (PowerShell, if you want them without Docker):
```powershell
python -m pip install pycryptodome gmpy2 sympy z3-solver pwntools ropgadget pyjwt base58
```
(`pwntools` on Windows is limited — real pwn should use the container.)

---

## PART 5 — (Optional) Wire an MCP for autonomous tool execution

You already have `hexstrike-ai/` (a real tool-orchestration server) but it needs the Linux tools
present — which the container provides. If you want the agent to drive tools via MCP instead of
shell, we can point an MCP at a running server. This is OPTIONAL; the agent can already call the
container through the shell tool. If you want it:

1. Start the hexstrike server inside the container (once its deps are installed there).
2. Create `.kiro/settings/mcp.json`:
   ```json
   {
     "mcpServers": {
       "hexstrike": {
         "command": "python",
         "args": ["F:/mission-git-hackss/mission-git-hackss/hexstrike-ai/hexstrike_mcp.py",
                  "--server", "http://127.0.0.1:8888"],
         "disabled": false,
         "autoApprove": []
       }
     }
   }
   ```
Recommendation: skip MCP for now. Shell + container covers everything and is simpler/more reliable.

---

## PART 6 — What this fixes (mapped to past failures)

| Past gap | Now solved by |
|----------|---------------|
| Couldn't run ELF64 (Encrypted Malware, Temporal Paradox) | qemu-user + gdb in container |
| Memory-dump forensics | volatility-style workflow + gdb + python in container |
| Proper stego (GIF/PNG/audio) | binwalk, foremost, zsteg, steghide, exiftool |
| Automated RSA/crypto attacks | RsaCtfTool, sympy, gmpy2, z3 |
| Web payload recall | offline PayloadsAllTheThings / GTFOBins / SecLists at /opt/refs |
| pwn (ROP, gadgets, libc) | pwntools, ROPgadget, one_gadget, patchelf |

---

## Maintenance
- Rebuild after editing the Dockerfile: `docker build -t ctf-env .\ctf-env`
- Update reference repos: rebuild, or inside the container `cd /opt/refs/PayloadsAllTheThings && git pull`
- Free space: `docker system prune` (careful — removes unused images/containers).

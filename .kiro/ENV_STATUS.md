# Environment Status & Startup — checked at session start

Verified live in this session. Update if it changes.

## Docker / ctf-env container
- `docker` CLI works (v29.7.2) but lives at a NON-DEFAULT path:
  `C:\Users\ghani\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe`
- **Docker DAEMON is NOT running** at session start (error: cannot connect to
  `npipe:////./pipe/dockerDesktopLinuxEngine`). Docker Desktop.exe is NOT in
  `C:\Program Files\Docker` — it's under `C:\Users\ghani\AppData\Local\Programs\DockerDesktop\`.
- **To use the Linux toolchain I must start Docker Desktop first.** Try:
  `Start-Process "C:\Users\ghani\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"`
  then wait ~30-60s and poll `docker info` until the daemon answers.
- Could NOT confirm the `ctf-env:latest` image exists (daemon was down). Once the daemon is up:
  `docker images ctf-env` — if missing, rebuild: `docker build -t ctf-env .\ctf-env`
- Run pattern (once daemon up):
  `docker run --rm -v "F:\mission-git-hackss\mission-git-hackss:/work" ctf-env bash -lc "cd /work && <cmd>"`
- ACTION when a challenge needs Linux tools (qemu-run ELF, volatility, zsteg, RsaCtfTool, ROP, tshark):
  ask the user to start Docker Desktop, or start it myself via the path above, then verify with
  `docker run --rm -v "F:\mission-git-hackss\mission-git-hackss:/work" ctf-env bash /work/ctf-env/smoke.sh`.

## Native Windows Python (works NOW, no Docker needed) — Python 3.10.7
Confirmed importable: `capstone`, `unicorn`, `PIL`, `requests`, `Crypto` (pycryptodome),
`sympy`, `pwn` (pwntools — limited on Windows), plus `oletools`, `numpy` (per notes).
NOT installed natively: `gmpy2` (use container, or `python -m pip install gmpy2` if needed).
Also available: 7-Zip, `Invoke-WebRequest`. `nc` NOT reliably present. Cannot run ELF64 natively.

## Fast triage without Docker
- Archives: 7-Zip (`& "C:\Program Files\7-Zip\7z.exe" l file.zip`).
- Binary parse / stego LSB / emulation: native Python (capstone/unicorn/PIL).
- Crypto: pycryptodome + sympy natively; RsaCtfTool/gmpy2 → container.
- Web: `requests` natively (works well); `curl`/browser via container if needed.

## Shell reminders (from lessons)
- PowerShell mangles multi-line / docker output → write results to a file under /work (container)
  or a local file, then READ the file with the read tool. Avoid long `python -c "..."` one-liners;
  write a `.py` and run it. Use `;` not `&&`; `$env:VAR` not `%VAR%`; quote paths with spaces;
  use ABSOLUTE paths (cwd doesn't persist across tool calls).

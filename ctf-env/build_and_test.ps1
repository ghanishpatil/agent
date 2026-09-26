# build_and_test.ps1 — run AFTER Docker Desktop is installed and "Engine running".
# Usage (PowerShell, from workspace root):  .\ctf-env\build_and_test.ps1

$ErrorActionPreference = "Stop"
$workspace = "F:\mission-git-hackss\mission-git-hackss"

Write-Host "== 1. Checking Docker ==" -ForegroundColor Cyan
docker --version
if ($LASTEXITCODE -ne 0) { Write-Host "Docker not found. Install Docker Desktop first (see ctf-env\SETUP.md Part 1)." -ForegroundColor Red; exit 1 }

Write-Host "`n== 2. Building ctf-env image (first build takes ~15-25 min) ==" -ForegroundColor Cyan
docker build -t ctf-env "$workspace\ctf-env"
if ($LASTEXITCODE -ne 0) { Write-Host "Build failed. Re-run this script to resume from cache." -ForegroundColor Red; exit 1 }

Write-Host "`n== 3. Smoke test — verifying key tools are present ==" -ForegroundColor Cyan
$test = @'
echo "--- versions ---"
python3 --version
gdb --version | head -1
r2 -v | head -1
binwalk --help >/dev/null 2>&1 && echo "binwalk OK"
exiftool -ver >/dev/null 2>&1 && echo "exiftool OK"
zsteg --help >/dev/null 2>&1 && echo "zsteg OK"
python3 -c "import pwn; print('pwntools OK')" 2>/dev/null || echo "pwntools MISSING"
python3 -c "import Crypto; print('pycryptodome OK')" 2>/dev/null || echo "pycryptodome MISSING"
python3 -c "import z3; print('z3 OK')" 2>/dev/null || echo "z3 MISSING"
python3 -c "import angr; print('angr OK')" 2>/dev/null || echo "angr MISSING (large; optional)"
ls /opt/refs 2>/dev/null && echo "refs OK"
qemu-x86_64 --version | head -1
echo "--- workspace mount ---"
ls /work | head -5
'@
docker run --rm -v "${workspace}:/work" ctf-env bash -lc $test

Write-Host "`n== DONE ==" -ForegroundColor Green
Write-Host "Interactive shell:  docker compose -f ctf-env\docker-compose.yml run --rm ctf" -ForegroundColor Yellow
Write-Host "One-off command:    docker run --rm -v `"${workspace}:/work`" ctf-env bash -lc `"cd /work && <cmd>`"" -ForegroundColor Yellow

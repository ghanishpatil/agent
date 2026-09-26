#!/bin/bash
# Smoke test — writes results to /work/ctf-env/smoke_result.txt
OUT=/work/ctf-env/smoke_result.txt
{
  echo "=== core ==="
  python3 --version
  gdb --version | head -1
  r2 -v | head -1
  qemu-x86_64 --version 2>/dev/null | head -1
  echo "=== python libs ==="
  for m in pwn Crypto z3 angr capstone unicorn PIL numpy oletools sympy gmpy2 jwt requests bs4; do
    python3 -c "import $m" 2>/dev/null && echo "$m OK" || echo "$m MISSING"
  done
  echo "=== cli tools ==="
  for t in binwalk foremost zsteg steghide exiftool tshark hashcat john ffuf gobuster ROPgadget one_gadget nc nmap openssl; do
    command -v "$t" >/dev/null 2>&1 && echo "$t OK" || echo "$t MISSING"
  done
  echo "=== RsaCtfTool ==="
  command -v RsaCtfTool >/dev/null 2>&1 && echo "RsaCtfTool OK" || echo "RsaCtfTool MISSING"
  echo "=== refs ==="
  ls /opt/refs 2>/dev/null
  echo "=== run-foreign-ELF check ==="
  command -v qemu-aarch64 >/dev/null 2>&1 && echo "qemu-aarch64 OK" || echo "qemu-aarch64 MISSING"
  echo "=== workspace mount ==="
  ls /work | head -5
} > "$OUT" 2>&1
echo "wrote $OUT"

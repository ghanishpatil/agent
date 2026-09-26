#!/bin/bash
cd "/work/emm/Encrypted Malware in Memory Dump" || exit 1
OUT=/work/emm/run_out.txt
{
  echo "=== file atlas-sync ==="
  file atlas-sync
  echo "=== file atlas-sync.core ==="
  file atlas-sync.core
  echo "=== no-arg run (qemu, 5s) ==="
  timeout 5 qemu-x86_64 ./atlas-sync; echo "EXIT=$?"
  echo "=== --help ==="
  timeout 5 qemu-x86_64 ./atlas-sync --help; echo "EXIT=$?"
  echo "=== strings that look like usage/flag ==="
  strings -n 6 atlas-sync | grep -iE "usage|flag\{|atlas|session|context|key|result|case" | head -40
} > "$OUT" 2>&1
echo "wrote $OUT"

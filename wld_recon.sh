#!/bin/bash
F="/work/AWholeNewWorld.wld"
OUT=/work/wld_recon.txt
{
  echo "=== file ==="
  file "$F"
  echo "=== size ==="
  ls -l "$F" | awk '{print $5}'
  echo "=== flag-prefix grep (strings) ==="
  strings -n 4 "$F" | grep -aiE "flag\{|ctf\{|iatcq\{|[A-Za-z0-9_]{3,}\{[^}]{3,}\}" | head -40
  echo "=== notable ASCII strings (n=6) sample ==="
  strings -n 6 "$F" | head -80
  echo "=== binwalk ==="
  binwalk "$F" | head -40
  echo "=== tail strings (last part often has signs/npc text) ==="
  strings -n 5 "$F" | tail -60
} > "$OUT" 2>&1
echo "wrote $OUT"

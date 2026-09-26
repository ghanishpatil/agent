#!/bin/bash
B=https://instantiator.secso.cc
for p in /auth/login /auth/register /register /instance /api ; do
  echo "=== GET $p ==="
  curl -s "$B$p" | head -c 1200
  echo; echo
done

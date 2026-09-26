#!/bin/bash
set -e
cd /work/waf
# Pull the EXACT remote libc from debian:13.4-slim (matches the Dockerfile base).
docker_ok=0
# We are already inside ctf-env (ubuntu). We cannot run docker-in-docker easily; instead download
# the debian trixie (13) libc6 .deb and extract libc.so.6.
mkdir -p libc && cd libc
# debian 13 = trixie. Fetch libc6 package.
apt-get download libc6 2>/dev/null || true
ls -la
# If apt-get download fails (wrong distro), fetch from debian pool via curl.
if ! ls libc6_*.deb >/dev/null 2>&1; then
  echo "apt download failed; trying debian snapshot pool"
  # trixie libc6 amd64
  curl -s -L -o libc6.deb "http://ftp.debian.org/debian/pool/main/g/glibc/libc6_2.41-12_amd64.deb" || \
  curl -s -L -o libc6.deb "http://deb.debian.org/debian/pool/main/g/glibc/libc6_2.41-12_amd64.deb" || true
  ls -la
fi

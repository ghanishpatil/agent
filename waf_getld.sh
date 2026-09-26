#!/bin/bash
set -e
cd /work/waf_chal
# copy the real ld (dereferenced) from the mounted debian rootfs is not available; instead
# we rely on docker cp done on host. This script just verifies files.
ls -la ld.so.2 libc.so.6
readlink -f ld.so.2 || true
file ld.so.2 || true

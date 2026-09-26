#!/bin/bash
cd /work/waf/waf
# Make a copy of chal that uses the REMOTE libc + ld so local runs match remote exactly.
cp chal chal_remote
chmod +x /work/waf/libc.so.6 /work/waf/ld-linux-x86-64.so.2 2>/dev/null
patchelf --set-interpreter /work/waf/ld-linux-x86-64.so.2 chal_remote 2>&1
patchelf --set-rpath /work/waf chal_remote 2>&1
echo "=== ldd ==="
ldd chal_remote 2>&1 | head
echo "=== quick run ==="
printf 'exit\n' | ./chal_remote 2>&1 | head -3

#!/bin/bash
cd /work/waf/waf
cp chal chal_remote
chmod +x /work/waf/libc.so.6 /work/waf/ld.so
patchelf --set-interpreter /work/waf/ld.so chal_remote
patchelf --set-rpath /work/waf chal_remote
echo "=== ldd ==="; ldd chal_remote 2>&1 | head
echo "=== run exit ==="; printf 'exit\n' | ./chal_remote 2>&1 | head -3

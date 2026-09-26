#!/bin/bash
cd /work/waf/waf
echo "=== glibc version in container ==="
ldd --version | head -1
echo "=== program headers (segments) ==="
readelf -l chal | sed -n '1,40p'
echo "=== section headers (key) ==="
readelf -S chal | grep -E "\.plt|\.got|\.bss|\.data|\.rela|\.dynsym|\.dynstr|\.rodata"
echo "=== .rela.plt (JMPREL) ==="
readelf -r chal
echo "=== dynamic ==="
readelf -d chal
echo "=== PLT disasm (first entries) ==="
objdump -d -j .plt chal | head -40
echo "=== .plt.sec? ==="
objdump -d chal | grep -A3 "plt.sec" | head

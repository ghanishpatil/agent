#!/bin/bash
cd /work/waf/waf
python3 /work/waf/memtest.py
gdb -q -batch -x /tmp/gs ./chal > /tmp/gdbout.txt 2>&1
grep -vE "warning|Thread|Using|pwndbg|created|loaded|Detected|Updating|terminfo|Terminal|Consider|Breakpoint 1 at" /tmp/gdbout.txt

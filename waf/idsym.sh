#!/bin/bash
L=/usr/lib/x86_64-linux-gnu/libc.so.6
echo "leaked offset = 0x21F380 (local)"
echo "=== nearest known symbols ==="
nm -D --defined-only "$L" 2>/dev/null | grep -iE "_IO_2_1_stdout_|_IO_2_1_stdin_|_IO_2_1_stderr_"
echo "=== what is at 0x21F380 ? ==="
python3 - <<'PY'
import subprocess
L="/usr/lib/x86_64-linux-gnu/libc.so.6"
out=subprocess.check_output(["readelf","-sW",L]).decode(errors="ignore")
target=0x21F380
best=None
for line in out.splitlines():
    parts=line.split()
    if len(parts)>=8 and parts[0].endswith(":"):
        try: val=int(parts[1],16)
        except: continue
        name=parts[7]
        if val<=target and (best is None or val>best[0]):
            best=(val,name,target-val)
print("nearest <= target:", hex(best[0]), best[1], "delta", hex(best[2]) if best else None)
# also exact
for line in out.splitlines():
    parts=line.split()
    if len(parts)>=8 and parts[0].endswith(":"):
        try: val=int(parts[1],16)
        except: continue
        if val==target: print("EXACT:", parts[7])
PY
echo "=== glibc version ==="
"$L" 2>/dev/null | head -1

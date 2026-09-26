#!/bin/bash
cd /work/bigwin
objdump -d -M intel chal_np > full.asm 2>&1
# extract challenge function
python3 - <<'PY'
lines=open("full.asm").read().splitlines()
out=[]; grab=False
for l in lines:
    if "<challenge>:" in l: grab=True
    if grab:
        out.append(l)
        if "<main>:" in l: break
open("challenge.asm","w").write("\n".join(out))
print("wrote challenge.asm", len(out), "lines")
PY
cat challenge.asm

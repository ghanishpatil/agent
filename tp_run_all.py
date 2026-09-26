import os, importlib.util

# load emulator module
spec = importlib.util.spec_from_file_location('tp_emu','tp_emu.py')
tp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tp)

img=os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img')
d=open(img,'rb').read()
offs=[]; s=0
while True:
    i=d.find(b'R9CF',s)
    if i<0: break
    offs.append(i); s=i+1

for n,o in enumerate(offs[:12]):
    ln = d[o+5] | (d[o+6]<<8)
    rec = d[o:o+ln]
    e = tp.Emu(rec)
    try:
        rax = e.run()
    except Exception as ex:
        print(f'rec {n:02d}: EMU ERR {ex}'); continue
    outs = e.format_outputs()
    if outs:
        fmt,a1,a2,a3 = outs[0]
        print(f'rec {n:02d}: accepted={a1 & 0xffffffff} guard={a2 & 0xff:02x}  (ret={rax:#x})')
    else:
        print(f'rec {n:02d}: no printf (ret={rax:#x})')

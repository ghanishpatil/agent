import os, importlib.util, struct
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

# use rec 02 (valid)
o = offs[2]
ln = d[o+5] | (d[o+6]<<8)
rec = d[o:o+ln]

e = tp.Emu(rec)
rax = e.run()
uc = e.uc
# dump .bss around 0x4040..0x4200
region = uc.mem_read(0x4000, 0x200)
print('=== .bss/data dump 0x4000..0x4200 ===')
for off in range(0, len(region), 16):
    chunk = region[off:off+16]
    hexs=' '.join(f'{b:02x}' for b in chunk)
    asc=''.join(chr(b) if 32<=b<127 else '.' for b in chunk)
    print(f'{0x4000+off:#06x}  {hexs:<48}  {asc}')

# The matrix at 0x4060: 20 codes * 12 bytes. Dump per-code.
print('\n=== per-code matrix at 0x4060 (index: 12 bytes) ===')
MOD=['o3','o4','o5','dx','da','ds','c7','c8','cf','cr','sn','g8','x3','mh','ml','xs','lc','zl','bz','xz']
mat = uc.mem_read(0x4060, 20*12)
marker = uc.mem_read(0x4040, 20)
for i in range(20):
    row = bytes(mat[i*12:(i+1)*12])
    if any(row) or marker[i]:
        print(f'  [{i:2}] {MOD[i]} marker={marker[i]:#04x} row={row.hex()}  ascii={"".join(chr(b) if 32<=b<127 else "." for b in row)}')

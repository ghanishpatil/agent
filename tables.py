import struct
from capstone import *
data=open(r'f:\mission-git-hackss\mission-git-hackss\out_r9sampler','rb').read()

# section helpers
e_shoff=struct.unpack('<Q',data[0x28:0x30])[0]
e_shentsize=struct.unpack('<H',data[0x3a:0x3c])[0]
e_shnum=struct.unpack('<H',data[0x3c:0x3e])[0]
e_shstrndx=struct.unpack('<H',data[0x3e:0x40])[0]
secs=[]
for i in range(e_shnum):
    off=e_shoff+i*e_shentsize
    secs.append((struct.unpack('<I',data[off:off+4])[0],
                 struct.unpack('<Q',data[off+16:off+24])[0],
                 struct.unpack('<Q',data[off+24:off+32])[0],
                 struct.unpack('<Q',data[off+32:off+40])[0]))
strtab_off=secs[e_shstrndx][2]
def sname(n):
    e=data.index(b'\x00',strtab_off+n); return data[strtab_off+n:e].decode()
sections={sname(s[0]):s for s in secs}

def addr_to_off(addr):
    for nm,(n,a,o,sz) in sections.items():
        if a<=addr<a+sz and a!=0:
            return o+(addr-a)
    return None

def read(addr,n):
    o=addr_to_off(addr); return data[o:o+n]

# jump table 1 at rip+0x91c where rip = addr of instruction AFTER lea? 
# lea rcx,[rip+0x91c] at 0x16e1 (len 7) -> base = 0x16e1+7+0x91c = 0x2004
base1=0x16e1+7+0x91c
print('base1',hex(base1))
# entries: index rdi in 0..(0x4b) after sub 0x22; table indexed rdi*4, size? we read up to 0x4b+1=76 entries
t1=[]
for i in range(0x4c):
    off=addr_to_off(base1+i*4)
    val=struct.unpack('<i',data[off:off+4])[0]
    t1.append((i, i+0x22, chr(i+0x22), hex((base1+val)&0xffffffffffff)))
print('--- table1 (char range 0x22..) target addresses ---')
for i,ch,c,tgt in t1:
    print(f'idx{i} char={ch:#x}({c!r}) -> {tgt}')

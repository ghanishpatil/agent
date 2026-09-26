import struct
ELF=open(r'f:\mission-git-hackss\mission-git-hackss\out_r9sampler','rb').read()
# .rodata at addr 0x2000 offset 0x2000 (from earlier)
def rd(addr,n):
    return ELF[addr:addr+n]  # PIE base 0, file offset==vaddr for these
for label,addr in [('memcmp magic @0x229a',0x229a),('fmt @1a02 rsi',0x1a02+7+0x88e),
                   ('fmt @1a7f',0x1a7f+7+0x7ea),('fmt @1c3b',0x1c3b+7+0x65d)]:
    print(label, hex(addr), rd(addr,32))

from elftools.elf.elffile import ELFFile
f=open('tp_files/usr__local__sbin__r9sampler','rb')
elf=ELFFile(f)
for name in ['.rodata','.data','.data.rel.ro']:
    s=elf.get_section_by_name(name)
    if s:
        print(f'=== {name} vaddr={s["sh_addr"]:#x} size={len(s.data())} ===')
        d=s.data()
        # hexdump
        for off in range(0,len(d),16):
            chunk=d[off:off+16]
            hexs=' '.join(f'{b:02x}' for b in chunk)
            asc=''.join(chr(b) if 32<=b<127 else '.' for b in chunk)
            print(f'{s["sh_addr"]+off:#06x}  {hexs:<48}  {asc}')

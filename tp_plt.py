from elftools.elf.elffile import ELFFile
f=open('tp_files/usr__local__sbin__r9sampler','rb')
elf=ELFFile(f)
# dynamic symbols and PLT relocations
rela = elf.get_section_by_name('.rela.plt')
dynsym = elf.get_section_by_name('.dynsym')
print('=== .rela.plt (GOT entries) ===')
for r in rela.iter_relocations():
    sym = dynsym.get_symbol(r['r_info_sym'])
    print(f'  GOT@{r["r_offset"]:#x} -> {sym.name}')
# .plt.sec stubs are typically at .plt.sec; each stub jmps [GOT]
for name in ['.plt','.plt.sec','.plt.got']:
    s=elf.get_section_by_name(name)
    if s:
        print(f'{name}: addr={s["sh_addr"]:#x} size={len(s.data())} entsize={s["sh_entsize"]}')
# print addresses of interest from disasm calls: 0x10c0,0x10d0,0x10e0,0x10f0,0x1100,0x1110,0x1120,0x1130,0x1140,0x1150

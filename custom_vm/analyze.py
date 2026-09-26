from pwn import *
context.arch = 'amd64'
p = r"f:\mission-git-hackss\mission-git-hackss\custom_vm\Custom VM\hyperstate\hyperstate4"
e = ELF(p, checksec=False)

print("entry:", hex(e.entry))
print("=== sections ===")
for name, s in e.sections_by_name.items() if hasattr(e,'sections_by_name') else []:
    pass
for s in e.sections:
    if s.name:
        print(f"  {s.name:20} addr={s.header.sh_addr:#x} size={s.header.sh_size:#x} off={s.header.sh_offset:#x}")

print("=== strings in .rodata/.data ===")
for sec in ['.rodata','.data']:
    s = e.get_section_by_name(sec)
    if s:
        data = s.data()
        cur=b''
        base=s.header.sh_addr
        for i,ch in enumerate(data):
            if 32<=ch<127:
                cur+=bytes([ch])
            else:
                if len(cur)>=3:
                    print(f"  {sec} {base+i-len(cur):#x}: {cur.decode()}")
                cur=b''
        if len(cur)>=3:
            print(f"  {sec}: {cur.decode()}")

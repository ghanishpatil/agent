from pwn import *
import itertools, re
context.arch='amd64'
P = r"f:\mission-git-hackss\mission-git-hackss\custom_vm\Custom VM\hyperstate\hyperstate4"
raw=open(P,'rb').read()
e=ELF(P,checksec=False)

def show_hits(tag, data):
    for m in re.finditer(rb'IATCQ', data):
        s=m.start(); seg=data[s:s+40]
        print(f"  [{tag}] off {s:#x}: {seg}")
    # also flag-ish { }
    for m in re.finditer(rb'[ -~]{6,}\{[ -~]{2,}\}', data):
        seg=m.group(0)
        if b'IATCQ' in seg or b'CTF' in seg or b'flag' in seg.lower():
            print(f"  [{tag}/brace] {m.start():#x}: {seg}")

print("== plain search ==")
show_hits("raw", raw)

print("== single-byte XOR scan for IATCQ ==")
for k in range(1,256):
    x=bytes(b^k for b in raw)
    if b'IATCQ' in x:
        i=x.find(b'IATCQ'); print(f"  xor {k:#x} off {i:#x}: {x[i:i+40]}")

print("== LCG keystream decrypt of ALL rodata (varying length) ==")
rod=e.get_section_by_name('.rodata'); rd=rod.data(); rb=rod.header.sh_addr
def lcg_dec(src, seed=0xC0FFEE42):
    out=bytearray(); s=seed
    for b in src:
        s=(s*0x41C64E6D+0x3039)&0xffffffff
        out.append(b^((s>>16)&0xff))
    return bytes(out)
dec=lcg_dec(rd)
show_hits("rodata-lcg-full", dec)
# also decrypt whole file / data section
for sec in ['.data','.bss','.text','.rodata']:
    s=e.get_section_by_name(sec)
    if s and s.data():
        show_hits(sec+"-lcg", lcg_dec(s.data()))

print("== search whole file for any 24+ printable run ==")
for m in re.finditer(rb'[ -~]{24,}', raw):
    seg=m.group(0)
    if b'{' in seg or b'IATCQ' in seg or seg.count(b'_')>=1:
        print(f"  {m.start():#x}: {seg[:60]}")

print("== .comment / build-id ==")
for sec in ['.comment']:
    s=e.get_section_by_name(sec)
    if s: print("  ",sec, s.data())

print("done")

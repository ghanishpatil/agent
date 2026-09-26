import vm_model as VM
T=0x86d03165
cands=[b"IATCQ{darkc0ver_vm_rev!!AB_tJh7G",
       b"IATCQ{d4rk_c0v3r_vm_rev33}Kbh<V}"]
for c in cands:
    print(len(c), c, hex(VM.vm(c)), "GRANTS" if VM.vm(c)==T else "no")
# also brute a totally different readable-ish one quickly by trying random-ish tails is slow; just show the two.

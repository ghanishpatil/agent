import binascii
for lane in (0,1):
    p = rf'f:\mission-git-hackss\mission-git-hackss\tp_files\var__lib__deltaforge__lane_{lane}.cal'
    d = open(p,'rb').read()
    print(f"lane_{lane}.cal len={len(d)}")
    print("hex:", binascii.hexlify(d).decode())
    print("magic:", d[:4])
    print()

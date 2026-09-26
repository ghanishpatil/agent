#!/usr/bin/env python3
import zipfile, os
XLSM = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\Phishtofortune.xlsm"
EXTRACTED = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune"

z=zipfile.ZipFile(XLSM)
names=z.namelist()
print(f"{len(names)} entries in xlsm\n")
for n in names:
    zdata=z.read(n)
    # map to extracted path
    ep=os.path.join(EXTRACTED, *n.split("/"))
    if not os.path.exists(ep):
        print(f"[MISSING on disk] {n}")
        continue
    fdata=open(ep,"rb").read()
    if zdata!=fdata:
        print(f"[DIFFERS] {n}: xlsm={len(zdata)}b disk={len(fdata)}b")
        # show a short diff of text
        try:
            zt=zdata.decode("utf-8","replace"); ft=fdata.decode("utf-8","replace")
            # find first difference
            for i in range(min(len(zt),len(ft))):
                if zt[i]!=ft[i]:
                    print(f"    first diff @char {i}:")
                    print(f"      xlsm: ...{zt[max(0,i-20):i+60]}...")
                    print(f"      disk: ...{ft[max(0,i-20):i+60]}...")
                    break
        except: pass
    else:
        pass
print("\ndone diff")

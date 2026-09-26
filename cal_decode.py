#!/usr/bin/env python3
mods="o3 o4 o5 dx da ds c7 c8 cf cr sn g8 x3 mh ml xs lc zl bz xz".split()
for lane in (0,1):
    p=rf"f:\mission-git-hackss\mission-git-hackss\tp_files\var__lib__deltaforge__lane_{lane}.cal"
    d=open(p,"rb").read()
    body=d[5:-2]
    print(f"\n=== lane_{lane} body ({len(body)} bytes): {body.hex()}")
    print("bytes:", list(body))
    # hypothesis: sequence of [count, then count bytes] groups
    i=0; grp=0
    while i < len(body):
        n=body[i]
        g=list(body[i+1:i+1+n])
        print(f"  group{grp}: len={n} data={g}")
        i+=1+n; grp+=1

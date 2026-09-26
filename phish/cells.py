#!/usr/bin/env python3
import re
ROOT=r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\xl\macrosheets"
ss = ["R","L","M","o","n","D","w","l","a","d","T","F","i","e","J","C","B","HERTY","A","http://","188.127.227.99/","45.150.67.29/"]

for sh in ["sheet1.xml","sheet2.xml"]:
    print(f"\n===== {sh} all cells =====")
    d=open(ROOT+"\\"+sh,encoding="utf-8").read()
    for m in re.finditer(r'<c r="([A-Z]+\d+)"[^>]*?(?:\st="(\w+)")?[^>]*>(.*?)</c>', d):
        ref,typ,inner=m.group(1),m.group(2),m.group(3)
        fmla=re.search(r"<f>(.*?)</f>",inner)
        val=re.search(r"<v>(.*?)</v>",inner)
        f=fmla.group(1) if fmla else ""
        v=val.group(1) if val else ""
        # resolve shared string
        resolved=""
        if typ=="s" and v.isdigit() and int(v)<len(ss):
            resolved=f"  =>'{ss[int(v)]}'"
        # unescape
        import html
        f=html.unescape(f); v=html.unescape(v)
        print(f"  {ref} t={typ}: f={f!r} v={v!r}{resolved}")

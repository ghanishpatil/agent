#!/usr/bin/env python3
import re, codecs
CORE = r"f:\mission-git-hackss\mission-git-hackss\phish\Phishtofortune\Phishtofortune\docProps\core.xml"
raw = open(CORE,"rb").read()
# extract exact bytes between tags
m = re.search(rb"<dc:creator>(.*?)</dc:creator>", raw, re.S)
c = m.group(1)
m2 = re.search(rb"<cp:lastModifiedBy>(.*?)</cp:lastModifiedBy>", raw, re.S)
lm = m2.group(1)
print("creator bytes:", c.hex(), "->", c)
print("lastModifiedBy bytes:", lm.hex(), "->", lm)
print("lastModifiedBy len:", len(lm))
print("each char:")
for b in lm:
    print(f"  {b:02x} {chr(b)!r}")

# rot13 char by char preserving everything
def rot13b(bs):
    out=bytearray()
    for b in bs:
        c=chr(b)
        if 'a'<=c<='z': out.append((b-97+13)%26+97)
        elif 'A'<=c<='Z': out.append((b-65+13)%26+65)
        else: out.append(b)
    return bytes(out)
print("\ncreator rot13:", rot13b(c))
print("lastModifiedBy rot13:", rot13b(lm))
print("combined rot13:", rot13b(c+lm))

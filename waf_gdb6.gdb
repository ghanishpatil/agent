set pagination off
set logging file /work/waf_gdb_log.txt
set logging overwrite on
set logging enabled on
tbreak *0x4010d4
run < /work/waf_payload.bin
printf "=== at printf@plt entry ===\n"
printf "rdi(fmt)=%p\n", $rdi
printf "rsp=%p  (return addr will be *rsp)\n", $rsp
printf "=== printf va_args come from: rsi,rdx,rcx,r8,r9 then stack ===\n"
printf "rsi=%p rdx=%p rcx=%p r8=%p r9=%p\n", $rsi,$rdx,$rcx,$r8,$r9
printf "=== stack from rsp (arg6+ are here) ===\n"
x/40gx $rsp
quit

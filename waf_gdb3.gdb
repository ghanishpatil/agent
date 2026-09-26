set pagination off
set logging file /work/waf_gdb_log.txt
set logging overwrite on
set logging enabled on
tbreak *0x401373
run < /work/waf_payload.bin
printf "=== registers at main ret ===\n"
info registers rax rbx rcx rdx rsi rdi rbp rsp r8 r9 r10 r11 r12 r13 r14 r15
printf "=== rdi points to: ===\n"
x/8gx $rdi
printf "=== rsi points to: ===\n"
x/4gx $rsi
printf "=== buffer (main s1) region content ===\n"
x/16gx $rsp-0x60
quit

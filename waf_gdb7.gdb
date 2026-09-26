set pagination off
set logging file /work/waf_gdb_log.txt
set logging overwrite on
set logging enabled on
# Break at printf@plt; the FIRST hit is printf(">> "). We want the SECOND (our printf(buf)).
break *0x4010d4
run < /work/waf_payload.bin
# first hit = ">> " ; continue to our call
continue
printf "=== OUR printf(buf) entry ===\n"
printf "rdi(fmt)=%p\n", $rdi
x/s $rdi
printf "rsp=%p (=> *rsp is printf return addr = eb90 region)\n", $rsp
printf "=== stack args (arg7=%%7$p is *rsp, etc). Dump 30 qwords from rsp ===\n"
x/30gx $rsp
printf "=== registers rsi rdx rcx r8 r9 (args2-6) ===\n"
printf "rsi=%p rdx=%p rcx=%p r8=%p r9=%p\n",$rsi,$rdx,$rcx,$r8,$r9
quit

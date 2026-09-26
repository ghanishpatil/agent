set pagination off
set logging file /work/waf_base_log.txt
set logging overwrite on
set logging enabled on
break *0x4010d4
run < /work/waf_leak_in.bin
info proc mappings
printf "RSP=%p RDI=%p\n", $rsp, $rdi
quit

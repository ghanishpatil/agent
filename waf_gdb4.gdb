set pagination off
set logging file /work/waf_gdb_log.txt
set logging overwrite on
set logging enabled on
# break at the printf@plt we return into, then finish and see where it returns
tbreak *0x401373
run < /work/waf_payload.bin
printf "=== main ret, target: ===\n"
x/gx $rsp
# step into printf@plt
stepi
printf "=== now in printf stub, rsp -> return addr after printf: ===\n"
x/4gx $rsp
printf "rdi=%p (fmt buf)\n", $rdi
quit

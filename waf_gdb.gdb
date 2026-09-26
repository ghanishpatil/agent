set pagination off
set logging file /work/waf_gdb_log.txt
set logging overwrite on
set logging enabled on
break *0x40124f
commands
  printf "=== after read (n at rbp-4) ===\n"
  x/2gx $rbp-8
  printf "buf dump (first 0x60):\n"
  x/12gx $rbp-0x18
  continue
end
break *0x401366
commands
  printf "=== after strncmp, eax=%d ===\n", $eax
  continue
end
break *0x401373
commands
  printf "=== at main ret ===\n"
  printf "saved_rip=%p  saved_rbp=%p\n", *(unsigned long*)$rsp, $rbp
  x/4gx $rsp
  continue
end
run < /work/waf_payload.bin
printf "=== program done / crashed ===\n"
info registers rip rsp rbp
quit

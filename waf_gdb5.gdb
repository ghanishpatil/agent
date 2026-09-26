set pagination off
set logging file /work/waf_gdb_log.txt
set logging overwrite on
set logging enabled on
tbreak *0x40134b
run < /work/waf_payload.bin
printf "=== after __gets returns (post-WAF), inspect ret slot & next ===\n"
x/6gx $rbp-0x50+0x50
printf "ret slot (rbp+8):\n"
x/4gx $rbp+8
quit

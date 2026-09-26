#!/bin/bash
cd /work/bigwin
# Use gdb to trace i and accum at the accum==67 check (0x40132f cmp) each iteration.
printf "0\n0\n0\n0\n0\n0\n67\n5\n5\n5\n5\n5\n" > in_b.txt
gdb -q -batch \
  -ex 'set pagination off' \
  -ex 'break *0x40132f' \
  -ex 'run < in_b.txt' \
  -ex 'commands
print/d $eax
print "accum_slot=" 
x/1dw $rbp-0x8
x/1dw $rbp-0x4
continue
end' \
  -ex 'run < in_b.txt' \
  ./chal_np 2>&1 | head -60

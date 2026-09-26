set pagination off
break *0x401373
run
echo \n===AT main ret===\n
info registers rbp rsp rdi rsi rdx rax
echo \n===[rsp] = saved RIP (post-memset)===\n
x/6gx $rsp
echo \n===buf region (rdi)===\n
x/16gx $rdi
quit

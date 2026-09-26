set pagination off
break *0x401373
run
echo \n===REGS AT MAIN RET===\n
info registers rdi rsi rdx rax rbx rbp rsp rcx r8 r9
echo \n===STACK AT RSP===\n
x/12gx $rsp
echo \n===WHAT RDI POINTS TO===\n
x/8gx $rdi
echo \n===WHAT RSI POINTS TO===\n
x/4gx $rsi
quit

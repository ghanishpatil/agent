import struct, sys
from unicorn import *
from unicorn.x86_const import *

ELF=open(r'f:\mission-git-hackss\mission-git-hackss\out_r9sampler','rb').read()
e_phoff=struct.unpack('<Q',ELF[0x20:0x28])[0]; e_phentsize=struct.unpack('<H',ELF[0x36:0x38])[0]; e_phnum=struct.unpack('<H',ELF[0x38:0x3a])[0]
LOAD=[]
for i in range(e_phnum):
    o=e_phoff+i*e_phentsize
    if struct.unpack('<I',ELF[o:o+4])[0]==1:
        LOAD.append((struct.unpack('<Q',ELF[o+16:o+24])[0],struct.unpack('<Q',ELF[o+8:o+16])[0],struct.unpack('<Q',ELF[o+32:o+40])[0]))

def crc16_ccitt(data, init=0xffff):
    crc=init
    for b in data:
        crc^=b<<8
        for _ in range(8):
            crc=((crc<<1)^0x1021)&0xffff if crc&0x8000 else (crc<<1)&0xffff
    return crc

# Build an R9CF record from a cal file: replace magic. Then figure length/crc that binary expects.
CAL=sys.argv[1] if len(sys.argv)>1 else r'f:\mission-git-hackss\mission-git-hackss\out_lane_1.cal'
raw=open(CAL,'rb').read()
# Try: keep structure but swap magic to R9CF and recompute inner crc16 over (len-2) bytes
# Binary: at magic+5,+6 = 16-bit length L (=whole record incl magic? incl crc). crc over first L-2 bytes vs last 2.
# The cal body length = len(raw). Let's craft: R9CF + [byte5][byte6]=L split + ... Actually just feed variants and trace.
variants={}
body=bytearray(raw)
body[0:4]=b'R9CF'
# recompute trailing crc over body[:-2]
c=crc16_ccitt(bytes(body[:-2]))
body[-2]=(c>>8)&0xff; body[-1]=c&0xff  # try big-endian trailer (binary reads [+len-2]<<8|[+len-1])
variants['swapmagic_becrc']=bytes(body)

filedata=variants['swapmagic_becrc']
print('feeding', filedata.hex(), file=sys.stderr)

mu=Uc(UC_ARCH_X86, UC_MODE_64)
mu.mem_map(0x0,0x8000)
for va,off,fsz in LOAD: mu.mem_write(va, ELF[off:off+fsz])
mu.mem_map(0x200000,0x100000); mu.reg_write(UC_X86_REG_RSP,0x200000+0x100000-0x1000)
mu.mem_map(0x400000,0x200000); heap=[0x401000]
def malloc(n):
    p=heap[0]; heap[0]=(heap[0]+n+15)&~15; return p
mu.mem_map(0x900000,0x1000); mu.mem_write(0x900000+0x28,struct.pack('<Q',0xdead)); 
try: mu.reg_write(UC_X86_REG_FS_BASE,0x900000)
except: pass

# plt stubs (from emu.py output)
plt={0x10d0:'free',0x10e0:'fread',0x10f0:'fclose',0x1100:'stkchk',0x1110:'memcmp',0x1120:'malloc',0x1130:'printf',0x1140:'fopen',0x1150:'fwrite'}
open_files={}
output=[]
def read_cstr(a):
    o=b''
    while True:
        ch=mu.mem_read(a,1)
        if ch==b'\x00': break
        o+=ch; a+=1
    return o
def retw(val):
    mu.reg_write(UC_X86_REG_RAX,val&0xffffffffffffffff)
    rsp=mu.reg_read(UC_X86_REG_RSP); ra=struct.unpack('<Q',mu.mem_read(rsp,8))[0]
    mu.reg_write(UC_X86_REG_RSP,rsp+8); mu.reg_write(UC_X86_REG_RIP,ra)

def hook(mu,addr,size,u):
    if addr in plt:
        s=plt[addr]
        rdi=mu.reg_read(UC_X86_REG_RDI);rsi=mu.reg_read(UC_X86_REG_RSI);rdx=mu.reg_read(UC_X86_REG_RDX);rcx=mu.reg_read(UC_X86_REG_RCX);r8=mu.reg_read(UC_X86_REG_R8)
        if s=='fopen':
            h=malloc(8);open_files[h]=[filedata,0];retw(h)
        elif s=='malloc': retw(malloc(rdi))
        elif s=='fread':
            f=open_files.get(rcx); want=rsi*rdx
            if not f: retw(0); return
            buf=f[0][f[1]:f[1]+want]; f[1]+=len(buf); mu.mem_write(rdi,buf); retw(len(buf)//rsi if rsi else 0)
        elif s=='fclose': retw(0)
        elif s=='free': retw(0)
        elif s=='memcmp':
            a=bytes(mu.mem_read(rdi,rdx)); b=bytes(mu.mem_read(rsi,rdx)); retw(0 if a==b else (1 if a>b else 0xffffffffffffffff))
        elif s=='fwrite':
            output.append(bytes(mu.mem_read(rdi,rsi*rdx))); retw(rdx)
        elif s=='printf':
            fmt=read_cstr(rsi).decode('latin1'); args=[rdx,rcx,r8]
            try: out=fmt%tuple((x&0xffffffff) for x in args[:fmt.count('%')])
            except: out=fmt
            output.append(out.encode('latin1')); retw(len(out))
        elif s=='stkchk': mu.emu_stop()
    # trace tag switch entry 0x16b1 and store 0x1656
    elif addr==0x16b1:
        dil=mu.reg_read(UC_X86_REG_RDI)&0xff
        print(f'[0x16b1] tag_byte={dil:#x}({chr(dil) if 32<=dil<127 else "?"})',file=sys.stderr)
    elif addr==0x1656:
        idx=mu.reg_read(UC_X86_REG_RDI); slen=mu.reg_read(UC_X86_REG_RDX); sptr=mu.reg_read(UC_X86_REG_RSI)
        payload=bytes(mu.mem_read(sptr,slen)) if 0<slen<64 else b''
        print(f'   [0x1656] slot_idx={idx} len={slen} payload={payload.hex()}',file=sys.stderr)

mu.hook_add(UC_HOOK_CODE,hook)
# argv
mu.mem_write(0x200000+0x100000-0x200,b'r9sampler\x00'); mu.mem_write(0x200000+0x100000-0x180,b'/x.cal\x00')
argv=0x200000+0x100000-0x100; mu.mem_write(argv,struct.pack('<QQQ',0x200000+0x100000-0x200,0x200000+0x100000-0x180,0))
mu.reg_write(UC_X86_REG_RDI,2); mu.reg_write(UC_X86_REG_RSI,argv)
mu.mem_write(0x7000,b'\xf4'); rsp=mu.reg_read(UC_X86_REG_RSP); mu.mem_write(rsp,struct.pack('<Q',0x7000))
try: mu.emu_start(0x19d5,0x7000)
except UcError as e: print('UC',e,hex(mu.reg_read(UC_X86_REG_RIP)),file=sys.stderr)
print('OUTPUT:',b''.join(output))
# dump internal tables: rip+0x29e1 base -> at instr 0x1678 (len7) => 0x1678+7+0x29e1
data_tbl=0x1678+7+0x29e1
len_tbl=0x169b+7+0x299e
print('data_table@%x:'%data_tbl, bytes(mu.mem_read(data_tbl,20*12)).hex())
print('len_table@%x:'%len_tbl, bytes(mu.mem_read(len_tbl,20)).hex())

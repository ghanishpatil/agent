import sys, struct
from unicorn import *
from unicorn.x86_const import *
from elftools.elf.elffile import ELFFile

ELF_PATH = 'tp_files/usr__local__sbin__r9sampler'

# PLT stub addresses (from .plt.sec order matching .rela.plt)
PLT = {
    0x10d0: 'free',
    0x10e0: 'fread',
    0x10f0: 'fclose',
    0x1100: '__stack_chk_fail',
    0x1110: 'memcmp',
    0x1120: 'malloc',
    0x1130: '__printf_chk',
    0x1140: 'fopen',
    0x1150: 'fwrite',
    0x10c0: '__cxa_finalize',
}

MAIN = 0x19d5

# memory layout
BASE = 0x0            # ELF is PIE, load at 0 (vaddrs are already small)
IMAGE_SIZE = 0x8000
STACK_ADDR = 0x200000
STACK_SIZE = 0x100000   # -> 0x300000
ARGV_ADDR  = 0x300000   # 0x300000-0x301000
HEAP_ADDR  = 0x400000
HEAP_SIZE  = 0x200000   # -> 0x600000
FS_BASE    = 0x700000
FAKE_RET   = 0x800000
FILE_FD    = 0x1000     # fake FILE* handle value

class Emu:
    def __init__(self, filedata):
        self.filedata = filedata
        self.filepos = 0
        self.heap_ptr = HEAP_ADDR
        self.printf_outputs = []
        self.uc = Uc(UC_ARCH_X86, UC_MODE_64)
        self._load()

    def _load(self):
        uc = self.uc
        # map image
        uc.mem_map(BASE, IMAGE_SIZE)
        elf = ELFFile(open(ELF_PATH,'rb'))
        for seg in elf.iter_segments():
            if seg['p_type']=='PT_LOAD':
                addr = seg['p_vaddr']
                data = seg.data()
                uc.mem_write(BASE+addr, data)
        # stack
        uc.mem_map(STACK_ADDR, STACK_SIZE)
        # heap
        uc.mem_map(HEAP_ADDR, HEAP_SIZE)
        # argv area
        uc.mem_map(ARGV_ADDR, 0x1000)
        # set up argv: argv[0]="r9s", argv[1]="file"
        fn = ARGV_ADDR+0x100
        uc.mem_write(fn, b'/tmp/rec\x00')
        argv0 = ARGV_ADDR+0x120
        uc.mem_write(argv0, b'r9s\x00')
        argv_arr = ARGV_ADDR+0x200
        uc.mem_write(argv_arr, struct.pack('<QQ', argv0, fn))
        self.argv_arr = argv_arr
        # hooks
        uc.hook_add(UC_HOOK_CODE, self._hook_code)

    def _heap_alloc(self, n):
        p = self.heap_ptr
        self.heap_ptr += (n+15)&~15
        return p

    def _hook_code(self, uc, address, size, user):
        if address in PLT:
            name = PLT[address]
            self._handle_plt(name)

    def _handle_plt(self, name):
        uc = self.uc
        rdi = uc.reg_read(UC_X86_REG_RDI)
        rsi = uc.reg_read(UC_X86_REG_RSI)
        rdx = uc.reg_read(UC_X86_REG_RDX)
        rcx = uc.reg_read(UC_X86_REG_RCX)
        r8  = uc.reg_read(UC_X86_REG_R8)
        # get return addr from stack, then simulate 'ret'
        rsp = uc.reg_read(UC_X86_REG_RSP)
        retaddr = struct.unpack('<Q', uc.mem_read(rsp,8))[0]
        ret = None
        if name=='fopen':
            ret = FILE_FD
            self.filepos = 0
        elif name=='malloc':
            ret = self._heap_alloc(rdi)
        elif name=='free':
            ret = 0
        elif name=='fclose':
            ret = 0
        elif name=='fread':
            # fread(ptr=rdi, size=rsi, nmemb=rdx, stream=rcx)
            ptr, sz, nm = rdi, rsi, rdx
            total = sz*nm
            avail = len(self.filedata)-self.filepos
            n = min(total, avail)
            uc.mem_write(ptr, self.filedata[self.filepos:self.filepos+n])
            self.filepos += n
            ret = n//sz if sz else 0
        elif name=='memcmp':
            a = uc.mem_read(rdi, rdx); b = uc.mem_read(rsi, rdx)
            ret = 0 if a==b else (1 if bytes(a)>bytes(b) else (2**64-1))
        elif name=='__printf_chk':
            # __printf_chk(flag=rdi, fmt=rsi, args...=rdx, rcx)
            fmt = self._cstr(rsi)
            self.printf_outputs.append((fmt, rdx, rcx, r8))
            ret = 0
        elif name=='fwrite':
            ret = rdx
        elif name=='__stack_chk_fail':
            uc.emu_stop(); return
        elif name=='__cxa_finalize':
            ret = 0
        else:
            ret = 0
        if ret is not None:
            uc.reg_write(UC_X86_REG_RAX, ret & 0xffffffffffffffff)
        # simulate ret: pop retaddr, jump
        uc.reg_write(UC_X86_REG_RSP, rsp+8)
        uc.reg_write(UC_X86_REG_RIP, retaddr)

    def _cstr(self, addr):
        out=b''
        while True:
            c=self.uc.mem_read(addr,1)
            if c==b'\x00': break
            out+=c; addr+=1
        return out.decode('latin1')

    def run(self):
        uc = self.uc
        # set stack
        rsp = STACK_ADDR + STACK_SIZE - 0x1000
        uc.reg_write(UC_X86_REG_RSP, rsp)
        # push a fake return address that we can detect
        uc.mem_map(FAKE_RET & ~0xfff, 0x1000)
        uc.reg_write(UC_X86_REG_RSP, rsp-8)
        uc.mem_write(rsp-8, struct.pack('<Q', FAKE_RET))
        # main(edi=argc=2, rsi=argv)
        uc.reg_write(UC_X86_REG_RDI, 2)
        uc.reg_write(UC_X86_REG_RSI, self.argv_arr)
        # fs base for stack canary at fs:[0x28]
        uc.mem_map(FS_BASE, 0x1000)
        uc.mem_write(FS_BASE+0x28, struct.pack('<Q', 0xdeadbeefcafebabe))
        try:
            uc.reg_write(UC_X86_REG_FS_BASE if hasattr(UC_X86_REG_FS_BASE,'__index__') else UC_X86_REG_FS, FS_BASE)
        except Exception:
            pass
        # Some unicorn need MSR for FS base
        try:
            from unicorn.x86_const import UC_X86_REG_MSR
            uc.msr_write(0xC0000100, FS_BASE)
        except Exception:
            pass
        try:
            uc.emu_start(MAIN, FAKE_RET, timeout=0, count=2000000)
        except UcError as e:
            print('UcError:', e, 'rip=', hex(uc.reg_read(UC_X86_REG_RIP)))
        rax = uc.reg_read(UC_X86_REG_RAX)
        return rax

    def format_outputs(self):
        res=[]
        for fmt, a1, a2, a3 in self.printf_outputs:
            # fmt 'accepted=%u guard=%02x\n' with args: first %u = a1(edx? no) -> per __printf_chk(flag,fmt,arg1,arg2)
            # __printf_chk(int flag, const char*fmt, ...): varargs start at rdx, rcx, r8...
            res.append((fmt, a1, a2, a3))
        return res

if __name__=='__main__':
    fn = sys.argv[1]
    data = open(fn,'rb').read()
    e = Emu(data)
    rax = e.run()
    print('main returned:', hex(rax), '=', rax if rax<0x80000000 else rax-0x100000000)
    for fmt,a1,a2,a3 in e.format_outputs():
        print('printf fmt=%r args=(%#x,%#x,%#x)'%(fmt,a1,a2,a3))
        try:
            print('  ->', fmt % (a1 & 0xffffffff, a2 & 0xff))
        except Exception as ex:
            print('  fmt err', ex)

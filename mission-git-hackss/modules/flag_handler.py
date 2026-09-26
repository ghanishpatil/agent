"""Flag detection and submission handler with advanced capabilities"""

import re
import math
import base64
import hashlib
import requests
from typing import Optional, List, Dict, Tuple
from collections import Counter
import json
import time

from core.config import Config


class FlagHandler:
    """Advanced flag detection, validation, decoding, and submission"""
    
    # Comprehensive CTF flag patterns
    DEFAULT_PATTERNS = [
        # Standard formats
        r'flag\{[^}]+\}',
        r'FLAG\{[^}]+\}',
        r'ctf\{[^}]+\}',
        r'CTF\{[^}]+\}',
        # Platform-specific
        r'htb\{[^}]+\}',
        r'HTB\{[^}]+\}',
        r'thm\{[^}]+\}',
        r'THM\{[^}]+\}',
        r'pico\{[^}]+\}',
        r'picoCTF\{[^}]+\}',
        r'PICO\{[^}]+\}',
        r'hack\{[^}]+\}',
        r'HACK\{[^}]+\}',
        r'root\{[^}]+\}',
        r'ROOT\{[^}]+\}',
        r'user\{[^}]+\}',
        r'USER\{[^}]+\}',
        # Regional/Event CTFs
        r'CSAW\{[^}]+\}',
        r'DEFCON\{[^}]+\}',
        r'SECCON\{[^}]+\}',
        r'HITCON\{[^}]+\}',
        r'ASIS\{[^}]+\}',
        r'RCTF\{[^}]+\}',
        r'SCTF\{[^}]+\}',
        r'BCTF\{[^}]+\}',
        r'TCTF\{[^}]+\}',
        r'WCTF\{[^}]+\}',
        r'HCTF\{[^}]+\}',
        r'NCTF\{[^}]+\}',
        r'ACTF\{[^}]+\}',
        r'DUCTF\{[^}]+\}',
        r'UIUCTF\{[^}]+\}',
        r'LACTF\{[^}]+\}',
        r'UTCTF\{[^}]+\}',
        r'TJCTF\{[^}]+\}',
        r'HSCTF\{[^}]+\}',
        r'BCACTF\{[^}]+\}',
        r'SDCTF\{[^}]+\}',
        r'LITCTF\{[^}]+\}',
        r'IMAGINARYCTF\{[^}]+\}',
        r'CORCTF\{[^}]+\}',
        r'DICECTF\{[^}]+\}',
        r'GOOGLECTF\{[^}]+\}',
        r'FBCTF\{[^}]+\}',
        r'INCTF\{[^}]+\}',
        r'BITSCTF\{[^}]+\}',
        r'RACTF\{[^}]+\}',
        r'NAHAMCON\{[^}]+\}',
        r'DEADFACE\{[^}]+\}',
        r'CYBERTALENTS\{[^}]+\}',
        # Hash-like patterns
        r'[A-Z0-9]{32}',
        r'[a-f0-9]{32}',
        r'[A-Z0-9]{64}',
        r'[a-f0-9]{64}',
        # UUID format
        r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',
    ]
    
    # Common false positives to filter
    FALSE_POSITIVES = [
        'flag{}', 'FLAG{}', 'ctf{}', 'CTF{}',
        'example', 'test', 'sample', 'placeholder',
        '00000000000000000000000000000000',
        'ffffffffffffffffffffffffffffffff',
        'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',
        '0123456789abcdef0123456789abcdef',
    ]
    
    def __init__(self, config: Config):
        self.config = config
        self.patterns = self._load_patterns()
        self._compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.patterns]
        self.submitted_flags: List[str] = []
        self.found_flags: List[Dict] = []
    
    def _load_patterns(self) -> List[str]:
        """Load flag patterns from config"""
        custom_patterns = self.config.get('flags.patterns', [])
        return custom_patterns + self.DEFAULT_PATTERNS
    
    def detect_flag(self, text: str, decode: bool = True) -> Optional[str]:
        """Detect flag in text with optional decoding"""
        if not text:
            return None
        
        # Direct pattern matching
        for pattern in self._compiled_patterns:
            match = pattern.search(text)
            if match:
                flag = match.group(0)
                if self._validate_flag(flag):
                    return flag
        
        # Try decoding if enabled
        if decode:
            decoded_flag = self._try_decode_flag(text)
            if decoded_flag:
                return decoded_flag
        
        return None
    
    def detect_all_flags(self, text: str, decode: bool = True) -> List[str]:
        """Detect all flags in text"""
        if not text:
            return []
        
        flags = []
        
        # Direct pattern matching
        for pattern in self._compiled_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                flag = match.group(0)
                if self._validate_flag(flag) and flag not in flags:
                    flags.append(flag)
        
        # Try decoding
        if decode:
            decoded_flag = self._try_decode_flag(text)
            if decoded_flag and decoded_flag not in flags:
                flags.append(decoded_flag)
        
        return flags

    def _try_decode_flag(self, text: str) -> Optional[str]:
        """Try various decodings to find hidden flags"""
        decoders = [
            ('base64', self._decode_base64),
            ('base32', self._decode_base32),
            ('hex', self._decode_hex),
            ('rot13', self._decode_rot13),
            ('url', self._decode_url),
            ('unicode', self._decode_unicode),
            ('binary', self._decode_binary),
            ('octal', self._decode_octal),
        ]
        
        for name, decoder in decoders:
            try:
                decoded = decoder(text)
                if decoded:
                    for pattern in self._compiled_patterns:
                        match = pattern.search(decoded)
                        if match:
                            return match.group(0)
            except:
                pass
        
        return None
    
    def _decode_base64(self, text: str) -> Optional[str]:
        """Decode base64"""
        b64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        matches = re.findall(b64_pattern, text)
        
        for match in matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                if decoded:
                    return decoded
            except:
                pass
        return None
    
    def _decode_base32(self, text: str) -> Optional[str]:
        """Decode base32"""
        b32_pattern = r'[A-Z2-7]{16,}={0,6}'
        matches = re.findall(b32_pattern, text)
        
        for match in matches:
            try:
                decoded = base64.b32decode(match).decode('utf-8', errors='ignore')
                if decoded:
                    return decoded
            except:
                pass
        return None
    
    def _decode_hex(self, text: str) -> Optional[str]:
        """Decode hex"""
        hex_pattern = r'[0-9a-fA-F]{20,}'
        matches = re.findall(hex_pattern, text)
        
        for match in matches:
            if len(match) % 2 == 0:
                try:
                    decoded = bytes.fromhex(match).decode('utf-8', errors='ignore')
                    if decoded:
                        return decoded
                except:
                    pass
        return None
    
    def _decode_rot13(self, text: str) -> Optional[str]:
        """Decode ROT13"""
        import codecs
        try:
            return codecs.decode(text, 'rot_13')
        except:
            return None
    
    def _decode_url(self, text: str) -> Optional[str]:
        """Decode URL encoding"""
        import urllib.parse
        try:
            decoded = urllib.parse.unquote(text)
            if decoded != text:
                return decoded
        except:
            pass
        return None
    
    def _decode_unicode(self, text: str) -> Optional[str]:
        """Decode unicode escapes"""
        try:
            if '\\u' in text or '\\x' in text:
                return text.encode().decode('unicode_escape')
        except:
            pass
        return None
    
    def _decode_binary(self, text: str) -> Optional[str]:
        """Decode binary"""
        binary_pattern = r'[01]{8,}'
        matches = re.findall(binary_pattern, text.replace(' ', ''))
        
        for match in matches:
            if len(match) % 8 == 0:
                try:
                    decoded = ''.join(chr(int(match[i:i+8], 2)) for i in range(0, len(match), 8))
                    if decoded:
                        return decoded
                except:
                    pass
        return None
    
    def _decode_octal(self, text: str) -> Optional[str]:
        """Decode octal"""
        try:
            parts = text.split()
            if all(all(c in '01234567' for c in p) for p in parts):
                decoded = ''.join(chr(int(p, 8)) for p in parts)
                return decoded
        except:
            pass
        return None
    
    def _validate_flag(self, flag: str) -> bool:
        """Validate flag format"""
        if not flag or len(flag) < 4:
            return False
        
        # Check for false positives
        if flag.lower() in [fp.lower() for fp in self.FALSE_POSITIVES]:
            return False
        
        # Check entropy for hash-like flags
        if re.match(r'^[a-fA-F0-9]{32,}$', flag):
            entropy = self.calculate_entropy(flag)
            if entropy < 2.0:
                return False
        
        return True
    
    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0
        
        counter = Counter(text)
        length = len(text)
        entropy = -sum((count/length) * math.log2(count/length) 
                      for count in counter.values() if count > 0)
        return entropy
    
    def is_encoded_flag(self, text: str) -> Tuple[bool, str]:
        """Check if text might be an encoded flag and identify encoding"""
        entropy = self.calculate_entropy(text)
        
        # High entropy suggests encoding
        if entropy > 4.0 and len(text) >= 20:
            # Try to identify encoding
            if re.match(r'^[A-Za-z0-9+/]+=*$', text) and len(text) % 4 == 0:
                return True, 'base64'
            if re.match(r'^[A-Z2-7]+=*$', text):
                return True, 'base32'
            if re.match(r'^[0-9a-fA-F]+$', text) and len(text) % 2 == 0:
                return True, 'hex'
            if re.match(r'^[01\s]+$', text):
                return True, 'binary'
            
            return True, 'unknown'
        
        return False, ''

    def submit_flag(self, flag: str, platform: str = 'ctfd', 
                   challenge_id: Optional[str] = None) -> Dict:
        """Submit flag to CTF platform"""
        if flag in self.submitted_flags:
            return {'success': False, 'error': 'Flag already submitted'}
        
        if not self.config.get('flags.auto_submit', False):
            return {'success': False, 'error': 'Auto-submit disabled'}
        
        result = {'success': False, 'flag': flag}
        
        if platform == 'ctfd':
            result = self._submit_ctfd(flag, challenge_id)
        elif platform == 'hackthebox':
            result = self._submit_htb(flag, challenge_id)
        elif platform == 'tryhackme':
            result = self._submit_thm(flag, challenge_id)
        elif platform == 'custom':
            result = self._submit_custom(flag, challenge_id)
        
        if result.get('success'):
            self.submitted_flags.append(flag)
            self.found_flags.append({
                'flag': flag,
                'platform': platform,
                'challenge_id': challenge_id,
                'timestamp': time.time(),
            })
        
        return result
    
    def _submit_ctfd(self, flag: str, challenge_id: Optional[str] = None) -> Dict:
        """Submit flag to CTFd platform"""
        url = self.config.get('platforms.ctfd.url')
        token = self.config.get('platforms.ctfd.token')
        
        if not url or not token:
            return {'success': False, 'error': 'CTFd not configured'}
        
        try:
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/json'
            }
            
            data = {'submission': flag}
            if challenge_id:
                data['challenge_id'] = challenge_id
            
            response = requests.post(
                f"{url}/api/v1/challenges/attempt",
                json=data,
                headers=headers,
                timeout=10
            )
            
            result = response.json()
            return {
                'success': result.get('data', {}).get('status') == 'correct',
                'response': result,
                'message': result.get('data', {}).get('message', '')
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _submit_htb(self, flag: str, challenge_id: Optional[str] = None) -> Dict:
        """Submit flag to HackTheBox"""
        api_key = self.config.get('platforms.hackthebox.api_key')
        
        if not api_key:
            return {'success': False, 'error': 'HTB not configured'}
        
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            url = 'https://www.hackthebox.com/api/v4/challenge/own'
            
            data = {
                'flag': flag,
                'id': challenge_id,
                'difficulty': 0
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            result = response.json()
            
            return {
                'success': result.get('success', False),
                'response': result
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _submit_thm(self, flag: str, challenge_id: Optional[str] = None) -> Dict:
        """Submit flag to TryHackMe"""
        api_key = self.config.get('platforms.tryhackme.api_key')
        
        if not api_key:
            return {'success': False, 'error': 'THM not configured'}
        
        return {'success': False, 'error': 'THM submission not fully implemented'}
    
    def _submit_custom(self, flag: str, challenge_id: Optional[str] = None) -> Dict:
        """Submit flag to custom platform"""
        url = self.config.get('platforms.custom.url')
        method = self.config.get('platforms.custom.method', 'POST')
        headers = self.config.get('platforms.custom.headers', {})
        
        if not url:
            return {'success': False, 'error': 'Custom platform not configured'}
        
        try:
            data = {'flag': flag}
            if challenge_id:
                data['challenge_id'] = challenge_id
            
            if method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                response = requests.get(url, params=data, headers=headers, timeout=10)
            
            return {
                'success': response.status_code == 200,
                'response': response.text
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def learn_pattern(self, flag: str):
        """Learn new flag pattern from successful flag"""
        if '{' in flag and '}' in flag:
            prefix = flag.split('{')[0]
            if prefix and len(prefix) <= 15:
                new_pattern = f'{re.escape(prefix)}\\{{[^}}]+\\}}'
                if new_pattern not in self.patterns:
                    self.patterns.append(new_pattern)
                    self._compiled_patterns.append(re.compile(new_pattern, re.IGNORECASE))
    
    def get_statistics(self) -> Dict:
        """Get flag handler statistics"""
        return {
            'total_found': len(self.found_flags),
            'total_submitted': len(self.submitted_flags),
            'patterns_count': len(self.patterns),
            'recent_flags': self.found_flags[-10:] if self.found_flags else [],
        }
    
    def export_flags(self, filepath: str):
        """Export found flags to file"""
        with open(filepath, 'w') as f:
            json.dump(self.found_flags, f, indent=2)
    
    def import_patterns(self, filepath: str):
        """Import additional patterns from file"""
        try:
            with open(filepath, 'r') as f:
                new_patterns = [line.strip() for line in f if line.strip()]
            
            for pattern in new_patterns:
                if pattern not in self.patterns:
                    self.patterns.append(pattern)
                    self._compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
        except Exception as e:
            raise ValueError(f"Failed to import patterns: {e}")

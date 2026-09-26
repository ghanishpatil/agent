"""Challenge classification using ML and advanced heuristics"""

import logging
import re
import mimetypes
from typing import Optional, List, Dict
from pathlib import Path
from collections import Counter

from .config import Config
from .challenge import Challenge


class ChallengeClassifier:
    """Advanced CTF challenge classifier with ML and heuristics"""
    
    CATEGORIES = ['web', 'crypto', 'pwn', 'reversing', 'forensics', 'osint', 'misc']
    
    # Comprehensive keyword mappings
    CATEGORY_KEYWORDS = {
        'web': [
            'web', 'http', 'https', 'url', 'website', 'xss', 'sql', 'sqli', 'injection',
            'ssrf', 'lfi', 'rfi', 'csrf', 'xxe', 'ssti', 'jwt', 'cookie', 'session',
            'php', 'javascript', 'html', 'css', 'api', 'rest', 'graphql', 'soap',
            'apache', 'nginx', 'tomcat', 'flask', 'django', 'express', 'node',
            'login', 'auth', 'admin', 'upload', 'download', 'form', 'input',
            'request', 'response', 'header', 'parameter', 'query', 'post', 'get',
            'deserialize', 'serialize', 'pickle', 'yaml', 'json', 'xml',
            'wordpress', 'drupal', 'joomla', 'laravel', 'spring', 'struts',
        ],
        'crypto': [
            'crypto', 'cryptography', 'cipher', 'encrypt', 'decrypt', 'hash',
            'rsa', 'aes', 'des', '3des', 'blowfish', 'rc4', 'chacha', 'salsa',
            'md5', 'sha', 'sha1', 'sha256', 'sha512', 'bcrypt', 'scrypt', 'argon',
            'base64', 'base32', 'base58', 'hex', 'binary', 'encode', 'decode',
            'caesar', 'rot13', 'vigenere', 'substitution', 'transposition',
            'xor', 'otp', 'one-time', 'pad', 'key', 'iv', 'nonce', 'salt',
            'prime', 'modulus', 'exponent', 'factor', 'gcd', 'lcm', 'euler',
            'diffie', 'hellman', 'ecdsa', 'ecdh', 'elliptic', 'curve',
            'signature', 'verify', 'sign', 'hmac', 'mac', 'padding', 'pkcs',
            'pem', 'der', 'certificate', 'openssl', 'gpg', 'pgp',
        ],
        'pwn': [
            'pwn', 'binary', 'exploit', 'exploitation', 'buffer', 'overflow',
            'bof', 'stack', 'heap', 'rop', 'ret2', 'shellcode', 'gadget',
            'libc', 'got', 'plt', 'canary', 'aslr', 'pie', 'nx', 'dep',
            'format', 'string', 'printf', 'scanf', 'gets', 'strcpy', 'memcpy',
            'use-after-free', 'uaf', 'double-free', 'tcache', 'fastbin',
            'malloc', 'free', 'chunk', 'arena', 'glibc', 'musl',
            'sigreturn', 'srop', 'csu', 'one_gadget', 'magic', 'offset',
            'remote', 'local', 'nc', 'netcat', 'socket', 'connect',
            'elf', 'executable', 'segment', 'section', 'symbol',
            'pwntools', 'gdb', 'peda', 'gef', 'pwndbg', 'radare',
        ],
        'reversing': [
            'reverse', 'reversing', 'engineering', 'decompile', 'disassemble',
            'binary', 'executable', 'elf', 'pe', 'mach-o', 'dll', 'so',
            'assembly', 'asm', 'x86', 'x64', 'arm', 'mips', 'risc',
            'ida', 'ghidra', 'radare', 'r2', 'objdump', 'readelf', 'nm',
            'debug', 'breakpoint', 'trace', 'step', 'register', 'memory',
            'obfuscate', 'pack', 'unpack', 'upx', 'vmprotect', 'themida',
            'anti-debug', 'anti-vm', 'anti-analysis', 'sandbox', 'evasion',
            'malware', 'virus', 'trojan', 'ransomware', 'backdoor',
            'java', 'class', 'jar', 'apk', 'android', 'dalvik', 'smali',
            'dotnet', '.net', 'csharp', 'msil', 'dnspy', 'ilspy',
            'python', 'pyc', 'pyo', 'bytecode', 'decompyle', 'uncompyle',
            'go', 'golang', 'rust', 'swift', 'kotlin',
        ],
        'forensics': [
            'forensics', 'forensic', 'investigation', 'analysis', 'examine',
            'stego', 'steganography', 'hidden', 'secret', 'embed', 'extract',
            'image', 'picture', 'photo', 'png', 'jpg', 'jpeg', 'gif', 'bmp',
            'audio', 'sound', 'wav', 'mp3', 'flac', 'ogg', 'spectrogram',
            'video', 'mp4', 'avi', 'mkv', 'mov', 'frame',
            'pcap', 'pcapng', 'network', 'packet', 'capture', 'wireshark',
            'memory', 'dump', 'volatility', 'ram', 'process', 'registry',
            'disk', 'image', 'dd', 'raw', 'e01', 'partition', 'filesystem',
            'file', 'carve', 'recover', 'deleted', 'slack', 'unallocated',
            'metadata', 'exif', 'timestamp', 'magic', 'signature', 'header',
            'zip', 'rar', '7z', 'tar', 'gzip', 'archive', 'compress',
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'office',
            'binwalk', 'foremost', 'scalpel', 'autopsy', 'sleuthkit',
            'strings', 'hexdump', 'xxd', 'file', 'exiftool',
        ],
        'osint': [
            'osint', 'recon', 'reconnaissance', 'intelligence', 'gathering',
            'social', 'media', 'twitter', 'facebook', 'instagram', 'linkedin',
            'github', 'gitlab', 'bitbucket', 'repository', 'commit', 'history',
            'google', 'search', 'dork', 'shodan', 'censys', 'zoomeye',
            'whois', 'dns', 'domain', 'subdomain', 'ip', 'geolocation',
            'email', 'phone', 'address', 'person', 'company', 'organization',
            'wayback', 'archive', 'cache', 'snapshot', 'historical',
            'image', 'reverse', 'tineye', 'yandex', 'bing',
            'metadata', 'exif', 'gps', 'location', 'coordinates',
            'username', 'profile', 'account', 'identity', 'track',
            'breach', 'leak', 'password', 'credential', 'haveibeenpwned',
        ],
    }
    
    # File extension to category mapping
    EXTENSION_MAPPING = {
        # Web
        '.php': 'web', '.html': 'web', '.htm': 'web', '.js': 'web',
        '.css': 'web', '.asp': 'web', '.aspx': 'web', '.jsp': 'web',
        # Crypto
        '.pem': 'crypto', '.key': 'crypto', '.crt': 'crypto', '.cer': 'crypto',
        '.p12': 'crypto', '.pfx': 'crypto', '.gpg': 'crypto', '.asc': 'crypto',
        # Binary/Pwn
        '.elf': 'pwn', '.bin': 'pwn', '.out': 'pwn',
        # Reversing
        '.exe': 'reversing', '.dll': 'reversing', '.so': 'reversing',
        '.apk': 'reversing', '.jar': 'reversing', '.class': 'reversing',
        '.pyc': 'reversing', '.pyo': 'reversing',
        # Forensics
        '.pcap': 'forensics', '.pcapng': 'forensics', '.cap': 'forensics',
        '.png': 'forensics', '.jpg': 'forensics', '.jpeg': 'forensics',
        '.gif': 'forensics', '.bmp': 'forensics', '.tiff': 'forensics',
        '.wav': 'forensics', '.mp3': 'forensics', '.flac': 'forensics',
        '.mp4': 'forensics', '.avi': 'forensics', '.mkv': 'forensics',
        '.pdf': 'forensics', '.doc': 'forensics', '.docx': 'forensics',
        '.zip': 'forensics', '.rar': 'forensics', '.7z': 'forensics',
        '.tar': 'forensics', '.gz': 'forensics', '.bz2': 'forensics',
        '.dmp': 'forensics', '.vmem': 'forensics', '.raw': 'forensics',
        '.e01': 'forensics', '.dd': 'forensics', '.img': 'forensics',
    }
    
    # Magic bytes for file type detection
    MAGIC_BYTES = {
        b'\x89PNG': 'forensics',
        b'\xff\xd8\xff': 'forensics',
        b'GIF8': 'forensics',
        b'PK\x03\x04': 'forensics',
        b'%PDF': 'forensics',
        b'\x7fELF': 'pwn',
        b'MZ': 'reversing',
        b'\xca\xfe\xba\xbe': 'reversing',
        b'\xd0\xcf\x11\xe0': 'forensics',
        b'RIFF': 'forensics',
        b'ID3': 'forensics',
        b'OggS': 'forensics',
        b'fLaC': 'forensics',
        b'\xd4\xc3\xb2\xa1': 'forensics',  # pcap
        b'\xa1\xb2\xc3\xd4': 'forensics',  # pcap
        b'\x0a\x0d\x0d\x0a': 'forensics',  # pcapng
    }
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger('md-exploit-engine.classifier')
        self.model = None
        
        # Try to load ML model
        model_path = config.get('classification.ml_model')
        if model_path and Path(model_path).exists():
            self._load_model(model_path)
    
    def _load_model(self, model_path: str):
        """Load pre-trained classification model"""
        try:
            import pickle
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.logger.info(f"Loaded ML model from {model_path}")
        except Exception as e:
            self.logger.warning(f"Failed to load ML model: {e}")
    
    def classify(self, challenge: Challenge) -> str:
        """Classify challenge into category using multiple methods"""
        scores = {cat: 0.0 for cat in self.CATEGORIES}
        
        # Try ML model first
        if self.model:
            try:
                ml_category = self._ml_classify(challenge)
                if ml_category:
                    scores[ml_category] += 5.0
            except Exception as e:
                self.logger.warning(f"ML classification failed: {e}")
        
        # Keyword analysis
        keyword_scores = self._keyword_classify(challenge)
        for cat, score in keyword_scores.items():
            scores[cat] += score
        
        # File extension analysis
        ext_category = self._extension_classify(challenge)
        if ext_category:
            scores[ext_category] += 3.0
        
        # Magic bytes analysis
        magic_category = self._magic_classify(challenge)
        if magic_category:
            scores[magic_category] += 4.0
        
        # URL analysis
        if challenge.url:
            scores['web'] += 5.0
        
        # Connection analysis
        if challenge.has_connection:
            scores['pwn'] += 2.0
            scores['web'] += 1.0
        
        # Get highest scoring category
        best_category = max(scores, key=scores.get)
        
        # If no clear winner, default to misc
        if scores[best_category] < 1.0:
            return 'misc'
        
        self.logger.info(f"Classification scores: {scores}")
        return best_category
    
    def _ml_classify(self, challenge: Challenge) -> Optional[str]:
        """Classify using ML model"""
        if not self.model:
            return None
        
        # Prepare features
        text = f"{challenge.name} {challenge.description}".lower()
        
        try:
            prediction = self.model.predict([text])[0]
            return prediction if prediction in self.CATEGORIES else None
        except:
            return None
    
    def _keyword_classify(self, challenge: Challenge) -> Dict[str, float]:
        """Classify based on keyword matching"""
        scores = {cat: 0.0 for cat in self.CATEGORIES}
        
        text = f"{challenge.name} {challenge.description}".lower()
        words = set(re.findall(r'\b\w+\b', text))
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    # Exact word match gets higher score
                    if keyword in words:
                        scores[category] += 1.0
                    else:
                        scores[category] += 0.5
        
        return scores
    
    def _extension_classify(self, challenge: Challenge) -> Optional[str]:
        """Classify based on file extensions"""
        if not challenge.has_files:
            return None
        
        ext_counts = Counter()
        
        for file in challenge.files:
            ext = file.suffix.lower()
            if ext in self.EXTENSION_MAPPING:
                ext_counts[self.EXTENSION_MAPPING[ext]] += 1
        
        if ext_counts:
            return ext_counts.most_common(1)[0][0]
        
        return None
    
    def _magic_classify(self, challenge: Challenge) -> Optional[str]:
        """Classify based on file magic bytes"""
        if not challenge.has_files:
            return None
        
        for file in challenge.files:
            try:
                with open(file, 'rb') as f:
                    header = f.read(16)
                
                for magic, category in self.MAGIC_BYTES.items():
                    if header.startswith(magic):
                        return category
            except:
                pass
        
        return None
    
    def _heuristic_classify(self, challenge: Challenge) -> str:
        """Legacy heuristic classification (fallback)"""
        text = f"{challenge.name} {challenge.description}".lower()
        
        # Simple keyword matching
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in text for kw in keywords[:10]):
                return category
        
        return 'misc'
    
    def get_confidence(self, challenge: Challenge) -> Dict[str, float]:
        """Get classification confidence scores for all categories"""
        scores = {cat: 0.0 for cat in self.CATEGORIES}
        
        keyword_scores = self._keyword_classify(challenge)
        for cat, score in keyword_scores.items():
            scores[cat] += score
        
        ext_category = self._extension_classify(challenge)
        if ext_category:
            scores[ext_category] += 3.0
        
        magic_category = self._magic_classify(challenge)
        if magic_category:
            scores[magic_category] += 4.0
        
        # Normalize to percentages
        total = sum(scores.values())
        if total > 0:
            scores = {cat: (score / total) * 100 for cat, score in scores.items()}
        
        return scores

"""Cryptography solver module - Advanced crypto analysis and attacks"""

import base64
import string
import hashlib
import binascii
import struct
import itertools
import re
from collections import Counter
from typing import Optional, List, Tuple, Dict
import math

# Try to import crypt (Unix only)
try:
    import crypt
    HAS_CRYPT = True
except ImportError:
    HAS_CRYPT = False

from core.challenge import Challenge, ChallengeResult
from .base import BaseModule


class CryptoModule(BaseModule):
    """Advanced automated cryptography solving with comprehensive attacks"""
    
    HASH_PATTERNS = {
        32: ['md5', 'md4', 'md2', 'ntlm'],
        40: ['sha1', 'ripemd160'],
        56: ['sha224', 'sha3-224'],
        64: ['sha256', 'sha3-256', 'blake2s'],
        96: ['sha384', 'sha3-384'],
        128: ['sha512', 'sha3-512', 'blake2b', 'whirlpool'],
    }
    
    # John the Ripper style hash format detection
    JOHN_HASH_FORMATS = {
        r'^\$1\$': 'md5crypt',           # $1$salt$hash
        r'^\$2[aby]?\$': 'bcrypt',       # $2a$, $2b$, $2y$
        r'^\$5\$': 'sha256crypt',        # $5$salt$hash
        r'^\$6\$': 'sha512crypt',        # $6$salt$hash
        r'^\$apr1\$': 'apr1',            # Apache MD5
        r'^\$P\$': 'phpass',             # PHPass (WordPress, phpBB)
        r'^\$H\$': 'phpass',             # PHPass variant
        r'^\{SHA\}': 'ldap_sha1',        # LDAP SHA1
        r'^\{SSHA\}': 'ldap_ssha',       # LDAP Salted SHA1
        r'^\{MD5\}': 'ldap_md5',         # LDAP MD5
        r'^\{SMD5\}': 'ldap_smd5',       # LDAP Salted MD5
        r'^[a-f0-9]{32}:[a-f0-9]+$': 'md5_salt',  # MD5 with salt
        r'^[a-f0-9]{64}:[a-f0-9]+$': 'sha256_salt',  # SHA256 with salt
        r'^[a-f0-9]{32}$': 'raw_md5',
        r'^[a-f0-9]{40}$': 'raw_sha1',
        r'^[a-f0-9]{64}$': 'raw_sha256',
        r'^[a-f0-9]{128}$': 'raw_sha512',
        r'^[A-Za-z0-9./]{13}$': 'descrypt',  # Traditional DES crypt
        r'^[A-Za-z0-9+/]{22}==$': 'base64_hash',
    }
    
    ENGLISH_FREQ = {
        'e': 12.7, 't': 9.1, 'a': 8.2, 'o': 7.5, 'i': 7.0, 'n': 6.7,
        's': 6.3, 'h': 6.1, 'r': 6.0, 'd': 4.3, 'l': 4.0, 'c': 2.8,
        'u': 2.8, 'm': 2.4, 'w': 2.4, 'f': 2.2, 'g': 2.0, 'y': 2.0,
        'p': 1.9, 'b': 1.5, 'v': 1.0, 'k': 0.8, 'j': 0.15, 'x': 0.15,
        'q': 0.10, 'z': 0.07
    }
    
    # Extended password wordlist for John the Ripper style cracking
    COMMON_PASSWORDS = [
        'flag', 'password', 'admin', '123456', 'secret', 'ctf', 'test',
        'root', 'toor', 'pass', 'letmein', 'welcome', 'monkey', 'dragon',
        'master', 'qwerty', 'login', 'passw0rd', 'abc123', 'iloveyou',
        'trustno1', 'sunshine', 'princess', 'football', 'shadow', 'superman',
        'michael', 'ninja', 'mustang', 'password1', 'password123', 'batman',
    ]
    
    # Extended John the Ripper wordlist
    JOHN_WORDLIST = [
        # Top 100 passwords
        '123456', 'password', '12345678', 'qwerty', '123456789', '12345', '1234',
        '111111', '1234567', 'dragon', '123123', 'baseball', 'abc123', 'football',
        'monkey', 'letmein', 'shadow', 'master', '666666', 'qwertyuiop', '123321',
        'mustang', '1234567890', 'michael', '654321', 'superman', '1qaz2wsx',
        '7777777', '121212', '000000', 'qazwsx', '123qwe', 'killer', 'trustno1',
        'jordan', 'jennifer', 'zxcvbnm', 'asdfgh', 'hunter', 'buster', 'soccer',
        'harley', 'batman', 'andrew', 'tigger', 'sunshine', 'iloveyou', '2000',
        'charlie', 'robert', 'thomas', 'hockey', 'ranger', 'daniel', 'starwars',
        'klaster', '112233', 'george', 'computer', 'michelle', 'jessica', 'pepper',
        '1111', 'zxcvbn', '555555', '11111111', '131313', 'freedom', '777777',
        'pass', 'maggie', '159753', 'aaaaaa', 'ginger', 'princess', 'joshua',
        'cheese', 'amanda', 'summer', 'love', 'ashley', 'nicole', 'chelsea',
        'biteme', 'matthew', 'access', 'yankees', '987654321', 'dallas', 'austin',
        'thunder', 'taylor', 'matrix', 'mobilemail', 'mom', 'monitor', 'monitoring',
        'montana', 'moon', 'moscow',
        # CTF specific
        'flag', 'ctf', 'capture', 'theflag', 'secret', 'hidden', 'admin', 'root',
        'user', 'guest', 'test', 'demo', 'hacker', 'hack', 'pwned', 'owned',
        'security', 'secure', 'private', 'public', 'key', 'token', 'auth',
        # Leetspeak variations
        'p4ssw0rd', 'p@ssw0rd', 'p@$$w0rd', 'adm1n', '@dm1n', 's3cr3t', 'fl4g',
        'h4ck3r', 'r00t', 't3st', 'us3r', 'gu3st', 'k3y', 't0k3n',
        # Common patterns
        'password1', 'password123', 'password!', 'admin123', 'admin1', 'root123',
        'test123', 'user123', 'guest123', 'letmein1', 'welcome1', 'changeme',
        # Years
        '2020', '2021', '2022', '2023', '2024', '2025', '2026',
        # Keyboard patterns
        'qwerty', 'qwerty123', 'asdfgh', 'zxcvbn', '1qaz2wsx', 'qazwsx',
        # Simple patterns
        'aaa', 'aaaa', 'aaaaa', 'aaaaaa', 'abc', 'abcd', 'abcde', 'abcdef',
        '111', '1111', '11111', '111111', '1234', '12345', '123456',
    ]
    
    # Playfair key matrix
    PLAYFAIR_KEYS = ['playfair', 'keyword', 'cipher', 'secret', 'crypto', 'matrix']
    
    def solve(self, challenge: Challenge) -> ChallengeResult:
        """Solve crypto challenge with comprehensive advanced techniques"""
        result = self.create_result(challenge, False)
        data = self._read_challenge_data(challenge)
        if not data:
            result.error = "No data to analyze"
            return result
        
        result.add_log(f"Analyzing {len(data)} bytes of data")
        
        # Comprehensive crypto techniques - ordered by likelihood
        techniques = [
            # Basic encodings
            self._try_base_encodings,
            self._try_hex,
            self._try_binary,
            self._try_octal,
            self._try_decimal_ascii,
            self._try_url_encoding,
            
            # Classical ciphers
            self._try_caesar,
            self._try_rot13,
            self._try_rot47,
            self._try_atbash,
            self._try_vigenere,
            self._try_vigenere_crack,
            self._try_rail_fence,
            self._try_affine,
            self._try_playfair,
            self._try_columnar_transposition,
            self._try_beaufort,
            self._try_autokey,
            
            # XOR attacks
            self._try_xor_bruteforce,
            self._try_xor_repeating_key,
            self._try_xor_known_plaintext,
            
            # Modern crypto attacks
            self._try_rsa_attacks,
            self._try_rsa_wiener,
            self._try_rsa_common_modulus,
            self._try_ecb_detection,
            self._try_padding_oracle_detect,
            
            # Hash attacks
            self._try_hash_lookup,
            self._try_hash_length_extension,
            self._try_john_crack,  # John the Ripper style cracking
            
            # Other encodings
            self._try_morse_code,
            self._try_bacon_cipher,
            self._try_a1z26,
            self._try_tap_code,
            self._try_polybius,
            
            # Advanced
            self._try_frequency_analysis,
            self._try_substitution_crack,
        ]
        
        for technique in techniques:
            try:
                flag = technique(data, result)
                if flag:
                    result.success = True
                    result.flag = flag
                    result.method = technique.__name__
                    return result
            except Exception as e:
                result.add_log(f"Error in {technique.__name__}: {e}")
        
        result.error = "Could not decrypt/decode data"
        return result
    
    def _read_challenge_data(self, challenge: Challenge) -> str:
        if challenge.has_files:
            try:
                return challenge.files[0].read_text()
            except:
                return challenge.files[0].read_bytes().decode('utf-8', errors='ignore')
        elif challenge.description:
            return challenge.description
        return ""
    
    def _try_decimal_ascii(self, data: str, result: ChallengeResult) -> str:
        """Try decimal ASCII decoding"""
        result.add_log("Trying decimal ASCII...")
        try:
            # Space-separated decimals
            parts = data.split()
            if all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
                decoded = ''.join(chr(int(p)) for p in parts)
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log("Found flag in decimal ASCII")
                    return flag
            
            # Comma-separated
            parts = data.replace(',', ' ').split()
            if all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
                decoded = ''.join(chr(int(p)) for p in parts)
                flag = self.extract_flag(decoded)
                if flag:
                    return flag
        except:
            pass
        return None
    
    def _try_url_encoding(self, data: str, result: ChallengeResult) -> str:
        """Try URL decoding"""
        result.add_log("Trying URL decoding...")
        try:
            import urllib.parse
            decoded = urllib.parse.unquote(data)
            if decoded != data:
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log("Found flag in URL decoded data")
                    return flag
                # Try double decoding
                decoded2 = urllib.parse.unquote(decoded)
                flag = self.extract_flag(decoded2)
                if flag:
                    return flag
        except:
            pass
        return None

    def _try_base_encodings(self, data: str, result: ChallengeResult) -> str:
        """Try various base encodings including base58, base62, base91"""
        result.add_log("Trying base encodings (64, 32, 16, 58, 62, 85, 91)...")
        clean_data = data.strip()
        
        # Base64 (nested up to 10 levels)
        try:
            temp = clean_data
            for i in range(10):
                try:
                    decoded = base64.b64decode(temp + '==').decode('utf-8', errors='ignore')
                    flag = self.extract_flag(decoded)
                    if flag:
                        result.add_log(f"Found flag in base64 (level {i+1})")
                        return flag
                    temp = decoded
                except:
                    break
        except:
            pass
        
        # Base64 URL-safe
        try:
            decoded = base64.urlsafe_b64decode(clean_data + '==').decode('utf-8', errors='ignore')
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log("Found flag in base64 URL-safe")
                return flag
        except:
            pass
        
        # Base32
        try:
            decoded = base64.b32decode(clean_data.upper()).decode('utf-8', errors='ignore')
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log("Found flag in base32")
                return flag
        except:
            pass
        
        # Base16 (hex)
        try:
            decoded = base64.b16decode(clean_data.upper()).decode('utf-8', errors='ignore')
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log("Found flag in base16")
                return flag
        except:
            pass
        
        # Base85 / ASCII85
        try:
            decoded = base64.b85decode(clean_data).decode('utf-8', errors='ignore')
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log("Found flag in base85")
                return flag
        except:
            pass
        
        try:
            decoded = base64.a85decode(clean_data).decode('utf-8', errors='ignore')
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log("Found flag in ASCII85")
                return flag
        except:
            pass
        
        # Base58 (Bitcoin style)
        try:
            flag = self._decode_base58(clean_data, result)
            if flag:
                return flag
        except:
            pass
        
        # Base62
        try:
            flag = self._decode_base62(clean_data, result)
            if flag:
                return flag
        except:
            pass
        
        return None
    
    def _decode_base58(self, data: str, result: ChallengeResult) -> str:
        """Decode base58"""
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        try:
            num = 0
            for char in data:
                num = num * 58 + alphabet.index(char)
            decoded = num.to_bytes((num.bit_length() + 7) // 8, 'big').decode('utf-8', errors='ignore')
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log("Found flag in base58")
                return flag
        except:
            pass
        return None
    
    def _decode_base62(self, data: str, result: ChallengeResult) -> str:
        """Decode base62"""
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        try:
            num = 0
            for char in data:
                num = num * 62 + alphabet.index(char)
            decoded = num.to_bytes((num.bit_length() + 7) // 8, 'big').decode('utf-8', errors='ignore')
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log("Found flag in base62")
                return flag
        except:
            pass
        return None
    
    def _try_caesar(self, data: str, result: ChallengeResult) -> str:
        """Try Caesar cipher with all shifts"""
        result.add_log("Trying Caesar cipher...")
        for shift in range(26):
            decoded = self._caesar_shift(data, shift)
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log(f"Found flag with Caesar shift {shift}")
                return flag
        return None
    
    def _caesar_shift(self, text: str, shift: int) -> str:
        result = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted = chr((ord(char) - base + shift) % 26 + base)
                result.append(shifted)
            else:
                result.append(char)
        return ''.join(result)
    
    def _try_rot13(self, data: str, result: ChallengeResult) -> str:
        """Try ROT13"""
        result.add_log("Trying ROT13...")
        import codecs
        decoded = codecs.decode(data, 'rot_13')
        flag = self.extract_flag(decoded)
        if flag:
            result.add_log("Found flag with ROT13")
            return flag
        return None
    
    def _try_rot47(self, data: str, result: ChallengeResult) -> str:
        """Try ROT47"""
        result.add_log("Trying ROT47...")
        decoded = []
        for char in data:
            if 33 <= ord(char) <= 126:
                decoded.append(chr(33 + ((ord(char) - 33 + 47) % 94)))
            else:
                decoded.append(char)
        decoded_str = ''.join(decoded)
        flag = self.extract_flag(decoded_str)
        if flag:
            result.add_log("Found flag with ROT47")
            return flag
        return None
    
    def _try_atbash(self, data: str, result: ChallengeResult) -> str:
        """Try Atbash cipher"""
        result.add_log("Trying Atbash cipher...")
        decoded = []
        for char in data:
            if char.isalpha():
                if char.isupper():
                    decoded.append(chr(ord('Z') - (ord(char) - ord('A'))))
                else:
                    decoded.append(chr(ord('z') - (ord(char) - ord('a'))))
            else:
                decoded.append(char)
        decoded_str = ''.join(decoded)
        flag = self.extract_flag(decoded_str)
        if flag:
            result.add_log("Found flag with Atbash")
            return flag
        return None

    def _try_vigenere(self, data: str, result: ChallengeResult) -> str:
        """Try Vigenere cipher with common keys"""
        result.add_log("Trying Vigenere cipher...")
        common_keys = ['flag', 'key', 'ctf', 'secret', 'password', 'crypto', 'cipher', 'hack',
                      'admin', 'test', 'hidden', 'encode', 'decode', 'vigenere', 'keyword']
        for key in common_keys:
            decoded = self._vigenere_decrypt(data, key)
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log(f"Found flag with Vigenere key: {key}")
                return flag
        return None
    
    def _try_vigenere_crack(self, data: str, result: ChallengeResult) -> str:
        """Crack Vigenere using Kasiski examination and frequency analysis"""
        result.add_log("Trying to crack Vigenere cipher...")
        
        # Only try on alphabetic data
        alpha_only = ''.join(c for c in data if c.isalpha())
        if len(alpha_only) < 20:
            return None
        
        # Try key lengths 1-10
        for key_len in range(1, 11):
            key = self._crack_vigenere_key(alpha_only, key_len)
            if key:
                decoded = self._vigenere_decrypt(data, key)
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log(f"Cracked Vigenere with key: {key}")
                    return flag
        return None
    
    def _crack_vigenere_key(self, ciphertext: str, key_length: int) -> str:
        """Crack Vigenere key using frequency analysis"""
        key = ''
        ciphertext = ciphertext.upper()
        
        for i in range(key_length):
            # Get every key_length-th character starting at position i
            substring = ciphertext[i::key_length]
            
            # Find the shift that produces the best frequency match
            best_shift = 0
            best_score = float('inf')
            
            for shift in range(26):
                decrypted = ''.join(chr((ord(c) - ord('A') - shift) % 26 + ord('A')) for c in substring)
                score = self._chi_squared_score(decrypted)
                if score < best_score:
                    best_score = score
                    best_shift = shift
            
            key += chr(best_shift + ord('A'))
        
        return key.lower()
    
    def _chi_squared_score(self, text: str) -> float:
        """Calculate chi-squared score for frequency analysis"""
        expected = {'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 12.7, 'F': 2.2,
                   'G': 2.0, 'H': 6.1, 'I': 7.0, 'J': 0.15, 'K': 0.8, 'L': 4.0,
                   'M': 2.4, 'N': 6.7, 'O': 7.5, 'P': 1.9, 'Q': 0.1, 'R': 6.0,
                   'S': 6.3, 'T': 9.1, 'U': 2.8, 'V': 1.0, 'W': 2.4, 'X': 0.15,
                   'Y': 2.0, 'Z': 0.07}
        
        counts = Counter(text.upper())
        total = sum(counts.values())
        if total == 0:
            return float('inf')
        
        score = 0
        for letter, exp_freq in expected.items():
            observed = counts.get(letter, 0) / total * 100
            score += (observed - exp_freq) ** 2 / exp_freq
        
        return score
    
    def _vigenere_decrypt(self, ciphertext: str, key: str) -> str:
        result = []
        key_index = 0
        key = key.lower()
        for char in ciphertext:
            if char.isalpha():
                shift = ord(key[key_index % len(key)]) - ord('a')
                if char.isupper():
                    decrypted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                else:
                    decrypted = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
                result.append(decrypted)
                key_index += 1
            else:
                result.append(char)
        return ''.join(result)
    
    def _try_rail_fence(self, data: str, result: ChallengeResult) -> str:
        """Try Rail Fence cipher"""
        result.add_log("Trying Rail Fence cipher...")
        for rails in range(2, 10):
            decoded = self._rail_fence_decrypt(data, rails)
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log(f"Found flag with Rail Fence ({rails} rails)")
                return flag
        return None
    
    def _rail_fence_decrypt(self, ciphertext: str, rails: int) -> str:
        if rails < 2:
            return ciphertext
        n = len(ciphertext)
        fence = [['' for _ in range(n)] for _ in range(rails)]
        rail, direction = 0, 1
        for i in range(n):
            fence[rail][i] = '*'
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        index = 0
        for r in range(rails):
            for c in range(n):
                if fence[r][c] == '*' and index < len(ciphertext):
                    fence[r][c] = ciphertext[index]
                    index += 1
        result = []
        rail, direction = 0, 1
        for i in range(n):
            result.append(fence[rail][i])
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        return ''.join(result)
    
    def _try_hex(self, data: str, result: ChallengeResult) -> str:
        """Try hex decoding"""
        result.add_log("Trying hex decode...")
        try:
            clean_data = data.replace(' ', '').replace(':', '').replace('-', '').replace('\n', '')
            if all(c in string.hexdigits for c in clean_data):
                decoded = bytes.fromhex(clean_data).decode('utf-8', errors='ignore')
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log("Found flag in hex-decoded data")
                    return flag
        except: pass
        return None
    
    def _try_binary(self, data: str, result: ChallengeResult) -> str:
        """Try binary decoding"""
        result.add_log("Trying binary decode...")
        try:
            clean_data = data.replace(' ', '').replace('\n', '')
            if all(c in '01' for c in clean_data):
                while len(clean_data) % 8 != 0:
                    clean_data = '0' + clean_data
                decoded = ''
                for i in range(0, len(clean_data), 8):
                    byte = clean_data[i:i+8]
                    decoded += chr(int(byte, 2))
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log("Found flag in binary data")
                    return flag
        except: pass
        return None
    
    def _try_octal(self, data: str, result: ChallengeResult) -> str:
        """Try octal decoding"""
        result.add_log("Trying octal decode...")
        try:
            parts = data.split()
            if all(all(c in '01234567' for c in p) for p in parts):
                decoded = ''.join(chr(int(p, 8)) for p in parts)
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log("Found flag in octal data")
                    return flag
        except: pass
        return None

    def _try_xor_bruteforce(self, data: str, result: ChallengeResult) -> str:
        """Try XOR with single-byte keys"""
        result.add_log("Trying XOR bruteforce...")
        try:
            data_bytes = data.encode('utf-8')
            for key in range(256):
                decoded = bytes([b ^ key for b in data_bytes]).decode('utf-8', errors='ignore')
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log(f"Found flag with XOR key {key}")
                    return flag
        except: pass
        return None
    
    def _try_xor_repeating_key(self, data: str, result: ChallengeResult) -> str:
        """Try XOR with repeating key"""
        result.add_log("Trying XOR with common keys...")
        common_keys = [b'flag', b'key', b'ctf', b'secret', b'password']
        try:
            data_bytes = data.encode('utf-8')
            for key in common_keys:
                decoded = bytes([data_bytes[i] ^ key[i % len(key)] for i in range(len(data_bytes))])
                decoded_str = decoded.decode('utf-8', errors='ignore')
                flag = self.extract_flag(decoded_str)
                if flag:
                    result.add_log(f"Found flag with XOR key: {key.decode()}")
                    return flag
        except: pass
        return None
    
    def _try_hash_lookup(self, data: str, result: ChallengeResult) -> str:
        """Try to identify and crack hash with extended wordlist"""
        result.add_log("Trying hash identification and cracking...")
        clean_data = data.strip().lower()
        
        # Check if it looks like a hash
        if not all(c in string.hexdigits for c in clean_data):
            return None
        
        hash_len = len(clean_data)
        if hash_len not in self.HASH_PATTERNS:
            return None
        
        result.add_log(f"Detected possible {self.HASH_PATTERNS[hash_len]} hash")
        
        # Extended wordlist
        wordlist = self.COMMON_PASSWORDS + [
            # Numbers
            str(i) for i in range(1000)
        ] + [
            # Common variations
            f"flag{{{w}}}" for w in ['test', 'admin', 'secret', 'password']
        ] + [
            # Leetspeak
            'p4ssw0rd', 'adm1n', 's3cr3t', 'fl4g', 'h4ck3r'
        ]
        
        for pwd in wordlist:
            for algo in ['md5', 'sha1', 'sha256', 'sha512', 'sha224', 'sha384']:
                try:
                    h = hashlib.new(algo)
                    h.update(pwd.encode())
                    if h.hexdigest() == clean_data:
                        result.add_log(f"Hash cracked ({algo}): {pwd}")
                        flag = self.extract_flag(pwd)
                        return flag if flag else pwd
                except:
                    pass
        
        # Try double hashing
        for pwd in self.COMMON_PASSWORDS[:20]:
            for algo in ['md5', 'sha1', 'sha256']:
                try:
                    h1 = hashlib.new(algo, pwd.encode()).hexdigest()
                    h2 = hashlib.new(algo, h1.encode()).hexdigest()
                    if h2 == clean_data:
                        result.add_log(f"Double {algo} hash cracked: {pwd}")
                        return pwd
                except:
                    pass
        
        return None
    
    def _try_hash_length_extension(self, data: str, result: ChallengeResult) -> str:
        """Detect potential hash length extension vulnerability"""
        result.add_log("Checking for hash length extension...")
        # This is a detection only - actual exploitation requires more context
        return None
    
    def _try_playfair(self, data: str, result: ChallengeResult) -> str:
        """Try Playfair cipher with common keys"""
        result.add_log("Trying Playfair cipher...")
        
        for key in self.PLAYFAIR_KEYS:
            decoded = self._playfair_decrypt(data, key)
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log(f"Found flag with Playfair key: {key}")
                return flag
        return None
    
    def _playfair_decrypt(self, ciphertext: str, key: str) -> str:
        """Decrypt Playfair cipher"""
        # Build key matrix
        key = key.upper().replace('J', 'I')
        matrix = []
        used = set()
        
        for c in key + 'ABCDEFGHIKLMNOPQRSTUVWXYZ':
            if c not in used and c.isalpha():
                matrix.append(c)
                used.add(c)
        
        # Create position lookup
        pos = {matrix[i]: (i // 5, i % 5) for i in range(25)}
        
        # Clean ciphertext
        ciphertext = ''.join(c.upper() for c in ciphertext if c.isalpha()).replace('J', 'I')
        
        # Decrypt pairs
        plaintext = ''
        for i in range(0, len(ciphertext) - 1, 2):
            a, b = ciphertext[i], ciphertext[i + 1]
            if a not in pos or b not in pos:
                continue
            
            r1, c1 = pos[a]
            r2, c2 = pos[b]
            
            if r1 == r2:  # Same row
                plaintext += matrix[r1 * 5 + (c1 - 1) % 5]
                plaintext += matrix[r2 * 5 + (c2 - 1) % 5]
            elif c1 == c2:  # Same column
                plaintext += matrix[((r1 - 1) % 5) * 5 + c1]
                plaintext += matrix[((r2 - 1) % 5) * 5 + c2]
            else:  # Rectangle
                plaintext += matrix[r1 * 5 + c2]
                plaintext += matrix[r2 * 5 + c1]
        
        return plaintext
    
    def _try_columnar_transposition(self, data: str, result: ChallengeResult) -> str:
        """Try columnar transposition cipher"""
        result.add_log("Trying columnar transposition...")
        
        clean = ''.join(c for c in data if c.isalpha())
        
        # Try different column counts
        for cols in range(2, min(10, len(clean) // 2)):
            if len(clean) % cols != 0:
                continue
            
            rows = len(clean) // cols
            
            # Try reading column by column
            decoded = ''
            for r in range(rows):
                for c in range(cols):
                    idx = c * rows + r
                    if idx < len(clean):
                        decoded += clean[idx]
            
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log(f"Found flag with columnar transposition ({cols} cols)")
                return flag
        
        return None
    
    def _try_beaufort(self, data: str, result: ChallengeResult) -> str:
        """Try Beaufort cipher"""
        result.add_log("Trying Beaufort cipher...")
        
        common_keys = ['flag', 'key', 'ctf', 'secret', 'beaufort']
        
        for key in common_keys:
            decoded = self._beaufort_decrypt(data, key)
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log(f"Found flag with Beaufort key: {key}")
                return flag
        return None
    
    def _beaufort_decrypt(self, ciphertext: str, key: str) -> str:
        """Decrypt Beaufort cipher (same as encrypt)"""
        result = []
        key = key.lower()
        key_idx = 0
        
        for char in ciphertext:
            if char.isalpha():
                k = ord(key[key_idx % len(key)]) - ord('a')
                if char.isupper():
                    p = (k - (ord(char) - ord('A'))) % 26
                    result.append(chr(p + ord('A')))
                else:
                    p = (k - (ord(char) - ord('a'))) % 26
                    result.append(chr(p + ord('a')))
                key_idx += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    def _try_autokey(self, data: str, result: ChallengeResult) -> str:
        """Try Autokey cipher"""
        result.add_log("Trying Autokey cipher...")
        
        common_keys = ['flag', 'key', 'ctf', 'secret', 'auto']
        
        for key in common_keys:
            decoded = self._autokey_decrypt(data, key)
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log(f"Found flag with Autokey key: {key}")
                return flag
        return None
    
    def _autokey_decrypt(self, ciphertext: str, key: str) -> str:
        """Decrypt Autokey cipher"""
        result = []
        key = key.lower()
        full_key = list(key)
        key_idx = 0
        
        for char in ciphertext:
            if char.isalpha():
                k = ord(full_key[key_idx]) - ord('a')
                if char.isupper():
                    p = (ord(char) - ord('A') - k) % 26
                    result.append(chr(p + ord('A')))
                    full_key.append(chr(p + ord('a')))
                else:
                    p = (ord(char) - ord('a') - k) % 26
                    result.append(chr(p + ord('a')))
                    full_key.append(chr(p + ord('a')))
                key_idx += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    def _try_rsa_attacks(self, data: str, result: ChallengeResult) -> str:
        """Try comprehensive RSA attacks"""
        result.add_log("Checking for RSA parameters...")
        
        # Extract RSA parameters
        n_match = re.search(r'n\s*[=:]\s*(\d+)', data)
        e_match = re.search(r'e\s*[=:]\s*(\d+)', data)
        c_match = re.search(r'c\s*[=:]\s*(\d+)', data)
        p_match = re.search(r'p\s*[=:]\s*(\d+)', data)
        q_match = re.search(r'q\s*[=:]\s*(\d+)', data)
        d_match = re.search(r'd\s*[=:]\s*(\d+)', data)
        
        if not (n_match or (p_match and q_match)):
            return None
        
        n = int(n_match.group(1)) if n_match else None
        e = int(e_match.group(1)) if e_match else 65537
        c = int(c_match.group(1)) if c_match else None
        p = int(p_match.group(1)) if p_match else None
        q = int(q_match.group(1)) if q_match else None
        d = int(d_match.group(1)) if d_match else None
        
        if p and q and not n:
            n = p * q
        
        result.add_log(f"RSA params: n={n}, e={e}, c={c}")
        
        # If we have p and q, decrypt directly
        if p and q and c:
            phi = (p - 1) * (q - 1)
            d = self._mod_inverse(e, phi)
            if d:
                m = pow(c, d, n)
                plaintext = self._int_to_bytes(m).decode('utf-8', errors='ignore')
                flag = self.extract_flag(plaintext)
                if flag:
                    result.add_log("Decrypted with known p, q")
                    return flag
        
        # If we have d, decrypt directly
        if d and c and n:
            m = pow(c, d, n)
            plaintext = self._int_to_bytes(m).decode('utf-8', errors='ignore')
            flag = self.extract_flag(plaintext)
            if flag:
                result.add_log("Decrypted with known d")
                return flag
        
        if not c or not n:
            return None
        
        # Small e attack (e=3 without padding)
        if e == 3:
            result.add_log("Trying small e attack (e=3)...")
            m = self._integer_nth_root(c, 3)
            if m ** 3 == c:
                plaintext = self._int_to_bytes(m).decode('utf-8', errors='ignore')
                flag = self.extract_flag(plaintext)
                if flag:
                    result.add_log("Small e attack successful")
                    return flag
            
            # Try with small multiples of n
            for k in range(1, 100):
                m = self._integer_nth_root(c + k * n, 3)
                if m ** 3 == c + k * n:
                    plaintext = self._int_to_bytes(m).decode('utf-8', errors='ignore')
                    flag = self.extract_flag(plaintext)
                    if flag:
                        return flag
        
        # Fermat factorization (close primes)
        result.add_log("Trying Fermat factorization...")
        p, q = self._fermat_factor(n, max_iterations=50000)
        if p and q:
            result.add_log(f"Factored: p={p}, q={q}")
            phi = (p - 1) * (q - 1)
            d = self._mod_inverse(e, phi)
            if d:
                m = pow(c, d, n)
                plaintext = self._int_to_bytes(m).decode('utf-8', errors='ignore')
                flag = self.extract_flag(plaintext)
                if flag:
                    return flag
        
        # Small n - try factordb or trial division
        if n < 10**30:
            result.add_log("Trying trial division for small n...")
            p = self._trial_division(n)
            if p and p != n:
                q = n // p
                phi = (p - 1) * (q - 1)
                d = self._mod_inverse(e, phi)
                if d:
                    m = pow(c, d, n)
                    plaintext = self._int_to_bytes(m).decode('utf-8', errors='ignore')
                    flag = self.extract_flag(plaintext)
                    if flag:
                        return flag
        
        return None
    
    def _try_rsa_wiener(self, data: str, result: ChallengeResult) -> str:
        """Try Wiener's attack for small d"""
        result.add_log("Trying Wiener's attack...")
        
        n_match = re.search(r'n\s*[=:]\s*(\d+)', data)
        e_match = re.search(r'e\s*[=:]\s*(\d+)', data)
        c_match = re.search(r'c\s*[=:]\s*(\d+)', data)
        
        if not (n_match and e_match and c_match):
            return None
        
        n = int(n_match.group(1))
        e = int(e_match.group(1))
        c = int(c_match.group(1))
        
        # Wiener's attack works when d < n^0.25 / 3
        # Use continued fractions
        convergents = self._continued_fraction_convergents(e, n)
        
        for k, d in convergents:
            if k == 0:
                continue
            
            # Check if d is valid
            phi = (e * d - 1) // k
            
            # phi = (p-1)(q-1) = n - p - q + 1
            # So p + q = n - phi + 1
            s = n - phi + 1
            
            # p and q are roots of x^2 - sx + n = 0
            discriminant = s * s - 4 * n
            if discriminant < 0:
                continue
            
            sqrt_disc = math.isqrt(discriminant)
            if sqrt_disc * sqrt_disc != discriminant:
                continue
            
            p = (s + sqrt_disc) // 2
            q = (s - sqrt_disc) // 2
            
            if p * q == n:
                result.add_log(f"Wiener's attack successful: d={d}")
                m = pow(c, d, n)
                plaintext = self._int_to_bytes(m).decode('utf-8', errors='ignore')
                flag = self.extract_flag(plaintext)
                if flag:
                    return flag
        
        return None
    
    def _continued_fraction_convergents(self, e: int, n: int) -> List[Tuple[int, int]]:
        """Generate convergents of e/n continued fraction"""
        convergents = []
        
        # Generate continued fraction expansion
        cf = []
        a, b = e, n
        while b:
            cf.append(a // b)
            a, b = b, a % b
            if len(cf) > 100:
                break
        
        # Generate convergents
        p_prev, p_curr = 0, 1
        q_prev, q_curr = 1, 0
        
        for a in cf:
            p_next = a * p_curr + p_prev
            q_next = a * q_curr + q_prev
            convergents.append((p_next, q_next))
            p_prev, p_curr = p_curr, p_next
            q_prev, q_curr = q_curr, q_next
        
        return convergents
    
    def _try_rsa_common_modulus(self, data: str, result: ChallengeResult) -> str:
        """Try common modulus attack"""
        result.add_log("Checking for common modulus attack...")
        
        # Look for two ciphertexts with same n but different e
        n_matches = re.findall(r'n\s*[=:]\s*(\d+)', data)
        e_matches = re.findall(r'e\s*[=:]\s*(\d+)', data)
        c_matches = re.findall(r'c\s*[=:]\s*(\d+)', data)
        
        if len(n_matches) >= 2 and len(e_matches) >= 2 and len(c_matches) >= 2:
            n1, n2 = int(n_matches[0]), int(n_matches[1])
            e1, e2 = int(e_matches[0]), int(e_matches[1])
            c1, c2 = int(c_matches[0]), int(c_matches[1])
            
            if n1 == n2 and e1 != e2:
                result.add_log("Common modulus detected!")
                
                # Extended GCD
                gcd, s, t = self._extended_gcd(e1, e2)
                
                if gcd == 1:
                    # m = c1^s * c2^t mod n
                    if s < 0:
                        c1 = self._mod_inverse(c1, n1)
                        s = -s
                    if t < 0:
                        c2 = self._mod_inverse(c2, n1)
                        t = -t
                    
                    m = (pow(c1, s, n1) * pow(c2, t, n1)) % n1
                    plaintext = self._int_to_bytes(m).decode('utf-8', errors='ignore')
                    flag = self.extract_flag(plaintext)
                    if flag:
                        result.add_log("Common modulus attack successful")
                        return flag
        
        return None
    
    def _extended_gcd(self, a: int, b: int) -> Tuple[int, int, int]:
        """Extended Euclidean algorithm"""
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = self._extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    def _trial_division(self, n: int, limit: int = 100000) -> int:
        """Trial division factorization"""
        if n % 2 == 0:
            return 2
        
        for i in range(3, min(limit, math.isqrt(n) + 1), 2):
            if n % i == 0:
                return i
        
        return None
    
    def _integer_nth_root(self, n: int, k: int) -> int:
        """Calculate integer k-th root of n"""
        if n < 0:
            return None
        if n == 0:
            return 0
        
        x = n
        while True:
            x1 = ((k - 1) * x + n // (x ** (k - 1))) // k
            if x1 >= x:
                return x
            x = x1
    
    def _try_ecb_detection(self, data: str, result: ChallengeResult) -> str:
        """Detect ECB mode encryption"""
        result.add_log("Checking for ECB mode...")
        
        # Look for hex or base64 encoded data
        try:
            if all(c in string.hexdigits for c in data.replace(' ', '').replace('\n', '')):
                cipher_bytes = bytes.fromhex(data.replace(' ', '').replace('\n', ''))
            else:
                cipher_bytes = base64.b64decode(data)
            
            # Check for repeated 16-byte blocks (AES block size)
            blocks = [cipher_bytes[i:i+16] for i in range(0, len(cipher_bytes), 16)]
            if len(blocks) != len(set(blocks)):
                result.add_log("ECB mode detected - repeated blocks found!")
        except:
            pass
        
        return None
    
    def _try_padding_oracle_detect(self, data: str, result: ChallengeResult) -> str:
        """Detect potential padding oracle vulnerability"""
        result.add_log("Checking for padding oracle indicators...")
        # Detection only - actual exploitation requires network interaction
        return None
    
    def _fermat_factor(self, n: int, max_iterations: int = 10000) -> Tuple[int, int]:
        a = math.isqrt(n)
        if a * a == n:
            return a, a
        for _ in range(max_iterations):
            a += 1
            b2 = a * a - n
            b = math.isqrt(b2)
            if b * b == b2:
                return a + b, a - b
        return None, None
    
    def _mod_inverse(self, a: int, m: int) -> int:
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        gcd, x, _ = extended_gcd(a % m, m)
        if gcd != 1:
            return None
        return (x % m + m) % m
    
    def _int_to_bytes(self, n: int) -> bytes:
        return n.to_bytes((n.bit_length() + 7) // 8, 'big')

    def _try_morse_code(self, data: str, result: ChallengeResult) -> str:
        """Try Morse code decoding with multiple formats"""
        result.add_log("Trying Morse code...")
        morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
            '...--': '3', '....-': '4', '.....': '5', '-....': '6',
            '--...': '7', '---..': '8', '----.': '9',
            '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'",
            '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')',
            '.-...': '&', '---...': ':', '-.-.-.': ';', '-...-': '=',
            '.-.-.': '+', '-....-': '-', '..--.-': '_', '.-..-.': '"',
            '...-..-': '$', '.--.-.': '@', '-.--.-': '{', '-.--.-': '}',
        }
        
        # Try different separators
        for word_sep in ['/', '  ', ' / ', '   ', '|', '\n']:
            for char_sep in [' ', '|', '/']:
                try:
                    words = data.split(word_sep)
                    decoded = ''
                    for word in words:
                        chars = word.split(char_sep)
                        for char in chars:
                            char = char.strip()
                            if char in morse_dict:
                                decoded += morse_dict[char]
                        decoded += ' '
                    
                    decoded = decoded.strip()
                    if decoded:
                        flag = self.extract_flag(decoded)
                        if flag:
                            result.add_log("Found flag in Morse code")
                            return flag
                except:
                    pass
        
        # Try binary morse (0/1 instead of ./-)
        try:
            binary_morse = data.replace('0', '.').replace('1', '-')
            for word_sep in ['  ', '   ', '/']:
                for char_sep in [' ']:
                    words = binary_morse.split(word_sep)
                    decoded = ''
                    for word in words:
                        chars = word.split(char_sep)
                        for char in chars:
                            char = char.strip()
                            if char in morse_dict:
                                decoded += morse_dict[char]
                        decoded += ' '
                    
                    flag = self.extract_flag(decoded.strip())
                    if flag:
                        result.add_log("Found flag in binary Morse")
                        return flag
        except:
            pass
        
        return None
    
    def _try_bacon_cipher(self, data: str, result: ChallengeResult) -> str:
        """Try Bacon cipher with multiple interpretations"""
        result.add_log("Trying Bacon cipher...")
        bacon_dict = {
            'AAAAA': 'A', 'AAAAB': 'B', 'AAABA': 'C', 'AAABB': 'D',
            'AABAA': 'E', 'AABAB': 'F', 'AABBA': 'G', 'AABBB': 'H',
            'ABAAA': 'I', 'ABAAB': 'J', 'ABABA': 'K', 'ABABB': 'L',
            'ABBAA': 'M', 'ABBAB': 'N', 'ABBBA': 'O', 'ABBBB': 'P',
            'BAAAA': 'Q', 'BAAAB': 'R', 'BAABA': 'S', 'BAABB': 'T',
            'BABAA': 'U', 'BABAB': 'V', 'BABBA': 'W', 'BABBB': 'X',
            'BBAAA': 'Y', 'BBAAB': 'Z',
        }
        
        # Method 1: lowercase = A, uppercase = B
        binary = ''
        for char in data:
            if char.isalpha():
                binary += 'A' if char.islower() else 'B'
        
        decoded = ''
        for i in range(0, len(binary) - 4, 5):
            chunk = binary[i:i+5]
            if chunk in bacon_dict:
                decoded += bacon_dict[chunk]
        
        flag = self.extract_flag(decoded)
        if flag:
            result.add_log("Found flag in Bacon cipher (case-based)")
            return flag
        
        # Method 2: two different characters
        if len(set(data.replace(' ', ''))) == 2:
            chars = list(set(data.replace(' ', '')))
            binary = data.replace(' ', '').replace(chars[0], 'A').replace(chars[1], 'B')
            
            decoded = ''
            for i in range(0, len(binary) - 4, 5):
                chunk = binary[i:i+5]
                if chunk in bacon_dict:
                    decoded += bacon_dict[chunk]
            
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log("Found flag in Bacon cipher (binary)")
                return flag
        
        return None
    
    def _try_a1z26(self, data: str, result: ChallengeResult) -> str:
        """Try A1Z26 cipher (A=1, B=2, etc.)"""
        result.add_log("Trying A1Z26 cipher...")
        
        # Try different separators
        for sep in [' ', '-', ',', '.', '/', '_', ':']:
            try:
                parts = data.split(sep)
                if all(p.isdigit() and 1 <= int(p) <= 26 for p in parts if p):
                    decoded = ''.join(chr(int(p) + ord('A') - 1) for p in parts if p)
                    flag = self.extract_flag(decoded)
                    if flag:
                        result.add_log("Found flag in A1Z26")
                        return flag
            except:
                pass
        
        return None
    
    def _try_tap_code(self, data: str, result: ChallengeResult) -> str:
        """Try tap code (Polybius-based prison code)"""
        result.add_log("Trying tap code...")
        
        # Tap code uses 5x5 grid (K=C)
        grid = 'ABCDEFGHIJLMNOPQRSTUVWXYZ'  # No K
        
        # Look for pairs of numbers
        pairs = re.findall(r'(\d)\s*[,.\s]\s*(\d)', data)
        if pairs:
            decoded = ''
            for row, col in pairs:
                row, col = int(row), int(col)
                if 1 <= row <= 5 and 1 <= col <= 5:
                    idx = (row - 1) * 5 + (col - 1)
                    if idx < len(grid):
                        decoded += grid[idx]
            
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log("Found flag in tap code")
                return flag
        
        return None
    
    def _try_polybius(self, data: str, result: ChallengeResult) -> str:
        """Try Polybius square cipher"""
        result.add_log("Trying Polybius square...")
        
        grid = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'  # I=J
        
        # Look for pairs of digits
        clean = data.replace(' ', '').replace(',', '')
        if all(c.isdigit() for c in clean) and len(clean) % 2 == 0:
            decoded = ''
            for i in range(0, len(clean), 2):
                row, col = int(clean[i]), int(clean[i+1])
                if 1 <= row <= 5 and 1 <= col <= 5:
                    idx = (row - 1) * 5 + (col - 1)
                    if idx < len(grid):
                        decoded += grid[idx]
            
            flag = self.extract_flag(decoded)
            if flag:
                result.add_log("Found flag in Polybius square")
                return flag
        
        return None
    
    def _try_frequency_analysis(self, data: str, result: ChallengeResult) -> str:
        """Perform frequency analysis for substitution ciphers"""
        result.add_log("Performing frequency analysis...")
        
        # Only analyze alphabetic text
        alpha_only = ''.join(c.lower() for c in data if c.isalpha())
        if len(alpha_only) < 50:
            return None
        
        # Calculate frequencies
        freq = Counter(alpha_only)
        total = sum(freq.values())
        
        # Sort by frequency
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        # English frequency order
        english_order = 'etaoinshrdlcumwfgypbvkjxqz'
        
        # Create simple substitution based on frequency
        mapping = {}
        for i, (char, _) in enumerate(sorted_freq):
            if i < len(english_order):
                mapping[char] = english_order[i]
        
        # Apply mapping
        decoded = ''.join(mapping.get(c.lower(), c) if c.isalpha() else c for c in data)
        
        flag = self.extract_flag(decoded)
        if flag:
            result.add_log("Found flag via frequency analysis")
            return flag
        
        return None
    
    def _try_substitution_crack(self, data: str, result: ChallengeResult) -> str:
        """Try to crack simple substitution cipher"""
        result.add_log("Trying substitution cipher crack...")
        # This is a simplified version - full implementation would use
        # dictionary attacks and pattern matching
        return None
    
    def _try_xor_known_plaintext(self, data: str, result: ChallengeResult) -> str:
        """Try XOR with known plaintext attack"""
        result.add_log("Trying XOR known plaintext attack...")
        
        known_plaintexts = [b'flag{', b'FLAG{', b'ctf{', b'CTF{', b'HTB{', b'THM{']
        
        try:
            # Try to decode as hex first
            if all(c in string.hexdigits for c in data.replace(' ', '')):
                cipher_bytes = bytes.fromhex(data.replace(' ', ''))
            else:
                cipher_bytes = data.encode()
            
            for known in known_plaintexts:
                if len(cipher_bytes) >= len(known):
                    # XOR to find potential key
                    key_fragment = bytes([cipher_bytes[i] ^ known[i] for i in range(len(known))])
                    
                    # Try to extend key and decrypt
                    for key_len in range(1, len(key_fragment) + 1):
                        key = key_fragment[:key_len]
                        decrypted = bytes([cipher_bytes[i] ^ key[i % len(key)] for i in range(len(cipher_bytes))])
                        decoded = decrypted.decode('utf-8', errors='ignore')
                        
                        flag = self.extract_flag(decoded)
                        if flag:
                            result.add_log(f"XOR known plaintext attack successful")
                            return flag
        except:
            pass
        
        return None
    
    def _try_affine(self, data: str, result: ChallengeResult) -> str:
        """Try Affine cipher"""
        result.add_log("Trying Affine cipher...")
        valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
        for a in valid_a:
            a_inv = self._mod_inverse(a, 26)
            if a_inv is None:
                continue
            for b in range(26):
                decoded = ''
                for char in data:
                    if char.isalpha():
                        if char.isupper():
                            decoded += chr((a_inv * (ord(char) - ord('A') - b)) % 26 + ord('A'))
                        else:
                            decoded += chr((a_inv * (ord(char) - ord('a') - b)) % 26 + ord('a'))
                    else:
                        decoded += char
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log(f"Found flag with Affine (a={a}, b={b})")
                    return flag
        return None

    # ==================== JOHN THE RIPPER STYLE HASH CRACKING ====================
    
    def _try_john_crack(self, data: str, result: ChallengeResult) -> str:
        """John the Ripper style comprehensive hash cracking"""
        result.add_log("Running John the Ripper style hash cracking...")
        
        # Try to identify hash format
        hash_format = self._identify_john_hash_format(data)
        if hash_format:
            result.add_log(f"Identified hash format: {hash_format}")
        
        # Try different cracking methods based on format
        crackers = [
            self._crack_raw_hash,
            self._crack_unix_crypt,
            self._crack_shadow_file,
            self._crack_htpasswd,
            self._crack_ldap_hash,
            self._crack_wordpress_hash,
            self._crack_salted_hash,
            self._crack_ntlm_hash,
            self._crack_mysql_hash,
        ]
        
        for cracker in crackers:
            try:
                cracked = cracker(data, result)
                if cracked:
                    return cracked
            except Exception as e:
                result.add_log(f"Cracker error: {e}")
        
        return None
    
    def _identify_john_hash_format(self, data: str) -> str:
        """Identify hash format like John the Ripper"""
        data = data.strip()
        
        for pattern, format_name in self.JOHN_HASH_FORMATS.items():
            if re.match(pattern, data, re.IGNORECASE):
                return format_name
        
        return None

    def _crack_raw_hash(self, data: str, result: ChallengeResult) -> str:
        """Crack raw MD5/SHA1/SHA256/SHA512 hashes"""
        clean_data = data.strip().lower()
        
        # Check if it's a valid hex hash
        if not all(c in string.hexdigits for c in clean_data):
            return None
        
        hash_len = len(clean_data)
        if hash_len not in self.HASH_PATTERNS:
            return None
        
        result.add_log(f"Cracking {hash_len}-char hash with extended wordlist...")
        
        # Build comprehensive wordlist
        wordlist = list(set(self.JOHN_WORDLIST + self.COMMON_PASSWORDS))
        
        # Add number variations
        wordlist.extend([str(i) for i in range(10000)])
        
        # Add common CTF flag formats
        for word in ['flag', 'ctf', 'secret', 'key', 'password']:
            wordlist.extend([
                f"{word}123", f"{word}!", f"{word}1", f"{word}2024",
                f"the{word}", f"my{word}", f"{word}here",
            ])
        
        # Try each password with each algorithm
        algos = {
            32: ['md5'],
            40: ['sha1'],
            64: ['sha256'],
            128: ['sha512'],
        }
        
        for algo in algos.get(hash_len, []):
            for pwd in wordlist:
                try:
                    h = hashlib.new(algo)
                    h.update(pwd.encode())
                    if h.hexdigest() == clean_data:
                        result.add_log(f"Cracked {algo}: {pwd}")
                        flag = self.extract_flag(pwd)
                        return flag if flag else pwd
                except:
                    pass
        
        return None

    def _crack_unix_crypt(self, data: str, result: ChallengeResult) -> str:
        """Crack Unix crypt hashes ($1$, $5$, $6$, DES)"""
        if not HAS_CRYPT:
            result.add_log("Unix crypt not available on this platform")
            return None
        
        data = data.strip()
        
        # Check for Unix crypt format
        if not (data.startswith('$') or len(data) == 13):
            return None
        
        result.add_log("Attempting Unix crypt hash crack...")
        
        wordlist = list(set(self.JOHN_WORDLIST + self.COMMON_PASSWORDS))
        
        for pwd in wordlist:
            try:
                # Use crypt module for proper Unix hash verification
                if crypt.crypt(pwd, data) == data:
                    result.add_log(f"Unix crypt cracked: {pwd}")
                    flag = self.extract_flag(pwd)
                    return flag if flag else pwd
            except Exception:
                pass
        
        return None
    
    def _crack_shadow_file(self, data: str, result: ChallengeResult) -> str:
        """Parse and crack /etc/shadow format entries"""
        lines = data.strip().split('\n')
        
        for line in lines:
            # Shadow file format: username:hash:lastchange:min:max:warn:inactive:expire:reserved
            parts = line.split(':')
            if len(parts) >= 2:
                username = parts[0]
                hash_field = parts[1]
                
                # Skip locked/disabled accounts
                if hash_field in ['*', '!', '!!', 'x', '']:
                    continue
                
                result.add_log(f"Cracking shadow entry for user: {username}")
                
                # Try to crack the hash
                cracked = self._crack_unix_crypt(hash_field, result)
                if cracked:
                    result.add_log(f"Shadow cracked - {username}:{cracked}")
                    return f"{username}:{cracked}"
        
        return None

    def _crack_htpasswd(self, data: str, result: ChallengeResult) -> str:
        """Crack Apache htpasswd format"""
        lines = data.strip().split('\n')
        
        for line in lines:
            if ':' not in line:
                continue
            
            parts = line.split(':', 1)
            if len(parts) != 2:
                continue
            
            username, hash_field = parts
            result.add_log(f"Cracking htpasswd for user: {username}")
            
            wordlist = list(set(self.JOHN_WORDLIST + self.COMMON_PASSWORDS))
            
            # Check hash type
            if hash_field.startswith('$apr1$'):
                # Apache MD5 - requires crypt module
                if HAS_CRYPT:
                    for pwd in wordlist:
                        try:
                            if crypt.crypt(pwd, hash_field) == hash_field:
                                result.add_log(f"htpasswd cracked - {username}:{pwd}")
                                return f"{username}:{pwd}"
                        except:
                            pass
            elif hash_field.startswith('{SHA}'):
                # SHA1 base64
                expected = hash_field[5:]
                for pwd in wordlist:
                    try:
                        computed = base64.b64encode(hashlib.sha1(pwd.encode()).digest()).decode()
                        if computed == expected:
                            result.add_log(f"htpasswd SHA cracked - {username}:{pwd}")
                            return f"{username}:{pwd}"
                    except:
                        pass
            else:
                # Try as Unix crypt
                cracked = self._crack_unix_crypt(hash_field, result)
                if cracked:
                    return f"{username}:{cracked}"
        
        return None
    
    def _crack_ldap_hash(self, data: str, result: ChallengeResult) -> str:
        """Crack LDAP password hashes"""
        data = data.strip()
        
        wordlist = list(set(self.JOHN_WORDLIST + self.COMMON_PASSWORDS))
        
        if data.startswith('{SHA}'):
            # LDAP SHA1
            expected = base64.b64decode(data[5:])
            for pwd in wordlist:
                try:
                    if hashlib.sha1(pwd.encode()).digest() == expected:
                        result.add_log(f"LDAP SHA cracked: {pwd}")
                        return pwd
                except:
                    pass
        
        elif data.startswith('{SSHA}'):
            # LDAP Salted SHA1
            decoded = base64.b64decode(data[6:])
            digest = decoded[:20]
            salt = decoded[20:]
            for pwd in wordlist:
                try:
                    if hashlib.sha1(pwd.encode() + salt).digest() == digest:
                        result.add_log(f"LDAP SSHA cracked: {pwd}")
                        return pwd
                except:
                    pass
        
        elif data.startswith('{MD5}'):
            # LDAP MD5
            expected = base64.b64decode(data[5:])
            for pwd in wordlist:
                try:
                    if hashlib.md5(pwd.encode()).digest() == expected:
                        result.add_log(f"LDAP MD5 cracked: {pwd}")
                        return pwd
                except:
                    pass
        
        return None

    def _crack_wordpress_hash(self, data: str, result: ChallengeResult) -> str:
        """Crack WordPress/PHPass hashes"""
        data = data.strip()
        
        if not (data.startswith('$P$') or data.startswith('$H$')):
            return None
        
        result.add_log("Cracking WordPress/PHPass hash...")
        
        # PHPass uses a custom iterated MD5
        itoa64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        
        wordlist = list(set(self.JOHN_WORDLIST + self.COMMON_PASSWORDS))
        
        for pwd in wordlist:
            try:
                # Extract iteration count and salt
                count_log2 = itoa64.index(data[3])
                count = 1 << count_log2
                salt = data[4:12]
                
                # Compute hash
                hash_val = hashlib.md5((salt + pwd).encode()).digest()
                for _ in range(count):
                    hash_val = hashlib.md5(hash_val + pwd.encode()).digest()
                
                # Encode result
                encoded = self._phpass_encode64(hash_val, 16)
                computed = data[:12] + encoded
                
                if computed == data:
                    result.add_log(f"WordPress hash cracked: {pwd}")
                    return pwd
            except:
                pass
        
        return None
    
    def _phpass_encode64(self, input_bytes: bytes, count: int) -> str:
        """PHPass base64 encoding"""
        itoa64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        output = ''
        i = 0
        while i < count:
            value = input_bytes[i]
            i += 1
            output += itoa64[value & 0x3f]
            if i < count:
                value |= input_bytes[i] << 8
            output += itoa64[(value >> 6) & 0x3f]
            if i >= count:
                break
            i += 1
            if i < count:
                value |= input_bytes[i] << 16
            output += itoa64[(value >> 12) & 0x3f]
            if i >= count:
                break
            i += 1
            output += itoa64[(value >> 18) & 0x3f]
        return output

    def _crack_salted_hash(self, data: str, result: ChallengeResult) -> str:
        """Crack salted hashes (hash:salt format)"""
        if ':' not in data:
            return None
        
        parts = data.strip().split(':')
        if len(parts) != 2:
            return None
        
        hash_val, salt = parts
        hash_val = hash_val.lower()
        
        # Determine hash type by length
        hash_len = len(hash_val)
        if hash_len not in [32, 40, 64, 128]:
            return None
        
        result.add_log(f"Cracking salted hash (len={hash_len})...")
        
        algos = {32: 'md5', 40: 'sha1', 64: 'sha256', 128: 'sha512'}
        algo = algos.get(hash_len)
        if not algo:
            return None
        
        wordlist = list(set(self.JOHN_WORDLIST + self.COMMON_PASSWORDS))
        
        # Try different salt positions
        for pwd in wordlist:
            try:
                # salt + password
                h = hashlib.new(algo)
                h.update((salt + pwd).encode())
                if h.hexdigest() == hash_val:
                    result.add_log(f"Salted hash cracked (salt+pwd): {pwd}")
                    return pwd
                
                # password + salt
                h = hashlib.new(algo)
                h.update((pwd + salt).encode())
                if h.hexdigest() == hash_val:
                    result.add_log(f"Salted hash cracked (pwd+salt): {pwd}")
                    return pwd
                
                # salt as bytes
                try:
                    salt_bytes = bytes.fromhex(salt)
                    h = hashlib.new(algo)
                    h.update(salt_bytes + pwd.encode())
                    if h.hexdigest() == hash_val:
                        result.add_log(f"Salted hash cracked (hex salt): {pwd}")
                        return pwd
                except:
                    pass
            except:
                pass
        
        return None

    def _crack_ntlm_hash(self, data: str, result: ChallengeResult) -> str:
        """Crack NTLM (Windows) hashes"""
        data = data.strip().lower()
        
        # NTLM is 32 hex chars (MD4 of UTF-16LE password)
        if len(data) != 32 or not all(c in string.hexdigits for c in data):
            return None
        
        result.add_log("Attempting NTLM hash crack...")
        
        wordlist = list(set(self.JOHN_WORDLIST + self.COMMON_PASSWORDS))
        
        for pwd in wordlist:
            try:
                # NTLM = MD4(UTF-16LE(password))
                import hashlib
                # Python's hashlib doesn't have MD4, try with passlib or manual
                try:
                    from passlib.hash import nthash
                    if nthash.hash(pwd).lower() == data:
                        result.add_log(f"NTLM cracked: {pwd}")
                        return pwd
                except ImportError:
                    # Manual NTLM calculation using hashlib md4 if available
                    try:
                        h = hashlib.new('md4')
                        h.update(pwd.encode('utf-16-le'))
                        if h.hexdigest() == data:
                            result.add_log(f"NTLM cracked: {pwd}")
                            return pwd
                    except:
                        pass
            except:
                pass
        
        return None
    
    def _crack_mysql_hash(self, data: str, result: ChallengeResult) -> str:
        """Crack MySQL password hashes"""
        data = data.strip()
        
        wordlist = list(set(self.JOHN_WORDLIST + self.COMMON_PASSWORDS))
        
        # MySQL 4.1+ (SHA1(SHA1(password)))
        if data.startswith('*') and len(data) == 41:
            expected = data[1:].lower()
            for pwd in wordlist:
                try:
                    h1 = hashlib.sha1(pwd.encode()).digest()
                    h2 = hashlib.sha1(h1).hexdigest()
                    if h2 == expected:
                        result.add_log(f"MySQL 4.1+ hash cracked: {pwd}")
                        return pwd
                except:
                    pass
        
        # Old MySQL (pre-4.1)
        elif len(data) == 16 and all(c in string.hexdigits for c in data):
            result.add_log("Attempting old MySQL hash crack...")
            # Old MySQL hash algorithm is complex, skip for now
            pass
        
        return None

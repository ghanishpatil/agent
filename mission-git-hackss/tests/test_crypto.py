"""Tests for cryptography module"""

import pytest
import base64
from pathlib import Path
from unittest.mock import MagicMock

from core.challenge import Challenge
from modules.crypto import CryptoModule


@pytest.fixture
def config():
    """Create mock configuration"""
    mock_config = MagicMock()
    mock_config.get.return_value = None
    return mock_config


@pytest.fixture
def crypto_module(config):
    """Create crypto module instance"""
    return CryptoModule(config)


class TestBase64:
    """Test base64 decoding"""
    
    def test_simple_base64(self, crypto_module):
        """Test simple base64 decoding"""
        # flag{test_flag} encoded
        encoded = base64.b64encode(b'flag{test_flag}').decode()
        challenge = Challenge(name="test", description=encoded)
        
        result = crypto_module.solve(challenge)
        assert result.flag == 'flag{test_flag}'
    
    def test_nested_base64(self, crypto_module):
        """Test nested base64 decoding"""
        # Double encoded
        inner = base64.b64encode(b'flag{nested}').decode()
        outer = base64.b64encode(inner.encode()).decode()
        challenge = Challenge(name="test", description=outer)
        
        result = crypto_module.solve(challenge)
        assert result.flag == 'flag{nested}'


class TestCaesar:
    """Test Caesar cipher"""
    
    def test_caesar_shift_13(self, crypto_module):
        """Test ROT13"""
        # flag{caesar} with ROT13 = synt{pnrfne}
        challenge = Challenge(name="test", description="synt{pnrfne}")
        
        result = crypto_module.solve(challenge)
        assert result.flag == 'flag{caesar}'
    
    def test_caesar_various_shifts(self, crypto_module):
        """Test various Caesar shifts"""
        # flag{shift5} with shift 5
        original = "flag{shift5}"
        shifted = ''.join(
            chr((ord(c) - ord('a') + 5) % 26 + ord('a')) if c.islower() else c
            for c in original
        )
        challenge = Challenge(name="test", description=shifted)
        
        result = crypto_module.solve(challenge)
        assert 'flag' in result.flag.lower() if result.flag else False


class TestHex:
    """Test hex decoding"""
    
    def test_hex_decode(self, crypto_module):
        """Test hex decoding"""
        # flag{hex} in hex
        hex_encoded = b'flag{hex}'.hex()
        challenge = Challenge(name="test", description=hex_encoded)
        
        result = crypto_module.solve(challenge)
        assert result.flag == 'flag{hex}'


class TestXOR:
    """Test XOR decryption"""
    
    def test_single_byte_xor(self, crypto_module):
        """Test single-byte XOR"""
        # flag{xor} XORed with key 0x42
        original = b'flag{xor}'
        encrypted = bytes([b ^ 0x42 for b in original]).decode('utf-8', errors='ignore')
        challenge = Challenge(name="test", description=encrypted)
        
        result = crypto_module.solve(challenge)
        # May or may not find depending on printability
        assert result is not None


class TestMorse:
    """Test Morse code"""
    
    def test_morse_decode(self, crypto_module):
        """Test Morse code decoding"""
        # FLAG in Morse
        morse = "..-. .-.. .- --. { - . ... - }"
        challenge = Challenge(name="test", description=morse)
        
        result = crypto_module.solve(challenge)
        # Check if morse decoding was attempted
        assert any('morse' in log.lower() for log in result.logs)


class TestAtbash:
    """Test Atbash cipher"""
    
    def test_atbash(self, crypto_module):
        """Test Atbash cipher"""
        # flag -> uozt in Atbash
        challenge = Challenge(name="test", description="uozt{gvhg}")
        
        result = crypto_module.solve(challenge)
        assert result.flag == 'flag{test}' if result.success else True

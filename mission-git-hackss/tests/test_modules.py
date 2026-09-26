"""Tests for solver modules"""

import pytest
from core.config import Config
from core.challenge import Challenge
from modules.crypto import CryptoModule
from modules.web import WebModule


@pytest.fixture
def config():
    return Config('config/config.example.yaml')


def test_crypto_base64(config):
    """Test base64 decoding"""
    module = CryptoModule(config)
    challenge = Challenge(
        name="test",
        description="ZmxhZ3t0ZXN0X2ZsYWd9"  # base64 encoded flag{test_flag}
    )
    
    result = module.solve(challenge)
    assert result.flag is not None


def test_crypto_caesar(config):
    """Test Caesar cipher"""
    module = CryptoModule(config)
    challenge = Challenge(
        name="test",
        description="synt{grfg_synt}"  # ROT13 of flag{test_flag}
    )
    
    result = module.solve(challenge)
    assert result.flag is not None


def test_web_module_init(config):
    """Test web module initialization"""
    module = WebModule(config)
    assert module.session is not None

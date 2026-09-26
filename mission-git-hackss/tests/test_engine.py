"""Tests for exploit engine"""

import pytest
from pathlib import Path
from core.engine import ExploitEngine
from core.config import Config
from core.challenge import Challenge


@pytest.fixture
def config():
    """Create test configuration"""
    return Config('config/config.example.yaml')


@pytest.fixture
def engine(config):
    """Create test engine"""
    return ExploitEngine(config, threads=2, timeout=10)


def test_engine_initialization(engine):
    """Test engine initializes correctly"""
    assert engine is not None
    assert engine.threads == 2
    assert engine.timeout == 10


def test_parse_challenge(engine):
    """Test challenge parsing"""
    # This would need actual test files
    pass


def test_solve_challenge_timeout(engine):
    """Test challenge solving with timeout"""
    # This would need actual test challenges
    pass


def test_module_registry(engine):
    """Test module registry"""
    modules = engine.module_registry.list_modules()
    assert 'web' in modules or 'crypto' in modules

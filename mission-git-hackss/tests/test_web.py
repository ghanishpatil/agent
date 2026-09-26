"""Tests for web exploitation module"""

import pytest
from unittest.mock import MagicMock, patch
import responses

from core.challenge import Challenge
from modules.web import WebModule


@pytest.fixture
def config():
    """Create mock configuration"""
    mock_config = MagicMock()
    mock_config.get.side_effect = lambda key, default=None: {
        'modules.web.user_agent': 'TestAgent',
        'modules.web.verify_ssl': False,
        'modules.web.timeout': 10,
        'modules.web.max_redirects': 5,
    }.get(key, default)
    return mock_config


@pytest.fixture
def web_module(config):
    """Create web module instance"""
    return WebModule(config)


class TestSourceCodeAnalysis:
    """Test source code analysis"""
    
    @responses.activate
    def test_flag_in_source(self, web_module):
        """Test finding flag in HTML source"""
        responses.add(
            responses.GET,
            'http://test.com/',
            body='<html><!-- flag{in_source} --></html>',
            status=200
        )
        
        challenge = Challenge(name="test", url="http://test.com/")
        result = web_module.solve(challenge)
        
        assert result.success
        assert result.flag == 'flag{in_source}'
    
    @responses.activate
    def test_flag_in_header(self, web_module):
        """Test finding flag in HTTP header"""
        responses.add(
            responses.GET,
            'http://test.com/',
            body='<html></html>',
            headers={'X-Flag': 'flag{in_header}'},
            status=200
        )
        
        challenge = Challenge(name="test", url="http://test.com/")
        result = web_module.solve(challenge)
        
        assert result.success
        assert result.flag == 'flag{in_header}'


class TestSQLInjection:
    """Test SQL injection detection"""
    
    @responses.activate
    def test_sqli_detection(self, web_module):
        """Test SQL injection detection"""
        # Normal response
        responses.add(
            responses.GET,
            'http://test.com/?id=1',
            body='<html>User: admin</html>',
            status=200
        )
        
        # SQLi response with flag
        responses.add(
            responses.GET,
            'http://test.com/',
            body='<html>flag{sqli_success}</html>',
            status=200
        )
        
        challenge = Challenge(name="test", url="http://test.com/?id=1")
        result = web_module.solve(challenge)
        
        # Check that SQLi was attempted
        assert any('sql' in log.lower() for log in result.logs)


class TestLFI:
    """Test Local File Inclusion"""
    
    @responses.activate
    def test_lfi_detection(self, web_module):
        """Test LFI detection"""
        responses.add(
            responses.GET,
            'http://test.com/',
            body='<html>flag{lfi_success}</html>',
            status=200
        )
        
        challenge = Challenge(name="test", url="http://test.com/")
        result = web_module.solve(challenge)
        
        # Check that LFI was attempted
        assert any('lfi' in log.lower() for log in result.logs)


class TestCommonPaths:
    """Test common path enumeration"""
    
    @responses.activate
    def test_robots_txt(self, web_module):
        """Test robots.txt check"""
        responses.add(
            responses.GET,
            'http://test.com/',
            body='<html></html>',
            status=200
        )
        responses.add(
            responses.GET,
            'http://test.com/robots.txt',
            body='User-agent: *\nDisallow: /secret/\n# flag{in_robots}',
            status=200
        )
        
        challenge = Challenge(name="test", url="http://test.com/")
        result = web_module.solve(challenge)
        
        assert result.success
        assert result.flag == 'flag{in_robots}'


class TestJWT:
    """Test JWT attacks"""
    
    def test_jwt_detection(self, web_module):
        """Test JWT token detection"""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        
        assert web_module._is_jwt(token)
        assert not web_module._is_jwt("not.a.jwt")
        assert not web_module._is_jwt("invalid")

"""
Unit tests for HeaderRotator.
"""
from crawlengine.headers.rotator import HeaderRotator

def test_header_rotator_structure():
    headers = HeaderRotator.get_headers(referer="https://example.com/test")
    assert "User-Agent" in headers
    assert "Accept-Language" in headers
    assert headers["Referer"] == "https://example.com/test"
    assert "Accept" in headers

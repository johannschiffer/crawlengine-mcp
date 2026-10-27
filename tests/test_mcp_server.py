"""
Unit tests for CrawlEngine MCP Server JSON-RPC protocol compliance.
"""
import pytest
import json
from unittest.mock import patch
from crawlengine.server import CrawlEngineServer

def test_mcp_initialize():
    server = CrawlEngineServer()
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }
    resp = server.handle_request(req)
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "crawlengine-mcp"

def test_mcp_tools_list():
    server = CrawlEngineServer()
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    resp = server.handle_request(req)
    tools = resp["result"]["tools"]
    names = [t["name"] for t in tools]
    assert "scrape_url" in names
    assert "extract_structured_data" in names
    assert "extract_links" in names
    assert "extract_metadata" in names
    assert "get_proxy_status" in names

@patch("crawlengine.server.CrawlEngineServer._fetch_html")
def test_mcp_scrape_url_mock(mock_fetch):
    mock_fetch.return_value = (200, "<html><head><title>Mock</title></head><body><h1>Heading</h1><p>Text</p></body></html>")
    server = CrawlEngineServer()
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "scrape_url",
            "arguments": {"url": "https://example.com"}
        }
    }
    resp = server.handle_request(req)
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["success"] is True
    assert content["title"] == "Mock"
    assert "# Heading" in content["markdown"]

"""
Security, proxy rotation, and Markdown extraction tests for crawlengine-mcp v2.0.1.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

from crawlengine import __version__
from crawlengine.core.proxy_pool import ProxyPool
from crawlengine.extractors.markdown import MarkdownExtractor
from crawlengine.server import CrawlEngineServer


def test_ssrf_guard_blocks_internal_targets():
    server = CrawlEngineServer()
    for bad_url in (
        "http://127.0.0.1:8000/admin",
        "http://169.254.169.254/latest/meta-data/",
        "http://localhost:5000/secret",
        "file:///etc/passwd",
        "http://2130706433/internal",
    ):
        res = server.handle_tool_call("scrape_url", {"url": bad_url})
        assert res["success"] is False


def test_proxy_pool_starts_with_first_configured_proxy():
    pool = ProxyPool(["http://p1:8080", "http://p2:8080", "http://p3:8080"])
    assert pool.get_proxy() == "http://p1:8080"
    assert pool.get_proxy() == "http://p2:8080"
    assert pool.get_proxy() == "http://p3:8080"
    assert pool.get_proxy() == "http://p1:8080"


def test_markdown_resolves_links_and_deduplicates_nested_li_paragraphs():
    html = """
    <main>
      <h1>Guide</h1>
      <p>Visit <a href="/docs/api">API Docs</a> now.</p>
      <ul>
        <li><p>Single bullet text</p></li>
      </ul>
    </main>
    """
    md = MarkdownExtractor.html_to_markdown(html, base_url="https://example.org")
    assert "[API Docs](https://example.org/docs/api)" in md
    assert md.count("Single bullet text") == 1


def test_cli_version_and_jsonrpc_parse_error():
    repo_root = str(Path(__file__).resolve().parents[1])
    env = {**os.environ, "PYTHONPATH": repo_root}

    ver = subprocess.run(
        [sys.executable, "-m", "crawlengine.server", "--version"],
        env=env,
        capture_output=True,
        text=True,
    )
    assert ver.returncode == 0
    assert __version__ in ver.stdout

    proc = subprocess.run(
        [sys.executable, "-m", "crawlengine.server"],
        input="{invalid-json\n",
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    err = json.loads(proc.stdout.strip())
    assert err["error"]["code"] == -32700

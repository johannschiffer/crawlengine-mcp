# crawlengine-mcp (v1.0.0)

[![PyPI version](https://img.shields.io/badge/PyPI-v1.0.0-blue.svg)](https://pypi.org/project/crawlengine-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Support on Ko-fi](https://img.shields.io/badge/Support%20on-Ko--fi-ff5e5b.svg)](https://ko-fi.com/johannschiffer)

<a href="https://glama.ai/mcp/servers/@johannschiffer/crawlengine-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@johannschiffer/crawlengine-mcp/badge" alt="crawlengine-mcp MCP server" />
</a>

[![PyPI](https://img.shields.io/pypi/v/crawlengine-mcp.svg)](https://pypi.org/project/crawlengine-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io)
[![Awesome MCP Servers](https://img.shields.io/badge/Awesome--MCP--Servers-TensorBlock-blue?style=flat-square)](https://github.com/TensorBlock/awesome-mcp-servers)

**Official Indexing:** Verified and listed in [TensorBlock/awesome-mcp-servers](https://github.com/TensorBlock/awesome-mcp-servers) under Browser Automation & Web Scraping. [![Awesome MCP Servers](https://img.shields.io/badge/Awesome--MCP--Servers-TensorBlock-blue?style=flat-square)](https://github.com/TensorBlock/awesome-mcp-servers)

**CrawlEngine MCP** is a resilient Model Context Protocol server that gives AI agents in **Claude Desktop**, **Cursor**, **Windsurf**, and **Antigravity** clean web-reading superpowers without choking context windows on raw HTML or getting instantly blocked by basic anti-bot firewalls.

---

## Run without cloning

```bash
uvx crawlengine-mcp
```

Claude Desktop / Cursor config entry:

```json
{
  "mcpServers": {
    "crawlengine-mcp": {
      "command": "uvx",
      "args": [
        "crawlengine-mcp"
      ]
    }
  }
}
```

[![CI](https://github.com/johannschiffer/crawlengine-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/johannschiffer/crawlengine-mcp/actions/workflows/ci.yml)

## 🕷️ Why CrawlEngine MCP?

Most default web-fetching tools used by AI models suffer from severe drawbacks:
2. **Instant HTTP 403 Blocks:** Default Python `urllib` or `requests` User-Agents trigger anti-bot WAFs immediately.
3. **Broken Relative Links:** Naive scrapers return unnavigable relative paths (`/docs/quickstart`) instead of canonical URLs.

**CrawlEngine** solves this by rotating realistic modern browser fingerprints and transforming messy DOM trees into pristine, semantic Markdown.

---

## Features

- 🧹 **Semantic Markdown Conversion**: Strips scripts, styles, popups, cookie consent overlays, and ads, keeping only the core article or documentation.
- 🎭 **Realistic Browser Fingerprinting**: Automatically rotates `User-Agent`, `Sec-Ch-Ua`, and platform headers across Chrome, Safari, and Firefox.
- 🔗 **Deep Link Discovery**: Extracts all outbound and internal links with anchor text.
- 🏷️ **Metadata Extraction**: Gathers OpenGraph, Twitter Cards, meta descriptions, and canonical URLs.
- 🌐 **Automatic Headless Browser Fallback**: Playwright Chromium support for complex JavaScript SPA hydration (React, Next.js, Vue).
- 🛡️ **Proxy Pool Rotation**: HTTP & SOCKS5 proxy rotation with automatic failure ejection.
- 📊 **Structured Data Extraction**: JSON-LD schema parsing, pricing tables, and product data.
- 🐳 **Production Docker Container**: Multi-stage containerized setup ready for production.
- 🪶 **Zero Complex Dependencies**: Pure Python using `httpx` and `beautifulsoup4`.
---

## 🚀 Quick Setup in 2 Minutes

### 1. Installation

```bash
git clone https://github.com/johannschiffer/crawlengine-mcp.git
cd crawlengine-mcp
pip install -r requirements.txt
```

### 2. Configure Claude Desktop (`claude_desktop_config.json`)

On Linux: `~/.config/Claude/claude_desktop_config.json`  
On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`  
On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crawlengine": {
      "command": "python",
      "args": ["-m", "crawlengine.server"],
      "cwd": "/path/to/crawlengine-mcp"
    }
  }
}
```

### 3. Verify via CLI

```bash
python -m crawlengine.cli scrape https://news.ycombinator.com
```

---

## 🛠️ MCP Tools Exposed to AI Agents

| Tool | Parameters | Description |
|---|---|---|
| `scrape_url` | `url`, `extract_markdown`, `timeout` | Fetches web page and extracts clean, token-efficient Markdown |
| `extract_links` | `url`, `internal_only` | Returns structured array of hyperlinks with anchor texts |
| `extract_metadata` | `url` | Retrieves page title, meta description, and OpenGraph data |

---

## Genesis MCP Ecosystem

| Module | Description | Repository |
|---|---|---|
| **CrawlEngine MCP** | Anti-bot web scraping, clean Markdown, proxy rotation, and TLS evasion | [GitHub](https://github.com/johannschiffer/crawlengine-mcp) |
| **BrowserBridge MCP** | Deterministic headless browser automation with cryptographic action receipts | [GitHub](https://github.com/johannschiffer/browserbridge-mcp) |
| **PgSafe MCP** | Zero-trust PostgreSQL/SQLite guard, live PII masking, and schema inspection | [GitHub](https://github.com/johannschiffer/pgsafe-mcp) |
| **OmniBridge MCP** | Multi-channel notification bus with persistent SQLite queue | [GitHub](https://github.com/johannschiffer/omnibridge-mcp) |
| **SysFlow MCP** | Safe Linux administration, systemd automation, and port auditing | [GitHub](https://github.com/johannschiffer/sysflow-mcp) |
| **FastMCP Forge** | Production FastMCP server scaffolder with stdio and SSE middleware | [GitHub](https://github.com/johannschiffer/fastmcp-forge) |

## Support

If you find this project helpful, you can support its ongoing maintenance on [Ko-fi](https://ko-fi.com/johannschiffer).

## License

MIT © 2026 [Johann Schiffer](https://github.com/johannschiffer)

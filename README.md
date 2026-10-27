# crawlengine-mcp (v2.0.0)

[![PyPI version](https://img.shields.io/badge/PyPI-v2.0.0-blue.svg)](https://pypi.org/project/crawlengine-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Support on Ko-fi](https://img.shields.io/badge/Support%20on-Ko--fi-ff5e5b.svg)](https://ko-fi.com/johannschiffer)

> **100% Free & Open Source (MIT)**: All features, proxy rotation, migration simulation, Docker stacks, and recipes are completely unlocked. Support open development on [Ko-fi](https://ko-fi.com/johannschiffer).

> ### ⚡ Open Source Ecosystem & Community Tools
> | Resource | Access | Description |
> |---|---|---|
> | **Ruleset Bundle** | **100% Free** | 55+ production rulesets & MCP config templates. [Download Free](https://johannschiffer.github.io/) |
> | **Support & Donate** | **Ko-fi** | Support open-source maintenance. [Support on Ko-fi](https://ko-fi.com/johannschiffer) |

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

## ⚡ Features (Open Source v2.0)

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

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

## Recommended Infrastructure

Proxies that work well with CrawlEngine MCP. Some links are referral links.

- [Webshare](https://www.webshare.io/)
- [ScraperAPI](https://www.scraperapi.com/)
- [Bright Data](https://brightdata.com/)

## Genesis MCP Ecosystem

| Module | What it does | Repo |
|---|---|---|
| **CrawlEngine MCP** (this repo) | Anti-bot web scraping, clean Markdown, proxy rotation and TLS evasion | [GitHub](https://github.com/johannschiffer/crawlengine-mcp) |
| **BrowserBridge MCP** | Deterministic headless browser automation with cryptographic action receipts | [GitHub](https://github.com/johannschiffer/browserbridge-mcp) |
| **PgSafe MCP** | Zero-trust PostgreSQL/SQLite guard, live PII masking, zero-downtime migration checks | [GitHub](https://github.com/johannschiffer/pgsafe-mcp) |
| **OmniBridge MCP** | Multi-channel notification and webhook bus with a persistent SQLite WAL queue | [GitHub](https://github.com/johannschiffer/omnibridge-mcp) |
| **SysFlow MCP** | Safe Linux administration plane: systemd, port audit, isolated execution | [GitHub](https://github.com/johannschiffer/sysflow-mcp) |
| **FastMCP Forge** | Production MCP server scaffolder: stdio, SSE and auth middleware | [GitHub](https://github.com/johannschiffer/fastmcp-forge) |

[Live config builder](https://johannschiffer.github.io) | [GitHub Profile](https://github.com/johannschiffer) | [Support on Ko-fi ☕](https://ko-fi.com/johannschiffer)

## Recommended Infrastructure & Sponsorship

- **Sponsorship & Corporate Support**: Support continued maintenance and priority feature requests via [GitHub Sponsors](https://github.com/sponsors/johannschiffer).
- **Verified Cloud & Network Infrastructure**:
  - **High-Performance VPS & Nodes**: [Hetzner Cloud](https://www.hetzner.com/cloud) & [DigitalOcean](https://m.do.co/c/johannschiffer)
  - **Reliable Proxy Pool & IP Rotation**: [Webshare](https://www.webshare.io/) & [Bright Data](https://brightdata.com/)
  - **Documentation & Setup Guides**: [johannschiffer.github.io](https://johannschiffer.github.io/)

---

## Support

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/johannschiffer)

If you find this tool helpful, you can support its maintenance via Ko-fi.

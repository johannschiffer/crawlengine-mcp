# CrawlEngine MCP (Lite Edition)

> **Free:** [Genesis Starter Kit](https://johanld.gumroad.com/l/genesis-starter-kit) (25 `.cursorrules`/`CLAUDE.md` rulesets + MCP configs). Try the [live config builder](https://johannschiffer.github.io).
> **Full stack:** all six servers in [Genesis Enterprise Suite ($19)](https://johanld.gumroad.com/l/genesis-enterprise-suite).


[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io)

**CrawlEngine MCP** is a resilient Model Context Protocol server that gives AI agents in **Claude Desktop**, **Cursor**, **Windsurf**, and **Antigravity** clean web-reading superpowers without choking context windows on raw HTML or getting instantly blocked by basic anti-bot firewalls.

---

## Run without cloning

```bash
uvx --from git+https://github.com/johannschiffer/crawlengine-mcp crawlengine-mcp
```

Claude Desktop / Cursor config entry:

```json
{
  "mcpServers": {
    "crawlengine-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/johannschiffer/crawlengine-mcp",
        "crawlengine-mcp"
      ]
    }
  }
}
```

[![CI](https://github.com/johannschiffer/crawlengine-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/johannschiffer/crawlengine-mcp/actions/workflows/ci.yml)

## 🕷️ Why CrawlEngine MCP?

Most default web-fetching tools used by AI models suffer from severe drawbacks:
1. **Raw HTML Token Bloat:** A 150KB web page contains ~90% useless boilerplate (navbars, tracking pixels, CSS bundles, cookie banners) that burns LLM tokens and induces hallucinations.
2. **Instant HTTP 403 Blocks:** Default Python `urllib` or `requests` User-Agents trigger anti-bot WAFs immediately.
3. **Broken Relative Links:** Naive scrapers return unnavigable relative paths (`/docs/quickstart`) instead of canonical URLs.

**CrawlEngine** solves this by rotating realistic modern browser fingerprints and transforming messy DOM trees into pristine, semantic Markdown.

---

## ⚡ Features (Lite Edition)

- 🧹 **Semantic Markdown Conversion**: Strips scripts, styles, popups, cookie consent overlays, and ads, keeping only the core article or documentation.
- 🎭 **Realistic Browser Fingerprinting**: Automatically rotates `User-Agent`, `Sec-Ch-Ua`, and platform headers across Chrome, Safari, and Firefox.
- 🔗 **Deep Link Discovery**: Extracts all outbound and internal links with anchor text.
- 🏷️ **Metadata Extraction**: Gathers OpenGraph, Twitter Cards, meta descriptions, and canonical URLs.
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

## 💎 Need Enterprise Anti-Bot Scraping? Upgrade to CrawlEngine Pro

Dealing with complex JavaScript SPAs, Cloudflare Turnstile, or scraping behind proxy pools?

| Feature | Lite (Open Source) | Enterprise Suite ($19) |
|---|:---:|:---:|
| **Semantic Markdown Extraction** | ✅ | ✅ |
| **Browser Fingerprint Rotation** | ✅ | ✅ |
| **OpenGraph & Link Extraction** | ✅ | ✅ |
| **Automatic Headless Browser Fallback** *(Playwright Chromium)* | ❌ | ✅ |
| **JavaScript SPA Hydration** *(React, Next.js, Vue)* | ❌ | ✅ |
| **Proxy Pool Rotation** *(HTTP & SOCKS5 with auto-ejection)* | ❌ | ✅ |
| **Structured Data Extractor** *(JSON-LD, Pricing Tables, Products)* | ❌ | ✅ |
| **Production Docker Container** | ❌ | ✅ |
| **Full Pytest Suite & Anti-Detection Guide** | ❌ | ✅ |

👉 **[Get the Genesis Enterprise Suite ($19)](https://johanld.gumroad.com/l/genesis-enterprise-suite)**

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

[Live config builder](https://johannschiffer.github.io) | [Starter Kit, free](https://johanld.gumroad.com/l/genesis-starter-kit) | [Enterprise Suite, $19](https://johanld.gumroad.com/l/genesis-enterprise-suite)

# crawlengine-mcp

[![PyPI version](https://img.shields.io/pypi/v/crawlengine-mcp.svg)](https://pypi.org/project/crawlengine-mcp/)
[![CI](https://github.com/johannschiffer/crawlengine-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/johannschiffer/crawlengine-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io)
[![Awesome MCP Servers](https://img.shields.io/badge/Awesome--MCP--Servers-TensorBlock-blue?style=flat-square)](https://github.com/TensorBlock/awesome-mcp-servers)

<a href="https://glama.ai/mcp/servers/@johannschiffer/crawlengine-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@johannschiffer/crawlengine-mcp/badge" alt="crawlengine-mcp MCP server" />
</a>

**CrawlEngine MCP** is a **Model Context Protocol (2024-11-05)** web extraction server built on `httpx` and `beautifulsoup4` that converts HTML pages into clean Markdown, resolves relative links, extracts JSON-LD and HTML tables, and rotates browser headers and HTTP/SOCKS5 proxies.

Listed in [TensorBlock/awesome-mcp-servers](https://github.com/TensorBlock/awesome-mcp-servers).

## Why CrawlEngine MCP?

1. **Context Window Efficiency**: Strips `<script>`, `<style>`, `<nav>`, `<footer>`, cookie banners, and ads before returning Markdown to the model.
2. **Resolved Canonical Links**: Converts relative `<a href="/docs/start">` paths into full URLs using the page's `base_url`.
3. **Outbound SSRF Protection**: Blocks loopback, RFC1918 private networks, and cloud metadata (`169.254.169.254`) on both initial requests and HTTP redirects.

## Features

- **Semantic Markdown Extraction**: Preserves headings, lists, code blocks, blockquotes, and resolved inline links without duplicating nested list paragraphs.
- **Browser Header Rotation**: Rotates realistic Chrome, Firefox, and Safari `User-Agent` and `Sec-Ch-Ua` client-hint headers.
- **HTTP & SOCKS5 Proxy Pool**: Round-robin rotation via `CRAWLENGINE_PROXIES` (`httpx[socks]`) with automatic ejection after 3 consecutive failures.
- **Structured Data & Metadata**: Extracts `application/ld+json` schemas, HTML `<table>` rows, OpenGraph tags, canonical URLs, and filtered internal/external links.

## Quickstart

### Run with `uvx`

```bash
uvx crawlengine-mcp
```

### Claude Desktop / Cursor Configuration

```json
{
  "mcpServers": {
    "crawlengine-mcp": {
      "command": "uvx",
      "args": ["crawlengine-mcp"]
    }
  }
}
```

### CLI Usage

```bash
crawlengine-cli scrape https://example.com
crawlengine-cli links https://example.com --internal-only
crawlengine-cli meta https://example.com
```

## MCP Tools Available

| Tool | Parameters | Description |
|---|---|---|
| `scrape_url` | `url`, `extract_markdown`, `use_proxy`, `timeout` | Fetch an HTTP(S) page and convert its main content into Markdown |
| `extract_structured_data` | `url` | Parse `application/ld+json` blocks and HTML tables into JSON records |
| `extract_links` | `url`, `internal_only` | Return deduplicated absolute hyperlinks with anchor text |
| `extract_metadata` | `url` | Extract page title, meta description, OpenGraph tags, and canonical URL |
| `get_proxy_status` | *(none)* | Inspect total, healthy, and ejected proxy counts in `CRAWLENGINE_PROXIES` |

## Genesis MCP Ecosystem

| Module | Description | Repository |
|---|---|---|
| **CrawlEngine MCP** | HTTP web extraction to clean Markdown, JSON-LD parsing, and proxy rotation | [GitHub](https://github.com/johannschiffer/crawlengine-mcp) |
| **BrowserBridge MCP** | Lightweight HTTP/DOM session automation with SHA-256 action receipts | [GitHub](https://github.com/johannschiffer/browserbridge-mcp) |
| **PgSafe MCP** | Read-only PostgreSQL/SQLite query guard, PII masking, and dry-run mutations | [GitHub](https://github.com/johannschiffer/pgsafe-mcp) |
| **OmniBridge MCP** | Multi-channel notification bus with SQLite retry queue | [GitHub](https://github.com/johannschiffer/omnibridge-mcp) |
| **SysFlow MCP** | Linux systemd inspection, confined log tailing, and port auditing | [GitHub](https://github.com/johannschiffer/sysflow-mcp) |
| **FastMCP Forge** | Zero-dependency FastMCP framework, CLI scaffolder, and SSE middleware | [GitHub](https://github.com/johannschiffer/fastmcp-forge) |

## Support

If you find this project useful, you can support maintenance on [Ko-fi](https://ko-fi.com/johannschiffer).

## License

MIT (c) 2026 [Johann Schiffer](https://github.com/johannschiffer)

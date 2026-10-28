"""
CrawlEngine MCP: Model Context Protocol Server.
Includes Header Fingerprint Rotation, Semantic Markdown Extractor,
Proxy Pool Manager, SSRF Guard, and JSON-LD/Table Structured Schema Extractor.
"""

import argparse
import json
import logging
import sys
from typing import Any, Dict, List, Optional

import httpx

from . import __version__
from .core.proxy_pool import ProxyPool
from .core.schema_extractor import SchemaExtractor
from .core.url_guard import validate_crawl_url
from .extractors.markdown import MarkdownExtractor
from .extractors.metadata import MetadataExtractor
from .headers.rotator import HeaderRotator

logger = logging.getLogger("CrawlEngineServer")

BOT_CHALLENGE_INDICATORS = [
    "attention required! | cloudflare",
    "just a moment...",
    "enable javascript and cookies to continue",
    "security check to access",
    "cf-browser-verification",
]


def _check_redirect_ssrf(request: httpx.Request) -> None:
    ok, reason = validate_crawl_url(str(request.url))
    if not ok:
        raise ValueError(reason)


class CrawlEngineServer:
    def __init__(self):
        self.server_name = "crawlengine-mcp"
        self.server_version = __version__
        self.proxy_pool = ProxyPool()

    def get_tools_definition(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "scrape_url",
                "description": "Fetch an HTTP(S) web page with browser header rotation and convert HTML into clean Markdown.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target web page URL"},
                        "extract_markdown": {"type": "boolean", "description": "Convert HTML to Markdown (default: true)"},
                        "use_proxy": {"type": "boolean", "description": "Route request through active proxy pool (default: false)"},
                        "timeout": {"type": "integer", "description": "Request timeout in seconds (default: 15)"},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "extract_structured_data",
                "description": "Extract structured JSON-LD schemas and HTML tabular data from a web page.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target web page URL"},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "extract_links",
                "description": "Extract navigable hyperlinks, anchor text, and canonical URLs from a web page.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target web page URL"},
                        "internal_only": {"type": "boolean", "description": "Only return links matching the base domain (default: false)"},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "extract_metadata",
                "description": "Retrieve page title, OpenGraph tags, meta descriptions, and canonical links.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target web page URL"},
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "get_proxy_status",
                "description": "Check configuration and health of active proxy rotation pool.",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    def _fetch_html(self, url: str, timeout: int = 15, use_proxy: bool = False) -> tuple[int, str]:
        headers = HeaderRotator.get_headers(referer=url)
        proxy = self.proxy_pool.get_proxy() if use_proxy else None
        bounded_timeout = float(max(1, min(int(timeout), 60)))

        client_kwargs: Dict[str, Any] = {
            "follow_redirects": True,
            "max_redirects": 5,
            "timeout": bounded_timeout,
            "headers": headers,
            "event_hooks": {"request": [_check_redirect_ssrf]},
        }
        if proxy:
            client_kwargs["proxy"] = proxy

        try:
            with httpx.Client(**client_kwargs) as client:
                resp = client.get(url)
                if proxy:
                    self.proxy_pool.report_success(proxy)
                return resp.status_code, resp.text
        except ImportError as exc:
            if proxy and proxy.lower().startswith("socks"):
                raise RuntimeError("SOCKS proxy support requires httpx[socks] (`pip install 'httpx[socks]'`).") from exc
            raise
        except Exception:
            if proxy:
                self.proxy_pool.report_failure(proxy)
            raise

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "get_proxy_status":
            return {"proxy_pool": self.proxy_pool.get_stats()}

        if name not in ("scrape_url", "extract_structured_data", "extract_links", "extract_metadata"):
            raise ValueError(f"Unknown tool: {name}")

        url = str(arguments.get("url", "")).strip()
        ok_url, reason = validate_crawl_url(url)
        if not ok_url:
            return {"success": False, "error": reason}

        timeout = arguments.get("timeout", 15)
        use_proxy = bool(arguments.get("use_proxy", False))

        try:
            status_code, html = self._fetch_html(url, timeout=timeout, use_proxy=use_proxy)
        except Exception as e:
            return {"success": False, "error": f"Network fetch error: {str(e)}", "url": url}

        html_lower = html.lower()
        is_blocked = status_code in (403, 503) and any(ind in html_lower for ind in BOT_CHALLENGE_INDICATORS)

        if is_blocked:
            return {
                "success": False,
                "bot_challenge_detected": True,
                "status_code": status_code,
                "error": "Target web server presented an anti-bot verification challenge (Cloudflare/WAF).",
                "suggestion": "Configure CRAWLENGINE_PROXIES for proxy pool rotation or query an API/feed endpoint.",
            }

        if status_code != 200:
            return {
                "success": False,
                "status_code": status_code,
                "error": f"Server returned HTTP {status_code}",
                "url": url,
            }

        if name == "scrape_url":
            extract_md = bool(arguments.get("extract_markdown", True))
            meta = MetadataExtractor.extract(html, base_url=url)
            content = MarkdownExtractor.html_to_markdown(html, base_url=url) if extract_md else html[:10000]

            return {
                "success": True,
                "url": url,
                "status_code": status_code,
                "title": meta.get("title", ""),
                "description": meta.get("description", ""),
                "markdown": content,
                "length_chars": len(content),
            }

        if name == "extract_structured_data":
            json_ld = SchemaExtractor.extract_json_ld(html)
            tables = SchemaExtractor.extract_tables(html)
            return {
                "success": True,
                "url": url,
                "json_ld_schemas": json_ld,
                "tables": tables,
                "tables_found": len(tables),
                "schemas_found": len(json_ld),
            }

        if name == "extract_links":
            internal_only = bool(arguments.get("internal_only", False))
            links = MetadataExtractor.extract_links(html, base_url=url, internal_only=internal_only)
            return {
                "success": True,
                "url": url,
                "count": len(links),
                "links": links,
            }

        meta = MetadataExtractor.extract(html, base_url=url)
        return {
            "success": True,
            "url": url,
            "metadata": meta,
        }

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(request, dict):
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32600, "message": "Invalid Request: expected JSON object"},
            }

        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params")
        if params is None:
            params = {}
        elif not isinstance(params, dict):
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": "Invalid params: expected JSON object"},
            }

        if req_id is None and "id" not in request:
            if method == "notifications/initialized":
                logger.info("Client completed initialization handshake.")
            return None

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": self.server_name,
                        "version": self.server_version,
                    },
                },
            }

        if method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.get_tools_definition()},
            }

        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments")
            if tool_args is None:
                tool_args = {}
            elif not isinstance(tool_args, dict):
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": "Invalid params: 'arguments' must be an object"},
                }
            try:
                output = self.handle_tool_call(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(output, indent=2, ensure_ascii=False),
                            }
                        ],
                        "isError": not output.get("success", True) if "success" in output else False,
                    },
                }
            except Exception as e:
                logger.error("Error calling tool %s: %s", tool_name, e)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)},
                }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    def run_stdio(self) -> None:
        if not logging.getLogger().handlers and not logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] [CrawlEngine] %(message)s",
                stream=sys.stderr,
            )
        logger.info("Starting %s v%s stdio listener...", self.server_name, self.server_version)
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError as e:
                logger.error("JSON parse error: %s", e)
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                logger.error("Error processing stdio line: %s", e)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="crawlengine-mcp",
        description="CrawlEngine MCP stdio server for HTTP web extraction and Markdown conversion",
    )
    parser.add_argument("-v", "--version", action="version", version=f"crawlengine-mcp {__version__}")
    parser.parse_args()
    server = CrawlEngineServer()
    server.run_stdio()


if __name__ == "__main__":
    main()

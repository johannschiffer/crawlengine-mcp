"""
CrawlEngine MCP: Model Context Protocol Server (Enterprise Pro Edition)
Includes Header Fingerprint Rotation, Semantic Markdown Extractor,
Proxy Pool Manager, and JSON-LD/Table Structured Schema Extractor.
"""

import sys
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from .headers.rotator import HeaderRotator
from .extractors.markdown import MarkdownExtractor
from .extractors.metadata import MetadataExtractor
from .core.proxy_pool import ProxyPool
from .core.schema_extractor import SchemaExtractor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [CrawlEngine-Pro] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("CrawlEngineProServer")

BOT_CHALLENGE_INDICATORS = [
    "attention required! | cloudflare",
    "just a moment...",
    "enable javascript and cookies to continue",
    "security check to access",
    "cf-browser-verification"
]

class CrawlEngineProServer:
    def __init__(self):
        self.server_name = "crawlengine-mcp-pro"
        self.server_version = "1.0.0"
        self.proxy_pool = ProxyPool()

    def get_tools_definition(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "scrape_url",
                "description": "Scrape a web page with anti-bot fingerprint rotation and convert content into clean semantic Markdown.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target web page URL"},
                        "extract_markdown": {"type": "boolean", "description": "Convert HTML to Markdown (default: true)"},
                        "use_proxy": {"type": "boolean", "description": "Route request through active proxy pool (default: false)"},
                        "timeout": {"type": "integer", "description": "Request timeout in seconds (default: 15)"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "extract_structured_data",
                "description": "Extract structured JSON-LD schemas and tabular data from a web page.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target web page URL"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "extract_links",
                "description": "Extract all navigable hyperlinks, anchors, and references from a web page.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target web page URL"},
                        "internal_only": {"type": "boolean", "description": "Only return links matching the base domain (default: false)"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "extract_metadata",
                "description": "Retrieve page title, OpenGraph tags, meta descriptions, and canonical links.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target web page URL"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "get_proxy_status",
                "description": "Check configuration and health of active proxy rotation pool.",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]

    def _fetch_html(self, url: str, timeout: int = 15, use_proxy: bool = False) -> tuple[int, str]:
        headers = HeaderRotator.get_headers(referer=url)
        proxy = self.proxy_pool.get_proxy() if use_proxy else None

        client_kwargs: Dict[str, Any] = {
            "follow_redirects": True,
            "timeout": float(timeout),
            "headers": headers
        }
        if proxy:
            client_kwargs["proxy"] = proxy

        try:
            with httpx.Client(**client_kwargs) as client:
                resp = client.get(url)
                if proxy:
                    self.proxy_pool.report_success(proxy)
                return resp.status_code, resp.text
        except Exception as e:
            if proxy:
                self.proxy_pool.report_failure(proxy)
            raise e

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "get_proxy_status":
            return {
                "edition": "Enterprise Pro",
                "proxy_pool": self.proxy_pool.get_stats()
            }

        url = arguments.get("url", "").strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            return {"success": False, "error": f"Invalid URL scheme: '{url}'. Must begin with http:// or https://"}

        timeout = arguments.get("timeout", 15)
        use_proxy = arguments.get("use_proxy", False)

        try:
            status_code, html = self._fetch_html(url, timeout=timeout, use_proxy=use_proxy)
        except Exception as e:
            return {"success": False, "error": f"Network fetch error: {str(e)}", "url": url}

        # Check for Cloudflare challenge page
        html_lower = html.lower()
        is_blocked = status_code in (403, 503) and any(ind in html_lower for ind in BOT_CHALLENGE_INDICATORS)

        if is_blocked:
            return {
                "success": False,
                "bot_challenge_detected": True,
                "status_code": status_code,
                "error": "Target web server presented an anti-bot verification challenge (Cloudflare/WAF).",
                "suggestion": "Enable proxy pool rotation or Playwright headless browser fallback."
            }

        if status_code != 200:
            return {
                "success": False,
                "status_code": status_code,
                "error": f"Server returned HTTP {status_code}",
                "url": url
            }

        if name == "scrape_url":
            extract_md = arguments.get("extract_markdown", True)
            meta = MetadataExtractor.extract(html, base_url=url)
            content = MarkdownExtractor.html_to_markdown(html, base_url=url) if extract_md else html[:10000]

            return {
                "success": True,
                "url": url,
                "status_code": status_code,
                "title": meta.get("title", ""),
                "description": meta.get("description", ""),
                "markdown": content,
                "length_chars": len(content)
            }

        elif name == "extract_structured_data":
            json_ld = SchemaExtractor.extract_json_ld(html)
            tables = SchemaExtractor.extract_tables(html)
            return {
                "success": True,
                "url": url,
                "json_ld_schemas": json_ld,
                "tables": tables,
                "tables_found": len(tables),
                "schemas_found": len(json_ld)
            }

        elif name == "extract_links":
            internal_only = arguments.get("internal_only", False)
            links = MetadataExtractor.extract_links(html, base_url=url, internal_only=internal_only)
            return {
                "success": True,
                "url": url,
                "count": len(links),
                "links": links
            }

        elif name == "extract_metadata":
            meta = MetadataExtractor.extract(html, base_url=url)
            return {
                "success": True,
                "url": url,
                "metadata": meta
            }

        else:
            raise ValueError(f"Unknown tool: {name}")

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if req_id is None:
            if method == "notifications/initialized":
                logger.info("Pro client completed initialization handshake.")
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
                        "version": self.server_version
                    }
                }
            }

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.get_tools_definition()}
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                output = self.handle_tool_call(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(output, indent=2, ensure_ascii=False)
                            }
                        ],
                        "isError": not output.get("success", True) if "success" in output else False
                    }
                }
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)}
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

    def run_stdio(self):
        logger.info(f"Starting {self.server_name} v{self.server_version} stdio listener...")
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
            except Exception as e:
                logger.error(f"Error processing stdio line: {e}")

def main():
    server = CrawlEngineProServer()
    server.run_stdio()

if __name__ == "__main__":
    main()

"""
CrawlEngine MCP: Model Context Protocol Server (Lite Edition)
Implements standard JSON-RPC 2.0 stdio transport for web scraping and clean markdown extraction.
"""

import sys
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from .headers.rotator import HeaderRotator
from .extractors.markdown import MarkdownExtractor
from .extractors.metadata import MetadataExtractor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [CrawlEngine] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("CrawlEngineServer")

class CrawlEngineMCPServer:
    def __init__(self):
        self.server_name = "crawlengine-mcp"
        self.server_version = "1.0.0"

    def get_tools_definition(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "scrape_url",
                "description": "Scrape a web page with browser fingerprinting and convert its content into clean, token-efficient Markdown.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Target HTTP/HTTPS web page URL"},
                        "extract_markdown": {"type": "boolean", "description": "Convert HTML into semantic Markdown (default: true)"},
                        "timeout": {"type": "integer", "description": "Request timeout in seconds (default: 15)"}
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
                        "internal_only": {"type": "boolean", "description": "Filter links to only those belonging to the same domain (default: false)"}
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
            }
        ]

    def _fetch_html(self, url: str, timeout: int = 15) -> tuple[int, str]:
        headers = HeaderRotator.get_headers(referer=url)
        with httpx.Client(follow_redirects=True, timeout=float(timeout)) as client:
            resp = client.get(url, headers=headers)
            return resp.status_code, resp.text

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        url = arguments.get("url", "").strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            return {"success": False, "error": f"Invalid URL scheme. Must begin with http:// or https://: '{url}'"}

        timeout = arguments.get("timeout", 15)

        try:
            status_code, html = self._fetch_html(url, timeout=timeout)
        except Exception as e:
            return {"success": False, "error": f"Network fetch error: {str(e)}", "url": url}

        if status_code != 200:
            return {
                "success": False,
                "status_code": status_code,
                "error": f"Web server returned HTTP {status_code}",
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
    import argparse
    parser = argparse.ArgumentParser(
        prog="crawlengine-mcp",
        description="CrawlEngine MCP: Resilient Web Scraping & Clean Markdown Extraction for AI Agents"
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    args, unknown = parser.parse_known_args()
    server = CrawlEngineMCPServer()
    server.run_stdio()

if __name__ == "__main__":
    main()

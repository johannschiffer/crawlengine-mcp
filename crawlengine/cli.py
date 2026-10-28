"""
CrawlEngine CLI utility.
Usage:
  crawlengine-cli scrape https://example.com
  crawlengine-cli links https://example.com
  crawlengine-cli meta https://example.com
"""

import argparse
import json
import sys

from . import __version__
from .server import CrawlEngineServer


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="crawlengine-cli",
        description="CrawlEngine CLI utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--version", action="version", version=f"crawlengine-cli {__version__}")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    scrape_parser = subparsers.add_parser("scrape", help="Fetch and convert URL to Markdown")
    scrape_parser.add_argument("url", help="URL to scrape")

    links_parser = subparsers.add_parser("links", help="Extract links from URL")
    links_parser.add_argument("url", help="URL to extract links from")
    links_parser.add_argument("--internal-only", action="store_true", help="Filter to internal links")

    meta_parser = subparsers.add_parser("meta", help="Extract OpenGraph and meta tags")
    meta_parser.add_argument("url", help="URL to inspect")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    server = CrawlEngineServer()
    if args.command == "scrape":
        res = server.handle_tool_call("scrape_url", {"url": args.url})
        if not res.get("success"):
            print(f"[ERROR] {res.get('error')}", file=sys.stderr)
            sys.exit(1)
        print(res["markdown"])
    elif args.command == "links":
        res = server.handle_tool_call("extract_links", {"url": args.url, "internal_only": args.internal_only})
        if not res.get("success"):
            print(f"[ERROR] {res.get('error')}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(res["links"], indent=2))
    elif args.command == "meta":
        res = server.handle_tool_call("extract_metadata", {"url": args.url})
        if not res.get("success"):
            print(f"[ERROR] {res.get('error')}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(res["metadata"], indent=2))


if __name__ == "__main__":
    main()

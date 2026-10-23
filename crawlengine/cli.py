"""
CrawlEngine CLI testing utility.
Usage:
  python -m crawlengine.cli scrape https://news.ycombinator.com
  python -m crawlengine.cli links https://github.com
  python -m crawlengine.cli meta https://dev.to
"""

import argparse
import json
import sys
import httpx
from .headers.rotator import HeaderRotator
from .extractors.markdown import MarkdownExtractor
from .extractors.metadata import MetadataExtractor

def main():
    parser = argparse.ArgumentParser(description="CrawlEngine CLI utility")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    scrape_parser = subparsers.add_parser("scrape", help="Scrape and convert URL to Markdown")
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

    headers = HeaderRotator.get_headers(referer=args.url)
    try:
        with httpx.Client(follow_redirects=True, timeout=15.0) as client:
            resp = client.get(args.url, headers=headers)
            html = resp.text
    except Exception as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "scrape":
        md = MarkdownExtractor.html_to_markdown(html, base_url=args.url)
        print(md)

    elif args.command == "links":
        links = MetadataExtractor.extract_links(html, base_url=args.url, internal_only=args.internal_only)
        print(json.dumps(links, indent=2))

    elif args.command == "meta":
        meta = MetadataExtractor.extract(html, base_url=args.url)
        print(json.dumps(meta, indent=2))



_main_impl = main


def main():
    from ._genesis import print_upgrade_notice
    try:
        return _main_impl()
    finally:
        print_upgrade_notice()

if __name__ == "__main__":
    main()

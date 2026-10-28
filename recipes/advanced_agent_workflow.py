"""
CrawlEngine MCP workflow recipe.
Demonstrates HTML-to-Markdown conversion with resolved links and JSON-LD/table schema extraction.
"""
import json

from crawlengine.core.schema_extractor import SchemaExtractor
from crawlengine.extractors.markdown import MarkdownExtractor

SAMPLE_HTML = """
<html>
  <head>
    <title>Docs</title>
    <script type="application/ld+json">
      {"@context": "https://schema.org", "@type": "TechArticle", "headline": "MCP Guide"}
    </script>
  </head>
  <body>
    <main>
      <h1>MCP Integration Guide</h1>
      <p>Read the <a href="/docs/quickstart">Quickstart</a> to get started.</p>
    </main>
  </body>
</html>
"""


def main() -> None:
    md = MarkdownExtractor.html_to_markdown(SAMPLE_HTML, base_url="https://example.com")
    schemas = SchemaExtractor.extract_json_ld(SAMPLE_HTML)
    print(json.dumps({"markdown": md, "schemas": schemas}, indent=2))


if __name__ == "__main__":
    main()

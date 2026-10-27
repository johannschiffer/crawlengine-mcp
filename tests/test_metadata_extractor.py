"""
Unit tests for MetadataExtractor.
"""
from crawlengine.extractors.metadata import MetadataExtractor

def test_metadata_and_links():
    html = """
    <html>
      <head>
        <title>Test Page Title</title>
        <meta name="description" content="A test page for web scraping.">
        <link rel="canonical" href="https://example.com/canonical">
      </head>
      <body>
        <a href="/internal/page">Internal Link</a>
        <a href="https://other.com/external">External Link</a>
        <a href="#hash">Hash Link</a>
      </body>
    </html>
    """
    meta = MetadataExtractor.extract(html, base_url="https://example.com")
    assert meta["title"] == "Test Page Title"
    assert meta["description"] == "A test page for web scraping."
    assert meta["canonical_url"] == "https://example.com/canonical"

    all_links = MetadataExtractor.extract_links(html, base_url="https://example.com", internal_only=False)
    assert len(all_links) == 2
    assert all_links[0]["url"] == "https://example.com/internal/page"
    assert all_links[0]["is_internal"] is True
    assert all_links[1]["url"] == "https://other.com/external"
    assert all_links[1]["is_internal"] is False

    internal_links = MetadataExtractor.extract_links(html, base_url="https://example.com", internal_only=True)
    assert len(internal_links) == 1
    assert internal_links[0]["url"] == "https://example.com/internal/page"

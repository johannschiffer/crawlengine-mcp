"""
Unit tests for MarkdownExtractor.
"""
from crawlengine.extractors.markdown import MarkdownExtractor

def test_markdown_extractor_noise_removal():
    html = """
    <html>
      <head><script>console.log('tracker');</script></head>
      <body>
        <nav><a href="/">Home</a></nav>
        <div class="cookie-banner-popup">Please accept our cookies!</div>
        <main>
          <h1>Project Overview</h1>
          <p>This is the primary content that should be extracted.</p>
          <ul>
            <li>Feature 1</li>
            <li>Feature 2</li>
          </ul>
        </main>
        <footer>Copyright 2026</footer>
      </body>
    </html>
    """
    md = MarkdownExtractor.html_to_markdown(html)
    assert "# Project Overview" in md
    assert "This is the primary content that should be extracted." in md
    assert "- Feature 1" in md
    assert "cookie" not in md.lower()
    assert "tracker" not in md
    assert "Copyright" not in md

"""
Unit tests for SchemaExtractor (JSON-LD and Tables).
"""
from crawlengine.core.schema_extractor import SchemaExtractor

def test_json_ld_extraction():
    html = """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "Product",
          "name": "Pro Widget",
          "price": "14.99"
        }
        </script>
      </head>
      <body></body>
    </html>
    """
    schemas = SchemaExtractor.extract_json_ld(html)
    assert len(schemas) == 1
    assert schemas[0]["name"] == "Pro Widget"
    assert schemas[0]["price"] == "14.99"

def test_html_table_extraction():
    html = """
    <table>
      <thead>
        <tr><th>Plan</th><th>Price</th></tr>
      </thead>
      <tbody>
        <tr><td>Lite</td><td>$0</td></tr>
        <tr><td>Pro</td><td>$14.99</td></tr>
      </tbody>
    </table>
    """
    tables = SchemaExtractor.extract_tables(html)
    assert len(tables) == 1
    assert tables[0]["headers"] == ["Plan", "Price"]
    assert len(tables[0]["rows"]) == 2
    assert tables[0]["rows"][0]["Plan"] == "Lite"
    assert tables[0]["rows"][1]["Price"] == "$14.99"

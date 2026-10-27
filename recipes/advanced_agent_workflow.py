import asyncio
from crawlengine.server import CrawlEngineServer

async def main():
    server = CrawlEngineServer()
    # Scrape with automatic User-Agent fingerprint rotation and clean markdown conversion
    result = await server.handle_scrape({
        "url": "https://news.ycombinator.com",
        "extract_markdown": True,
        "extract_schema": True
    })
    print(f"Scraped {len(result['markdown'])} chars of markdown.")
    print("Extracted schema objects:", result.get("schema", []))

if __name__ == "__main__":
    asyncio.run(main())

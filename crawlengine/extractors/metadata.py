"""
Web Metadata & Hyperlink Extractor.
Extracts title, meta tags, OpenGraph data, and structured links.
"""
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class MetadataExtractor:
    @staticmethod
    def extract(html_content: str, base_url: str = "") -> Dict[str, Any]:
        soup = BeautifulSoup(html_content, "html.parser")

        # Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Meta tags
        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()

        og_title = ""
        og_tag = soup.find("meta", attrs={"property": "og:title"})
        if og_tag and og_tag.get("content"):
            og_title = og_tag["content"].strip()

        canonical = ""
        can_tag = soup.find("link", attrs={"rel": "canonical"})
        if can_tag and can_tag.get("href"):
            canonical = urljoin(base_url, can_tag["href"])

        return {
            "title": title or og_title,
            "description": meta_desc,
            "canonical_url": canonical,
            "has_opengraph": bool(og_title or desc_tag)
        }

    @staticmethod
    def extract_links(html_content: str, base_url: str = "", internal_only: bool = False) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html_content, "html.parser")
        base_domain = urlparse(base_url).netloc if base_url else ""

        links = []
        seen = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                continue

            full_url = urljoin(base_url, href)
            target_domain = urlparse(full_url).netloc

            if internal_only and base_domain and target_domain != base_domain:
                continue

            if full_url in seen:
                continue
            seen.add(full_url)

            text = a.get_text(strip=True)
            links.append({
                "url": full_url,
                "text": text[:100] if text else "",
                "is_internal": (target_domain == base_domain) if base_domain else True
            })

        return links

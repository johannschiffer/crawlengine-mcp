"""
HTML to Clean Semantic Markdown Extractor.
Strips boilerplate, navigation elements, tracking scripts, and cookie banners
to produce token-efficient, clean Markdown for LLMs.
"""
import re
from bs4 import BeautifulSoup

NOISE_TAGS = ["script", "style", "noscript", "iframe", "svg", "canvas", "nav", "footer", "aside"]
NOISE_CLASSES_IDS = re.compile(
    r"(cookie|banner|advert|popup|modal|tracking|newsletter|social-share|sidebar|header|footer)",
    re.IGNORECASE
)

class MarkdownExtractor:
    @staticmethod
    def html_to_markdown(html_content: str, base_url: str = "") -> str:
        if not html_content or not html_content.strip():
            return ""

        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Remove noise tags
        for tag in soup(NOISE_TAGS):
            tag.decompose()

        # 2. Remove noise divs/elements
        for el in soup.find_all(attrs={"class": NOISE_CLASSES_IDS}):
            # Don't delete main content container even if class has matching substring
            if el.name in ["main", "article", "body"]:
                continue
            el.decompose()

        for el in soup.find_all(attrs={"id": NOISE_CLASSES_IDS}):
            if el.name in ["main", "article", "body"]:
                continue
            el.decompose()

        # 3. Locate primary container if available
        main_content = soup.find("main") or soup.find("article") or soup.find("body") or soup

        markdown_lines = []

        for element in main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "blockquote"]):
            text = element.get_text(strip=True)
            if not text:
                continue

            tag_name = element.name
            if tag_name == "h1":
                markdown_lines.append(f"\n# {text}\n")
            elif tag_name == "h2":
                markdown_lines.append(f"\n## {text}\n")
            elif tag_name == "h3":
                markdown_lines.append(f"\n### {text}\n")
            elif tag_name == "h4":
                markdown_lines.append(f"\n#### {text}\n")
            elif tag_name == "h5" or tag_name == "h6":
                markdown_lines.append(f"\n##### {text}\n")
            elif tag_name == "p":
                markdown_lines.append(f"\n{text}\n")
            elif tag_name == "li":
                markdown_lines.append(f"- {text}")
            elif tag_name == "pre":
                markdown_lines.append(f"\n```\n{text}\n```\n")
            elif tag_name == "blockquote":
                markdown_lines.append(f"\n> {text}\n")

        raw_md = "\n".join(markdown_lines)
        # Collapse multiple blank lines
        clean_md = re.sub(r"\n{3,}", "\n\n", raw_md).strip()

        # Fallback if no specific tags matched
        if not clean_md:
            clean_md = main_content.get_text(separator="\n", strip=True)

        return clean_md

"""
HTML to Clean Semantic Markdown Extractor.
Strips boilerplate, navigation elements, tracking scripts, and cookie banners
to produce clean Markdown with resolved anchor URLs.
"""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup, NavigableString, Tag

NOISE_TAGS = ["script", "style", "noscript", "iframe", "svg", "canvas", "nav", "footer", "aside"]
NOISE_CLASSES_IDS = re.compile(
    r"(cookie|banner|advert|popup|modal|tracking|newsletter|social-share|sidebar|header|footer)",
    re.IGNORECASE,
)


def _render_inline(node: Tag, base_url: str = "") -> str:
    """Render inline text while converting <a href> elements into Markdown links."""
    parts = []
    for child in node.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
        elif isinstance(child, Tag):
            if child.name == "a" and child.get("href"):
                href = str(child["href"]).strip()
                label = child.get_text(" ", strip=True)
                if label and href and not href.lower().startswith("javascript:"):
                    resolved = urljoin(base_url, href) if base_url else href
                    parts.append(f"[{label}]({resolved})")
                elif label:
                    parts.append(label)
            elif child.name in ("ul", "ol"):
                continue
            else:
                parts.append(_render_inline(child, base_url=base_url))
    return re.sub(r"[ \t]+", " ", "".join(parts)).strip()


class MarkdownExtractor:
    @staticmethod
    def html_to_markdown(html_content: str, base_url: str = "") -> str:
        if not html_content or not html_content.strip():
            return ""

        soup = BeautifulSoup(html_content, "html.parser")

        for tag in soup(NOISE_TAGS):
            tag.decompose()

        for el in list(soup.find_all(attrs={"class": NOISE_CLASSES_IDS})):
            if el.name in ("main", "article", "body"):
                continue
            el.decompose()

        for el in list(soup.find_all(attrs={"id": NOISE_CLASSES_IDS})):
            if el.name in ("main", "article", "body"):
                continue
            el.decompose()

        main_content = soup.find("main") or soup.find("article") or soup.find("body") or soup

        markdown_lines = []

        for element in main_content.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "blockquote"]
        ):
            tag_name = element.name
            if tag_name == "p" and element.find_parent(["li", "blockquote"]) is not None:
                continue

            if tag_name == "pre":
                text = element.get_text(strip=True)
            else:
                text = _render_inline(element, base_url=base_url)

            if not text:
                continue

            if tag_name == "h1":
                markdown_lines.append(f"\n# {text}\n")
            elif tag_name == "h2":
                markdown_lines.append(f"\n## {text}\n")
            elif tag_name == "h3":
                markdown_lines.append(f"\n### {text}\n")
            elif tag_name == "h4":
                markdown_lines.append(f"\n#### {text}\n")
            elif tag_name in ("h5", "h6"):
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
        clean_md = re.sub(r"\n{3,}", "\n\n", raw_md).strip()

        if not clean_md:
            clean_md = main_content.get_text(separator="\n", strip=True)

        return clean_md

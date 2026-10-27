"""
Structured Data & Schema Extractor (CrawlEngine Pro Core).
Parses JSON-LD blocks and tabular data into clean structured JSON schemas for LLMs.
"""
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any

class SchemaExtractor:
    @staticmethod
    def extract_json_ld(html_content: str) -> List[Dict[str, Any]]:
        """Finds and parses all JSON-LD scripts in HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        schemas = []

        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            raw = script.string
            if not raw or not raw.strip():
                continue
            try:
                data = json.loads(raw.strip())
                if isinstance(data, list):
                    schemas.extend(data)
                elif isinstance(data, dict):
                    schemas.append(data)
            except Exception:
                continue

        return schemas

    @staticmethod
    def extract_tables(html_content: str) -> List[Dict[str, Any]]:
        """Parses HTML tables into structured row records."""
        soup = BeautifulSoup(html_content, "html.parser")
        extracted_tables = []

        for table_idx, table in enumerate(soup.find_all("table")):
            headers = []
            thead = table.find("thead")
            if thead:
                headers = [th.get_text(strip=True) for th in thead.find_all(["th", "td"])]
            
            # If no thead, check first tr
            first_tr = table.find("tr")
            if not headers and first_tr:
                th_cells = first_tr.find_all("th")
                if th_cells:
                    headers = [th.get_text(strip=True) for th in th_cells]

            rows_data = []
            tbody = table.find("tbody") or table
            for tr in tbody.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if not cells or cells == headers:
                    continue

                if headers and len(headers) == len(cells):
                    row_obj = {headers[i]: cells[i] for i in range(len(headers))}
                    rows_data.append(row_obj)
                else:
                    rows_data.append(cells)

            if rows_data:
                extracted_tables.append({
                    "table_index": table_idx,
                    "headers": headers,
                    "row_count": len(rows_data),
                    "rows": rows_data
                })

        return extracted_tables

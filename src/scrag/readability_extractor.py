import requests
from readability import Document
from lxml import html

class ReadabilityExtractor:

    def extract(self, url=None, html_content=None):
        try:
            if not url and not html_content:
                return {"error": "give either a URL or raw HTML input"}

            if url:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                html_content = response.text

            doc = Document(html_content)
            title = doc.title()
            summary_html = doc.summary()
            parsed = html.fromstring(summary_html)
            text = parsed.text_content().strip()

            return {
                "title": title,
                "text": text,
                "html": summary_html,
                "url": url,
            }

        except Exception as e:
            return {"error": str(e)}

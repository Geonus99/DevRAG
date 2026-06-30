from dataclasses import dataclass
from io import BytesIO
from typing import List
from urllib.parse import urljoin, urlparse

import fitz
import requests
from bs4 import BeautifulSoup


MAX_PAGES = 5
REQUEST_TIMEOUT = 15


@dataclass
class CrawledDocument:
    title: str
    content: str
    page_url: str


def crawl_source(source_url: str, source_type: str) -> List[CrawledDocument]:
    if source_type == 'PDF':
        return parse_pdf(source_url)
    if source_type == 'URL':
        return crawl_url(source_url)
    raise ValueError('source_type은 URL 또는 PDF여야 합니다')


def crawl_url(start_url: str, max_pages: int = MAX_PAGES) -> List[CrawledDocument]:
    visited = set()
    queue = [start_url]
    documents = []
    origin = urlparse(start_url).netloc

    while queue and len(documents) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue

        visited.add(url)
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={'User-Agent': 'DevRAG/1.0'})
        response.raise_for_status()

        content_type = response.headers.get('content-type', '')
        if 'pdf' in content_type:
            documents.extend(parse_pdf_bytes(response.content, url))
            continue
        if 'html' not in content_type:
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()

        title = soup.title.get_text(' ', strip=True) if soup.title else url
        text = soup.get_text('\n', strip=True)
        if text:
            documents.append(CrawledDocument(title=title, content=text, page_url=url))

        for link in soup.find_all('a', href=True):
            href = urljoin(url, link['href']).split('#')[0]
            parsed = urlparse(href)
            if parsed.scheme in ('http', 'https') and parsed.netloc == origin and href not in visited:
                queue.append(href)

    return documents


def parse_pdf(source_url: str) -> List[CrawledDocument]:
    response = requests.get(source_url, timeout=REQUEST_TIMEOUT, headers={'User-Agent': 'DevRAG/1.0'})
    response.raise_for_status()
    return parse_pdf_bytes(response.content, source_url)


def parse_pdf_bytes(pdf_bytes: bytes, page_url: str) -> List[CrawledDocument]:
    documents = []
    with fitz.open(stream=BytesIO(pdf_bytes), filetype='pdf') as pdf:
        title = pdf.metadata.get('title') or page_url
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text('text').strip()
            if text:
                documents.append(
                    CrawledDocument(
                        title=f'{title} p.{page_number}',
                        content=text,
                        page_url=f'{page_url}#page={page_number}',
                    )
                )
    return documents

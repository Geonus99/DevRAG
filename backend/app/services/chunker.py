from typing import Dict, List

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.crawler import CrawledDocument


CHUNK_SIZE = 900
CHUNK_OVERLAP = 120
ENCODING_NAME = 'cl100k_base'


def split_documents(documents: List[CrawledDocument]) -> List[Dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=['\n\n', '\n', '. ', ' ', ''],
    )
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    chunks = []

    for document in documents:
        for content in splitter.split_text(document.content):
            clean_content = content.strip()
            if not clean_content:
                continue

            chunks.append(
                {
                    'title': document.title,
                    'content': clean_content,
                    'page_url': document.page_url,
                    'token_count': len(encoding.encode(clean_content)),
                }
            )

    return chunks

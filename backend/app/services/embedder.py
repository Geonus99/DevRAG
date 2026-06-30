import os
from pathlib import Path
from typing import Iterable, List

from dotenv import load_dotenv
from openai import OpenAI


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / '.env')

EMBEDDING_MODEL = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def embed_texts(texts: Iterable[str]) -> List[List[float]]:
    text_list = list(texts)
    if not text_list:
        return []

    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text_list)
    return [item.embedding for item in response.data]


def embed_query(query: str) -> List[float]:
    return embed_texts([query])[0]

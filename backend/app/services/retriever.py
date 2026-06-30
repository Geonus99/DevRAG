import json
from math import sqrt
from typing import Dict, List

from app.models.database import get_db
from app.services.embedder import embed_query


DEFAULT_MATCH_COUNT = 5
MIN_RELEVANCE_SCORE = 0.2


def retrieve_relevant_chunks(query: str, match_count: int = DEFAULT_MATCH_COUNT) -> List[Dict]:
    query_embedding = embed_query(query)
    db = get_db()

    try:
        result = db.rpc(
            'match_document_chunks',
            {'query_embedding': query_embedding, 'match_count': match_count},
        ).execute()
        if result.data:
            return [
                chunk for chunk in result.data
                if (chunk.get('relevance_score') or 0) >= MIN_RELEVANCE_SCORE
            ]
    except Exception:
        # Local fallback keeps development usable before the Supabase RPC is installed.
        pass

    result = db.table('document_chunks').select('*').execute()
    chunks = result.data or []
    ranked = []
    for chunk in chunks:
        embedding = parse_embedding(chunk.get('embedding'))
        if not embedding:
            continue
        score = cosine_similarity(query_embedding, embedding)
        if score < MIN_RELEVANCE_SCORE:
            continue
        ranked.append({**chunk, 'relevance_score': score})

    return sorted(ranked, key=lambda item: item['relevance_score'], reverse=True)[:match_count]


def parse_embedding(embedding) -> List[float]:
    if embedding is None:
        return []
    if isinstance(embedding, str):
        # pgvector columns come back from PostgREST as their text
        # representation (e.g. "[0.01,0.02,...]"), not a JSON array.
        return json.loads(embedding)
    return embedding


def cosine_similarity(left: List[float], right: List[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sqrt(sum(a * a for a in left))
    right_norm = sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)

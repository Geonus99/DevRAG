import os
import re
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from openai import OpenAI

from app.models.database import get_db
from app.services.retriever import retrieve_relevant_chunks


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / '.env')

CHAT_MODEL = os.getenv('OPENAI_CHAT_MODEL', 'gpt-4o-mini')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

chat_bp = Blueprint('chat', __name__)

CODE_BLOCK_PATTERN = re.compile(r'```.*?```', re.DOTALL)


@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    session_id = data.get('session_id')

    if not message:
        return jsonify({'error': 'message는 필수입니다'}), 400

    db = get_db()
    session = ensure_session(db, session_id, message)
    user_message = db.table('chat_messages').insert({
        'session_id': session['id'],
        'role': 'user',
        'message': message,
    }).execute().data[0]

    has_code = bool(CODE_BLOCK_PATTERN.search(message))
    search_query = build_search_query(message) if has_code else message

    chunks = retrieve_relevant_chunks(search_query, match_count=data.get('match_count', 5))
    context = build_context(chunks)
    answer = generate_answer(message, context, has_code)

    assistant_message = db.table('chat_messages').insert({
        'session_id': session['id'],
        'role': 'assistant',
        'message': answer,
    }).execute().data[0]

    references = []
    for chunk in chunks:
        chunk_id = chunk.get('id')
        if not chunk_id:
            continue
        reference = db.table('source_references').insert({
            'message_id': assistant_message['id'],
            'chunk_id': chunk_id,
            'relevance_score': chunk.get('relevance_score') or chunk.get('similarity'),
        }).execute().data[0]
        references.append({**reference, 'chunk': chunk})

    db.table('chat_sessions').update({
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }).eq('id', session['id']).execute()

    return jsonify({
        'session_id': session['id'],
        'user_message_id': user_message['id'],
        'assistant_message_id': assistant_message['id'],
        'answer': answer,
        'references': references,
        'has_code': has_code,
    }), 200


@chat_bp.route('/sessions', methods=['GET'])
def get_sessions():
    db = get_db()
    result = db.table('chat_sessions').select('*').order('updated_at', desc=True).execute()
    return jsonify(result.data), 200


@chat_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    db = get_db()
    session_result = db.table('chat_sessions').select('*').eq('id', session_id).execute()
    if not session_result.data:
        return jsonify({'error': '세션을 찾을 수 없습니다'}), 404

    messages = db.table('chat_messages').select('*').eq(
        'session_id', session_id
    ).order('created_at').execute().data

    return jsonify({**session_result.data[0], 'messages': messages}), 200


@chat_bp.route('/messages/<message_id>/references', methods=['GET'])
def get_message_references(message_id):
    db = get_db()
    result = db.table('source_references').select(
        '*, chunk:document_chunks(*)'
    ).eq('message_id', message_id).order('relevance_score', desc=True).execute()

    return jsonify(result.data), 200


def ensure_session(db, session_id, message):
    if session_id:
        result = db.table('chat_sessions').select('*').eq('id', session_id).execute()
        if result.data:
            return result.data[0]

    title = message[:40] if len(message) <= 40 else f'{message[:37]}...'
    return db.table('chat_sessions').insert({'title': title}).execute().data[0]


def build_context(chunks):
    lines = []
    for index, chunk in enumerate(chunks, start=1):
        source_title = chunk.get('title') or 'Untitled'
        page_url = chunk.get('page_url') or ''
        content = chunk.get('content') or ''
        lines.append(f'[{index}] {source_title}\nURL: {page_url}\n{content}')
    return '\n\n---\n\n'.join(lines)


def build_search_query(message):
    # Embedding a question's natural-language part retrieves better matches
    # than embedding raw code, so fenced code blocks are stripped for search.
    stripped = CODE_BLOCK_PATTERN.sub(' ', message).strip()
    return stripped or message


def generate_answer(question, context, has_code=False):
    if not context:
        return '등록된 문서에서 관련 근거를 찾지 못했습니다. 먼저 URL 또는 PDF를 등록하고 수집을 실행해주세요.'

    system_prompt = (
        'You are DevRAG, a Korean RAG assistant. Answer only from the provided context. '
        'If the context is insufficient, say that the registered documents do not contain enough evidence. '
        'Cite evidence with bracket numbers like [1], [2].'
    )
    if has_code:
        system_prompt += (
            ' The user included a code snippet. Explain how the provided context relates to that code '
            'and point out relevant APIs, parameters, or usage patterns from the context.'
        )

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                'role': 'system',
                'content': system_prompt,
            },
            {
                'role': 'user',
                'content': f'질문:\n{question}\n\n등록 문서 컨텍스트:\n{context}',
            },
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content

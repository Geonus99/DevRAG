from flask import Blueprint, request, jsonify
from datetime import datetime, timezone

from app.models.database import get_db
from app.services.chunker import split_documents
from app.services.crawler import crawl_source
from app.services.embedder import embed_texts

sources_bp = Blueprint('sources', __name__)

# 문서 등록
@sources_bp.route('/sources', methods=['POST'])
def create_source():
    data = request.get_json()
    
    if not data.get('source_name'):
        return jsonify({'error': 'source_name은 필수입니다'}), 400
    if not data.get('source_type') in ['URL', 'PDF']:
        return jsonify({'error': 'source_type은 URL 또는 PDF여야 합니다'}), 400
    if not data.get('source_url'):
        return jsonify({'error': 'source_url은 필수입니다'}), 400

    db = get_db()
    result = db.table('knowledge_sources').insert({
        'source_name': data['source_name'],
        'source_url': data.get('source_url'),
        'source_type': data['source_type'],
        'status': 'PENDING'
    }).execute()

    return jsonify(result.data[0]), 201


# 전체 목록 조회
@sources_bp.route('/sources', methods=['GET'])
def get_sources():
    db = get_db()
    result = db.table('knowledge_sources').select('*').order('created_at', desc=True).execute()
    return jsonify(result.data), 200


# 단일 조회
@sources_bp.route('/sources/<source_id>', methods=['GET'])
def get_source(source_id):
    db = get_db()
    result = db.table('knowledge_sources').select('*').eq('id', source_id).execute()

    if not result.data:
        return jsonify({'error': '문서를 찾을 수 없습니다'}), 404

    return jsonify(result.data[0]), 200


# 삭제
@sources_bp.route('/sources/<source_id>', methods=['DELETE'])
def delete_source(source_id):
    db = get_db()
    result = db.table('knowledge_sources').delete().eq('id', source_id).execute()

    if not result.data:
        return jsonify({'error': '문서를 찾을 수 없습니다'}), 404

    return jsonify({'message': '삭제 완료'}), 200


# 수집/청킹/임베딩 실행
@sources_bp.route('/sources/<source_id>/ingest', methods=['POST'])
def ingest_source(source_id):
    db = get_db()
    source_result = db.table('knowledge_sources').select('*').eq('id', source_id).execute()

    if not source_result.data:
        return jsonify({'error': '문서를 찾을 수 없습니다'}), 404

    source = source_result.data[0]
    job = db.table('ingestion_jobs').insert({
        'source_id': source_id,
        'status': 'PROCESSING',
    }).execute().data[0]

    try:
        db.table('knowledge_sources').update({
            'status': 'PROCESSING',
            'error_message': None,
        }).eq('id', source_id).execute()

        db.table('document_chunks').delete().eq('source_id', source_id).execute()

        documents = crawl_source(source['source_url'], source['source_type'])
        chunks = split_documents(documents)
        embeddings = embed_texts(chunk['content'] for chunk in chunks)

        rows = []
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            rows.append({
                'source_id': source_id,
                'title': chunk['title'],
                'content': chunk['content'],
                'chunk_index': index,
                'token_count': chunk['token_count'],
                'page_url': chunk['page_url'],
                'embedding': embedding,
            })

        if rows:
            db.table('document_chunks').insert(rows).execute()

        db.table('knowledge_sources').update({
            'status': 'COMPLETED',
            'crawled_pages': len(documents),
            'chunk_count': len(rows),
            'error_message': None,
        }).eq('id', source_id).execute()

        db.table('ingestion_jobs').update({
            'status': 'COMPLETED',
            'completed_at': datetime.now(timezone.utc).isoformat(),
        }).eq('id', job['id']).execute()

        return jsonify({
            'source_id': source_id,
            'status': 'COMPLETED',
            'crawled_pages': len(documents),
            'chunk_count': len(rows),
        }), 200

    except Exception as exc:
        error_message = str(exc)
        db.table('knowledge_sources').update({
            'status': 'FAILED',
            'error_message': error_message,
        }).eq('id', source_id).execute()
        db.table('ingestion_jobs').update({
            'status': 'FAILED',
            'error_message': error_message,
            'completed_at': datetime.now(timezone.utc).isoformat(),
        }).eq('id', job['id']).execute()
        return jsonify({'error': error_message}), 500


# 수집 상태 조회
@sources_bp.route('/sources/<source_id>/status', methods=['GET'])
def get_source_status(source_id):
    db = get_db()
    result = db.table('knowledge_sources').select(
        'id, status, crawled_pages, chunk_count, error_message, created_at'
    ).eq('id', source_id).execute()

    if not result.data:
        return jsonify({'error': '문서를 찾을 수 없습니다'}), 404

    job_result = db.table('ingestion_jobs').select('*').eq(
        'source_id', source_id
    ).order('started_at', desc=True).limit(1).execute()

    payload = result.data[0]
    payload['latest_job'] = job_result.data[0] if job_result.data else None
    return jsonify(payload), 200

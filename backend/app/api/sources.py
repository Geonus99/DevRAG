from flask import Blueprint, request, jsonify
from models.database import get_db
import uuid

sources_bp = Blueprint('sources', __name__)

# 문서 등록
@sources_bp.route('/sources', methods=['POST'])
def create_source():
    data = request.get_json()
    
    if not data.get('source_name'):
        return jsonify({'error': 'source_name은 필수입니다'}), 400
    if not data.get('source_type') in ['URL', 'PDF']:
        return jsonify({'error': 'source_type은 URL 또는 PDF여야 합니다'}), 400

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
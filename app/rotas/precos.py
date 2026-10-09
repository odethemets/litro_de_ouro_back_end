from flask import Blueprint, request, jsonify
import pymysql
from ..db import get_db_connection
from ..utils import token_obrigatorio

bp = Blueprint('precos', __name__)

@bp.route('/api/precos', methods=['POST'])
@token_obrigatorio
def registrar_preco(usuario_id_token):
    data = request.get_json()

    if not data or not data.get('posto_id') or not data.get('tipo_combustivel') or not data.get('preco'):
        return jsonify({"error": "Dados incompletos!"}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO registos_preco (posto_id, usuario_id, tipo_combustivel, preco, confianca_score, data_registro)
                VALUES (%s, %s, %s, %s, 1, NOW())
            """
            cursor.execute(sql, (data['posto_id'], usuario_id_token, data['tipo_combustivel'], data['preco']))
            conn.commit()
            
        return jsonify({"message": "Preço registado com sucesso por utilizador autenticado!"}), 201
    except pymysql.MySQLError as e:
        if conn: conn.rollback()
        return jsonify({"error": "Erro ao salvar o preço", "detalhes": str(e)}), 500
    finally:
        if conn: conn.close()
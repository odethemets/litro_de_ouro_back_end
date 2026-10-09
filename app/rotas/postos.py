from flask import Blueprint, jsonify
import pymysql
from ..db import get_db_connection
from flask import Blueprint, jsonify, request

bp = Blueprint('postos', __name__)

@bp.route('/', methods=['GET'])
def index():
    return jsonify({"projeto": "Litro de Ouro", "status": "online"}), 200

@bp.route('/api/postos', methods=['GET'])
def listar_postos():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome, endereco, bairro, cidade, uf, latitude, longitude FROM postos")
            postos = cursor.fetchall()
        return jsonify(postos), 200
    except pymysql.MySQLError as e:
        return jsonify({"error": "Erro ao procurar postos", "detalhes": str(e)}), 500
    finally:
        if conn: conn.close()
@bp.route('/api/postos/<int:posto_id>/precos', methods=['GET'])
def listar_precos_posto(posto_id):
    """
    O que faz: Retorna todo o histórico de preços de um posto específico.
    Como faz: Junta a tabela 'registos_preco' com a tabela 'usuarios' para sabermos quem registou.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # JOIN para cruzar os dados do preço com o nome do utilizador que o reportou
            sql = """
                SELECT 
                    rp.id AS registo_id, 
                    rp.tipo_combustivel, 
                    rp.preco, 
                    rp.data_registro, 
                    u.nome AS reportado_por
                FROM registos_preco rp
                JOIN usuarios u ON rp.usuario_id = u.id
                WHERE rp.posto_id = %s
                ORDER BY rp.data_registro DESC
            """
            cursor.execute(sql, (posto_id,))
            precos = cursor.fetchall()
            
            if not precos:
                return jsonify({"message": "Nenhum preço registado para este posto ainda."}), 404

        return jsonify(precos), 200

    except pymysql.MySQLError as e:
        return jsonify({"error": "Erro ao buscar os preços", "detalhes": str(e)}), 500
    finally:
        if conn: conn.close()
@bp.route('/api/postos/menor-preco', methods=['GET'])
def buscar_menor_preco():
    """
    O que faz: Procura os postos com o menor preço para um tipo específico de combustível.
    Como faz: Filtra recebendo 'tipo' pelo URL. Usa uma subquery (INNER JOIN) para garantir 
              que apenas o preço mais recente de cada posto seja considerado, evitando 
              mostrar preços antigos desatualizados.
    """
    # Lê o parâmetro 'tipo' do URL (ex: ?tipo=gasolina_comum)
    tipo_combustivel = request.args.get('tipo')

    if not tipo_combustivel:
        return jsonify({"error": "Informe o tipo de combustível. Exemplo de uso: /api/postos/menor-preco?tipo=gasolina_comum"}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Query Inteligente: Primeiro descobre a data máxima (mais recente) de cada posto.
            # Depois, junta com a tabela original para obter o preço dessa data exata, e finalmente ordena.
            sql = """
                SELECT 
                    p.id AS posto_id, 
                    p.nome, 
                    p.endereco, 
                    p.bairro, 
                    rp.preco, 
                    rp.data_registro 
                FROM postos p
                JOIN registos_preco rp ON p.id = rp.posto_id
                INNER JOIN (
                    SELECT posto_id, MAX(data_registro) as data_recente
                    FROM registos_preco
                    WHERE tipo_combustivel = %s
                    GROUP BY posto_id
                ) ultimos ON rp.posto_id = ultimos.posto_id AND rp.data_registro = ultimos.data_recente
                WHERE rp.tipo_combustivel = %s
                ORDER BY rp.preco ASC
            """
            
            # Passamos o tipo_combustivel duas vezes porque a query tem dois '%s'
            cursor.execute(sql, (tipo_combustivel, tipo_combustivel))
            resultados = cursor.fetchall()
            
            if not resultados:
                return jsonify({"message": f"Nenhum preço encontrado para {tipo_combustivel} neste momento."}), 404

        return jsonify(resultados), 200

    except pymysql.MySQLError as e:
        return jsonify({"error": "Erro ao procurar o menor preço", "detalhes": str(e)}), 500
    finally:
        if conn: conn.close()

        
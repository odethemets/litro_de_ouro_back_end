from flask import Blueprint, request, jsonify
import pymysql
from .db import get_db_connection # Importa a nossa função de conexão ao banco de dados

bp = Blueprint('main', __name__)

# ==========================================
# ROTA DE TESTE DA API
# ==========================================
@bp.route('/', methods=['GET'])
def index():
    # O que faz: Verifica se a API está online.
    # Como faz: Retorna um JSON simples com código HTTP 200 (OK).
    return jsonify({
        "projeto": "Litro de Ouro",
        "status": "online",
        "mensagem": "A API está a funcionar perfeitamente!"
    }), 200


# ==========================================
# ROTAS PARA POSTOS DE COMBUSTÍVEL
# ==========================================
@bp.route('/api/postos', methods=['GET'])
def listar_postos():
    """
    O que faz: Retorna a lista de todos os postos de combustível cadastrados no banco de dados.
    Como faz: Abre a conexão com o banco, executa um comando 'SELECT' na tabela 'postos' e devolve os dados convertidos em formato JSON.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Seleciona as colunas importantes dos postos
            sql = "SELECT id, nome, endereco, bairro, cidade, uf, latitude, longitude FROM postos"
            cursor.execute(sql)
            
            # Fetchall recolhe todos os resultados devolvidos pelo MySQL
            postos = cursor.fetchall()
            
        return jsonify(postos), 200

    except pymysql.MySQLError as e:
        # Se houver erro no banco, retorna erro 500 (Erro Interno do Servidor)
        return jsonify({"error": "Erro ao procurar postos no banco de dados", "detalhes": str(e)}), 500
    finally:
        # Fecha sempre a conexão no final, mesmo que ocorra um erro
        if conn:
            conn.close()


# ==========================================
# ROTAS PARA REGISTOS DE PREÇOS
# ==========================================
@bp.route('/api/precos', methods=['POST'])
def registrar_preco():
    """
    O que faz: Grava o registo de um novo preço para um combustível num posto específico.
    Como faz: Recebe os dados em JSON, valida se nada está em falta, e faz um INSERT no banco usando parâmetros (%s) para evitar ataques de injeção de SQL (SQL Injection).
    """
    data = request.get_json()

    # 1. Validação Básica: Verifica se o JSON foi enviado com todos os dados obrigatórios
    if not data or not data.get('posto_id') or not data.get('usuario_id') or not data.get('tipo_combustivel') or not data.get('preco'):
        return jsonify({"error": "Dados incompletos! É obrigatório enviar: posto_id, usuario_id, tipo_combustivel e preco."}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 2. Query Parametrizada (Segura)
            # O NOW() pega a data e hora atual do servidor automaticamente
            sql = """
                INSERT INTO registos_preco (posto_id, usuario_id, tipo_combustivel, preco, confianca_score, data_registro)
                VALUES (%s, %s, %s, %s, 1, NOW())
            """
            
            # 3. Execução da Query
            cursor.execute(sql, (
                data['posto_id'], 
                data['usuario_id'], 
                data['tipo_combustivel'], 
                data['preco']
            ))
            
            # 4. Confirmação (Commit)
            # Sem o commit, os dados não são realmente salvos no MySQL!
            conn.commit()
            
        return jsonify({"message": "Preço registado com sucesso!"}), 201

    except pymysql.MySQLError as e:
        # Se algo falhar, faz Rollback (cancela a operação)
        if conn:
            conn.rollback()
        return jsonify({"error": "Erro ao salvar o preço", "detalhes": str(e)}), 500
    finally:
        if conn:
            conn.close()
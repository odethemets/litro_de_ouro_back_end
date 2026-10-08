from flask import Blueprint, jsonify

# O que faz: 
#   Agrupa e define os URLs (endpoints) que o frontend vai chamar.
# Como faz: 
#   Utiliza a classe "Blueprint" do Flask para criar um mini-módulo de rotas chamado 'main'. O decorador "@bp.route" liga um URL específico (como '/') a uma função Python, que processa o pedido e retorna os dados convertidos para JSON através do "jsonify".

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    return jsonify({
        "projeto": "Litro de Ouro",
        "status": "online",
        "mensagem": "A API está a funcionar perfeitamente e pronta para receber requisições!"
    }), 200
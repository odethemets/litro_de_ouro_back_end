from flask import Flask
from flask_cors import CORS

# O que faz: 
#   Atua como a "fábrica" (App Factory) da nossa API. Configura o servidor Flask, ativa a segurança CORS e regista as rotas do projeto.
# Como faz: 
#   Instancia a classe Flask, passa essa instância para a biblioteca CORS (permitindo que o futuro aplicativo React Native consiga comunicar com esta API sem ser bloqueado pelos navegadores/sistemas móveis) e utiliza "register_blueprint" para acoplar os URLs separados noutros ficheiros.

def create_app():
    app = Flask(__name__)
    
    # Permite acessos de outras origens (Ex: App Mobile / Web Frontend)
    CORS(app) 

    # Importa as rotas locais e regista-as na aplicação
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
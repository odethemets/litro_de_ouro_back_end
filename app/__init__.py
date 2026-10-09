from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app) 

    # Importa os Blueprints dos ficheiros modulares
    from .rotas.auth import bp as auth_bp
    from .rotas.postos import bp as postos_bp
    from .rotas.precos import bp as precos_bp

    # Regista as rotas na aplicação principal
    app.register_blueprint(auth_bp)
    app.register_blueprint(postos_bp)
    app.register_blueprint(precos_bp)

    return app
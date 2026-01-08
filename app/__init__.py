
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Setup Extensions
    CORS(app)

    # Blueprints/Routes registrieren
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
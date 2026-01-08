
from flask import Flask
from flask_cors import CORS
from pythonjsonlogger import jsonlogger
import logging

def create_app():
    app = Flask(__name__)

    # Setup Extensions
    CORS(app)

    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    logHandler.setFormatter(formatter)
    app.logger.addHandler(logHandler)
    app.logger.setLevel(logging.INFO) #TODO: Configurable log level

    # Blueprints/Routes registrieren
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
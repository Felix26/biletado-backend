
"""Application factory and Flask initialization.

This module exposes 'create_app()' which builds and configures a Flask
application instance including logging, CORS, database integration and
route registration.
"""

from flask import Flask
from flask_cors import CORS
from pythonjsonlogger import jsonlogger
import logging
from .models import db
from .config import Config

from sqlalchemy import create_engine


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        Flask: A configured Flask application instance ready to be run.
    """
    app: Flask = Flask(__name__)

    # Setup extensions
    CORS(app)

    # Configure JSON logging handler
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    logHandler.setFormatter(formatter)
    app.logger.addHandler(logHandler)
    app.logger.setLevel(Config.LOG_LEVEL)

    # Blueprints/Routes registrieren
    from .routes import main_bp
    app.register_blueprint(main_bp)

    
    # 1. Connection String definieren
    # Format: postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
    db_url: str = Config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url

    db.init_app(app)

    # 2. Engine erstellen (Verwalter der Verbindung)
    app.engine = create_engine(db_url, connect_args={"connect_timeout": 2})

    return app
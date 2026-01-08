
from flask import Flask
from flask_cors import CORS
from pythonjsonlogger import jsonlogger
import logging
from .models import db

from sqlalchemy import create_engine

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

    
    # 1. Connection String definieren
    # Format: postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME
    db_url = "postgresql+psycopg://postgres:postgres@localhost:50000/reservations_v3" #TODO: Aus Konfiguration laden
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url

    db.init_app(app)

    # 2. Engine erstellen (Verwalter der Verbindung)
    app.engine = create_engine(db_url, connect_args={"connect_timeout": 2})

    return app
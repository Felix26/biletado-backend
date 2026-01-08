from flask import Blueprint, jsonify, make_response
import uuid

from .helpers import Helpers

main_bp = Blueprint('main', __name__)

# --- HELPER ---
def error_resp(code, msg, logUUID, status=400):
    if status in (400, 401, 404):
        return make_response(jsonify({}), status)
    return make_response(jsonify({
        "errors": [{"code": code, "message": msg}],
        "trace": str(logUUID)
    }), status)

@main_bp.route('/api/v3/reservations/status', methods=['GET'])
def get_status():
    return jsonify({"authors": ["Felix Miller", "Nik Wachsmann", "Ben Stahl"], "api_version": "3.0.0"})

@main_bp.route('/api/v3/reservations/health', methods=['GET'])
def get_health():
    # Check DB Connection
    try:
        Helpers.getDatabaseReady()
        return jsonify({
            "live": True,
            "ready": True,
            "databases": {
                "assets": {
                    "connected": True
                }
            }
        })
    except Exception as e:
        logUUID = uuid.uuid4()

        return error_resp("service_unavailable", "Database check failed", logUUID, 503)

@main_bp.route('/api/v3/reservations/health/live', methods=['GET'])
def get_liveness():
    # Eine Liveness-Probe prüft normalerweise, ob der Webserver antwortet. try-except ist hier etwas witzlos, wenn jsonify fehlschlägt, dann ist dem System gar nicht mehr zu helfen
    try:
        return jsonify({
            "live": True
        })
    except Exception as e:
        logUUID = uuid.uuid4()

        return error_resp("service_unavailable", "Liveness check failed", logUUID, 503)
    
@main_bp.route('/api/v3/reservations/health/ready', methods=['GET'])
def get_readiness():
    # Eine Readiness-Probe prüft, ob der Service bereit ist, Anfragen zu verarbeiten.
    # Hierzu gehört auch die Datenbank-Verbindung.
    try:
        Helpers.getDatabaseReady()
        return jsonify({
            "ready": True,
        })
    except Exception as e:
        logUUID = uuid.uuid4()

        return error_resp("service_unavailable", "Readiness check failed",logUUID, 503)
    





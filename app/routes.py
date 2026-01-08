from flask import Blueprint, jsonify, make_response
import uuid

main_bp = Blueprint('main', __name__)

# --- HELPER ---
def error_resp(code, msg, status=400):
    if status in (400, 401, 404):
        return make_response(jsonify({}), status)
    return make_response(jsonify({
        "errors": [{"code": code, "message": msg}],
        "trace": str(uuid.uuid4())
    }), status)
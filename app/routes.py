from flask import Blueprint, jsonify, make_response, current_app, request
import uuid
from datetime import datetime

from .helpers import Helpers
from .models import Reservation, db

main_bp = Blueprint('main', __name__)

# --- HELPER ---
def error_resp(code, msg, logUUID, status=400, more_info="not provided"):
    if status in (401):
        return make_response(jsonify({}), status)
    return make_response(jsonify({
        "errors": [{"code": code, "message": msg, "more_info": more_info}],
        "trace": str(logUUID)
    }), status)

@main_bp.route('/api/v3/reservations/status', methods=['GET'])
def get_status():
    return jsonify({"authors": ["Felix Miller", "Nik Wachsmann", "Ben Stahl"], "api_version": "3.0.0"})

@main_bp.route('/api/v3/reservations/health', methods=['GET'])
def get_health():
    # Check DB Connection
    try:
        readyness, db_error = Helpers.getDatabaseReady()
        if readyness:
            return jsonify({
                "live": True,
                "ready": True,
                "databases": {
                    "reservations": {
                        "connected": True
                    }
                }
            })
        else:
            raise Exception("Database not reachable: " + db_error)
        
    except Exception as e:
        logUUID = uuid.uuid4()

        current_app.logger.error("Health check failed", extra={
            "event.action": "health_check",
            "error.message": str(e),
            "trace.id": logUUID,
            "service.name": "reservations-api"
        })

        return error_resp("service_unavailable", "Database check failed", logUUID, 503, str(e))

@main_bp.route('/api/v3/reservations/health/live', methods=['GET'])
def get_liveness():
    # Eine Liveness-Probe prüft normalerweise, ob der Webserver antwortet. try-except ist hier etwas witzlos, wenn jsonify fehlschlägt, dann ist dem System gar nicht mehr zu helfen
    try:
        return jsonify({
            "live": True
        })
    except Exception as e:
        logUUID = uuid.uuid4()

        current_app.logger.error("Liveness check failed", extra={
            "event.action": "health_check",
            "error.message": str(e),
            "trace.id": logUUID,
            "service.name": "reservations-api"
        })

        return error_resp("service_unavailable", "Liveness check failed", logUUID, 503)
    
@main_bp.route('/api/v3/reservations/health/ready', methods=['GET'])
def get_readiness():
    # Eine Readiness-Probe prüft, ob der Service bereit ist, Anfragen zu verarbeiten.
    # Hierzu gehört auch die Datenbank-Verbindung.
    try:
        readyness, db_error = Helpers.getDatabaseReady()
        if readyness:
            return jsonify({
                "ready": True,
            })
        else:
            raise Exception("Database not ready: " + db_error)
        
    except Exception as e:
        logUUID = uuid.uuid4()

        current_app.logger.error("Readiness check failed", extra={
            "event.action": "health_check",
            "error.message": str(e),
            "trace.id": logUUID,
            "service.name": "reservations-api"
        })

        return error_resp("service_unavailable", "Readiness check failed",logUUID, 503, str(e))
    


@main_bp.route('/api/v3/reservations/reservations', methods=['GET'])
def get_reservations():
    results = []
    try:
        # Query Params
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        room_id = request.args.get('room_id')
        before = request.args.get('before')
        after = request.args.get('after')
        
        query = Reservation.query

        if not include_deleted:
            query = query.filter(Reservation.deleted_at == None)
        
        if room_id:
            query = query.filter(Reservation.room_id == room_id)

        if after:
            after_date = datetime.fromisoformat(after).date()
            query = query.filter(Reservation.end_date > after_date)

        if before:
            before_date = datetime.fromisoformat(before).date()
            query = query.filter(Reservation.start_date < before_date)

        results = [r.to_dict() for r in query.all()]
        return jsonify({"reservations": results})
    
    except Exception as e:
        logUUID = uuid.uuid4()

        current_app.logger.error("Error fetching reservations", extra={
            "event.action": "get_reservations",
            "error.message": str(e),
            "trace.id": logUUID,
            "service.name": "reservations-api"
        })

        return error_resp("internal_error", "Error fetching reservations", logUUID, 500, str(e))

@main_bp.route('/api/v3/reservations/reservations', methods=['POST'])
def create_reservation():
    data = request.json
    try:
        req_from = datetime.fromisoformat(data['from']).date()
        req_to = datetime.fromisoformat(data['to']).date()
        room_id = uuid.UUID(data['room_id'])
        
        if req_from >= req_to:
            return error_resp("bad_request", "From must be before To", str(uuid.uuid4()), 400, "'from' date must be before 'to' date")
    except (KeyError, ValueError, TypeError) as e:
        return error_resp("bad_request", "Invalid Input", str(uuid.uuid4()), 400, str(e))

    # Overlap Check via DB (SQLAlchemy)
    overlap = Reservation.query.filter(
        Reservation.room_id == room_id,
        Reservation.deleted_at == None,
        Reservation.start_date < req_to,
        Reservation.end_date > req_from
    ).first()

    if overlap:
        return error_resp("bad_request", "Overlap detected", str(uuid.uuid4()), 400, "The requested reservation overlaps with an existing reservation.")

    new_res = Reservation(
        room_id=room_id,
        start_date=req_from,
        end_date=req_to
    )
    db.session.add(new_res)
    db.session.commit()

    current_app.logger.info("Reservation created", extra={
        "action": "CREATE",
        "object_type": "reservation",
        "object_id": new_res.id,
        "user_id": getattr(request, 'user_id', 'anonymous')
    })

    resp = make_response(jsonify(new_res.to_dict()), 201)
    resp.headers['Location'] = f"/api/v3/reservations/reservations/{new_res.id}"
    return resp

@main_bp.route('/api/v3/reservations/reservations/<string:res_id>', methods=['GET'])
def get_reservation(res_id):
    try:
        valid_uuid = uuid.UUID(res_id)
    except ValueError:
        # Ungültige UUID
        return error_resp("not_found", "Not found", 404)

    res = Reservation.query.get(valid_uuid)
    
    if not res:
        # Ungültige Reservation ID
        return error_resp("not_found", "Not found", 404)
        
    return jsonify(res.to_dict())
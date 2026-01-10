from flask import Blueprint, jsonify, make_response, current_app, request
import uuid
from datetime import datetime

from .helpers import Helpers
from .models import Reservation, db
from .auth import require_auth

main_bp = Blueprint('main', __name__)

# --- HELPER ---
def error_resp(code, msg, logUUID, status=400, more_info="not provided"):
    if status == 401:
        return make_response(jsonify({}), status)
    return make_response(jsonify({
        "errors": [{"code": code, "message": msg, "more_info": more_info}],
        "trace": str(logUUID)
    }), status)

# --- ROUTES ---
# --- STATUS AND HEALTHCHECK ENDPOINTS ---

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
    

# --- RESERVATIONS ENDPOINTS ---

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
        "event.action": "create",
        "resource.type": "reservation",
        "resource.id": str(new_res.id),
        "user.id": getattr(request, 'user_id', 'anonymous'),
        "service.name": "reservations-api"
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
        return error_resp("not_found", "Not found", str(uuid.uuid4()), 404)

    res = Reservation.query.get(valid_uuid)
    
    if not res:
        # Ungültige Reservation ID
        return error_resp("not_found", "Not found", str(uuid.uuid4()), 404)
        
    return jsonify(res.to_dict())

@main_bp.route('/api/v3/reservations/reservations/<string:res_id>', methods=['PUT'])
#TODO: Auth
def update_reservation(res_id):
    data = request.json
    try:
        valid_uuid = uuid.UUID(res_id)
    except ValueError:
        return error_resp("not_found", "Invalid reservation UUID", str(uuid.uuid4()), 400)
    

    wants_restore = ("deleted_at" in data and data["deleted_at"] is None)

    existing = Reservation.query.get(valid_uuid)
    if not existing or (existing.deleted_at and not wants_restore):
        return error_resp("not_found", "Not found", str(uuid.uuid4()), 400, "Reservation does not exist or is deleted.")
    
    # Wenn restore gewünscht und Reservation existiert & ist deleted:
    if existing is not None and existing.deleted_at is not None and wants_restore:
        # Spec: Prototype muss enthalten sein
        for k in ("room_id", "from", "to"):
            if k not in data:
                return error_resp("bad_request", "Prototype required to restore (room_id, from, to)", str(uuid.uuid4()), 400)
            
    # Die Reservierung existiert (ggf. gelöscht), aber ein Update ist gewünscht
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
        Reservation.end_date > req_from,
    )

    # Wenn Update einer bestehenden Reservation, diese von Overlap ausschließen
    if existing and existing.deleted_at is None:
        overlap = overlap.filter(Reservation.id != existing.id)

    overlap = overlap.first()
    if overlap:
        return error_resp("bad_request", "Overlap detected", str(uuid.uuid4()), 400, "The requested reservation overlaps with an existing reservation.")
    
    # Alle Checks bestanden, Update durchführen. Differenziere zwischen Update und Create
    created = False
    if existing is None:
        created = True
        res = Reservation(id=valid_uuid)
        db.session.add(existing)
    else:
        res = existing

    # Update Felder
    res.room_id = room_id
    res.start_date = req_from
    res.end_date = req_to

    # Wenn restore gewünscht
    if wants_restore:
        res.deleted_at = None

    db.session.commit()

    # Antwort und Audit Log
    if created: action = "CREATE"
    if wants_restore: action = "RESTORE"
    else: action = "UPDATE"

    current_app.logger.info(f"Reservation {action.lower()}d", extra={
        "event.action": action,
        "resource.type": "reservation",
        "resource.id": str(res.id),
        "user.id": getattr(request, 'user_id', 'anonymous'),
        "service.name": "reservations-api"
        })

    resp = make_response(jsonify(res.to_dict()), 200 if not created else 201)
    if created:
        resp.headers['Location'] = f"/api/v3/reservations/reservations/{res.id}"
    return resp

@main_bp.route('/api/v3/reservations/reservations/<string:res_id>', methods=['DELETE'])
@require_auth
def delete_reservation(res_id):
    permanent = request.args.get('permanent', 'false').lower() == 'true'
    try:
        uuid_res_id = uuid.UUID(res_id)
    except (ValueError, AttributeError):
        return error_resp("invalid_id", "Reservation ID is not a valid UUID", str(uuid.uuid4()), 400)
    res = Reservation.query.get(uuid_res_id)

    if not res or (res.deleted_at and not permanent):
         return error_resp("not_found", "Not found", str(uuid.uuid4()), 404)

    if permanent:
        db.session.delete(res)
        action = "DELETE_PERMANENT"
    else:
        res.deleted_at = Helpers.get_current_time()
        action = "SOFT_DELETE"
    
    db.session.commit()

    # Audit Log
    current_app.logger.info("Reservation deleted", extra={
        "event.action": action,
        "resource.type": "reservation",
        "resource.id": str(res_id),
        "user.id": getattr(request, 'user_id', request.user_id),
        "service.name": "reservations-api"
    })

    return '', 204


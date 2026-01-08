import uuid
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()

def get_current_time():
    return datetime.now(timezone.utc)

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = db.Column(UUID(as_uuid=True), nullable=False)
    
    start_date = db.Column("from", db.Date, nullable=False)
    end_date = db.Column("to", db.Date, nullable=False)
    
    deleted_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        res = {
            "id": str(self.id),
            "room_id": str(self.room_id),
            "from": self.start_date.isoformat(),
            "to": self.end_date.isoformat(),
        }
        if self.deleted_at:
            res["deleted_at"] = self.deleted_at.isoformat()
        return res
"""Database model for reservations.

This module provides the SQLAlchemy instance, a small helper that
returns the current UTC timestamp, and the 'Reservation' model.
"""

import uuid
from datetime import datetime, timezone, date
from typing import Optional, Dict, Any
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()


def get_current_time() -> datetime:
    """Return the current time in UTC.

    Returns:
        datetime: A timezone-aware 'datetime' object in UTC.
    """
    return datetime.now(timezone.utc)


class Reservation(db.Model):
    """Represents a room reservation in the database.

    Attributes:
        id (UUID): Primary key for the reservation.
        room_id (UUID): Reference to the room (UUID).
        start_date (date): Reservation start date (column "from").
        end_date (date): Reservation end date (column "to").
        deleted_at (datetime | None): Deletion timestamp, if soft-deleted.
    """

    __tablename__ = 'reservations'

    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id: uuid.UUID = db.Column(UUID(as_uuid=True), nullable=False)
    
    start_date: date = db.Column("from", db.Date, nullable=False)
    end_date: date = db.Column("to", db.Date, nullable=False)
    
    deleted_at: Optional[datetime] = db.Column(db.DateTime, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a serializable dictionary.

        Date and time fields are returned as ISO-8601 strings.

        Returns:
            dict: Representation of the reservation with keys
                'id', 'room_id', 'from', 'to' and optionally 'deleted_at'.
        """
        res = {
            "id": str(self.id),
            "room_id": str(self.room_id),
            "from": self.start_date.isoformat(),
            "to": self.end_date.isoformat(),
        }
        if self.deleted_at:
            res["deleted_at"] = self.deleted_at.isoformat()
        return res
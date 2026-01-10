"""Helper utilities for infrastructure and DB checks.

This module provides small helpers that e.g. verify the database
connection is available and a central time helper.
"""

from typing import Tuple

from flask import current_app
from sqlalchemy import text, select
from datetime import datetime, timezone

from .models import Reservation, db


class Helpers:
    """Collection of small helper routines.

    Methods are defined as '@staticmethod' because they do not require
    access to instance or class state.
    """

    @staticmethod
    def getDatabaseReady() -> Tuple[bool, str]:
        """Check whether the database connection is available.

        Executes a simple, safe SQL statement ('SELECT 1') and returns a
        tuple containing a boolean success flag and an error message
        (empty string on success).

        Returns:
            Tuple[bool, str]: '(ready, message)' — 'message' is empty on success.
        """
        try:
            with current_app.engine.connect().execution_options(timeout=2) as connection:
                # Ein sicheres SQL-Statement ausführen
                connection.execute(text("SELECT 1"))
                connection.close()
                return True, ""
        except Exception as e:
            return False, str(e)

    # def get_any_reservation():
    #     # 1. Abfrage für bis zu 4 Einträge
    #     stmt = select(Reservation).limit(4)
        
    #     # 2. Ausführen
    #     # .all() gibt IMMER eine Liste zurück (z.B. [ReservationA, ReservationB])
    #     reservations = db.session.execute(stmt).scalars().all()
        
    #     # 3. Testen ob was zurückkam
    #     if reservations:
    #         # WICHTIG: Wir müssen über die Liste iterieren und jedes einzelne
    #         # Objekt in ein Dict umwandeln!
    #         return {"reservations": [res.to_dict() for res in reservations]}
    #     else:
    #         return {"message": "Datenbank ist leer"}

    @staticmethod
    def get_current_time() -> datetime:
        """Return the current time in UTC.

        Returns:
            datetime: timezone-aware 'datetime' in UTC.
        """
        return datetime.now(timezone.utc)
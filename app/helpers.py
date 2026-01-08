from flask import current_app
from sqlalchemy import text, select

from .models import Reservation, db

class Helpers:

    def getDatabaseReady():
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
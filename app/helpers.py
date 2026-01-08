from flask import current_app
from sqlalchemy import text

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
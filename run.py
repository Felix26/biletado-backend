"""Application entrypoint used for local execution.

This module loads environment variables, creates the Flask application
using the application factory and runs the development server when the
module is executed directly.
"""

from dotenv import load_dotenv
from typing import NoReturn

from flask import Flask

load_dotenv()

from app import create_app
from app.config import Config


# Create the Flask application using the factory.
app: Flask = create_app()


def _run() -> NoReturn:
    """Run the Flask development server.

    This wrapper exists to provide a typed function that starts the
    server when run as a script.
    """
    app.run(host="0.0.0.0", port=Config.SERVER_PORT, debug=Config.DEBUG_SERVER)


if __name__ == "__main__":
    _run()
"""Application configuration.

This module exposes central configuration values for the application.
Values are primarily read from environment variables and converted to
appropriate Python types. The 'Config' class acts as a container for
these constants (suitable for Flask app configuration).
"""

import os
from typing import ClassVar


class Config:
    """Container for application configuration.

    Attributes are annotated as class variables so type-checkers and IDEs
    can infer expected types. Values are initialized from environment
    variables at import time.
    """

    POSTGRES_RESERVATIONS_DBNAME: ClassVar[str] = os.getenv(
        "POSTGRES_RESERVATIONS_DBNAME", "reservations_v3"
    )
    POSTGRES_RESERVATIONS_HOST: ClassVar[str] = os.getenv(
        "POSTGRES_RESERVATIONS_HOST", "localhost"
    )
    POSTGRES_RESERVATIONS_USER: ClassVar[str] = os.getenv(
        "POSTGRES_RESERVATIONS_USER", "postgres"
    )
    POSTGRES_RESERVATIONS_PASSWORD: ClassVar[str] = os.getenv(
        "POSTGRES_RESERVATIONS_PASSWORD", "postgres"
    )
    POSTGRES_RESERVATIONS_PORT: ClassVar[str] = os.getenv(
        "POSTGRES_RESERVATIONS_PORT", "5432"
    )

    SQLALCHEMY_DATABASE_URI: ClassVar[str] = (
        f"postgresql+psycopg://{POSTGRES_RESERVATIONS_USER}:{POSTGRES_RESERVATIONS_PASSWORD}@{POSTGRES_RESERVATIONS_HOST}:{POSTGRES_RESERVATIONS_PORT}/{POSTGRES_RESERVATIONS_DBNAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS: ClassVar[bool] = False

    LOG_LEVEL: ClassVar[str] = os.getenv("LOG_LEVEL", "INFO").upper()

    DEBUG_SERVER: ClassVar[bool] = os.getenv("DEBUG_SERVER", "False").lower() in (
        "true",
        "1",
        "t",
    )

    SERVER_PORT: ClassVar[int] = int(os.getenv("SERVER_PORT", 9099))

    # Keycloak Konfiguration
    KEYCLOAK_HOST: ClassVar[str] = os.getenv("KEYCLOAK_HOST", "localhost:9090")
    KEYCLOAK_REALM: ClassVar[str] = os.getenv("KEYCLOAK_REALM", "biletado")

    KEYCLOAK_URL: ClassVar[str] = f"http://{KEYCLOAK_HOST}/auth/realms/{KEYCLOAK_REALM}"
    KEYCLOAK_CERTS_URL: ClassVar[str] = (
        f"http://{KEYCLOAK_HOST}/auth/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
    )
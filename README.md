# biletado-backend

## Configuration

The application reads configuration from environment variables (defaults shown). These can be set by a .env file and will be read on program start.

- **POSTGRES_RESERVATIONS_DBNAME**: `reservations_v3` — Postgres database name used for reservations.
- **POSTGRES_RESERVATIONS_HOST**: `localhost` — Postgres host.
- **POSTGRES_RESERVATIONS_USER**: `postgres` — Postgres user.
- **POSTGRES_RESERVATIONS_PASSWORD**: `postgres` — Postgres password.
- **POSTGRES_RESERVATIONS_PORT**: `5432` — Postgres port.

- **LOG_LEVEL**: `INFO` — Logging level (e.g. INFO, WARNING, ERROR).
- **DEBUG_SERVER**: `False` — When `true` enables debug mode for the server.
- **SERVER_PORT**: `80` — Port the server binds to.
- **KEYCLOAK_HOST**: `localhost:9090` — Host (and port) for Keycloak.
- **KEYCLOAK_REALM**: `biletado` — Keycloak realm used by the application.
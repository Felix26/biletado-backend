# biletado-backend

## Configuration

The application reads configuration from environment variables (defaults shown). These can be set by a .env file and will be read on program start.

- **POSTGRES_RESERVATIONS_DBNAME**: `reservations_v3` — Postgres database name used for reservations.
- **POSTGRES_RESERVATIONS_HOST**: `postgres` — Postgres host.
- **POSTGRES_RESERVATIONS_USER**: `postgres` — Postgres user.
- **POSTGRES_RESERVATIONS_PASSWORD**: `postgres` — Postgres password.
- **POSTGRES_RESERVATIONS_PORT**: `5432` — Postgres port.

- **LOG_LEVEL**: `INFO` — Logging level (e.g. INFO, WARNING, ERROR).
- **DEBUG_SERVER**: `False` — When `true` enables debug mode for the server.
- **SERVER_PORT**: `80` — Port the server binds to.
- **KEYCLOAK_HOST**: `keycloak:9090` — Host (and port) for Keycloak.
- **KEYCLOAK_REALM**: `biletado` — Keycloak realm used by the application.

## Version Control
https://github.com/Felix26/biletado-backend

## Image
ghcr.io/felix26/biletado-backend:latest


## Container-Image erzeugen

Voraussetzungen: Docker installiert, Repository neu geclont (damit keine .venv/etc dabei sind)

Build lokal mit Dockerfile:
```bash
podman build -t biletado-backend:latest .
```
## Integration

- .env-Datei schreiben
z.B.:
```bash
KEYCLOAK_HOST: keycloak:9090
KEYCLOAK_REALM: biletado
POSTGRES_RESERVATIONS_USER: postgres
POSTGRES_RESERVATIONS_PASSWORD: postgres
POSTGRES_RESERVATIONS_DBNAME: reservations_v3
POSTGRES_RESERVATIONS_HOST: postgres
POSTGRES_RESERVATIONS_PORT: 5432
```

- Deploy

```bash
kubectl apply -k . --prune -l app.kubernetes.io/part-of=biletado -n biletado
kubectl wait pods -n biletado -l app.kubernetes.io/part-of=biletado --for condition=Ready --timeout=120s
```
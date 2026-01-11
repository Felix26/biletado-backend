# biletado-backend

## Antworten aus dem Vorab-Fragebogen:
- Gruppenname: Finesse-Ja
- Gruppenteilnehmer: Ben Stahl, Felix Miller, Nik Wachsmann
- Sprache und Framework: Python 3.13 mit Flask 3.1.2

## Configuration

The application reads configuration from environment variables (defaults shown). These can be set by a .env file and will be read on program start.

- **POSTGRES_RESERVATIONS_DBNAME**=`reservations_v3` — Postgres database name used for reservations.
- **POSTGRES_RESERVATIONS_HOST**=`postgres` — Postgres host.
- **POSTGRES_RESERVATIONS_USER**=`postgres` — Postgres user.
- **POSTGRES_RESERVATIONS_PASSWORD**=`postgres` — Postgres password.
- **POSTGRES_RESERVATIONS_PORT**=`5432` — Postgres port.

- **LOG_LEVEL**=`INFO` — Logging level (e.g. INFO, WARNING, ERROR).
- **DEBUG_SERVER**=`False` — When `true` enables debug mode for the server.
- **SERVER_PORT**=`9099` — Port the server binds to.
- **KEYCLOAK_HOST**=`keycloak:9090` — Host (and port) for Keycloak.
- **KEYCLOAK_REALM**=`biletado` — Keycloak realm used by the application.

## Version Control
https://github.com/Felix26/biletado-backend

## Image
ghcr.io/felix26/biletado-backend:latest
Auffindbar unter https://github.com/Felix26/biletado-backend/pkgs/container/biletado-backend

## Integration

- .env-Datei schreiben
z.B.:
```bash
KEYCLOAK_HOST=keycloak:9090
KEYCLOAK_REALM=biletado
POSTGRES_RESERVATIONS_USER=postgres
POSTGRES_RESERVATIONS_PASSWORD=postgres
POSTGRES_RESERVATIONS_DBNAME=reservations_v3
POSTGRES_RESERVATIONS_HOST=postgres
POSTGRES_RESERVATIONS_PORT=5432
```

- Deploy

```bash
kubectl apply -k . --prune -l app.kubernetes.io/part-of=biletado -n biletado
kubectl wait pods -n biletado -l app.kubernetes.io/part-of=biletado --for condition=Ready --timeout=120s
```
## Test-Automation
Bei jedem Push wird ein automatischer Test über GitHub Actions ausgeführt. Ausgeführt werden die Tests unter https://github.com/Felix26/biletado-backend/tree/main/tests.

## Build-Automation
Unter oben angegebenem Link wird bei jedem Push mit durchlaufenden Tests das Image neu gebaut.

## Container-Image erzeugen

Voraussetzungen=Docker installiert, Repository neu geclont (damit keine .venv/etc dabei sind)

Build lokal mit Dockerfile:
```bash
podman build -t biletado-backend:latest .
```
# biletado-backend

## Container-Image erzeugen

Voraussetzungen: Docker installiert, Repository neu geclont (damit keine .venv/etc dabei sind)

Build lokal:
```bash
podman build -t biletado-backend:latest .
```
## Integration

- .env-Datei schreiben
z.B.:
```bash
KEYCLOAK_HOST: keycloak
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

# --- STAGE 1: Build ---
FROM python:3.13-slim as builder

WORKDIR /app

# 1. Venv erstellen
RUN python -m venv /opt/venv
# 2. Venv aktivieren (für den Build-Prozess)
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# 3. Abhängigkeiten INS Venv installieren
# (Kein --user nötig, da wir im venv sind)
RUN pip install --no-cache-dir -r requirements.txt

# --- STAGE 2: Runtime ---
FROM python:3.13-slim

WORKDIR /app

# 1. Das fertige Venv aus Stage 1 kopieren
COPY --from=builder /opt/venv /opt/venv

# 2. Venv global aktivieren
# Damit nutzt der Befehl "python" automatisch die Pakete in /opt/venv
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Code kopieren
COPY . .

# Security: User anlegen
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 9099

CMD ["python", "run.py"]
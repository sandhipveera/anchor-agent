# Anchor backend — Cloud Run container.
# Build context is backend/. Cloud Run sets $PORT (default 8080); we bind it.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8080

# --no-access-log: disable per-request access logging (ARCHITECTURE.md §7).
# Logging is further configured in app.logging_config (PII scrub + no uvicorn.access).
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --no-access-log"]

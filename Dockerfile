# Multi-stage Dockerfile for Daily Hadith (FastAPI)

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

COPY app.py db_utils.py db_seed_samples.py seed_hadiths.py README.md requirements.txt ./
COPY templates ./templates
COPY static ./static

# Include CSV source files (e.g. Sahih al-Bukhari.csv) inside the image
# so the seeding script can run inside the container if needed.
COPY *.csv ./ 

# Directory for SQLite database file (can be backed by a Docker volume).
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


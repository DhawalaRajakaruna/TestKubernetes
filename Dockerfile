# ---------- Builder ----------
FROM python:3.10-slim AS builder

WORKDIR /install
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ---------- Runtime ----------
FROM python:3.10-slim

WORKDIR /app

# Copy installed dependencies
COPY --from=builder /install /usr/local

# Copy application source code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

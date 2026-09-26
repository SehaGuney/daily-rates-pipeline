# Base: application dependencies and code
FROM python:3.11-slim AS base
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .

# Test: install dev dependencies and run the test suite
FROM python:3.11-slim AS test
WORKDIR /src
COPY requirements-dev.txt .
COPY app/ app/
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests/ tests/
RUN python -m pytest -v

# Runtime: final image served by gunicorn
FROM base AS runtime
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]

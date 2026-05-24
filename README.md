# Daily Rates Pipeline

An automated data pipeline that fetches daily EUR exchange rates, stores them as artifacts, and exposes the latest report via a REST API.

## Architecture

```
Airflow DAG (daily @ 09:00)
    └── Fetch EUR rates from external API
    └── Save as CSV + JSON artifact
    └── Trigger Jenkins CI job

Flask API
    └── GET /latest-report  →  serves the most recent JSON report
    └── GET /health         →  health check

Jenkins Pipeline
    └── Checkout
    └── Docker build & tag
    └── Run container test
    └── Deploy
```

## Stack

| Layer | Technology |
|---|---|
| Orchestration | Apache Airflow 2.6.2 |
| API | Flask (Python) |
| CI/CD | Jenkins |
| Containerization | Docker, Docker Compose |
| Database | PostgreSQL (Airflow backend) |
| Message Broker | Redis |

## Running Locally

```bash
docker-compose up -d
```

Services:

| Service | URL |
|---|---|
| Airflow UI | http://localhost:8082 |
| Flask API | http://localhost:5000 |
| Jenkins | http://localhost:8081 |

## API Endpoints

```
GET /                → lists available endpoints
GET /health          → returns service status
GET /latest-report   → returns the most recent exchange rate report
```

Example response from `/latest-report`:

```json
{
  "date": "2025-07-10",
  "min": 0.82,
  "max": 154.3,
  "avg": 18.7
}
```

## Airflow DAG

- **DAG ID:** `daily_rates`
- **Schedule:** Every day at 09:00
- **Tasks:**
  1. `fetch_and_report` — fetches EUR rates, writes CSV and JSON to `artifacts/`
  2. `trigger_ci` — triggers Jenkins build via HTTP

## Project Structure

```
├── app/
│   ├── app.py              # Flask API
│   └── requirements.txt
├── dags/
│   └── daily_rates.py      # Airflow DAG
├── Dockerfile              # Flask app image
├── Dockerfile.jenkins      # Jenkins image with Docker support
├── Jenkinsfile             # CI/CD pipeline
└── docker-compose.yml      # Full stack
```

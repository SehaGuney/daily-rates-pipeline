# Daily Rates Pipeline

An automated data pipeline that fetches daily EUR exchange rates, stores them as report artifacts, serves the latest report through a REST API, and triggers a Jenkins CI pipeline that tests, builds and verifies the API image.

Built during my DevOps internship as a research task, to learn how orchestration, CI and containerized services work together.

## Architecture

```
Airflow DAG: daily_rates (every day at 09:00 UTC)
    │
    ├── fetch_and_report (PythonOperator)
    │       ├── Fetches EUR rates (USD, GBP, TRY, JPY, CHF) from the Frankfurter API
    │       └── Writes rates_<date>.csv and report_<date>.json to artifacts/
    │
    └── trigger_ci (SimpleHttpOperator)
            └── Triggers the Jenkins job through its REST API

Flask API (gunicorn)
    ├── GET /               → service info
    ├── GET /health         → health check
    └── GET /latest-report  → most recent report from artifacts/

Jenkins pipeline (Jenkinsfile)
    ├── Checkout
    ├── Test        → runs pytest in the "test" stage of the Dockerfile
    ├── Build       → builds the runtime image, tagged with the build number
    └── Smoke Test  → starts the image and checks /health
```

Airflow and the Flask API share the `artifacts/` directory: Airflow writes reports, the API reads the newest one.

## Stack

| Layer | Technology |
|---|---|
| Orchestration | Apache Airflow 2.6.2 (LocalExecutor) |
| Data source | [Frankfurter API](https://frankfurter.dev) (European Central Bank rates) |
| API | Flask, gunicorn |
| Tests | pytest |
| CI | Jenkins |
| Containerization | Docker (multi-stage build), Docker Compose |
| Airflow backend | PostgreSQL 13 |

## Running Locally

### 1. Configure environment variables

```bash
cp .env.example .env
```

Generate a Fernet key and paste it into `AIRFLOW__CORE__FERNET_KEY` in `.env`:

```bash
docker run --rm apache/airflow:2.6.2 python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Replace every `change_me` value with your own password. The `.env` file is ignored by Git.

### 2. Start the stack

```bash
docker compose up -d --build
```

The `airflow-init` service runs first: it waits for PostgreSQL, runs the database migrations and creates the Airflow admin user.

| Service | URL | Login |
|---|---|---|
| Airflow UI | http://localhost:8082 | `_AIRFLOW_WWW_USER_*` values from `.env` |
| Flask API | http://localhost:5001 | none |
| Jenkins | http://localhost:8081 | see step 3 |

The API is published on port **5001** because port 5000 is used by AirPlay Receiver on macOS.

### 3. Set up Jenkins

1. Open Jenkins, go to **Manage Jenkins → Security** and set **Security Realm** to "Jenkins' own user database".
2. Create a user under **Manage Jenkins → Users**.
3. Back in **Security**, set **Authorization** to "Logged-in users can do anything" and disable anonymous read access.
4. Create a **Pipeline** job named `daily-rates-pipeline`:
   - Definition: Pipeline script from SCM
   - SCM: Git, repository URL of this repo, branch `*/main`
   - Script path: `Jenkinsfile`
5. Generate an API token under **your user → Security → API Token**.

### 4. Connect Airflow to Jenkins

Airflow reads connections from `AIRFLOW_CONN_*` environment variables. Set the Jenkins user and API token in `.env`:

```
AIRFLOW_CONN_JENKINS_API=http://JENKINS_USER:JENKINS_API_TOKEN@jenkins:8080
```

`jenkins` is the Compose service name, reachable from the Airflow containers. Recreate the Airflow containers to apply the change:

```bash
docker compose up -d --force-recreate airflow-webserver airflow-scheduler
```

### 5. Run the pipeline

```bash
docker compose exec airflow-scheduler airflow dags unpause daily_rates
docker compose exec airflow-scheduler airflow dags trigger daily_rates
```

Then check the result:

```bash
docker compose exec airflow-scheduler airflow dags list-runs -d daily_rates
curl http://localhost:5001/latest-report
```

### 6. Stop the stack

```bash
docker compose down        # stop containers, keep data
docker compose down -v     # stop containers and delete volumes
```

## API

Example response from `GET /latest-report`:

```json
{
  "base": "EUR",
  "date": "2026-09-26",
  "rate_date": "2026-09-25",
  "rates": {
    "CHF": 0.9445,
    "GBP": 0.86045,
    "JPY": 179.7,
    "TRY": 55.7975,
    "USD": 1.1403
  }
}
```

`date` is the Airflow run date. `rate_date` is the date of the published rates: the European Central Bank does not publish rates on weekends and holidays, so the latest business day is returned.

## Tests

The test suite covers the health endpoint, the latest-report logic (newest file wins) and error handling (missing and invalid reports).

Run the tests the same way Jenkins does:

```bash
docker build --target test .
```

## Project Structure

```
├── app/
│   ├── app.py              # Flask API
│   └── requirements.txt    # Runtime dependencies
├── dags/
│   └── daily_rates.py      # Airflow DAG
├── tests/
│   ├── conftest.py
│   └── test_app.py         # API tests
├── Dockerfile              # Multi-stage build: base, test, runtime
├── Dockerfile.jenkins      # Jenkins image with Docker CLI
├── Jenkinsfile             # CI pipeline
├── docker-compose.yml      # Airflow, PostgreSQL, API, Jenkins
├── requirements-dev.txt    # Test dependencies
└── .env.example            # Environment variable template
```

## Notes

- Jenkins uses the host Docker daemon through the mounted Docker socket. This is convenient for local development but gives the Jenkins container full control over Docker, so it is not a production setup.
- The pipeline has no deployment stage yet. The image is built and verified, but not pushed to a registry.

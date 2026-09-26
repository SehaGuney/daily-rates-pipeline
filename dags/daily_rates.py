import csv
import json
import os
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator

API_URL = "https://api.frankfurter.dev/v1/latest"
BASE_CURRENCY = "EUR"
CURRENCIES = ["USD", "GBP", "TRY", "JPY", "CHF"]
ARTIFACTS_DIR = os.environ.get("ARTIFACTS_DIR", "/opt/airflow/artifacts")


def fetch_and_report(ds, **_):
    """Fetch the latest EUR rates and write CSV + JSON artifacts for the run date."""
    response = requests.get(
        API_URL,
        params={"base": BASE_CURRENCY, "symbols": ",".join(CURRENCIES)},
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    rates = payload["rates"]

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    csv_path = os.path.join(ARTIFACTS_DIR, f"rates_{ds}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["currency", "rate"])
        writer.writerows(sorted(rates.items()))

    report = {
        "date": ds,
        "rate_date": payload["date"],
        "base": payload["base"],
        "rates": rates,
    }
    report_path = os.path.join(ARTIFACTS_DIR, f"report_{ds}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)


default_args = {
    "owner": "seha",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="daily_rates",
    description="Fetch daily EUR exchange rates and trigger CI",
    default_args=default_args,
    start_date=datetime(2025, 7, 1),
    schedule_interval="0 9 * * *",
    catchup=False,
) as dag:

    fetch = PythonOperator(
        task_id="fetch_and_report",
        python_callable=fetch_and_report,
    )

    trigger_ci = SimpleHttpOperator(
        task_id="trigger_ci",
        http_conn_id="jenkins_api",
        endpoint="job/daily-rates-pipeline/build",
        method="POST",
    )

    fetch >> trigger_ci

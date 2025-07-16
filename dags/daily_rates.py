from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from datetime import datetime, timedelta
import requests, csv, os

def fetch_and_report(**ctx):
    url = "https://api.exchangerate.host/latest?base=EUR"
    data = requests.get(url).json()["rates"]
    dt = ctx["ds"]
    os.makedirs("artifacts", exist_ok=True)
    csv_path = f"artifacts/rates_{dt}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["currency","rate"])
        for k,v in data.items():
            writer.writerow([k,v])
    rates = list(data.values())
    report = {
        "date": dt,
        "min": min(rates),
        "max": max(rates),
        "avg": sum(rates)/len(rates)
    }
    with open(f"artifacts/report_{dt}.json","w") as f:
        import json; json.dump(report,f)

def trigger_jenkins():
    # Airflow HTTP hook ile tetik; connection jenkins_api tanımlı olmalı
    from airflow.providers.http.operators.http import SimpleHttpOperator
    # (Or, burada requests ile direk çağrı da yapabiliriz)
    pass

with DAG(
    "daily_rates",
    start_date=datetime(2025,7,1),
    schedule_interval="0 9 * * *",
    catchup=False,
) as dag:

    fetch = PythonOperator(
        task_id="fetch_and_report",
        python_callable=fetch_and_report,
        provide_context=True,
    )

    trigger = SimpleHttpOperator(
        task_id="trigger_ci",
        http_conn_id="jenkins_api",
        endpoint="job/daily-rates-pipeline/build",
        method="POST",
        headers={"Content-Type":"application/json"},
    )

    fetch >> trigger

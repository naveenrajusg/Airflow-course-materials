from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor

from airflow.sensors.filesystem import FileSensor

from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "admin@localhost.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

from airflow.operators.python_operator import PythonOperator
import csv
import requests
import json

from airflow.operators.bash_operator import BashOperator

from airflow.providers.apache.hive.operators.hive import HiveOperator

from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

from airflow.operators.email import EmailOperator

from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.hooks.base_hook import BaseHook

def download_rates():
    BASE_URL = "https://gist.githubusercontent.com/naveenrajusg/497e10579edfe65fdf1c3d60a387fa20/raw/"
    ENDPOINTS = {
        'USD': 'api_forex_exchange_usd.json',
        'EUR': 'api_forex_exchange_eur.json'
    }
    with open('/opt/airflow/dags/files/forex_currencies.csv') as forex_currencies:
        reader = csv.DictReader(forex_currencies, delimiter=';')
        for idx, row in enumerate(reader):
            base = row['base']
            with_pairs = row['with_pairs'].split(' ')
            indata = requests.get(f"{BASE_URL}{ENDPOINTS[base]}").json()
            outdata = {'base': base, 'rates': {}, 'last_update': indata['date']}
            for pair in with_pairs:
                outdata['rates'][pair] = indata['rates'][pair]
            with open('/opt/airflow/dags/files/forex_rates.json', 'a') as outfile:
                json.dump(outdata, outfile)
                outfile.write('\n')

def _get_message() -> str:
    return "Hi from forex_data_pipeline"

with DAG("forex_data_pipeline", start_date=datetime(2023, 8 ,2),
    schedule_interval="@daily", default_args=default_args, catchup=True) as dag:
    is_forex_rates_available = HttpSensor(
        task_id="is_forex_rates_available",
        http_conn_id="forex_api",
        endpoint="naveenrajusg/497e10579edfe65fdf1c3d60a387fa20",
        response_check=lambda response: "rates" in response.text,
        poke_interval=5,
        timeout=20
    )

    is_forex_currencies_file_available = FileSensor(
        task_id="is_forex_currencies_file_available",
        fs_conn_id="forex_path",
        filepath="forex_currencies.csv",
        poke_interval=5,
        timeout=20
    )

    downloading_rates = PythonOperator(
            task_id="downloading_rates",
            python_callable=download_rates
    )

    saving_rates = BashOperator(
        task_id="saving_rates",
        bash_command="""
            hdfs dfs -mkdir -p /forex && \
            hdfs dfs -put -f $AIRFLOW_HOME/dags/files/forex_rates.json /forex
            """
    )

    creating_forex_rates_table = HiveOperator(
        task_id="creating_forex_rates_table",
        hive_cli_conn_id="hive_conn",
        hql="""
            CREATE EXTERNAL TABLE IF NOT EXISTS forex_rates(
                base STRING,
                last_update DATE,
                eur DOUBLE,
                usd DOUBLE,
                nzd DOUBLE,
                gbp DOUBLE,
                jpy DOUBLE,
                cad DOUBLE
                )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """
    )

    forex_processing = SparkSubmitOperator(
        task_id="forex_processing",
        application="/opt/airflow/dags/scripts/forex_processing.py",
        conn_id="spark_conn",
        verbose=False
    )

    send_email_notification = EmailOperator(
        task_id="send_email_notification",
        to="nsreeramarajugovinda@hawk.iit.edu",
        subject="forex_data_pipeline",
        html_content="<h3>forex_data_pipeline</h3>"
    )

    send_slack_notification = SlackWebhookOperator(
        task_id="send_slack_notification",
        http_conn_id="slack_conn",
        message=_get_message(),
        channel="#airflow"
    )


    is_forex_rates_available >> is_forex_currencies_file_available >> downloading_rates >> saving_rates
    saving_rates >> creating_forex_rates_table >> forex_processing
    forex_processing >> send_email_notification >> send_slack_notification
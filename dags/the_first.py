from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.decorators import task
import pandas as pd
from datetime import datetime 
from datetime import timedelta

def main():
    di = {'Texto': 'Hello World', 'Msg': 'Primeira dag feita'}
    df = pd.DataFrame([di])

    df.to_csv('./outputs/saida.csv')

with DAG(
    dag_id='SimpleDAG', 
    schedule_interval=timedelta(days=3),
    start_date=datetime.now()
) as dag: 
    t1 = PythonOperator(
        task_id = 'printdf',
        python_callable=main
    )

    t1
    
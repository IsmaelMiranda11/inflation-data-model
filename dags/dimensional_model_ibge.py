'''DAG script to create a dimensional model from IBGE data

'''

# Airflow imports
from airflow.models.dag import DAG
from airflow.models.dagrun import DagRun
from airflow.decorators import task, task_group
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.empty import EmptyOperator

# General imports
import pandas as pd
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from datetime import timedelta
import pendulum

# Folder project for imports
sys.path.insert(0, Path(__file__).parents[1].as_posix())
print(sys.path)

# ETL imports
from etl.ibge.dimensionals import dim_calendar, dim_categories, dim_cities
from etl.ibge.raw_table import raw_table
from etl.ibge.inflation import inflation

# This project was created in Lisbon
lisbon = pendulum.timezone('Europe/Lisbon') #type:ignore

# Tasks defaults arguments
default_args = {
    'owner': 'airflow',
    'execution_timeout': timedelta(minutes=60),
    'wait_for_downstream': True
}

# DAG
with DAG(
    dag_id='dimensional_model_ibge', # DAG name
    doc_md=Path(__file__).stem, # Documentation
    start_date=datetime(2019, 12, 5, tzinfo=lisbon), # Start date
    schedule='0 10 5 * *', # 5th day of the month at 10:00
    # catchup=True, # Run backfill at creation
    max_active_runs=1, # Only one run at a time
    render_template_as_native_obj=True, # Render template as native object

) as dag:

    start = EmptyOperator(task_id='start') #type: ignore

    # Dimensional task group
    @task_group(group_id='dimensionals')
    def dimensionals(dag_run: DagRun=None): #type: ignore

        @task(task_id='calendar')
        # print the execution date
        def calendar(**kwargs):
            period = kwargs['dag_run'].data_interval_end.strftime('%Y%m')
            dim_calendar(period=period) # Create the calendar dimension

        @task(task_id='categories')
        def categories():
            dim_categories()

        @task(task_id='cities')
        def cities():
            dim_cities()

        (
            calendar()
            >> categories()
            >> cities()
        ) #type: ignore

    @task_group(group_id='raw-table')
    def raw(): #type: ignore

        @task(task_id='raw-table')
        def raw(**kwargs):
            period = kwargs['dag_run'].data_interval_end.strftime('%Y%m')
            raw_table(period=period) # Create the raw table

        (
            raw()
        ) #type: ignore

    @task_group(group_id='fact-table')
    def fact(): #type: ignore

        @task(task_id='inflation')
        def inflation_table(**kwargs):
            period = kwargs['dag_run'].data_interval_end.strftime('%Y%m')
            inflation(period=period) # Create the inflation fact table

        (
            inflation_table()
        ) #type: ignore

    end = EmptyOperator(task_id='end') #type: ignore

    start >> dimensionals() >> raw() >> fact() >> end #type: ignore

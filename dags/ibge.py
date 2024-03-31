from airflow.models.dag import DAG
from airflow.models.taskinstance import TaskInstance
from airflow.models.dagrun import DagRun
from airflow.decorators import task, task_group

import pandas as pd
import requests
import json
import datetime
import os 
from pathlib import Path

os.chdir(
    f'{os.environ["AIRFLOW_HOME"]}/dags'
)
print(os.getcwd())

doc = open(f'./{Path(__file__).stem}.md', 'r').read()

with DAG(
    dag_id='dimensional_model_ibge',
    doc_md=doc,
    start_date=datetime.datetime(2022, 1, 1),
    schedule_interval='0 10 5 * *', #10:00 of day 5 of month,
    # sla_miss_callback=print('oi'),
    catchup=False
) as dag:

    # @task
    # def print_con(**context):
    #     print(context)
    #     print(context['ds_nodash'])

    @task_group(group_id='raw_data')
    def get_raw_data():
        @task(task_id='get_url')
        def ibge_url(**context):
            end_period = datetime.datetime.now().strftime('%Y%m')
            
            print(context['ds_nodash'])
            
            url = (
                "https://servicodados.ibge.gov.br/api/v3/"
                f"agregados/7060/periodos/202201-{end_period}"
                "/variaveis/63|69|2265|66?localidades=N1[all]"
                "&classificacao=315[all]"
            )
            
            return url

        def read_api_data(url):
            '''Read date from IBGE api'''
            res = requests.get(url)

            df = pd.DataFrame.from_dict(res.json())

            # with open('file.json', 'w') as f:
            #     f.write(res.text)

            print(df)
        
        # read_api_data(ibge_url())

        ibge_url()

    
    # @task
    # def print_ti_info(task_instance: TaskInstance | None = None, dag_run: DagRun | None = None):
    #     print(f"Run ID: {task_instance.run_id}")  # Run ID: scheduled__2023-08-09T00:00:00+00:00
    #     print(f"Duration: {task_instance.duration}")  # Duration: 0.972019
    #     print(f"DAG Run queued at: {dag_run.queued_at}")  # 2023-08-10 00:00:01+02:20
    
    get_raw_data()

    dag.test()
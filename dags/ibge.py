from airflow.models.dag import DAG
from airflow.models.taskinstance import TaskInstance
from airflow.models.dagrun import DagRun
from airflow.decorators import task, task_group
from airflow.timetables.events import EventsTimetable

from timetable import ScheduleCustom

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

import pandas as pd
import requests
import json
import datetime
import os 
from pathlib import Path
from datetime import timedelta
from datetime import datetime
import pendulum

from sqlalchemy import Column
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base
from sqlalchemy import select
from pandas import date_range

# Used links
# https://stackoverflow.com/questions/61528860/sqlalchemy-engine-from-airflow-database-hook


# Change folder to run at dags
os.chdir(
    f'{os.environ["AIRFLOW_HOME"]}/dags'
)
print(os.getcwd())

doc = open(f'./{Path(__file__).stem}.md', 'r').read()

# Project tables
Base = declarative_base()

class IBGE(Base):
    __tablename__ = '   '

    id = Column(type_=postgresql.INTEGER, primary_key=True)
    id_variavel = Column(name='ID Variável', type_=postgresql.INTEGER)
    variavel = Column(name='Variável', type_=postgresql.VARCHAR(40))
    unidade = Column(name='Unidade', type_=postgresql.VARCHAR(40))
    resultados = Column(name='Resultados', type_=postgresql.JSONB)

    def columns(self):
        return [c.name for c in self.__table__.columns if not c.primary_key] #type:ignore
    
    def fields_columns(self):
        return [f'"{c}"' for c in self.columns()]


# Project functions
def ibge_url(end_period):
    '''Function to get the URL from API'''
    # end_period = datetime.datetime.now().strftime('%Y%m')
    
    url = (
        "https://servicodados.ibge.gov.br/api/v3/"
        f"agregados/7060/periodos/202201-{end_period}"
        "/variaveis/63|69|2265|66?localidades=N1[all]"
        "&classificacao=315[all]"
    )
    
    return url

lisbon = pendulum.timezone('Europe/Lisbon') #type:ignore
# DAG
with DAG(
    dag_id='dimensional_model_ibge',
    doc_md=doc,
    start_date=datetime(2022, 1, 1, tzinfo=lisbon),
    schedule='0 10 1 * *',
    catchup=False
) as dag:

    # Ingestion task group
    @task_group(group_id='ingestion') 
    def get_raw_data():

        @task(task_id='create_table_db')
        def create_raw_igbe_table():
            '''Create the raw table in database defined previously'''

            # Use the sqlaclchemy default from connections
            engine = PostgresHook().get_sqlalchemy_engine()
            # Create the table with this engine
            Base.metadata.create_all(engine) #type:ignore
        
        @task(task_id='get_data_from_api')
        def read_api_data(**context):
            '''Read data from IBGE api'''
            
            # Get most updated data from IBGE based on schedule
            url = ibge_url(end_period=context['ds_nodash'][:-2])
            res = requests.get(url)

            # Put data into dataframe
            df = pd.DataFrame.from_dict(res.json())

            # Some transformations
            df_treated = (
                df
                .astype({
                    'id':int
                    }
                )
                # transform resultados in a real json with json dumps
                .assign(resultados=lambda df: df['resultados'].apply(json.dumps))
                .rename(columns={
                    'id':'ID Variável',
                    'variavel':'Variável',
                    'unidade':'Unidade',
                    'resultados':'Resultados'
                })
            )

            # Garantee same columns defined earlier
            df_table = df_treated[IBGE().columns()]

            # Go to database, erase past data and insert whole new one
            post_hook = PostgresHook()
            post_hook.run('TRUNCATE TABLE ibge_raw_variaveis',)
            post_hook.insert_rows(
                table='ibge_raw_variaveis', 
                # itertuples provide a list of rows 
                rows=df_table.itertuples(index=False),
                target_fields=IBGE().fields_columns()
            )

            return None

        (
            create_raw_igbe_table() 
            >> read_api_data()
            
        ) #type: ignore
        
    @task_group(group_id='treate_variables')
    def treate_variables():
        @task(task_id='get_63_month_var')
        def var_63_month_var():
            # Get data from database
            df = PostgresHook().get_pandas_df('SELECT * FROM ibge_raw_variaveis where "ID Variável" = 63')
            

        var_63_month_var()
    
    get_raw_data() >> treate_variables() #type:ignore
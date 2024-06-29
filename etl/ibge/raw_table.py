'''Script to create raw tables for IBGE data

'''

from .utils import get_url_response, urls

import pandas as pd
import logging

import json

# Airflow
from airflow.providers.postgres.hooks.postgres import PostgresHook #type: ignore

def list_cities():
    '''Read the city from database and return a list of them.

    This returns the cities that are already in the database.

    '''
    # Connect to database with Airflow hook
    postgres_hook = PostgresHook() #Use the default connection

    # Get the cities already in the database
    list_cities = (
        postgres_hook.get_pandas_df('SELECT DISTINCT city_id FROM cities')
        ['city_id'].tolist()
    )

    return list_cities

def raw_table(period:str):
    '''Retrieve the data from the API and store them in the raw table

    Args:
        period (str): Period to be retrieved from the API. This came from Airflow
            logical date. Thereby, it is represent the month of processing.

    '''
    # Get the base url
    base_url = urls('base_url')

    # For each city, get the data from the API
    logging.info('Getting data from API')
    dfs = []
    for city in list_cities():
        # Difine the url
        url = base_url.format(period=period, city=city)
        print(url)
        logging.info(f'Getting data from {url} for city id {city}')
        # Get the data from the API
        data = get_url_response(url)
        df = pd.DataFrame.from_dict(data)
        print(df)
        
        # Add the city_id, period and url to the dataframe
        df['month_id'] = period
        df['city_id'] = city
        df['api_url'] = url

        # Append the data to the list of dataframes
        dfs.append(df)

    # Concatenate the dataframes
    df = pd.concat(dfs)

    logging.info(f'Columns: {df.columns} and lines: {df.shape[0]}')

    # Make the column results a json
    
    df = (
        df
        .drop(columns=['unidade'])
        .assign(resultados = lambda x: x['resultados'].apply(json.dumps))
        .rename(columns={'id': 'aggregate_id', 'variavel': 'aggregate_name', 
                         'resultados': 'json_data'})
    )

    # Connect to database with Airflow hook
    postgres_hook = PostgresHook() #Use the default connection

    logging.info('Inserting new data')

    logging.info(f'Deleting existing data for period {period}')
    # Delete existing data for period
    postgres_hook.run(
        f'''
        DELETE FROM raw_data_ibge
        WHERE month_id = {period}
        '''
    )

    # Insert the new data
    postgres_hook.insert_rows(
        table='raw_data_ibge',
        rows=df.itertuples(index=False),
        target_fields=['aggregate_id', 'aggregate_name', 'json_data', 
                       'month_id', 'city_id', 'api_url']
    )

    logging.info(f'Data inserted for period {period}. Lines: {df.shape[0]}')

    return None

# if __name__ == '__main__':
#     raw_table('202101')
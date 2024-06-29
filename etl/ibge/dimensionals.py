'''Script to create dimensional tables for IBGE data

'''

from .utils import get_url_response, urls

import pandas as pd
import logging

# Airflow
from airflow.providers.postgres.hooks.postgres import PostgresHook #type: ignore

# 1. Cities Read cities from the API and store them in the `cities` table.
def dim_cities():
    '''Retrieve the cities from the API and store them in the `cities` table

    '''

    # Get data from API
    logging.info('Getting data from API')
    data = get_url_response(urls('cities'))
    df_city = pd.DataFrame.from_dict(data)

    # Treat the data
    df_city = (
        df_city
        [['id', 'nome']]
        .astype({'id': 'int64', 'nome': 'object'})
        .infer_objects()
    )
    logging.info(f'Columns: {df_city.columns} and lines: {df_city.shape[0]}')

    # Connect to database with Airflow hook
    postgres_hook = PostgresHook() #Use the default connection

    # Insert the new cities
    logging.info('Inserting new cities')

    # Get the cities already in the database
    df_city_database = postgres_hook.get_pandas_df('SELECT * FROM cities')
    # Filter the new cities from API
    df_new_city = df_city[~df_city['id'].isin(df_city_database['city_id'])]

    # Insert rows in the `cities` table
    postgres_hook.insert_rows(
        table='cities',
        rows=df_new_city.itertuples(index=False),
        target_fields=['city_id', 'city_name']
    )
    logging.info(f'New cities inserted: {df_new_city.shape[0]}')

    logging.info('Updating cities that have name changed')
    # Update the cities that have name changed
    df_conf = df_city.merge(df_city_database, left_on='id', right_on='city_id', 
                            how='inner')
    # Get the cities that have name changed
    df_update_city = df_conf[df_conf['nome'] != df_conf['city_name']]

    # Update the cities that have name changed
    for index, row in df_update_city.iterrows():
        postgres_hook.run(
            f'''
            UPDATE cities
            SET city_name = '{row['nome']}'
            WHERE city_id = {row['id']}
            '''
        )
    logging.info(f'Cities updated: {df_update_city.shape[0]}')

    return None

# 2. Categories Read categories from the API and store them in the `categories`
# table.
def dim_categories():
    '''Retrieve the categories from the API and store them in the `categories` table

    '''

    # Get data from API
    logging.info('Getting data from API')
    data = get_url_response(urls('categories'))
    categories = data['classificacoes'][0]['categorias']

    df_category = pd.DataFrame.from_dict(categories)

    # # Treat the data
    df_category = (
        df_category
        [['id', 'nome', 'nivel']]
        .astype({'id': 'int64', 'nome': 'object'})
        .assign(
            code=lambda df:
                df['nome'].apply(lambda row:
                                 int(row.split('.')[0]) if '.' in row else 0
                )
        )
        .assign(
            name=lambda df:
                df['nome'].apply(lambda row:
                                 row.split('.')[1] if '.' in row else row
                )
        )
    )
    logging.info(f'Columns: {df_category.columns} and lines: {df_category.shape[0]}')

    # Connect to database with Airflow hook
    postgres_hook = PostgresHook() #Use the default connection

    # Insert the new categories
    logging.info('Inserting new categories')
    # Get the categories already in the database
    df_category_database = postgres_hook.get_pandas_df('SELECT * FROM categories')
    # Filter the new cities from API
    df_new_category = df_category[~df_category['id'].isin(df_category_database['category_id'])]
    
    # Insert rows in the `categories` table
    postgres_hook.insert_rows(
        table='categories',
        rows=df_new_category.itertuples(index=False),
        target_fields=['category_id', 'category_id_name', 'level', 'category_code', 'category_name']
    )
    logging.info(f'New categories inserted: {df_new_category.shape[0]}')

    # Update the categories that have name changed
    logging.info('Updating categories that have name changed')

    df_conf = df_category.merge(df_category_database, left_on='id', 
                                right_on='category_id', how='inner')
    
    # Get the categories that have name changed
    df_update_category = df_conf[df_conf['nome'] != df_conf['category_id_name']]

    # Update the categories that have name changed
    for index, row in df_update_category.iterrows():
        postgres_hook.run(
            f'''
            UPDATE categories
            SET category_id_name = '{row['nome']}',
                category_code = {row['code']},
                category_name = '{row['name']}',
                level = {row['nivel']}
            WHERE category_id = {row['id']}
            '''
        )

    logging.info(f'Categories updated: {df_update_category.shape[0]}')    

    return None

# 3. Calendar Create a calendar table to store the date information for the
# project. This could be used in a BI project, for example.This is dependent
# on the year of processing. If the new year is processed, the calendar table
# will be updated.
def dim_calendar(period:str):
    '''Create a calendar table to store the date information for the project

    The calendar table will be updated according to the period informed. The
    base is the year.

    '''

    # Transform the period id to get the year
    # The peiod came in the format 'YYYYMMDD'
    year = int(period[:4])
    logging.info(f'Year of process: {year}')

    # Check if the year exists in the database
    postgres_hook = PostgresHook()
    existing_years = postgres_hook \
        .get_pandas_df('SELECT DISTINCT year FROM calendar')['year'].tolist()
    is_in_database = year in existing_years
    if not is_in_database:
        logging.info(f'Year {year} not in the database. Creating the calendar table')
        # Create a pandas datarange for the year
        date_range = pd.date_range(start=f'{year}-01-01',
                                   end=f'{year}-12-31',
                                   freq='D'
                                   )
        # Add the columns
        df_calendar = (
            pd.DataFrame(date_range, columns=['date'])
            .assign(month = lambda x: x['date'].dt.month)
            .assign(month_name = lambda x: x['date'].dt.month_name())
            .assign(month_abbr = lambda x: x.month_name.str.slice(0, 3))
            .assign(year = lambda x: x['date'].dt.year)
        )

        # Insert the new year in the database
        postgres_hook.insert_rows(
            table='calendar',
            rows=df_calendar.itertuples(index=False),
            target_fields=['date', 'month', 'month_name', 'month_abbr', 'year']
        )
    else:
        logging.info(f'Year {year} already in the database. Nothing to do')

# if __name__ == '__main__':
#     # dim_cities()
#     # dim_calendar('20250101')
#     dim_categories()
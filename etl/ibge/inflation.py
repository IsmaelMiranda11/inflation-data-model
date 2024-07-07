'''Script to assemble the inflation table

'''

from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import pandas as pd
import logging

def inflation(period:str):
    '''Retrieve the inflation data from the API and store it in the `inflation` table

    '''

    logging.info('Getting data from database')
    # Connect to database and get the raw_data_ibge
    postgres_hook = PostgresHook()
    df_raw_data_ibge = postgres_hook.get_pandas_df(
        f'SELECT * FROM raw_data_ibge WHERE month_id = {period}'
    )


    logging.info('Treating the data')
    # The json data is a list of json for each category
    # Expand the list into rows
    df = df_raw_data_ibge.explode('json_data')

    df = (
        df
        # category_id
        .assign(
            category_id=lambda df:
                df['json_data'].apply(
                    lambda row:
                        int(
                            list(
                                row
                                .get('classificacoes', [])[0]
                                .get('categoria').keys()
                            )[0]
                        )
            )
        )
        # month_date
        .assign(month_date=lambda df: pd.to_datetime(df['month_id'],
                                                     format='%Y%m')
        )
        # value
        .assign(
            value=lambda df:
                df['json_data'].apply(
                    lambda row:
                    pd.to_numeric(
                        list(
                            row.get('series',[])[0].get('serie').values()
                        )[0],
                        errors='coerce'
                    )
            )
        )
        # Pivot the table
        .pivot_table(columns='aggregate_id', index=['month_id','month_date',
                                                    'category_id', 'city_id'],
                     values='value')
        .reset_index()
        .rename_axis(None, axis=1)
        .rename(columns={63: r'ipca_month_variation',
                         69: r'ipca_accumulated_year_variation',
                         2265: r'ipca_accumulated_12_months_variation',
                         66: r'ipca_month_weight'
                        }
        )
        # For month without ipca_accumulated_12_months_variation
        .pipe(lambda df: 
              df.assign(ipca_accumulated_12_months_variation=None)
              if 'ipca_accumulated_12_months_variation' not in df.columns
              else df
        )
    )

    logging.info(f'Columns: {df.columns} and lines: {df.shape[0]}')

    logging.info('Inserting new data')
    logging.info(f'Deleting existing data for period {period}')
    # Delete the existing data for the month_id
    postgres_hook.run(
        f'''
        DELETE FROM inflation
        WHERE month_id = '{period}'
        '''
    )

    target_fields = ['month_id', 'month_date', 'category_id', 'city_id',
                     'ipca_month_variation', 'ipca_month_weight',
                     'ipca_accumulated_year_variation',
                     'ipca_accumulated_12_months_variation'
                    ]

    # Organize dataframe
    df = df[target_fields]

    # Insert the new data
    postgres_hook.insert_rows(
        table='inflation',
        rows=df.itertuples(index=False),
        target_fields=target_fields
    )

    logging.info(f'Inflation inserted: {df.shape[0]}')

# if __name__ == '__main__':
#     inflation('202001')
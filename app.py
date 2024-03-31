import pandas as pd
import requests
import json
import datetime

def ibge_url():
    end_period = datetime.datetime.now().strftime('%Y%m')
    
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


read_api_data(ibge_url())
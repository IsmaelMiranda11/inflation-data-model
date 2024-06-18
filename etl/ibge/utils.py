'''This module contains utility functions for the IBGE ETL process.

'''

import requests
import requests.adapters
import ssl
import os
import configparser

def get_url_response(url) -> dict:
    '''Function to fix a problem in get URL
    
    In some periods, the requests wont get reponse from server.
    This function was copied from StackOverflow to solve this.
    '''
    class TLSAdapter(requests.adapters.HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            ctx = ssl.create_default_context()
            ctx.set_ciphers("DEFAULT@SECLEVEL=1")
            ctx.options |= 0x4   # <-- the key part here, OP_LEGACY_SERVER_CONNECT
            kwargs["ssl_context"] = ctx
            return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

    with requests.session() as s: 
        s.mount("https://", TLSAdapter())
        return s.get(url).json()
    
def urls(information:str) -> str:
    '''Read the urls.ini file and return the url for the requested information

    Args:
        information (str): Information to be searched in the urls.ini file

    '''
    # Get the current directory
    current_directory = os.path.dirname(__file__)

    # Get the path to the urls.ini file
    path = os.path.join(current_directory, 'urls.ini')

    # Read the urls.ini file
    config = configparser.ConfigParser()
    config.read(path)

    # Return the url for the requested information
    return config['urls'][information]
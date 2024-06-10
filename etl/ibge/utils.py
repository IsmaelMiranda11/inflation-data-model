'''This module contains utility functions for the IBGE ETL process.

'''

import requests
import requests.adapters
import ssl

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
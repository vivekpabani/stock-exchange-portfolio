import requests
from .api_info import API_URL
from .exceptions import CannotConnectToServerException


def fetch_json_from_symbol(symbol):
    try:
        r = requests.get(API_URL.format(symbol))
    except:
        raise CannotConnectToServerException("Error fetching data from server. Please try again later.") 

    return r.json()

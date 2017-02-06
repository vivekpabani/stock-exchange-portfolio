import requests
from .api_info import API_URL
from .exceptions import CannotConnectToServerException


def fetch_json_from_symbol(symbol, api_url=None):
    if not api_url:
        api_url = API_URL
    try:
        r = requests.get(api_url.format(symbol))
    except:
        raise CannotConnectToServerException("Error fetching data from server. Please try again later.") 

    return r.json()

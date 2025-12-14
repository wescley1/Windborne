def fetch_data_from_api(api_key, symbol, function, datatype='json'):
    import requests

    base_url = "https://www.alphavantage.co/query"
    params = {
        'function': function,
        'symbol': symbol,
        'apikey': api_key,
        'datatype': datatype
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching data from API: {response.status_code} - {response.text}")

def format_financial_data(data):
    # This function can be expanded to format the financial data as needed
    return data

def log_error(message):
    import logging

    logging.basicConfig(level=logging.ERROR)
    logging.error(message)
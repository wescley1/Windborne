class AlphaVantageClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

    def fetch_financial_statements(self, symbol, statement_type, years=3):
        params = {
            "function": statement_type,
            "symbol": symbol,
            "apikey": self.api_key,
            "datatype": "json"
        }
        response = self._make_request(params)
        return self._process_response(response, years)

    def _make_request(self, params):
        import requests
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()

    def _process_response(self, response, years):
        if "Error Message" in response:
            raise ValueError("Error fetching data from Alpha Vantage: " + response["Error Message"])
        
        # Process the response to extract the last 'years' of data
        # This is a placeholder for actual processing logic
        return response

    def get_income_statement(self, symbol):
        return self.fetch_financial_statements(symbol, "INCOME_STATEMENT")

    def get_balance_sheet(self, symbol):
        return self.fetch_financial_statements(symbol, "BALANCE_SHEET")

    def get_cash_flow_statement(self, symbol):
        return self.fetch_financial_statements(symbol, "CASH_FLOW")
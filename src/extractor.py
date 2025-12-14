from alphavantage_client import AlphaVantageClient
import time

class Extractor:
    def __init__(self, api_client: AlphaVantageClient, companies):
        self.api_client = api_client
        self.companies = companies  # waits dict {name: ticker}

    def fetch_financial_statements(self):
        financial_data = {}
        for name, ticker in self.companies.items():
            time.sleep(1)  # To respect API rate limits
            income_statement = self.api_client.get_income_statement(ticker)
            time.sleep(1)  # To respect API rate limits
            balance_sheet = self.api_client.get_balance_sheet(ticker)
            time.sleep(1)  # To respect API rate limits
            cash_flow_statement = self.api_client.get_cash_flow_statement(ticker)

            financial_data[name] = {
                'income_statement': income_statement,
                'balance_sheet': balance_sheet,
                'cash_flow_statement': cash_flow_statement
            }
        return financial_data

    def extract_data(self):
        return self.fetch_financial_statements()
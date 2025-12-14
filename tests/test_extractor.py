import unittest
from src.extractor import Extractor
from src.alphavantage_client import AlphaVantageClient

class TestExtractor(unittest.TestCase):

    def setUp(self):
        self.api_key = "test_api_key"
        self.client = AlphaVantageClient(self.api_key)
        self.extractor = Extractor(self.client)

    def test_fetch_income_statement(self):
        company_symbol = "TEL"
        data = self.extractor.fetch_income_statement(company_symbol)
        self.assertIsInstance(data, dict)
        self.assertIn("annualReports", data)
        self.assertGreater(len(data["annualReports"]), 0)

    def test_fetch_balance_sheet(self):
        company_symbol = "ST"
        data = self.extractor.fetch_balance_sheet(company_symbol)
        self.assertIsInstance(data, dict)
        self.assertIn("annualReports", data)
        self.assertGreater(len(data["annualReports"]), 0)

    def test_fetch_cash_flow_statement(self):
        company_symbol = "DD"
        data = self.extractor.fetch_cash_flow_statement(company_symbol)
        self.assertIsInstance(data, dict)
        self.assertIn("annualReports", data)
        self.assertGreater(len(data["annualReports"]), 0)

if __name__ == "__main__":
    unittest.main()
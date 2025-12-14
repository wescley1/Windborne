import unittest
from unittest.mock import patch, MagicMock
from src.alphavantage_client import AlphaVantageClient

class TestAlphaVantageClient(unittest.TestCase):

    @patch('src.alphavantage_client.requests.get')
    def test_get_financial_statements_success(self, mock_get):
        # Arrange
        mock_response = {
            "annualReports": [
                {
                    "fiscalDateEnding": "2022-12-31",
                    "totalRevenue": "150000000",
                    "netIncome": "30000000"
                },
                {
                    "fiscalDateEnding": "2021-12-31",
                    "totalRevenue": "140000000",
                    "netIncome": "28000000"
                },
                {
                    "fiscalDateEnding": "2020-12-31",
                    "totalRevenue": "130000000",
                    "netIncome": "26000000"
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        client = AlphaVantageClient(api_key='test_key')

        # Act
        result = client.get_financial_statements('TEL')

        # Assert
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['fiscalDateEnding'], '2022-12-31')
        self.assertEqual(result[0]['totalRevenue'], '150000000')

    @patch('src.alphavantage_client.requests.get')
    def test_get_financial_statements_failure(self, mock_get):
        # Arrange
        mock_get.return_value.json.return_value = {"Error Message": "Invalid API call"}
        client = AlphaVantageClient(api_key='test_key')

        # Act
        result = client.get_financial_statements('INVALID')

        # Assert
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
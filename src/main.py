# windborne-extractor/windborne-extractor/src/main.py

import os
from dotenv import load_dotenv

# Load environment variables early so `config` can read them
load_dotenv()

from config import API_KEY, COMPANIES
from alphavantage_client import AlphaVantageClient
from extractor import Extractor
from logger import get_logger


def main():
    logger = get_logger(__name__)

    # Initialize the Alpha Vantage client
    av_client = AlphaVantageClient(api_key=API_KEY)

    # Initialize the extractor with the client and companies
    extractor = Extractor(api_client=av_client, companies=COMPANIES)

    logger.info("Starting data extraction for %d companies.", len(COMPANIES))

    # Trigger the data extraction process
    financial_data = extractor.extract_data()

    te_income = financial_data.get("TE Connectivity", {}).get("income_statement")
    logger.info("TE Connectivity income statement keys: %s", list(te_income.keys()) if te_income else "no data")

    import json

    try:
        with open("financial_data.json", 'w', encoding='utf-8') as f:
            # O 'indent=4' formata o JSON para fácil leitura.
            json.dump(financial_data, f, indent=4, ensure_ascii=False)
        print(f"DEBUG: Dados salvos com sucesso em financial_data.json")
    except Exception as e:
        print(f"DEBUG ERRO: Não foi possível salvar o arquivo: {e}")

    for company, statements in financial_data.items():
        logger.info("Company=%s statements=%s", company, list(statements.keys()))


    logger.info("Data extraction completed.")


if __name__ == "__main__":
    main()
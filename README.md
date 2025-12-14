# WindBorne — Finance Data Extractor

## Overview
- Python app to extract financial statements from Alpha Vantage, persist raw JSON and load into a relational DB for analysis.

## Repository layout (relevant)
- src/ — application code (main.py, config.py, alphavantage_client.py, extractor.py, models.py, db.py, logger.py)
- data/ — extracted JSON (financial_data.json)
- scripts/ — helper scripts (load_financials.py, query examples)
- docker-compose.yml — local Postgres for dev
- requirements.txt, .env.example, README.md

## Prerequisites
- Python 3.10+ (venv)
- pip, Docker Desktop (Windows)
- Optional: psql or any DB client

## Quick setup (Windows PowerShell)
1. Create venv and install:
   ```
   $ python -m venv venv
   $ .\venv\Scripts\Activate.ps1
   $ pip install -r requirements.txt
   ```

2. Environment:
   - Copy .env.example -> .env and set API_KEY
   - For DB loader set DATABASE_URL in shell when running loader (examples below)

## Usage
1. To run the data extraction process, execute the following command:
   ```
   python src/main.py
   ```

2. Alternatively, you can use the provided shell script:
   ```
   bash scripts/run_fetch.sh
   ```

3. To run Postgres via docker-compose (defaults mapped to host):
   ```
   # from repo root
   docker-compose up -d
   ```

4. To load JSON into Postgres (script uses src package; set PYTHONPATH):
   ```
   # set DB URL to point to your Postgres host/port/credentials
   $ $env:DATABASE_URL='postgresql+psycopg2://windborne:password@localhost:5233/windborne'
   $ $env:PYTHONPATH='.'
   $ python .\scripts\load_financials.py
   ```

## Notes for Windows + Docker Desktop
- Docker Desktop exposes containers on localhost. If you map a different host port, use that port in DATABASE_URL.
- If you get import errors for src, ensure PYTHONPATH='.' or run via container as described in scripts.

## Common queries
- List tables:
  ```
  docker-compose exec db psql -U windborne -d windborne -c "\dt"
  ```
- Sample SQL:
  ```
  SELECT id, name, ticker FROM companies LIMIT 10;
  ```

## Testing
To run the unit tests, use:
```
pytest tests/
```

## Development tips
- Use feature branches (e.g. feature/etl_process).
- Use `docker-compose down -v` if you change POSTGRES_* envs and need a fresh DB.
- Add Alembic for migrations before schema changes.

## Troubleshooting
- If loader connects to SQLite, ensure DATABASE_URL is exported before running the script.
- If you see SQLAlchemy JSON/JSONB errors on SQLite, the models file falls back to SQL JSON automatically.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- [Alpha Vantage API](https://www.alphavantage.co/documentation/) for providing financial data.
- Open-source community for the libraries and tools used in this project.

## TODO
If you want, I can:
- add a small scripts/query_db.py example,
- add an Alembic configuration,
- or create a docker-compose "worker" service to run the loader inside the compose network.
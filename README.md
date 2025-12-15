# WindBorne — Finance Data Automation Platform


> Automated ETL pipeline for financial statement analysis with PostgreSQL, Alpha Vantage API, and interactive dashboards.

## Live Demo

**Dashboard:** [https://windborne-s220.onrender.com](https://windborne-s220.onrender.com)

## Overview

WindBorne is a production-ready financial data pipeline that:
- Extracts financial statements from Alpha Vantage API
- Transforms and normalizes data into PostgreSQL
- Calculates key financial metrics (margins, YoY growth)
- Provides interactive dashboards for analysis
- Includes production deployment strategy

### Companies Tracked
- **TE Connectivity** (TEL)
- **Sensata Technologies** (ST)
- **DuPont de Nemours** (DD)

## Architecture

```
┌─────────────────┐
│ Alpha Vantage   │
│      API        │
└────────┬────────┘
         │ Extract (main.py)
         ↓
┌─────────────────┐
│  Raw JSON Data  │
│ (financial_data │
│     .json)      │
└────────┬────────┘
         │ Load (load_financials.py)
         ↓
┌─────────────────┐
│  PostgreSQL     │
│  (Supabase)     │
│  ├─ companies   │
│  ├─ financial_  │
│  │   statements │
│  └─ metrics     │
└────────┬────────┘
         │ Calculate (calc_metrics.py)
         ↓
┌─────────────────┐
│   Streamlit     │
│   Dashboard     │
│  (Render)       │
└─────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (local or Supabase)
- Alpha Vantage API key (free tier)

### 1. Clone & Install

```bash
git clone https://github.com/wescley1/Windborne.git
cd Windborne
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file:

```env
# Alpha Vantage API
API_KEY=your_alpha_vantage_key

# Database (local or Supabase)
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname

# Logging
LOG_LEVEL=INFO
```

### 3. Run ETL Pipeline

```bash
# Extract data from API
python src/main.py

# Load into database
python scripts/load_financials.py

# Calculate metrics
python scripts/calc_metrics.py
```

### 4. Launch Dashboard

```bash
streamlit run app/Home.py
```

Visit `http://localhost:8501`

## Docker Setup (Alternative)

```bash
# Start PostgreSQL
docker-compose up -d db

# Run worker (ETL pipeline)
docker-compose run --rm worker
```

## Database Schema

### `companies`
```sql
id              SERIAL PRIMARY KEY
name            VARCHAR(255) UNIQUE NOT NULL
ticker          VARCHAR(32) NOT NULL
metadata_json   JSONB
created_at      TIMESTAMP DEFAULT NOW()
```

### `financial_statements`
```sql
id                  SERIAL PRIMARY KEY
company_id          INT REFERENCES companies(id)
statement_type      VARCHAR(64)  -- 'income_statement', 'balance_sheet', 'cash_flow'
period              VARCHAR(32)  -- 'annual', 'quarterly'
fiscal_date         DATE
data                JSONB        -- Raw API response
-- Normalized columns for fast queries
revenue             FLOAT
gross_profit        FLOAT
net_income          FLOAT
total_assets        FLOAT
total_liabilities   FLOAT
operating_cashflow  FLOAT
currency            VARCHAR(8)
created_at          TIMESTAMP DEFAULT NOW()

CONSTRAINT u_company_statement_fiscal UNIQUE (company_id, statement_type, fiscal_date)
```

### `metrics`
```sql
id              SERIAL PRIMARY KEY
company_id      INT REFERENCES companies(id)
year            INT NOT NULL
metric_name     VARCHAR(64)  -- 'gross_margin', 'net_margin', 'revenue_yoy'
value           FLOAT
created_at      TIMESTAMP DEFAULT NOW()

CONSTRAINT u_company_year_metric UNIQUE (company_id, year, metric_name)
```

## Calculated Metrics

| Metric | Formula | Unit |
|--------|---------|------|
| **Gross Margin** | (Gross Profit / Revenue) × 100 | % |
| **Net Margin** | (Net Income / Revenue) × 100 | % |
| **Revenue YoY** | ((Current - Previous) / Previous) × 100 | % |

## Project Structure

```
Windborne/
├── app/
│   ├── Home.py                      # Streamlit home page
│   └── pages/
│       ├── 1_Metrics_Dashboard.py
│       └── 2_Production_Design.py
├── src/
│   ├── main.py                      # Extract from API
│   ├── extractor.py                 # Data extraction logic
│   ├── alphavantage_client.py       # API client
│   ├── models.py                    # SQLAlchemy models
│   ├── db.py                        # Database connection
│   ├── db_manager.py                # Database operations
│   ├── utils.py                     # Parsing & normalization
│   ├── config.py                    # Configuration
│   └── logger.py                    # Logging setup
├── scripts/
│   ├── load_financials.py           # Load JSON → PostgreSQL
│   └── calc_metrics.py              # Calculate metrics
├── data/
│   └── financial_data.json          # Extracted API data
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Production Deployment

### Hosting Options

**Current Setup:**
- **Database:** Supabase PostgreSQL (free tier)
- **App:** Render Web Service (free tier)

**Alternative Stacks:**
- Vercel (frontend) + Supabase (database)
- AWS Lambda + RDS
- Google Cloud Run + Cloud SQL

### Environment Variables (Render)

```
DATABASE_URL=postgresql://...@...supabase.co:5432/postgres
API_KEY=your_alpha_vantage_key
PYTHONUNBUFFERED=1
```

### Build Command (Render)

```bash
pip install -r requirements.txt
```

### Start Command (Render)

```bash
streamlit run app/Home.py --server.port=$PORT --server.address=0.0.0.0
```

## Production Pipeline Design

See the **Production Design** page in the live dashboard for detailed explanations of:

1. **Monthly Scheduling** — n8n workflow vs Kubernetes CronJob
2. **API Rate Limit Handling** — Multi-day batching for 100 companies
3. **Google Sheets Integration** — BigQuery sync architecture
4. **Monitoring & Alerts** — Health checks and failure detection

## Testing

```bash
# Run unit tests (coming soon)
pytest tests/

# Test database connection
python -c "from src.db_manager import DBManager; print(DBManager().get_companies())"

# Validate metrics calculation
python scripts/calc_metrics.py
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'src'`
**Solution:** Set `PYTHONPATH`
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Unix
$env:PYTHONPATH='.'  # Windows
```

### Issue: API rate limit exceeded
**Solution:** Alpha Vantage free tier = 25 calls/day
- Wait 24 hours or upgrade to premium
- Use cached `data/financial_data.json`

### Issue: Database connection failed
**Solution:** Check `DATABASE_URL` in `.env`
```bash
# Test connection
docker-compose exec db psql -U windborne -d windborne -c "SELECT 1;"
```

## API Documentation

- [Alpha Vantage API Docs](https://www.alphavantage.co/documentation/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)

## License

MIT License — see [LICENSE](LICENSE) file

## Acknowledgments

- Alpha Vantage for financial data API
- Streamlit for rapid dashboard development
- WindBorne Systems for the assignment opportunity

---

**Questions?** Open an issue or contact [your-email@example.com](mailto:your-email@example.com)

**Live Dashboard:** [https://windborne-s220.onrender.com](https://windborne-s220.onrender.com)
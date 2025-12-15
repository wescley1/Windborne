import streamlit as st

st.set_page_config(page_title="Production Design — WindBorne", layout="wide")

st.title("Production Pipeline Design")

st.markdown("""
This section explains how to productionize the WindBorne ETL pipeline with:
- **n8n** (workflow automation)
- **PostgreSQL** (database)
- **Google Sheets** (executive reporting)
- **Alpha Vantage API** (5 calls/min, 25/day limit)
""")

st.markdown("---")

# Question 1
st.header("1. Monthly Scheduling Strategy")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Recommended: n8n Workflow")
    st.code("""
# n8n Workflow Configuration
Trigger: Cron (1st of month, 2 AM UTC)
    ↓
HTTP Request → POST /api/etl/run
    ↓
Wait 5 min between companies
    ↓
Notification (Slack/Email)
    ├─ Success: "ETL completed"
    └─ Failure: "Alert: Pipeline failed"
    """, language="text")
    
    st.markdown("""
    **Why n8n?**
    - Visual workflow builder (no-code)
    - Built-in error handling & retries
    - Slack/email integrations
    - Execution logs & monitoring
    """)

with col2:
    st.subheader("Alternative: Kubernetes CronJob")
    st.code("""
apiVersion: batch/v1
kind: CronJob
metadata:
  name: windborne-etl
spec:
  schedule: "0 2 1 * *"  # 1st of month
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: etl-runner
            image: windborne:latest
            command: ["python", "src/main.py"]
          restartPolicy: OnFailure
    """, language="yaml")

st.markdown("---")

# Question 2
st.header("2. Handling 100 Companies (API Rate Limits)")

st.error("""
**Problem:** 100 companies × 3 statements = 300 API calls  
**Limit:** 25 calls/day → Need 12 days for full refresh
""")

st.subheader("Solution: Multi-Day Batching")

col1, col2 = st.columns([1, 1])

with col1:
    st.code("""
# Daily batch strategy
def get_companies_to_update():
    # Query companies not updated in 30 days
    return db.query(Company).filter(
        Company.last_updated < 
        datetime.now() - timedelta(days=30)
    ).order_by(
        Company.last_updated.asc()
    ).limit(8)  # 8 companies × 3 = 24 calls

# n8n runs daily, processes 8 companies
# Full cycle: 100 ÷ 8 = 12.5 days
    """, language="python")

with col2:
    st.markdown("""
    **Enhancements:**
    
    1. **Priority Queue**
       - Process earnings season companies first
       - Flag stale data (>60 days old)
    
    2. **Exponential Backoff**
       ```python
       @retry(stop=stop_after_attempt(3),
              wait=wait_exponential(min=4, max=60))
       def fetch_statement(ticker):
           ...
       ```
    
    3. **Response Caching**
       - Store ETag headers
       - Skip unchanged data
    """)

st.info("**Note:** For real-time needs, consider Alpha Vantage Premium ($50/mo = 120 calls/min)")

st.markdown("---")

# Question 3
st.header("3. Google Sheets Access for Executives")

st.subheader("Comparison of Approaches")

comparison_data = {
    "Approach": ["Direct Postgres", "CSV Export to Drive", "Sync to BigQuery", "REST API + Apps Script"],
    "Setup Complexity": ["Medium", "Low", "High", "Medium"],
    "Real-time Data": ["Yes", "No", "Near real-time (1h lag)", "Yes"],
    "Scalability": ["Poor", "Poor", "Excellent", "Good"],
    "Cost": ["Free", "Free", "$5-10/mo", "Free"],
    "Security Risk": ["High", "Low", "Low", "Medium"],
    "Verdict": ["Not Recommended", "MVP only", "RECOMMENDED", "Alternative"]
}

st.table(comparison_data)

st.success("""
### Recommended: Postgres → BigQuery → Google Sheets

**Architecture:**
```
[Supabase Postgres] 
   ↓ (nightly sync via Cloud Functions)
[BigQuery]
   ↓ (CONNECTED_SHEETS function)
[Google Sheets]
   └─ Execs: pivot tables, charts, formulas
```

**Advantages:**
- Native Sheets integration (no add-ons)
- Query 1M+ rows without performance degradation
- Version control via BigQuery snapshots
- Handles complex JOINs (statements + metrics)

**Disadvantages:**
- $5-10/month BigQuery cost
- 1-hour data latency (acceptable for monthly financials)
- Initial setup: Cloud Function + service account
""")

with st.expander("Implementation Steps"):
    st.code("""
# Step 1: Create BigQuery dataset
bq mk --dataset windborne_finance

# Step 2: Deploy Cloud Function (Python)
import functions_framework
from google.cloud import bigquery
import psycopg2

@functions_framework.cloud_event
def sync_to_bigquery(cloud_event):
    # Connect to Supabase
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    
    # Query data
    df = pd.read_sql_query(\"\"\"
        SELECT c.name, c.ticker, m.year, 
               m.metric_name, m.value
        FROM companies c
        JOIN metrics m ON c.id = m.company_id
    \"\"\", conn)
    
    # Load to BigQuery
    client = bigquery.Client()
    table_id = 'windborne_finance.metrics'
    client.load_table_from_dataframe(df, table_id)

# Step 3: Schedule Cloud Scheduler
gcloud scheduler jobs create http sync-financials \\
  --schedule="0 3 * * *" \\
  --uri="https://REGION-PROJECT.cloudfunctions.net/sync_to_bigquery"

# Step 4: In Google Sheets
=CONNECTED_SHEETS("windborne_finance.metrics")
    """, language="bash")

st.markdown("---")

# Question 4
st.header("4. Monitoring & Failure Detection")

st.subheader("What Breaks First?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Critical Failures
    
    **1. API Rate Limits (Most Common)**
    - **Detection:** Track 429 responses
    - **Alert:** Slack when hitting 20/25 limit
    - **Fix:** Implement queue + exponential backoff
    
    **2. Database Connection Loss**
    - **Detection:** Health check endpoint
    - **Alert:** PagerDuty on 3 consecutive failures
    - **Fix:** Connection pooling + auto-reconnect
    
    **3. Stale Data (Pipeline Not Running)**
    - **Detection:** `MAX(created_at) < NOW() - 2 days`
    - **Alert:** Dashboard shows "Data X days old"
    - **Fix:** n8n workflow timeout alerts
    """)

with col2:
    st.markdown("""
    ### Data Quality Issues
    
    **4. Bad API Data (Schema Changes)**
    - **Detection:** Pydantic validation on responses
    - **Alert:** Email when >10% records fail
    - **Fix:** Log to `failed_extracts` table
    
    **5. Missing Financial Data**
    - **Detection:** NULL revenue for recent quarters
    - **Alert:** Dashboard shows data gaps
    - **Fix:** Manual backfill or API re-fetch
    
    **6. Calculation Errors**
    - **Detection:** Metric outliers (>3 std devs)
    - **Alert:** Flag in Streamlit UI
    - **Fix:** Audit trail + recalculation
    """)

st.subheader("Monitoring Stack")

st.code("""
# Logging & Metrics
[Application Logs] → CloudWatch / DataDog
    ├─ Log level: INFO for success, ERROR for failures
    └─ Structured JSON logs

[Metrics] → Prometheus + Grafana
    ├─ API calls remaining (gauge)
    ├─ ETL duration (histogram)
    └─ Row counts per table (counter)

[Alerts] → Slack (warnings) + PagerDuty (critical)
    ├─ API rate limit warning (20/25)
    ├─ Failed extractions (>5 in 1 hour)
    └─ Database connection failures

[Data Quality] → dbt tests on BigQuery
    ├─ not_null: revenue, fiscal_date
    ├─ unique: (company_id, statement_type, fiscal_date)
    └─ accepted_values: statement_type in [income, balance, cash]
""", language="yaml")

st.info("""
**Dashboard KPIs to Monitor:**
- API calls remaining today: `25 - count(api_logs WHERE date=today)`
- Last successful ETL: `MAX(etl_runs.completed_at)`
- Row counts per table: Detect sudden drops
- Metric calculation success rate: `successful / total`
""")

with st.expander("Example Health Check Endpoint"):
    st.code("""
from fastapi import FastAPI
from src.db_manager import DBManager

app = FastAPI()

@app.get("/health")
async def health_check():
    try:
        dbm = DBManager()
        # Test DB connection
        companies = dbm.get_companies()
        
        # Check data freshness
        latest = max([c.created_at for c in companies])
        age_hours = (datetime.now() - latest).total_seconds() / 3600
        
        if age_hours > 48:
            return {"status": "degraded", 
                    "message": f"Data is {age_hours:.1f}h old"}
        
        return {"status": "healthy", 
                "companies": len(companies),
                "last_update": latest.isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
    """, language="python")

st.markdown("---")

st.success("""
### Summary

This production design prioritizes:
1. **Reliability:** Multi-day batching handles API limits gracefully
2. **Observability:** Comprehensive monitoring catches failures early
3. **Scalability:** BigQuery enables 100+ companies without performance issues
4. **Maintainability:** n8n visual workflows simplify debugging

**Estimated Monthly Cost:** $10-15 (BigQuery + Cloud Functions + monitoring)
""")

st.markdown("---")
st.caption("Built with Streamlit • Data from Alpha Vantage API • Hosted on Render")
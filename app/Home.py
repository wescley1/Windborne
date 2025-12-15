import streamlit as st

st.set_page_config(
    page_title="WindBorne Finance Automation",
    page_icon="💼",
    layout="wide"
)

st.title("WindBorne Finance Automation")

st.markdown("""
## Welcome to the Financial Data Pipeline

This application demonstrates an automated ETL pipeline for financial statement analysis.

### Available Pages

Navigate using the sidebar:

- **Metrics Dashboard** — Interactive visualizations of financial metrics (Gross Margin, Net Margin, Revenue YoY)
- **Production Design** — Detailed answers to production deployment questions

### Project Overview

This system extracts, transforms, and analyzes financial data for:
- **TE Connectivity** (TEL)
- **Sensata Technologies** (ST)
- **DuPont de Nemours** (DD)

**Data Source:** Alpha Vantage API  
**Database:** Supabase PostgreSQL  
**Hosting:** Render

### Tech Stack

- **Backend:** Python 3.12 + SQLAlchemy
- **Database:** PostgreSQL (Supabase)
- **Visualization:** Streamlit + Plotly
- **API:** Alpha Vantage

### Calculated Metrics

1. **Gross Margin %** = (Gross Profit / Revenue) × 100
2. **Net Margin %** = (Net Income / Revenue) × 100
3. **Revenue YoY %** = ((Current Revenue - Previous Revenue) / Previous Revenue) × 100

---

**Get started** by selecting a page from the sidebar.
""")

st.info("**Tip:** Use the filters in the Metrics Dashboard to compare companies across different time periods.")

st.markdown("---")
st.caption("WindBorne Finance Automation • Built for the Junior Finance Automation Engineer Assignment")
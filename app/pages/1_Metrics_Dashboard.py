import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

from src.db_manager import DBManager

st.set_page_config(page_title="WindBorne — Metrics", layout="wide")

dbm = DBManager()

# Metric units mapping
METRIC_UNITS = {
    "gross_margin": "%",
    "net_margin": "%",
    "revenue_yoy": "%",
    "revenue": "USD",
    "gross_profit": "USD",
    "net_income": "USD",
    "total_assets": "USD",
    "total_liabilities": "USD",
    "operating_cashflow": "USD",
}

def get_metric_label(metric_name: str) -> str:
    """Return metric name with unit."""
    unit = METRIC_UNITS.get(metric_name, "")
    if unit:
        return f"{metric_name.replace('_', ' ').title()} ({unit})"
    return metric_name.replace('_', ' ').title()

@st.cache_data(ttl=60)
def load_metrics_df():
    comps = dbm.get_companies()
    comp_map = {c.id: {"name": c.name, "ticker": c.ticker} for c in comps}
    metrics = dbm.get_metrics()
    rows = []
    for m in metrics:
        meta = comp_map.get(m.company_id, {})
        rows.append({
            "company_id": m.company_id,
            "company": meta.get("name") or f"id:{m.company_id}",
            "ticker": meta.get("ticker") or "",
            "year": int(m.year) if m.year is not None else None,
            "metric": m.metric_name,
            "value": float(m.value) if m.value is not None else None,
        })
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df = df.dropna(subset=["year"]).sort_values(["company","metric","year"])
    return df

def filter_df(df, selected_companies, metric, year_range):
    out = df[df["metric"] == metric]
    if selected_companies:
        out = out[out["company"].isin(selected_companies)]
    out = out[(out["year"] >= year_range[0]) & (out["year"] <= year_range[1])]
    return out

st.title("Financial Metrics Dashboard")

with st.sidebar:
    st.header("Filters")
    df_all = load_metrics_df()
    if df_all.empty:
        st.warning("No metrics found. Run loader and calc scripts first.")
        st.stop()
    companies = sorted(df_all["company"].unique().tolist())
    default_comp = companies[0] if companies else None
    selected_companies = st.multiselect("Companies", companies, default=[default_comp] if default_comp else [])
    
    metrics = sorted(df_all["metric"].unique().tolist())
    metric_display = {m: get_metric_label(m) for m in metrics}
    selected_metric_display = st.selectbox("Metric", options=list(metric_display.values()))
    selected_metric = [k for k, v in metric_display.items() if v == selected_metric_display][0]
    
    years = sorted(df_all["year"].unique())
    ymin, ymax = (min(years), max(years)) if years else (None, None)
    year_range = st.slider("Year range", ymin, ymax, (ymin, ymax)) if years else (None, None)
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

main_df = filter_df(df_all, selected_companies, selected_metric, year_range)

col1, col2 = st.columns([2,1])
with col1:
    metric_label = get_metric_label(selected_metric)
    st.subheader(f"{metric_label} — {', '.join(selected_companies) if selected_companies else 'All companies'}")
    if main_df.empty:
        st.info("No data for selected filters.")
    else:
        fig = px.line(main_df, x="year", y="value", color="company", markers=True,
                      labels={"value": metric_label, "year": "Year", "company": "Company"})
        fig.update_layout(
            legend_title_text="Company", 
            xaxis=dict(dtick=1),
            yaxis_title=metric_label,
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Summary")
    if main_df.empty:
        st.write("—")
    else:
        latest = main_df.groupby("company").apply(lambda g: g.loc[g["year"].idxmax()]).reset_index(drop=True)
        latest = latest[["company","year","value"]].rename(columns={"year":"latest_year","value":"latest_value"})
        unit = METRIC_UNITS.get(selected_metric, "")
        latest["latest_value_formatted"] = latest["latest_value"].apply(
            lambda x: f"{x:.2f} {unit}".strip() if x is not None else "—"
        )
        
        def native_val(v):
            if v is None:
                return None
            if isinstance(v, np.generic):
                try:
                    return v.item()
                except Exception:
                    return int(v)
            return v
        records = []
        for r in latest.to_dict(orient="records"):
            records.append({k: native_val(v) for k, v in r.items()})
        latest_py = pd.DataFrame(records).set_index("company")
        st.dataframe(latest_py[["latest_year", "latest_value_formatted"]].rename(columns={"latest_value_formatted": f"Latest Value ({unit})"}))

st.markdown("---")
st.subheader("Data table")
unit = METRIC_UNITS.get(selected_metric, "")
main_df_display = main_df.copy()
main_df_display["value_formatted"] = main_df_display["value"].apply(
    lambda x: f"{x:.2f} {unit}".strip() if x is not None else "—"
)
st.dataframe(main_df_display[["company", "ticker", "year", "value_formatted"]].rename(columns={"value_formatted": f"Value ({unit})"}).reset_index(drop=True))

csv = main_df.to_csv(index=False)
st.download_button("Download CSV", csv, file_name=f"metrics_{selected_metric}_{datetime.utcnow().date()}.csv", mime="text/csv")
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
TABLE_DIR = BASE_DIR / "outputs" / "tables"
REPORT_PATH = BASE_DIR / "outputs" / "reports" / "executive_summary.md"


@st.cache_data
def load_table(name: str) -> pd.DataFrame:
    path = TABLE_DIR / name
    if not path.exists():
        st.error(f"Missing output table: {path}. Run `python src/run_pipeline.py` first.")
        st.stop()
    return pd.read_csv(path)


def money(value: float) -> str:
    return f"${value:,.0f}"


st.set_page_config(page_title="Medicare Reimbursement Benchmarking", layout="wide")

provider = load_table("provider_benchmarking.csv")
hcpcs = load_table("hcpcs_variance_analysis.csv")
variance = load_table("reimbursement_variance.csv")
over = load_table("overpayment_flags.csv")
under = load_table("underpayment_flags.csv")
scenarios = load_table("scenario_impact_summary.csv")
forecast = load_table("forecast_summary.csv")
kpis = load_table("executive_kpis.csv")

st.title("Medicare Reimbursement Benchmarking System")
st.caption("Synthetic contract rates benchmarked against CMS-style Medicare reimbursement references.")

total_paid = float(kpis.loc[kpis["metric"].eq("total_contract_paid"), "value"].iloc[0])
total_variance = float(kpis.loc[kpis["metric"].eq("total_financial_variance"), "value"].iloc[0])
avg_ratio = float(kpis.loc[kpis["metric"].eq("average_contract_to_medicare_ratio"), "value"].iloc[0])

cols = st.columns(4)
cols[0].metric("Contract Paid", money(total_paid))
cols[1].metric("Financial Variance", money(total_variance))
cols[2].metric("Avg Contract / Medicare", f"{avg_ratio:.2f}x")
cols[3].metric("Review Flags", f"{len(over) + len(under):,}")

tabs = st.tabs(
    [
        "Executive Overview",
        "Provider Benchmarking",
        "HCPCS/Procedure Analysis",
        "Overpayment/Underpayment Flags",
        "Scenario Modeling",
        "Forecasts",
        "Data Dictionary",
    ]
)

with tabs[0]:
    st.subheader("Executive KPIs")
    st.dataframe(kpis, use_container_width=True, hide_index=True)
    if REPORT_PATH.exists():
        st.markdown(REPORT_PATH.read_text())

with tabs[1]:
    st.subheader("Provider Benchmarking")
    risk = st.multiselect("Risk Tier", sorted(provider["risk_tier"].dropna().unique()))
    view = provider[provider["risk_tier"].isin(risk)] if risk else provider
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.bar_chart(view.nlargest(15, "reimbursement_risk_score").set_index("provider_name")["reimbursement_risk_score"])

with tabs[2]:
    st.subheader("HCPCS / Procedure Exposure")
    st.dataframe(hcpcs, use_container_width=True, hide_index=True)
    st.bar_chart(hcpcs.nsmallest(15, "exposure_rank").set_index("hcpcs_code")["total_financial_variance"])

with tabs[3]:
    st.subheader("Overpayment Flags")
    st.dataframe(over, use_container_width=True, hide_index=True)
    st.subheader("Underpayment Flags")
    st.dataframe(under, use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Scenario Modeling")
    change = st.slider("Live all-rate change", -15, 15, 5, format="%d%%") / 100
    st.metric("Estimated Dollar Impact", money(total_paid * change))
    st.dataframe(scenarios, use_container_width=True, hide_index=True)
    st.bar_chart(scenarios.set_index("scenario_name")["dollar_impact"])

with tabs[5]:
    st.subheader("Forecasts")
    chart = forecast.pivot(index="forecast_month", columns="metric", values="forecast_value")
    st.line_chart(chart)
    st.dataframe(forecast, use_container_width=True, hide_index=True)

with tabs[6]:
    st.markdown(
        """
        **Synthetic contract data:** simulated provider/service reimbursement rates used for benchmarking.

        **CMS public benchmark data:** optional local public CMS files from Physician Fee Schedule or Medicare Physician & Other Practitioners by Provider and Service.

        **Core fields:** provider, state, locality, HCPCS code, service category, contract allowed, contract paid, billed amount, utilization count, and Medicare benchmark amount.
        """
    )

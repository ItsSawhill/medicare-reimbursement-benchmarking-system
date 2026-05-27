from pathlib import Path
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import matplotlib.pyplot as plt
import pandas as pd


def save_figures(
    variance: pd.DataFrame,
    provider: pd.DataFrame,
    hcpcs: pd.DataFrame,
    overpayment: pd.DataFrame,
    underpayment: pd.DataFrame,
    scenarios: pd.DataFrame,
    monthly_forecast_base: pd.DataFrame,
    forecast: pd.DataFrame,
    figure_dir: Path,
) -> None:
    figure_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(variance["contract_to_medicare_ratio"].dropna(), bins=28, color="#2f6f8f", edgecolor="white")
    ax.axvline(1.0, color="black", linewidth=1)
    ax.axvline(1.2, color="#8b1e3f", linestyle="--", linewidth=1)
    ax.axvline(0.8, color="#8b1e3f", linestyle="--", linewidth=1)
    ax.set_title("Contract-to-Medicare Ratio Distribution", weight="bold")
    ax.set_xlabel("Contract Allowed / Medicare Benchmark")
    ax.set_ylabel("Provider-Service Rows")
    fig.tight_layout()
    fig.savefig(figure_dir / "contract_to_medicare_distribution.png", dpi=180)
    plt.close()

    top_provider = provider.assign(abs_variance=provider["total_dollar_variance"].abs()).nlargest(12, "abs_variance")
    top_provider = top_provider.sort_values("total_dollar_variance")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_provider["provider_name"], top_provider["total_dollar_variance"], color="#6d8f3f")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("Top Provider Financial Variance", weight="bold")
    ax.set_xlabel("Total Contract vs Medicare Variance")
    fig.tight_layout()
    fig.savefig(figure_dir / "top_provider_variance.png", dpi=180)
    plt.close()

    top_hcpcs = hcpcs.nsmallest(12, "exposure_rank").sort_values("total_financial_variance")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_hcpcs["hcpcs_code"] + " - " + top_hcpcs["service_description"].str.slice(0, 28), top_hcpcs["total_financial_variance"], color="#9b5f31")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("HCPCS Financial Exposure", weight="bold")
    ax.set_xlabel("Utilization-Adjusted Dollar Variance")
    fig.tight_layout()
    fig.savefig(figure_dir / "hcpcs_financial_exposure.png", dpi=180)
    plt.close()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(["Overpayment Flags", "Underpayment Flags"], [len(overpayment), len(underpayment)], color=["#8b1e3f", "#1f7a5c"])
    ax.set_title("Overpayment / Underpayment Review Counts", weight="bold")
    ax.set_ylabel("Flag Count")
    fig.tight_layout()
    fig.savefig(figure_dir / "overpayment_underpayment_counts.png", dpi=180)
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(scenarios["scenario_name"], scenarios["dollar_impact"], color="#744c7d")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("Scenario Financial Impact", weight="bold")
    ax.set_xlabel("Dollar Impact")
    fig.tight_layout()
    fig.savefig(figure_dir / "scenario_financial_impact.png", dpi=180)
    plt.close()

    pred = forecast[forecast["metric"] == "monthly_benchmark_variance"].copy()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(monthly_forecast_base["service_month"], monthly_forecast_base["monthly_benchmark_variance"], marker="o", label="Actual")
    ax.plot(pd.to_datetime(pred["forecast_month"]), pred["forecast_value"], marker="o", linestyle="--", label="Forecast")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Benchmark Variance Forecast", weight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Benchmark Variance")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(figure_dir / "forecast_variance_trend.png", dpi=180)
    plt.close()


def executive_kpis(provider: pd.DataFrame, variance: pd.DataFrame, overpayment: pd.DataFrame, underpayment: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"metric": "total_contract_paid", "value": variance["contract_total_paid"].sum()},
            {"metric": "total_medicare_benchmark", "value": variance["medicare_total_benchmark"].sum()},
            {"metric": "total_financial_variance", "value": variance["total_financial_variance"].sum()},
            {"metric": "average_contract_to_medicare_ratio", "value": variance["contract_to_medicare_ratio"].mean()},
            {"metric": "high_risk_providers", "value": provider["risk_tier"].isin(["Critical", "High"]).sum()},
            {"metric": "overpayment_flag_count", "value": len(overpayment)},
            {"metric": "underpayment_flag_count", "value": len(underpayment)},
            {"metric": "largest_scenario_impact", "value": scenarios["dollar_impact"].abs().max()},
        ]
    )


def write_executive_summary(provider: pd.DataFrame, hcpcs: pd.DataFrame, overpayment: pd.DataFrame, underpayment: pd.DataFrame, scenarios: pd.DataFrame, forecast: pd.DataFrame, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    top_provider = provider.iloc[0]
    top_hcpcs = hcpcs.iloc[0]
    top_scenario = scenarios.sort_values("dollar_impact", key=lambda s: s.abs(), ascending=False).iloc[0]
    next_variance = forecast[forecast["metric"] == "monthly_benchmark_variance"].sort_values("forecast_month").iloc[0]
    text = f"""# Executive Summary

## Key Findings
- Highest-risk provider: {top_provider.provider_name} ({top_provider.provider_id}), risk tier {top_provider.risk_tier}.
- Largest HCPCS exposure: {top_hcpcs.hcpcs_code} - {top_hcpcs.service_description}, variance ${top_hcpcs.total_financial_variance:,.0f}.
- Overpayment review flags: {len(overpayment):,}; underpayment review flags: {len(underpayment):,}.
- Largest scenario impact: {top_scenario.scenario_name}, ${top_scenario.dollar_impact:,.0f}.
- Next forecasted monthly benchmark variance: ${next_variance.forecast_value:,.0f}.

## Recommended Actions
1. Review Critical and High risk providers for contract repricing or documentation issues.
2. Prioritize HCPCS codes with high utilization-adjusted variance.
3. Investigate provider-service rows above 120% or below 80% of Medicare benchmark.
4. Use scenario impact outputs before approving reimbursement structure changes.
5. Refresh the benchmark package when new CMS public files or contract terms are available.
"""
    report_path.write_text(text)


def write_workbook(kpis: pd.DataFrame, provider: pd.DataFrame, hcpcs: pd.DataFrame, overpayment: pd.DataFrame, underpayment: pd.DataFrame, scenarios: pd.DataFrame, forecast: pd.DataFrame, workbook_path: Path) -> None:
    workbook_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        kpis.to_excel(writer, sheet_name="Executive Summary", index=False)
        provider.to_excel(writer, sheet_name="Provider Benchmarking", index=False)
        hcpcs.to_excel(writer, sheet_name="HCPCS Variance", index=False)
        overpayment.to_excel(writer, sheet_name="Overpayment Flags", index=False)
        underpayment.to_excel(writer, sheet_name="Underpayment Flags", index=False)
        scenarios.to_excel(writer, sheet_name="Scenario Impact", index=False)
        forecast.to_excel(writer, sheet_name="Forecast Summary", index=False)
        for sheet in writer.book.worksheets:
            sheet.freeze_panes = "A2"
            for cell in sheet[1]:
                cell.style = "Headline 3"
            for col in sheet.columns:
                width = min(max(max(len(str(cell.value)) if cell.value is not None else 0 for cell in col) + 2, 12), 38)
                sheet.column_dimensions[col[0].column_letter].width = width

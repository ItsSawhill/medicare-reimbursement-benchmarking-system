from pathlib import Path

from benchmarking import calculate_reimbursement_variance, provider_benchmarking
from cms_fee_schedule_loader import load_or_generate_fee_schedule
from cms_provider_payment_loader import load_cms_provider_payment
from forecasting import forecast_reimbursement
from preprocessing import clean_contract_rates
from provider_risk_scoring import add_provider_risk
from reporting import executive_kpis, save_figures, write_executive_summary, write_workbook
from scenario_modeling import scenario_impact_summary
from synthetic_contract_generator import generate_synthetic_contract_rates, save_sample_contracts
from variance_analysis import hcpcs_variance_analysis, overpayment_flags, underpayment_flags


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SAMPLE_DIR = BASE_DIR / "data" / "sample"
TABLE_DIR = BASE_DIR / "outputs" / "tables"
FIGURE_DIR = BASE_DIR / "outputs" / "figures"
REPORT_DIR = BASE_DIR / "outputs" / "reports"


def write_table(df, filename: str) -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLE_DIR / filename, index=False)


def main() -> None:
    for directory in [PROCESSED_DIR, SAMPLE_DIR, TABLE_DIR, FIGURE_DIR, REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    fee_schedule, fee_source = load_or_generate_fee_schedule(RAW_DIR / "cms_fee_schedule.csv")
    provider_payment, provider_source = load_cms_provider_payment(RAW_DIR / "cms_provider_service.csv")
    if not provider_payment.empty:
        fee_schedule = fee_schedule.merge(
            provider_payment.groupby("hcpcs_code").agg(
                medicare_benchmark_amount=("avg_medicare_allowed", "mean"),
                service_description=("service_description", "first"),
            ).reset_index(),
            on="hcpcs_code",
            how="left",
            suffixes=("", "_provider_public"),
        )
        fee_schedule["medicare_benchmark_amount"] = fee_schedule["medicare_benchmark_amount_provider_public"].fillna(
            fee_schedule["medicare_benchmark_amount"]
        )
        fee_schedule["service_description"] = fee_schedule["service_description_provider_public"].fillna(
            fee_schedule["service_description"]
        )
        fee_schedule = fee_schedule.drop(columns=["medicare_benchmark_amount_provider_public", "service_description_provider_public"])
        fee_schedule["benchmark_source"] = provider_source

    contracts = generate_synthetic_contract_rates(fee_schedule, n_rows=20000)
    contracts = clean_contract_rates(contracts)
    contracts.to_csv(PROCESSED_DIR / "contract_rates_clean.csv", index=False)
    save_sample_contracts(contracts, SAMPLE_DIR / "synthetic_contract_rates_sample.csv")

    variance = calculate_reimbursement_variance(contracts)
    provider = add_provider_risk(provider_benchmarking(variance))
    hcpcs = hcpcs_variance_analysis(variance)
    over = overpayment_flags(variance)
    under = underpayment_flags(variance)
    scenarios = scenario_impact_summary(variance)
    forecast, monthly_forecast_base = forecast_reimbursement(variance)
    kpis = executive_kpis(provider, variance, over, under, scenarios)

    write_table(variance, "reimbursement_variance.csv")
    write_table(provider, "provider_benchmarking.csv")
    write_table(hcpcs, "hcpcs_variance_analysis.csv")
    write_table(over, "overpayment_flags.csv")
    write_table(under, "underpayment_flags.csv")
    write_table(scenarios, "scenario_impact_summary.csv")
    write_table(forecast, "forecast_summary.csv")
    write_table(kpis, "executive_kpis.csv")

    save_figures(variance, provider, hcpcs, over, under, scenarios, monthly_forecast_base, forecast, FIGURE_DIR)
    write_executive_summary(provider, hcpcs, over, under, scenarios, forecast, REPORT_DIR / "executive_summary.md")
    write_workbook(kpis, provider, hcpcs, over, under, scenarios, forecast, REPORT_DIR / "executive_workbook.xlsx")

    print("Medicare reimbursement benchmarking pipeline completed.")
    print(f"Rows processed: {len(variance):,}")
    print(f"Fee schedule source: {fee_source}")
    print(f"Provider payment source: {provider_source}")
    print(f"Tables: {TABLE_DIR}")
    print(f"Figures: {FIGURE_DIR}")
    print(f"Reports: {REPORT_DIR}")


if __name__ == "__main__":
    main()

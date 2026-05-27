from pathlib import Path

import pandas as pd


def export_powerbi_star_schema(
    variance: pd.DataFrame,
    provider: pd.DataFrame,
    hcpcs: pd.DataFrame,
    overpayment: pd.DataFrame,
    underpayment: pd.DataFrame,
    scenarios: pd.DataFrame,
    forecast: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    dim_provider = provider[
        [
            "provider_id",
            "provider_name",
            "provider_type",
            "state",
            "total_services",
            "average_contract_to_medicare_ratio",
            "reimbursement_risk_score",
            "risk_tier",
            "recommended_action",
        ]
    ].drop_duplicates("provider_id")

    dim_hcpcs = hcpcs[
        [
            "hcpcs_code",
            "service_description",
            "service_category",
            "avg_medicare_benchmark",
            "avg_contract_to_medicare_ratio",
            "exposure_rank",
        ]
    ].drop_duplicates("hcpcs_code")

    dim_state = variance[["state"]].drop_duplicates().sort_values("state")
    dim_state["state_name"] = dim_state["state"]

    dim_time = variance[["service_month"]].drop_duplicates().copy()
    dim_time["month"] = pd.to_datetime(dim_time["service_month"]).dt.to_period("M").astype(str)
    dim_time["year"] = pd.to_datetime(dim_time["service_month"]).dt.year
    dim_time["quarter"] = pd.to_datetime(dim_time["service_month"]).dt.quarter
    dim_time["month_number"] = pd.to_datetime(dim_time["service_month"]).dt.month
    dim_time = dim_time[["month", "year", "quarter", "month_number"]].drop_duplicates().sort_values("month")

    fact_reimbursement = variance.copy()
    fact_reimbursement["month"] = pd.to_datetime(fact_reimbursement["service_month"]).dt.to_period("M").astype(str)
    fact_reimbursement = fact_reimbursement[
        [
            "provider_id",
            "hcpcs_code",
            "state",
            "month",
            "payer_product",
            "contract_type",
            "utilization_count",
            "billed_amount",
            "contract_allowed_amount",
            "contract_paid_amount",
            "medicare_benchmark_amount",
            "contract_total_paid",
            "medicare_total_benchmark",
            "contract_to_medicare_ratio",
            "dollar_variance",
            "percent_variance",
            "total_financial_variance",
            "benchmark_band",
            "over_benchmark_flag",
            "under_benchmark_flag",
        ]
    ]

    fact_scenario = scenarios.copy()
    fact_scenario["provider_id"] = pd.NA
    fact_scenario = fact_scenario[
        [
            "scenario_name",
            "provider_id",
            "baseline_spend",
            "simulated_spend",
            "dollar_impact",
            "percent_impact",
            "top_provider_impact",
            "top_hcpcs_impact",
            "top_service_category_impact",
        ]
    ]

    fact_forecast = forecast.copy()
    fact_forecast["month"] = pd.to_datetime(fact_forecast["forecast_month"]).dt.to_period("M").astype(str)
    fact_forecast = fact_forecast[["month", "metric", "forecast_value", "method"]]

    over = overpayment.copy()
    over["flag_type"] = "Overpayment"
    under = underpayment.copy()
    under["flag_type"] = "Underpayment"
    fact_flags = pd.concat([over, under], ignore_index=True)
    fact_flags["month"] = pd.to_datetime(fact_flags["service_month"]).dt.to_period("M").astype(str)
    fact_flags = fact_flags[
        [
            "flag_type",
            "provider_id",
            "hcpcs_code",
            "state",
            "month",
            "service_category",
            "benchmark_band",
            "utilization_count",
            "contract_to_medicare_ratio",
            "dollar_variance",
            "total_financial_variance",
        ]
    ]

    dim_provider.to_csv(output_dir / "dim_provider.csv", index=False)
    dim_hcpcs.to_csv(output_dir / "dim_hcpcs.csv", index=False)
    dim_state.to_csv(output_dir / "dim_state.csv", index=False)
    dim_time.to_csv(output_dir / "dim_time.csv", index=False)
    fact_reimbursement.to_csv(output_dir / "fact_reimbursement.csv", index=False)
    fact_scenario.to_csv(output_dir / "fact_scenario_impact.csv", index=False)
    fact_forecast.to_csv(output_dir / "fact_forecast.csv", index=False)
    fact_flags.to_csv(output_dir / "fact_flags.csv", index=False)

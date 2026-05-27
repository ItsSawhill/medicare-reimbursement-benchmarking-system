import numpy as np
import pandas as pd


def calculate_reimbursement_variance(contracts: pd.DataFrame) -> pd.DataFrame:
    frame = contracts.copy()
    frame["contract_to_medicare_ratio"] = frame["contract_allowed_amount"] / frame["medicare_benchmark_amount"].replace(0, pd.NA)
    frame["dollar_variance"] = frame["contract_allowed_amount"] - frame["medicare_benchmark_amount"]
    frame["percent_variance"] = frame["dollar_variance"] / frame["medicare_benchmark_amount"].replace(0, pd.NA)
    frame["total_financial_variance"] = frame["dollar_variance"] * frame["utilization_count"]
    frame["over_benchmark_flag"] = (frame["contract_to_medicare_ratio"] > 1.20).astype(int)
    frame["under_benchmark_flag"] = (frame["contract_to_medicare_ratio"] < 0.80).astype(int)
    frame["benchmark_band"] = np.select(
        [
            frame["contract_to_medicare_ratio"] < 0.80,
            frame["contract_to_medicare_ratio"] < 1.00,
            frame["contract_to_medicare_ratio"] <= 1.20,
            frame["contract_to_medicare_ratio"] > 1.20,
        ],
        ["below_80_percent_of_medicare", "80_to_100_percent", "100_to_120_percent", "above_120_percent"],
        default="unclassified",
    )
    return frame


def provider_benchmarking(variance: pd.DataFrame) -> pd.DataFrame:
    provider = variance.groupby(["provider_id", "provider_name", "provider_type", "state"]).agg(
        total_services=("utilization_count", "sum"),
        total_contract_paid=("contract_total_paid", "sum"),
        total_medicare_benchmark_amount=("medicare_total_benchmark", "sum"),
        total_dollar_variance=("total_financial_variance", "sum"),
        average_contract_to_medicare_ratio=("contract_to_medicare_ratio", "mean"),
        percent_services_above_benchmark=("over_benchmark_flag", "mean"),
        percent_services_below_benchmark=("under_benchmark_flag", "mean"),
    )
    provider["reimbursement_risk_score"] = (
        provider["average_contract_to_medicare_ratio"].sub(1).abs().rank(pct=True) * 40
        + provider["total_dollar_variance"].abs().rank(pct=True) * 35
        + provider["total_services"].rank(pct=True) * 25
    ).round(2)
    provider["recommended_action"] = np.select(
        [
            (provider["average_contract_to_medicare_ratio"] > 1.20) & (provider["total_dollar_variance"] > 0),
            provider["average_contract_to_medicare_ratio"] < 0.80,
            provider["reimbursement_risk_score"] >= 70,
        ],
        ["Review for potential overpayment / renegotiation", "Review for underpayment / access risk", "Prioritize for contract review"],
        default="Monitor",
    )
    return provider.reset_index().sort_values("reimbursement_risk_score", ascending=False)

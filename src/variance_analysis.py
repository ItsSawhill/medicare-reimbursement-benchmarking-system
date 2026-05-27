import pandas as pd


def hcpcs_variance_analysis(variance: pd.DataFrame) -> pd.DataFrame:
    hcpcs = variance.groupby(["hcpcs_code", "service_description", "service_category"]).agg(
        total_services=("utilization_count", "sum"),
        avg_contract_allowed=("contract_allowed_amount", "mean"),
        avg_medicare_benchmark=("medicare_benchmark_amount", "mean"),
        avg_contract_to_medicare_ratio=("contract_to_medicare_ratio", "mean"),
        total_financial_variance=("total_financial_variance", "sum"),
        overpayment_flags=("over_benchmark_flag", "sum"),
        underpayment_flags=("under_benchmark_flag", "sum"),
    )
    hcpcs["utilization_adjusted_variance"] = hcpcs["total_financial_variance"] / hcpcs["total_services"].replace(0, pd.NA)
    hcpcs["exposure_rank"] = hcpcs["total_financial_variance"].abs().rank(method="dense", ascending=False).astype(int)
    return hcpcs.reset_index().sort_values("exposure_rank")


def overpayment_flags(variance: pd.DataFrame) -> pd.DataFrame:
    return variance[
        (variance["over_benchmark_flag"].eq(1))
        | ((variance["utilization_count"] >= variance["utilization_count"].quantile(0.75)) & (variance["percent_variance"] > 0.15))
    ].sort_values("total_financial_variance", ascending=False)


def underpayment_flags(variance: pd.DataFrame) -> pd.DataFrame:
    return variance[
        (variance["under_benchmark_flag"].eq(1))
        | ((variance["utilization_count"] >= variance["utilization_count"].quantile(0.75)) & (variance["percent_variance"] < -0.15))
    ].sort_values("total_financial_variance")

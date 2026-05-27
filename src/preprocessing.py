import pandas as pd


REQUIRED_COLUMNS = {
    "provider_id",
    "provider_name",
    "provider_type",
    "state",
    "locality",
    "hcpcs_code",
    "service_description",
    "service_category",
    "contract_allowed_amount",
    "contract_paid_amount",
    "billed_amount",
    "utilization_count",
    "effective_date",
    "contract_type",
    "payer_product",
    "medicare_benchmark_amount",
}


def clean_contract_rates(contracts: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(contracts.columns)
    if missing:
        raise ValueError(f"Contract rate data is missing columns: {sorted(missing)}")
    frame = contracts.copy()
    frame["effective_date"] = pd.to_datetime(frame["effective_date"], errors="coerce")
    frame = frame.dropna(subset=["provider_id", "hcpcs_code", "effective_date"])
    for col in ["contract_allowed_amount", "contract_paid_amount", "billed_amount", "utilization_count", "medicare_benchmark_amount"]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce").fillna(0).clip(lower=0)
    frame["service_month"] = frame["effective_date"].dt.to_period("M").dt.to_timestamp()
    frame["contract_total_paid"] = frame["contract_paid_amount"] * frame["utilization_count"]
    frame["medicare_total_benchmark"] = frame["medicare_benchmark_amount"] * frame["utilization_count"]
    return frame

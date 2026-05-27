from pathlib import Path

import numpy as np
import pandas as pd


def generate_synthetic_contract_rates(fee_schedule: pd.DataFrame, n_rows: int = 20000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    providers = pd.DataFrame(
        {
            "provider_id": [f"PRV{i:03d}" for i in range(1, 61)],
            "provider_name": [f"Provider Network {i:02d}" for i in range(1, 61)],
            "provider_type": rng.choice(["Physician Group", "Hospital Outpatient", "Ambulatory Surgery", "Imaging Center", "Lab"], 60),
            "state": rng.choice(["MD", "VA", "PA", "NY", "NC", "FL"], 60),
            "contract_factor": rng.normal(1.08, 0.18, 60).clip(0.65, 1.65),
        }
    )
    providers.loc[providers["provider_id"].isin(["PRV004", "PRV017", "PRV043"]), "contract_factor"] *= 1.35
    providers.loc[providers["provider_id"].isin(["PRV011", "PRV029"]), "contract_factor"] *= 0.72

    schedule = fee_schedule.copy().reset_index(drop=True)
    provider_rows = providers.iloc[rng.integers(0, len(providers), n_rows)].reset_index(drop=True)
    service_rows = schedule.iloc[rng.integers(0, len(schedule), n_rows)].reset_index(drop=True)
    months = pd.date_range("2024-01-01", "2025-12-01", freq="MS")
    month_idx = rng.integers(0, len(months), n_rows)
    effective_dates = months[month_idx]
    trend = 1 + 0.004 * month_idx
    utilization = rng.poisson(lam=np.where(service_rows["service_category"].isin(["Professional", "Lab"]), 45, 18)) + 1
    utilization = np.where(service_rows["hcpcs_code"].isin(["99213", "99214"]), utilization * 2, utilization)
    contract_allowed = (
        service_rows["medicare_benchmark_amount"].to_numpy()
        * provider_rows["contract_factor"].to_numpy()
        * rng.normal(1.0, 0.09, n_rows)
        * trend
    ).clip(3)
    billed = contract_allowed * rng.normal(1.55, 0.25, n_rows).clip(1.05, 2.4)
    paid = contract_allowed * rng.normal(0.93, 0.04, n_rows).clip(0.75, 1.0)
    contract_type = rng.choice(["Fee Schedule", "Percent of Medicare", "Case Rate", "Negotiated Commercial"], n_rows)
    payer_product = rng.choice(["Commercial PPO", "Commercial HMO", "Medicare Advantage", "Exchange"], n_rows)

    return pd.DataFrame(
        {
            "provider_id": provider_rows["provider_id"],
            "provider_name": provider_rows["provider_name"],
            "provider_type": provider_rows["provider_type"],
            "state": provider_rows["state"],
            "locality": provider_rows["state"] + " Locality",
            "hcpcs_code": service_rows["hcpcs_code"],
            "service_description": service_rows["service_description"],
            "service_category": service_rows["service_category"],
            "contract_allowed_amount": contract_allowed.round(2),
            "contract_paid_amount": paid.round(2),
            "billed_amount": billed.round(2),
            "utilization_count": utilization.astype(int),
            "effective_date": effective_dates,
            "contract_type": contract_type,
            "payer_product": payer_product,
            "medicare_benchmark_amount": service_rows["medicare_benchmark_amount"].round(2),
            "benchmark_source": service_rows["benchmark_source"],
        }
    )


def save_sample_contracts(contracts: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    contracts.head(500).to_csv(path, index=False)

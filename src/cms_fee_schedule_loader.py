from pathlib import Path

import numpy as np
import pandas as pd


SIMULATED_SOURCE = "simulated_cms_style_fee_schedule"
CMS_FEE_SCHEDULE_SOURCE = "local_cms_physician_fee_schedule"


def load_cms_fee_schedule(path: Path | str | None) -> tuple[pd.DataFrame, str]:
    if path is None or not Path(path).exists():
        return pd.DataFrame(), SIMULATED_SOURCE

    fee_schedule = pd.read_csv(path)
    fee_schedule.columns = [c.strip().lower() for c in fee_schedule.columns]
    rename = {
        "hcpcs": "hcpcs_code",
        "procedure_code": "hcpcs_code",
        "benchmark_amount": "medicare_benchmark_amount",
        "payment_amount": "medicare_benchmark_amount",
        "description": "service_description",
    }
    fee_schedule = fee_schedule.rename(columns={k: v for k, v in rename.items() if k in fee_schedule.columns})
    required = {"hcpcs_code", "medicare_benchmark_amount", "year"}
    missing = required.difference(fee_schedule.columns)
    if missing:
        raise ValueError(f"CMS fee schedule file is missing required columns: {sorted(missing)}")

    if "service_description" not in fee_schedule.columns:
        fee_schedule["service_description"] = "CMS fee schedule service"
    if "locality" not in fee_schedule.columns:
        fee_schedule["locality"] = "National"
    if "state" not in fee_schedule.columns:
        fee_schedule["state"] = "NA"

    fee_schedule["hcpcs_code"] = fee_schedule["hcpcs_code"].astype(str).str.strip()
    fee_schedule["medicare_benchmark_amount"] = pd.to_numeric(fee_schedule["medicare_benchmark_amount"], errors="coerce")
    fee_schedule["year"] = pd.to_numeric(fee_schedule["year"], errors="coerce").astype("Int64")
    fee_schedule = fee_schedule.dropna(subset=["hcpcs_code", "medicare_benchmark_amount", "year"])
    fee_schedule = fee_schedule[fee_schedule["medicare_benchmark_amount"] >= 0]
    fee_schedule["benchmark_source"] = CMS_FEE_SCHEDULE_SOURCE
    return fee_schedule, CMS_FEE_SCHEDULE_SOURCE


def generate_sample_fee_schedule(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = [
        ("99213", "Office/outpatient established visit", "Professional", 92),
        ("99214", "Office/outpatient established visit high complexity", "Professional", 132),
        ("93000", "Electrocardiogram complete", "Diagnostic", 23),
        ("80053", "Comprehensive metabolic panel", "Lab", 14),
        ("71046", "Chest x-ray two views", "Imaging", 34),
        ("70551", "MRI brain without contrast", "Imaging", 235),
        ("27447", "Total knee arthroplasty", "Surgery", 1250),
        ("45378", "Diagnostic colonoscopy", "Outpatient", 390),
        ("J3490", "Unclassified drug", "Pharmacy", 115),
        ("A0429", "Ambulance basic life support", "Emergency", 310),
    ]
    states = ["MD", "VA", "PA", "NY", "NC", "FL"]
    records = []
    for hcpcs, desc, category, base in rows:
        for state in states:
            locality_factor = rng.normal(1.0, 0.08)
            records.append(
                {
                    "hcpcs_code": hcpcs,
                    "service_description": desc,
                    "service_category": category,
                    "medicare_benchmark_amount": round(max(5, base * locality_factor), 2),
                    "year": 2025,
                    "locality": f"{state} Locality",
                    "state": state,
                    "benchmark_source": SIMULATED_SOURCE,
                }
            )
    return pd.DataFrame(records)


def load_or_generate_fee_schedule(path: Path | str | None, seed: int = 42) -> tuple[pd.DataFrame, str]:
    loaded, source = load_cms_fee_schedule(path)
    if not loaded.empty:
        return loaded, source
    return generate_sample_fee_schedule(seed), SIMULATED_SOURCE

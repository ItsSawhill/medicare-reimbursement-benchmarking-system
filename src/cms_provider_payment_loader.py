from pathlib import Path

import pandas as pd


CMS_PROVIDER_SOURCE = "local_cms_provider_service_public_data"
SIMULATED_PROVIDER_SOURCE = "simulated_provider_payment_reference"


ALIASES = {
    "provider_npi": ["provider_npi", "npi", "rndrng_npi"],
    "provider_name": ["provider_name", "rndrng_prvdr_last_org_name", "provider_last_name_organization_name"],
    "provider_state": ["provider_state", "state", "rndrng_prvdr_state_abrvtn"],
    "hcpcs_code": ["hcpcs_code", "hcpcs_cd", "procedure_code"],
    "service_description": ["service_description", "hcpcs_desc", "hcpcs_description"],
    "number_of_services": ["number_of_services", "tot_srvcs", "total_services"],
    "submitted_charge_amount": ["submitted_charge_amount", "avg_sbmtd_chrg", "average_submitted_charge_amount"],
    "medicare_allowed_amount": ["medicare_allowed_amount", "avg_mdcr_alowd_amt", "average_medicare_allowed_amount"],
    "medicare_payment_amount": ["medicare_payment_amount", "avg_mdcr_pymt_amt", "average_medicare_payment_amount"],
}


def _normalize(column: str) -> str:
    value = column.strip().lower()
    for char in [" ", "-", "/", ".", "(", ")"]:
        value = value.replace(char, "_")
    while "__" in value:
        value = value.replace("__", "_")
    return value.strip("_")


def load_cms_provider_payment(path: Path | str | None) -> tuple[pd.DataFrame, str]:
    if path is None or not Path(path).exists():
        return pd.DataFrame(), SIMULATED_PROVIDER_SOURCE

    frame = pd.read_csv(path)
    frame.columns = [_normalize(c) for c in frame.columns]
    rename = {}
    for target, aliases in ALIASES.items():
        for alias in aliases:
            if _normalize(alias) in frame.columns:
                rename[_normalize(alias)] = target
                break
    frame = frame.rename(columns=rename)
    required = set(ALIASES)
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"CMS provider payment file is missing required columns: {sorted(missing)}")

    selected = frame[list(required)].copy()
    selected["hcpcs_code"] = selected["hcpcs_code"].astype(str).str.strip()
    selected["provider_state"] = selected["provider_state"].astype(str).str.upper().str.strip()
    for col in ["number_of_services", "submitted_charge_amount", "medicare_allowed_amount", "medicare_payment_amount"]:
        selected[col] = pd.to_numeric(selected[col], errors="coerce")
    selected = selected.dropna(subset=["hcpcs_code", "number_of_services"])
    selected = selected[selected["number_of_services"] > 0]
    selected["avg_submitted_charge"] = selected["submitted_charge_amount"]
    selected["avg_medicare_allowed"] = selected["medicare_allowed_amount"]
    selected["avg_medicare_payment"] = selected["medicare_payment_amount"]
    selected["benchmark_source"] = CMS_PROVIDER_SOURCE
    return selected, CMS_PROVIDER_SOURCE

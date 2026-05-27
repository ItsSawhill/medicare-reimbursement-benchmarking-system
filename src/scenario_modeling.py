import pandas as pd


def _impact_summary(frame: pd.DataFrame, scenario_name: str, group_cols: list[str]) -> pd.DataFrame:
    grouped = frame.groupby(group_cols).agg(
        baseline_spend=("baseline_spend", "sum"),
        simulated_spend=("simulated_spend", "sum"),
        utilization_count=("utilization_count", "sum"),
    )
    grouped["dollar_impact"] = grouped["simulated_spend"] - grouped["baseline_spend"]
    grouped["percent_impact"] = grouped["dollar_impact"] / grouped["baseline_spend"].replace(0, pd.NA)
    grouped["scenario_name"] = scenario_name
    return grouped.reset_index().sort_values("dollar_impact", key=lambda s: s.abs(), ascending=False)


def simulate_rate_change(variance: pd.DataFrame, percent_change: float = 0.05) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = variance.copy()
    frame["baseline_spend"] = frame["contract_total_paid"]
    frame["simulated_spend"] = frame["contract_total_paid"] * (1 + percent_change)
    scenario = f"All Rates {percent_change:+.0%}"
    return (
        _impact_summary(frame, scenario, ["provider_id", "provider_name"]),
        _impact_summary(frame, scenario, ["hcpcs_code", "service_description"]),
        _impact_summary(frame, scenario, ["service_category"]),
    )


def simulate_medicare_alignment(variance: pd.DataFrame, target_ratio: float = 1.0) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frame = variance.copy()
    frame["baseline_spend"] = frame["contract_total_paid"]
    frame["simulated_spend"] = frame["medicare_benchmark_amount"] * target_ratio * frame["utilization_count"]
    scenario = f"Align to {target_ratio:.0%} Medicare"
    return (
        _impact_summary(frame, scenario, ["provider_id", "provider_name"]),
        _impact_summary(frame, scenario, ["hcpcs_code", "service_description"]),
        _impact_summary(frame, scenario, ["service_category"]),
    )


def simulate_provider_contract_change(variance: pd.DataFrame, provider_id: str, percent_change: float = -0.05) -> pd.DataFrame:
    frame = variance.copy()
    frame["baseline_spend"] = frame["contract_total_paid"]
    frame["simulated_spend"] = frame["contract_total_paid"]
    mask = frame["provider_id"].eq(provider_id)
    frame.loc[mask, "simulated_spend"] = frame.loc[mask, "contract_total_paid"] * (1 + percent_change)
    return _impact_summary(frame, f"{provider_id} Contract {percent_change:+.0%}", ["provider_id", "provider_name"])


def simulate_service_category_change(variance: pd.DataFrame, service_category: str, percent_change: float = 0.05) -> pd.DataFrame:
    frame = variance.copy()
    frame["baseline_spend"] = frame["contract_total_paid"]
    frame["simulated_spend"] = frame["contract_total_paid"]
    mask = frame["service_category"].eq(service_category)
    frame.loc[mask, "simulated_spend"] = frame.loc[mask, "contract_total_paid"] * (1 + percent_change)
    return _impact_summary(frame, f"{service_category} {percent_change:+.0%}", ["service_category"])


def scenario_impact_summary(variance: pd.DataFrame) -> pd.DataFrame:
    top_provider = variance.groupby("provider_id")["contract_total_paid"].sum().idxmax()
    top_category = variance.groupby("service_category")["contract_total_paid"].sum().idxmax()
    scenarios = []
    for name, provider, hcpcs, category in [
        ("All Rates +5%", *simulate_rate_change(variance, 0.05)),
        ("All Rates -5%", *simulate_rate_change(variance, -0.05)),
        ("Align to 100% Medicare", *simulate_medicare_alignment(variance, 1.0)),
    ]:
        baseline = provider["baseline_spend"].sum()
        simulated = provider["simulated_spend"].sum()
        scenarios.append(
            {
                "scenario_name": name,
                "baseline_spend": baseline,
                "simulated_spend": simulated,
                "dollar_impact": simulated - baseline,
                "percent_impact": (simulated - baseline) / baseline if baseline else 0,
                "top_provider_impact": provider.iloc[0]["dollar_impact"],
                "top_hcpcs_impact": hcpcs.iloc[0]["dollar_impact"],
                "top_service_category_impact": category.iloc[0]["dollar_impact"],
            }
        )
    provider_change = simulate_provider_contract_change(variance, top_provider, -0.05)
    category_change = simulate_service_category_change(variance, top_category, 0.05)
    for name, frame in [(f"{top_provider} -5%", provider_change), (f"{top_category} +5%", category_change)]:
        baseline = frame["baseline_spend"].sum()
        simulated = frame["simulated_spend"].sum()
        scenarios.append(
            {
                "scenario_name": name,
                "baseline_spend": baseline,
                "simulated_spend": simulated,
                "dollar_impact": simulated - baseline,
                "percent_impact": (simulated - baseline) / baseline if baseline else 0,
                "top_provider_impact": frame.iloc[0]["dollar_impact"],
                "top_hcpcs_impact": pd.NA,
                "top_service_category_impact": pd.NA,
            }
        )
    return pd.DataFrame(scenarios)

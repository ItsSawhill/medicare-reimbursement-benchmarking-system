from pathlib import Path
import re
import subprocess
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "outputs" / "tables"
FIGURE_DIR = ROOT / "outputs" / "figures"
REPORT_DIR = ROOT / "outputs" / "reports"
POWERBI_DIR = ROOT / "outputs" / "powerbi"


def test_pipeline_runs():
    result = subprocess.run(
        [sys.executable, "src/run_pipeline.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "pipeline completed" in result.stdout


def test_required_output_files_exist():
    required = [
        TABLE_DIR / "provider_benchmarking.csv",
        TABLE_DIR / "hcpcs_variance_analysis.csv",
        TABLE_DIR / "reimbursement_variance.csv",
        TABLE_DIR / "overpayment_flags.csv",
        TABLE_DIR / "underpayment_flags.csv",
        TABLE_DIR / "scenario_impact_summary.csv",
        TABLE_DIR / "forecast_summary.csv",
        TABLE_DIR / "executive_kpis.csv",
        FIGURE_DIR / "contract_to_medicare_distribution.png",
        FIGURE_DIR / "top_provider_variance.png",
        FIGURE_DIR / "hcpcs_financial_exposure.png",
        FIGURE_DIR / "overpayment_underpayment_counts.png",
        FIGURE_DIR / "scenario_financial_impact.png",
        FIGURE_DIR / "forecast_variance_trend.png",
        REPORT_DIR / "executive_summary.md",
        REPORT_DIR / "executive_workbook.xlsx",
        POWERBI_DIR / "dim_provider.csv",
        POWERBI_DIR / "dim_hcpcs.csv",
        POWERBI_DIR / "dim_state.csv",
        POWERBI_DIR / "dim_time.csv",
        POWERBI_DIR / "fact_reimbursement.csv",
        POWERBI_DIR / "fact_scenario_impact.csv",
        POWERBI_DIR / "fact_forecast.csv",
        POWERBI_DIR / "fact_flags.csv",
    ]
    missing = [str(path) for path in required if not path.exists()]
    assert not missing, f"Missing outputs: {missing}"


def test_benchmark_ratios_calculate_correctly():
    variance = pd.read_csv(TABLE_DIR / "reimbursement_variance.csv")
    sample = variance.head(100)
    expected_ratio = sample["contract_allowed_amount"] / sample["medicare_benchmark_amount"]
    expected_dollar = sample["contract_allowed_amount"] - sample["medicare_benchmark_amount"]
    assert np.allclose(sample["contract_to_medicare_ratio"], expected_ratio, atol=0.001)
    assert np.allclose(sample["dollar_variance"], expected_dollar, atol=0.001)


def test_overpayment_underpayment_flags_generated():
    over = pd.read_csv(TABLE_DIR / "overpayment_flags.csv")
    under = pd.read_csv(TABLE_DIR / "underpayment_flags.csv")
    assert len(over) > 0
    assert len(under) > 0
    assert (over["contract_to_medicare_ratio"] > 1.0).any()
    assert (under["contract_to_medicare_ratio"] < 1.0).any()


def test_scenario_impact_math():
    scenarios = pd.read_csv(TABLE_DIR / "scenario_impact_summary.csv")
    diff = scenarios["simulated_spend"] - scenarios["baseline_spend"]
    assert np.allclose(diff, scenarios["dollar_impact"], atol=0.01)


def test_no_negative_payment_amounts():
    variance = pd.read_csv(TABLE_DIR / "reimbursement_variance.csv")
    assert (variance["contract_allowed_amount"] >= 0).all()
    assert (variance["contract_paid_amount"] >= 0).all()
    assert (variance["billed_amount"] >= 0).all()


def test_readme_image_paths_exist():
    readme = (ROOT / "README.md").read_text()
    image_paths = re.findall(r"\((outputs/figures/[^)]+\.png)\)", readme)
    missing = [path for path in image_paths if not (ROOT / path).exists()]
    assert not missing, f"README references missing images: {missing}"


def test_powerbi_outputs_exist_and_have_required_keys():
    assert POWERBI_DIR.exists()
    fact_reimbursement = pd.read_csv(POWERBI_DIR / "fact_reimbursement.csv")
    fact_scenario = pd.read_csv(POWERBI_DIR / "fact_scenario_impact.csv")
    fact_forecast = pd.read_csv(POWERBI_DIR / "fact_forecast.csv")
    fact_flags = pd.read_csv(POWERBI_DIR / "fact_flags.csv")

    assert {"provider_id", "hcpcs_code", "state", "month"}.issubset(fact_reimbursement.columns)
    assert {"scenario_name", "baseline_spend", "simulated_spend", "dollar_impact"}.issubset(fact_scenario.columns)
    assert {"month", "metric", "forecast_value"}.issubset(fact_forecast.columns)
    assert {"provider_id", "hcpcs_code", "state", "month", "flag_type"}.issubset(fact_flags.columns)


def test_powerbi_dimension_primary_keys_are_unique():
    dim_provider = pd.read_csv(POWERBI_DIR / "dim_provider.csv")
    dim_hcpcs = pd.read_csv(POWERBI_DIR / "dim_hcpcs.csv")
    dim_state = pd.read_csv(POWERBI_DIR / "dim_state.csv")
    dim_time = pd.read_csv(POWERBI_DIR / "dim_time.csv")

    assert dim_provider["provider_id"].is_unique
    assert dim_hcpcs["hcpcs_code"].is_unique
    assert dim_state["state"].is_unique
    assert dim_time["month"].is_unique


def test_powerbi_no_negative_reimbursement_amounts():
    fact = pd.read_csv(POWERBI_DIR / "fact_reimbursement.csv")
    for column in ["contract_allowed_amount", "contract_paid_amount", "contract_total_paid", "medicare_benchmark_amount"]:
        assert (fact[column] >= 0).all()


def test_powerbi_docs_exist():
    required_docs = [
        ROOT / "docs" / "powerbi_data_model.md",
        ROOT / "docs" / "powerbi_dashboard_spec.md",
        ROOT / "docs" / "powerbi_dax_measures.md",
        ROOT / "docs" / "power_query_steps.md",
    ]
    missing = [str(path) for path in required_docs if not path.exists()]
    assert not missing, f"Missing Power BI docs: {missing}"

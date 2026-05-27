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

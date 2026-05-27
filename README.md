# Medicare Reimbursement Benchmarking System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Healthcare](https://img.shields.io/badge/Healthcare-Reimbursement%20Analytics-2f6f8f)
![CMS](https://img.shields.io/badge/CMS-Public%20Benchmark%20Ready-1f7a5c)
![Status](https://img.shields.io/badge/Status-Portfolio%20Ready-6d8f3f)

An end-to-end Medicare reimbursement benchmarking system that compares synthetic provider contract rates against CMS-style Medicare benchmarks, detects overpayment/underpayment patterns, and models financial impact under reimbursement changes.

**Important:** Provider contract rates are synthetic. CMS integration is optional and public-data based. This project does not use private patient-level claims or actual hospital contract rates.

## Key Features

| Capability | What It Answers |
| --- | --- |
| Medicare Benchmarking | Which providers and services are above or below Medicare benchmark? |
| Provider Benchmarking | Which providers create the largest contract variance and financial exposure? |
| HCPCS Analysis | Which procedure codes drive over-Medicare or under-Medicare payment patterns? |
| Overpayment / Underpayment Detection | Which provider-service rows need reimbursement review? |
| Scenario Modeling | What happens if rates increase, decrease, or align to Medicare? |
| Forecasting | What is the projected monthly spend and benchmark variance? |
| Executive Reporting | What should leadership review first? |
| Streamlit Dashboard | How can analysts interactively review providers, HCPCS codes, flags, and scenarios? |
| SQL Layer | How would the same logic translate into warehouse reporting? |

## Quick Start

```bash
pip install -r requirements.txt
python src/run_pipeline.py
streamlit run app.py
```

Run tests:

```bash
pytest
```

## Example Business Questions

- Which providers are paid above or below Medicare benchmark?
- Which HCPCS/procedure codes create the largest reimbursement variance?
- Which providers have high financial exposure from contract changes?
- What is the projected impact of increasing or decreasing rates?
- Where are potential underpayment or overpayment patterns?
- What should leadership review first?

## Architecture

```mermaid
flowchart LR
    A[Optional CMS Public Data] --> C[Benchmark Data Layer]
    B[Synthetic Contract Rates] --> D[Preprocessing]
    C --> D
    D --> E[Medicare Benchmarking]
    E --> F[Provider + HCPCS Variance]
    F --> G[Overpayment / Underpayment Flags]
    F --> H[Scenario Modeling]
    F --> I[Forecasting]
    G --> J[Dashboard + Excel + Executive Report]
    H --> J
    I --> J
```

## Data Sources

The project supports optional local CMS public files:

- CMS Physician Fee Schedule: https://pfs.data.cms.gov/datasets
- CMS Physician Fee Schedule API information: https://pfs.data.cms.gov/about/api
- CMS Medicare Physician & Other Practitioners by Provider and Service: https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service

Expected optional files:

```text
data/raw/cms_fee_schedule.csv
data/raw/cms_provider_service.csv
```

If files are missing, the pipeline generates realistic CMS-style benchmark data and labels the source as simulated.

## Methodology

Core benchmark calculations:

```text
contract_to_medicare_ratio = contract_allowed_amount / medicare_benchmark_amount
dollar_variance = contract_allowed_amount - medicare_benchmark_amount
percent_variance = dollar_variance / medicare_benchmark_amount
total_financial_variance = dollar_variance * utilization_count
```

Benchmark bands:

- `below_80_percent_of_medicare`
- `80_to_100_percent`
- `100_to_120_percent`
- `above_120_percent`

Scenario models:

- all-rate increase/decrease
- Medicare alignment
- provider contract change
- service category change

## Dashboard

Launch with:

```bash
streamlit run app.py
```

Dashboard tabs:

- Executive Overview
- Provider Benchmarking
- HCPCS/Procedure Analysis
- Overpayment/Underpayment Flags
- Scenario Modeling
- Forecasts
- Data Dictionary

## Outputs

### Tables

```text
outputs/tables/provider_benchmarking.csv
outputs/tables/hcpcs_variance_analysis.csv
outputs/tables/reimbursement_variance.csv
outputs/tables/overpayment_flags.csv
outputs/tables/underpayment_flags.csv
outputs/tables/scenario_impact_summary.csv
outputs/tables/forecast_summary.csv
outputs/tables/executive_kpis.csv
```

### Figures

![Contract to Medicare Distribution](outputs/figures/contract_to_medicare_distribution.png)

![Top Provider Variance](outputs/figures/top_provider_variance.png)

![HCPCS Financial Exposure](outputs/figures/hcpcs_financial_exposure.png)

![Scenario Financial Impact](outputs/figures/scenario_financial_impact.png)

### Reports

```text
outputs/reports/executive_summary.md
outputs/reports/executive_workbook.xlsx
```

Workbook tabs:

- Executive Summary
- Provider Benchmarking
- HCPCS Variance
- Overpayment Flags
- Underpayment Flags
- Scenario Impact
- Forecast Summary

## SQL Layer

The `sql/` folder includes:

- reimbursement variance
- provider benchmarking
- HCPCS rate analysis
- contract impact model
- executive summary

## Repository Structure

```text
medicare-reimbursement-benchmarking-system/
├── app.py
├── README.md
├── requirements.txt
├── data/
├── docs/
├── outputs/
├── sql/
├── src/
└── tests/
```

## Resume Bullets

- Built a Medicare reimbursement benchmarking system using Python, SQL, Streamlit, and Excel-style reporting to compare synthetic provider contract rates against CMS-style Medicare benchmarks.
- Developed provider and HCPCS variance analytics, overpayment/underpayment detection, reimbursement risk scoring, and financial impact scenario modeling for payer/provider decision support.
- Created executive-ready dashboards, forecasts, SQL reporting scripts, and workbook outputs for reimbursement leadership review.

## Limitations

- Synthetic contract rates are not actual payer or hospital contracts.
- CMS public data is optional and must be downloaded locally by the user.
- Public CMS provider/service data is aggregated and not patient-level claims data.
- Forecasts are baseline planning estimates and do not claim model accuracy without backtesting.

## Future Improvements

- Add locality, modifier, facility/non-facility, and year-specific Physician Fee Schedule logic.
- Add provider specialty and place-of-service normalization.
- Add contract term and fee schedule version tracking.
- Add forecast backtesting and confidence intervals.

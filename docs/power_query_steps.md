# Power Query Steps

## Import CSVs

1. Open Power BI Desktop.
2. Select **Get Data > Text/CSV**.
3. Import each CSV from:

```text
outputs/powerbi/
```

Required files:

- `dim_provider.csv`
- `dim_hcpcs.csv`
- `dim_state.csv`
- `dim_time.csv`
- `fact_reimbursement.csv`
- `fact_scenario_impact.csv`
- `fact_forecast.csv`
- `fact_flags.csv`

## Set Data Types

Recommended types:

- IDs and codes: Text
- Month: Text or Date using first day of month
- Currency fields: Decimal Number or Fixed Decimal Number
- Ratios and percentages: Decimal Number
- Counts: Whole Number
- Flags: Whole Number

## Create Relationships

Create these relationships in Model view:

- `fact_reimbursement.provider_id` to `dim_provider.provider_id`
- `fact_reimbursement.hcpcs_code` to `dim_hcpcs.hcpcs_code`
- `fact_reimbursement.state` to `dim_state.state`
- `fact_reimbursement.month` to `dim_time.month`
- `fact_flags.provider_id` to `dim_provider.provider_id`
- `fact_flags.hcpcs_code` to `dim_hcpcs.hcpcs_code`
- `fact_flags.state` to `dim_state.state`
- `fact_flags.month` to `dim_time.month`
- `fact_forecast.month` to `dim_time.month`

Use single-direction filtering from dimensions to facts.

## Refresh Workflow

1. Rerun the Python pipeline:

```bash
python src/run_pipeline.py
```

2. Open the Power BI report.
3. Click **Refresh**.
4. Validate totals against `outputs/tables/executive_kpis.csv`.

## Publishing Notes

The `.pbix` file is not committed by default. If a Power BI file is created manually, store it outside git or commit it only if the file size and privacy rules are acceptable.

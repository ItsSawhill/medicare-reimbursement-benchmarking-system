# Power BI DAX Measures

```DAX
Total Contract Paid =
SUM ( fact_reimbursement[contract_total_paid] )
```

```DAX
Total Medicare Benchmark =
SUM ( fact_reimbursement[medicare_total_benchmark] )
```

```DAX
Dollar Variance =
SUM ( fact_reimbursement[total_financial_variance] )
```

```DAX
Percent Variance =
DIVIDE ( [Dollar Variance], [Total Medicare Benchmark] )
```

```DAX
Avg Contract to Medicare Ratio =
AVERAGE ( fact_reimbursement[contract_to_medicare_ratio] )
```

```DAX
Total Utilization =
SUM ( fact_reimbursement[utilization_count] )
```

```DAX
Overpayment Count =
CALCULATE (
    COUNTROWS ( fact_flags ),
    fact_flags[flag_type] = "Overpayment"
)
```

```DAX
Underpayment Count =
CALCULATE (
    COUNTROWS ( fact_flags ),
    fact_flags[flag_type] = "Underpayment"
)
```

```DAX
Net Financial Impact =
SUM ( fact_scenario_impact[dollar_impact] )
```

```DAX
Forecasted Spend =
CALCULATE (
    SUM ( fact_forecast[forecast_value] ),
    fact_forecast[metric] = "monthly_reimbursement_spend"
)
```

```DAX
Forecasted Benchmark Variance =
CALCULATE (
    SUM ( fact_forecast[forecast_value] ),
    fact_forecast[metric] = "monthly_benchmark_variance"
)
```

```DAX
Provider Risk Score =
AVERAGE ( dim_provider[reimbursement_risk_score] )
```

```DAX
High Risk Provider Count =
CALCULATE (
    DISTINCTCOUNT ( dim_provider[provider_id] ),
    dim_provider[risk_tier] IN { "Critical", "High" }
)
```

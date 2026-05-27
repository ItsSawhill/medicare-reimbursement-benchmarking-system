# Methodology

## Benchmarking

The core comparison is contract allowed amount versus Medicare benchmark amount:

```text
contract_to_medicare_ratio = contract_allowed_amount / medicare_benchmark_amount
dollar_variance = contract_allowed_amount - medicare_benchmark_amount
percent_variance = dollar_variance / medicare_benchmark_amount
total_financial_variance = dollar_variance * utilization_count
```

## Benchmark Bands

- `below_80_percent_of_medicare`
- `80_to_100_percent`
- `100_to_120_percent`
- `above_120_percent`

## Flagging

Overpayment candidates are provider-service rows above 120% of Medicare or high-utilization rows more than 15% above benchmark.

Underpayment candidates are provider-service rows below 80% of Medicare or high-utilization rows more than 15% below benchmark.

## Scenario Modeling

The scenario layer estimates financial impact for rate changes, Medicare alignment, provider-level contract changes, and service-category changes. Outputs include baseline spend, simulated spend, dollar impact, percent impact, provider impact, HCPCS impact, and service-category impact.

## Forecasting

Forecasts use a practical baseline that blends a three-month rolling average, exponential smoothing, and recent trend. No model accuracy metric is claimed without backtesting.

-- Executive KPI summary.

SELECT
    SUM(contract_paid_amount * utilization_count) AS total_contract_paid,
    SUM(medicare_benchmark_amount * utilization_count) AS total_medicare_benchmark,
    SUM((contract_allowed_amount - medicare_benchmark_amount) * utilization_count) AS total_financial_variance,
    AVG(contract_allowed_amount / NULLIF(medicare_benchmark_amount, 0)) AS average_contract_to_medicare_ratio,
    SUM(CASE WHEN contract_allowed_amount / NULLIF(medicare_benchmark_amount, 0) > 1.20 THEN 1 ELSE 0 END) AS overpayment_flag_count,
    SUM(CASE WHEN contract_allowed_amount / NULLIF(medicare_benchmark_amount, 0) < 0.80 THEN 1 ELSE 0 END) AS underpayment_flag_count
FROM contract_rates_clean;

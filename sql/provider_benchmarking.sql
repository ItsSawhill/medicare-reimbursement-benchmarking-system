-- Provider reimbursement benchmarking summary.

SELECT
    provider_id,
    provider_name,
    provider_type,
    state,
    SUM(utilization_count) AS total_services,
    SUM(contract_paid_amount * utilization_count) AS total_contract_paid,
    SUM(medicare_benchmark_amount * utilization_count) AS total_medicare_benchmark_amount,
    SUM((contract_allowed_amount - medicare_benchmark_amount) * utilization_count) AS total_dollar_variance,
    AVG(contract_allowed_amount / NULLIF(medicare_benchmark_amount, 0)) AS average_contract_to_medicare_ratio,
    AVG(CASE WHEN contract_allowed_amount / NULLIF(medicare_benchmark_amount, 0) > 1.20 THEN 1.0 ELSE 0.0 END) AS percent_services_above_benchmark,
    AVG(CASE WHEN contract_allowed_amount / NULLIF(medicare_benchmark_amount, 0) < 0.80 THEN 1.0 ELSE 0.0 END) AS percent_services_below_benchmark
FROM contract_rates_clean
GROUP BY provider_id, provider_name, provider_type, state
ORDER BY ABS(SUM((contract_allowed_amount - medicare_benchmark_amount) * utilization_count)) DESC;

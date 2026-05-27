-- HCPCS/procedure rate and exposure analysis.

SELECT
    hcpcs_code,
    service_description,
    service_category,
    SUM(utilization_count) AS total_services,
    AVG(contract_allowed_amount) AS avg_contract_allowed,
    AVG(medicare_benchmark_amount) AS avg_medicare_benchmark,
    AVG(contract_allowed_amount / NULLIF(medicare_benchmark_amount, 0)) AS avg_contract_to_medicare_ratio,
    SUM((contract_allowed_amount - medicare_benchmark_amount) * utilization_count) AS total_financial_variance
FROM contract_rates_clean
GROUP BY hcpcs_code, service_description, service_category
ORDER BY ABS(SUM((contract_allowed_amount - medicare_benchmark_amount) * utilization_count)) DESC;

-- Contract-to-Medicare reimbursement variance by provider-service row.

SELECT
    provider_id,
    provider_name,
    hcpcs_code,
    service_category,
    contract_allowed_amount,
    medicare_benchmark_amount,
    contract_allowed_amount / NULLIF(medicare_benchmark_amount, 0) AS contract_to_medicare_ratio,
    contract_allowed_amount - medicare_benchmark_amount AS dollar_variance,
    (contract_allowed_amount - medicare_benchmark_amount) / NULLIF(medicare_benchmark_amount, 0) AS percent_variance,
    (contract_allowed_amount - medicare_benchmark_amount) * utilization_count AS total_financial_variance
FROM contract_rates_clean;

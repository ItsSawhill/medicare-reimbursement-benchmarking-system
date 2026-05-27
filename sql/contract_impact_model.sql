-- Simple financial impact model for a reimbursement rate change.
-- Replace 0.05 with the target rate change.

SELECT
    provider_id,
    provider_name,
    SUM(contract_paid_amount * utilization_count) AS baseline_spend,
    SUM(contract_paid_amount * utilization_count) * (1 + 0.05) AS simulated_spend,
    SUM(contract_paid_amount * utilization_count) * 0.05 AS dollar_impact,
    0.05 AS percent_impact
FROM contract_rates_clean
GROUP BY provider_id, provider_name
ORDER BY ABS(SUM(contract_paid_amount * utilization_count) * 0.05) DESC;

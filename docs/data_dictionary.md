# Data Dictionary

| Field | Description |
| --- | --- |
| provider_id | Synthetic provider identifier. |
| provider_name | Synthetic provider display name. |
| provider_type | Provider type such as physician group, hospital outpatient, imaging center, or lab. |
| state | Provider state. |
| locality | Synthetic or CMS locality value. |
| hcpcs_code | HCPCS/procedure code used for Medicare benchmarking. |
| service_description | Procedure/service description. |
| service_category | Business grouping for service-line analysis. |
| contract_allowed_amount | Synthetic contracted allowed amount. |
| contract_paid_amount | Synthetic paid amount. |
| billed_amount | Synthetic submitted charge. |
| utilization_count | Service volume used for exposure weighting. |
| effective_date | Contract effective month. |
| contract_type | Synthetic contract type. |
| payer_product | Synthetic payer product. |
| medicare_benchmark_amount | CMS public benchmark amount if supplied locally, otherwise simulated CMS-style benchmark. |
| contract_to_medicare_ratio | Contract allowed amount divided by Medicare benchmark amount. |
| dollar_variance | Contract allowed amount minus Medicare benchmark amount. |
| total_financial_variance | Dollar variance multiplied by utilization count. |
| benchmark_band | Contract-to-Medicare band used for overpayment/underpayment review. |

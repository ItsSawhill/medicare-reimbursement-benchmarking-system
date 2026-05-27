# CMS Data Sources

This project is designed for optional CMS public data integration. It does not use private patient-level claims or actual hospital contract rates.

## CMS Physician Fee Schedule

Official references:

- https://pfs.data.cms.gov/datasets
- https://pfs.data.cms.gov/about/api

Optional local file:

```text
data/raw/cms_fee_schedule.csv
```

Recommended columns:

- `hcpcs_code`
- `service_description`
- `medicare_benchmark_amount`
- `year`
- optional `locality`
- optional `state`

## CMS Medicare Physician & Other Practitioners by Provider and Service

Official source:

https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service

Optional local file:

```text
data/raw/cms_provider_service.csv
```

The loader supports common CMS export names such as `Rndrng_NPI`, `HCPCS_Cd`, `HCPCS_Desc`, `Tot_Srvcs`, `Avg_Sbmtd_Chrg`, `Avg_Mdcr_Alowd_Amt`, and `Avg_Mdcr_Pymt_Amt`.

## Fallback Mode

If local CMS files are not present, the pipeline generates CMS-style benchmark data and labels it as simulated. This keeps the project reproducible for portfolio review and CI.

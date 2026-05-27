# Raw Data

This folder is for optional local CMS public data files. Large raw CMS files are intentionally ignored by git.

## Optional CMS Files

### Medicare Physician Fee Schedule

Official source:

- https://pfs.data.cms.gov/datasets
- https://pfs.data.cms.gov/about/api

Expected optional filename:

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

### Medicare Physician & Other Practitioners by Provider and Service

Official source:

https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service

Expected optional filename:

```text
data/raw/cms_provider_service.csv
```

If these files are absent, the pipeline generates CMS-style simulated benchmark data and clearly labels it as simulated.

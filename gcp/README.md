
# GCP Deployment Guide

## 1. Prerequisites
- Google Cloud Platform Account
- `gcloud` CLI installed
- Terraform installed

## 2. Infrastructure Setup (Terraform)
Navigate to `gcp/terraform` and run:

```bash
terraform init
terraform plan
terraform apply
```

This will create:
- Cloud Storage Bucket: `finance-data-raw`
- BigQuery Dataset: `finance_dw`
- Cloud Function: `trigger-etl`

## 3. Deploy Cloud Function
The ETL logic can be wrapped in a Cloud Function triggered by GCS file upload.

```bash
gcloud functions deploy finance-etl \
  --runtime python310 \
  --trigger-resource finance-data-raw \
  --trigger-event google.storage.object.finalize \
  --entry-point main
```

## 4. BigQuery Connection
Use Looker Studio to connect directly to the BigQuery `finance_dw` dataset for live dashboards.

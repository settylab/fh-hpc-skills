# Uploading Data to Fred Hutch cBioPortal

Source: https://sciwiki.fredhutch.org/pathways/path-cbio-fh-instance/

## Key Facts

- Fred Hutch cBioPortal instance is at https://cbioportal.fredhutch.org
- IRB approval is required when working with human subjects research data
- Upload uses AWS S3 bucket `fh-dasl-cbio` (write-only access)
- An automated pipeline validates and loads uploaded data; users receive a validation email
- Requires a Fred Hutch AWS lab account with individual AWS credentials

## Steps

1. Request upload access via RedCap form at redcap.fredhutch.org (Data Governance & Protection team approves)
2. Set up AWS credentials for the team's Fred Hutch AWS lab account
3. Request write-only access to S3 bucket `fh-dasl-cbio` via Slack #cbioportal-support
4. Prepare study files following cBioPortal data structure requirements
5. Upload compressed study data

## Minimum Required Files

- `meta_study.txt`
- `meta_clinical_sample.txt` and `data_clinical_sample.txt`
- `case_lists/cases_sequenced.txt`

## Commands & Examples

```bash
# Compress study directory
cd /path/to/folder
zip -r cancer_study_identifier.zip cancer_study_identifier

# Upload via AWS CLI
aws s3 cp cancer_study_identifier.zip s3://fh-dasl-cbio/

# Alternative upload methods:
# - Motuz: https://motuz.fredhutch.org
# - Mountain Duck: mount S3 bucket as local drive
```

## Common Pitfalls

- Not getting IRB approval before uploading human subjects data
- Missing required metadata files (validation will fail)
- Not having individual AWS credentials set up (team-level account alone is insufficient)
- Uploading uncompressed directories instead of zip files

## Cross-references

- AWS credentials: /scicomputing/access_credentials/
- Data storage: /scicomputing/store_objectstore/
- Support: Slack #cbioportal-support, dataprotection@fredhutch.org

# UCSC Genome Browser Tracks via S3

Source: https://sciwiki.fredhutch.org/compdemos/ucsc-track-s3/

## Overview

Upload genomic tracks to UCSC Genome Browser using Amazon S3 storage. Two options: Custom Tracks (quick viewing) or Track Hubs (sustainable).

## SECURITY WARNING

Never upload data containing PHI/PII or requiring HIPAA compliance.

## Upload Commands

```bash
ml purge
ml awscli

# Single files
aws s3 cp vcfs/foo.vcf.gz s3://fh-pi-doe-j-eco-public/ucsc-tracks/
aws s3 cp vcfs/foo.vcf.gz.tbi s3://fh-pi-doe-j-eco-public/ucsc-tracks/

# Multiple files/directories
aws s3 sync hub s3://fh-pi-doe-j-eco-public/track-hub/ --acl public-read
```

## Setup

1. Configure S3 credentials
2. Upload to PI's public S3 bucket
3. Email CLD team to enable public sharing (buckets restrict external access by default)
4. Use `--acl public-read` flag

Resulting URLs: `https://[bucket-name].s3.amazonaws.com/[path]/[filename]`

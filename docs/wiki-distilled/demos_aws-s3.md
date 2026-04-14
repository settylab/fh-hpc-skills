# AWS S3 Access from Fred Hutch

Source: https://sciwiki.fredhutch.org/compdemos/aws-s3/

## Overview

Access AWS S3 object storage via CLI, Python (boto3), and R (aws.s3). Requires AWS credentials configured first.

## AWS CLI

```bash
# Upload
aws s3 cp hello.txt s3://fh-pi-doe-j-eco/
aws s3 cp hello.txt s3://fh-pi-doe-j-eco/a/b/c/  # nested (auto-creates path)

# Download
aws s3 cp s3://fh-pi-doe-j-eco/hello.txt .

# List
aws s3 ls s3://fh-pi-doe-j-eco/
aws s3 ls --recursive --summarize --human-readable s3://fh-pi-doe-j-eco/

# Cross-lab bucket access (ACL required)
aws s3 cp --acl bucket-owner-full-control s3://fh-pi-doe-j-eco/test.txt s3://fh-pi-heisenberg-w-eco/
```

Trailing `/` on destination path matters: without it, the file is renamed to the destination name.

Warning: Large bucket listings may take hours. AWS paginates results.

## Python (boto3)

```python
import boto3
import pandas as pd
from io import StringIO, BytesIO

s3 = boto3.client("s3")
s3_resource = boto3.resource('s3')
bucket_name = "fh-pi-doe-j-eco"

# List buckets
response = s3.list_buckets()
for bucket in response['Buckets']:
    print(bucket['Name'])

# List objects (first 1000; use paginator for more)
paginator = s3.get_paginator('list_objects_v2')
for page in paginator.paginate(Bucket=bucket_name):
    for item in page['Contents']:
        print(item['Key'])

# Save DataFrame to S3
df = pd.DataFrame(...)
csv_buffer = StringIO()
df.to_csv(csv_buffer)
s3_resource.Object(bucket_name, 'df.csv').put(Body=csv_buffer.getvalue())

# Read CSV from S3
obj = s3.get_object(Bucket=bucket_name, Key="df.csv")
df2 = pd.read_csv(BytesIO(obj['Body'].read()))

# Upload/download files
s3.upload_file("df.csv", Bucket=bucket_name, Key="df.csv")
s3.download_file(bucket_name, "df.csv", "df.csv")
```

Use Dask for datasets larger than memory.

## R (aws.s3)

```r
# Setup with SSO
# ml purge && ml awscli && aws sso login && ml fhR && R

library(aws.s3)
b <- 'fh-pi-doe-j-eco'

# List buckets and objects
blist <- bucketlist()
objects <- get_bucket(b)
df <- get_bucket_df(b)

# Save/load R objects
s3save(df, bucket=b, object="foo/bar/baz/df")
s3load(object="foo/bar/baz/df", bucket=b)

# Upload/download files
put_object("df.csv", "foo/bar/baz/df.csv", b)
save_object("foo/bar/baz/df.csv", b)

# Read CSV directly
df <- s3read_using(read.csv, object="foo/bar/baz/df.csv", bucket=b)
```

Note: `paws` package works without extra SSO setup; `aws.s3` requires extracting credentials from SSO cache.

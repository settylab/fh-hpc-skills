# AWS CLI on Windows Subsystem for Linux

Source: https://sciwiki.fredhutch.org/compdemos/AWSCLI_WSL/

## Installation

```bash
# Install WSL
wsl --install

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version

# Configure
aws configure
# Region: us-west-2
```

## File Access

Windows files accessible via `/mnt/c`.

## S3 Commands

```bash
aws s3 mv s3://source-bucket/file s3://target-bucket/
aws s3 cp test.txt s3://mybucket/test2.txt
aws s3 cp s3://source-bucket/file s3://target-bucket/
aws s3 ls
aws s3 rb s3://mybucket
```

Keys expire after 6 months. Do not share keys.

# Motuz Data Transfer

Source: https://sciwiki.fredhutch.org/compdemos/motuz/

## Overview

Motuz is a web-based data transfer tool at https://motuz.fredhutch.org (campus network/VPN required). Authenticate with HutchNet credentials.

## Supported Storage Systems

- Campus shared filesystems (home, `/fh/fast`, `/hpc/temp`)
- Amazon S3
- Azure Blob Storage
- Google Cloud Bucket
- SFTP
- WebDAV
- Dropbox (Beta)
- Microsoft OneDrive (Beta)

## AWS S3 Connection Setup

### Authentication Methods

1. **SSO** (default since 2024): Lasts 12 hours
2. **IAM Access Key Pairs**: Non-expiring, for long-running transfers

### Configuration Steps

1. Access AWS SSO Portal: https://d-92674cb6d7.awsapps.com/start/#/?tab=accounts
2. In Motuz, go to "Cloud Connections" > "New Connection"
3. Change "S3 Connection Type" to "Temporary Security Credentials (STS)"
4. Copy credentials from AWS (access key ID, secret key, session token)
5. Set Type to "Amazon Simple Storage Service (s3)"
6. Enter bucket name (format: `fh-pi-lastname-initial-eco`)
7. Click "Verify Connection" then "Create Cloud Connection"

### KMS Encryption Fix

If seeing "corrupted on transfer: md5 hash differ" errors:
1. Go to AWS SSO Portal > S3 > bucket > Properties > Default Encryption
2. Copy Encryption key ARN
3. Paste into Motuz "KMS Encryption key ARN" field

## Transfer Operations

Two-pane UI: left pane = source, right pane = destination. Blue arrows initiate transfers in either direction.

## API Access

API endpoint: `https://motuz.fredhutch.org/api/`
Documentation: https://github.com/FredHutch/motuz/#how-to-use-the-api

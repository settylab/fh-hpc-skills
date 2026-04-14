# Sharing Data via Pre-Signed URLs

Source: https://sciwiki.fredhutch.org/compdemos/sharing-data-presigned-url/

## Overview

AWS pre-signed URLs grant temporary access to specific S3 objects without modifying bucket policies. Support both GET (download) and PUT (upload) operations.

## Requirements

- An S3 bucket
- Object key (filename)
- HTTP method (GET or PUT)
- Expiration timeframe (max 7 days)

## Security

- RESTRICTED to non-sensitive data only (no PHI/PII)
- Maximum validity: 7 days
- Access tracking is difficult post-creation
- Compromised URLs enable unauthorized access until expiration
- For systematic collaboration, contact IT for permanent bucket policies

## Usage

Pre-signed URLs work as standard web addresses with browsers, `wget`, and `curl`. Generate via AWS Console, CLI, or SDK.

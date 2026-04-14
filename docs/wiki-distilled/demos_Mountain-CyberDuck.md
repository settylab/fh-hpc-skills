# Mountain Duck and Cyberduck for S3 Access

Source: https://sciwiki.fredhutch.org/compdemos/Mountain-CyberDuck/

## Overview

Two GUI clients for accessing Economy Cloud (AWS S3) storage.

- **Mountain Duck**: Maps S3 as a drive in Windows Explorer or Mac Finder. Upload ~5MB/s, download ~20MB/s.
- **Cyberduck**: File transfer tool, 5-10x faster than Mountain Duck. Free at https://cyberduck.io/.

## Configuration

Both clients: Select "Amazon S3", enter AWS Access Key ID and Secret Access Key, create a bookmark.

## SSO Configuration

1. Configure AWS CLI access with SSO
2. Retrieve access keys from AWS IAM Identity Center
3. Add profile to `~/.aws/credentials`
4. Select "S3 (Credentials from AWS Command Line Interface)" in Mountain Duck
5. Reference the profile name

SSO credentials require periodic re-authentication when tokens expire.

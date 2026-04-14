---
description: "Managing Fred Hutch HutchNet credentials, Slurm cluster access, GitHub org membership, and MFA"
---

# Fred Hutch Credentials Management

## HutchNet ID

Your HutchNet ID is the universal credential issued when you join Fred Hutch. It provides access to:

- Network and WiFi
- Rhino and Gizmo compute clusters
- Email and institutional services
- AWS (via SSO) and other cloud resources

### For Collaborators / Non-Employees

External collaborators need a non-employee action form to get HutchNet credentials. Contact your PI or admin to initiate.

## Slurm Cluster Access

Your HutchNet ID must be associated with a PI's Slurm account before you can submit jobs.

### Setup via Self-Service Portal

Use the **SciComp Self-Service** portal to:

1. Add yourself (or lab members) to a PI's Slurm account
2. Enable cluster access
3. Verify access for the "Intro to Fred Hutch Cluster Computing" workshop

### Troubleshooting

If you see this error when submitting jobs:

```
Invalid account or account/partition
```

Your HutchNet ID is not linked to a PI account. Use the SciComp Self-Service portal to fix this, or email scicomp@fredhutch.org.

## GitHub Organization

Fred Hutch has an official GitHub organization at **github.com/FredHutch** with public and private repositories.

### Joining

1. Create a GitHub.com account (or use your existing one)
2. Email scicomp@fredhutch.org with your GitHub username
3. SciComp will add you to the FredHutch organization

### Security Rules

**Never commit secrets to GitHub repositories.** Structure code so that credentials, API keys, and tokens are loaded from:

- Environment variables
- External config files (added to `.gitignore`)

```bash
# Good: load from environment
export AWS_PROFILE=my-profile

# Bad: hardcoded in source
aws_key = "AKIA..."  # NEVER DO THIS
```

## AWS Credentials

Each Fred Hutch employee can get personal AWS credentials through the **MyApps** portal using their HutchNet ID.

### Lab AWS Account Format

```
fh-pi-lastname-f
```

### AWS CLI SSO Setup (One-Time)

```bash
# SSH into rhino first
ssh HutchID@rhino

# Load the AWS CLI module
ml awscli
aws --version

# Configure SSO (interactive)
aws configure sso
```

When prompted, provide:
- **Session name**: any descriptive name
- **SSO start URL**: get this from MyApps portal
- **SSO region**: `us-west-2`

The command opens a browser for authentication. Select your AWS account and role, then set a profile name.

### Refreshing Expired Credentials

```bash
aws sso login --profile <profile-name>
```

### Testing S3 Access

```bash
# Upload
echo hello | aws s3 cp - s3://fh-pi-lastname-f-eco/hello.txt

# Download
aws s3 cp s3://fh-pi-lastname-f-eco/hello.txt .
cat hello.txt

# Cleanup
aws s3 rm s3://fh-pi-lastname-f-eco/hello.txt
```

### Motuz (Data Transfer Tool)

When using Motuz with AWS, select the **Temporary Security Credentials (STS)** option and provide:

- Access Key ID
- Secret Access Key
- Session Token

Get these from the SSO portal (Option 3). **Credentials expire after 8 hours** and must be refreshed.

## File System Permissions

Fred Hutch storage uses UNIX ACLs organized by PI:

- PI directories: `/path/lastname_f/`
- Group: `lastname_f_grp` (contains lab members)
- Subfolders can have distinct ACLs for collaborations

### Checking Permissions

```bash
ls -la /path/to/directory
getfacl /path/to/directory
```

### Access Issues

Email scicomp@fredhutch.org with:
1. The folder path you need access to
2. Error messages you received
3. CC the PI or manager associated with the storage

## Common Pitfalls

- **Slurm "Invalid account" errors** mean your HutchNet ID is not linked to a PI. Fix via Self-Service portal.
- **Never share AWS credentials** via email, Slack, or GitHub.
- **Motuz STS tokens expire after 8 hours.** Refresh before long transfers.
- **Subfolder ACLs may differ from parent directory.** Do not assume inherited permissions.
- **GitHub org membership requires manual request** to scicomp. It is not automatic.

## Reference Links

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/access_credentials/
- SciComp Wiki (Permissions): https://sciwiki.fredhutch.org/scicomputing/access_permissions/

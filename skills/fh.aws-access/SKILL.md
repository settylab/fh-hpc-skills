---
description: "AWS account access, SSO login, S3 storage, Batch compute, and cost management at Fred Hutch"
---

# AWS Access at Fred Hutch

## Account Types

### Lab Account (Most Common)

Granted to any PI via helpdesk ticket. Includes:

- Pre-configured S3 buckets for secure data storage
- Default AWS Batch environment for compute workflows
- S3 bucket naming: `fh-pi-lastname-f-eco` (and other suffixes)

### Specialized Use Account

Near-unrestricted AWS access for software development teams or research requiring hosted websites / persistent services. Key limitation: cannot grant account access to others. Request via helpdesk ticket with coordination from the Cloud and Data team.

### Proof-of-Concept Account

For labs with AWS Credit grants for technology evaluation. Created in the Sandbox environment. Requires Cloud and Data team configuration via helpdesk.

## SSO Login

### Web Console

Navigate to the SSO Landing Page:

```
https://d-92674cb6d7.awsapps.com/start
```

Authenticate with your Fred Hutch (HutchNet) credentials. The interface shows all accounts you can access, with options for console access or CLI credential retrieval.

### CLI Access

```bash
# Load AWS CLI on rhino/gizmo
ml awscli

# One-time SSO configuration
aws configure sso
# SSO start URL: (from MyApps portal)
# SSO region: us-west-2
# Select account and role when prompted
# Set a profile name

# Login (and refresh when expired)
aws sso login --profile <profile-name>

# Verify access
aws sts get-caller-identity --profile <profile-name>
```

### Retrieving Temporary Credentials

From the SSO Landing Page, click on your account, then use "Command line or programmatic access" (Option 3) to get:

- Access Key ID
- Secret Access Key
- Session Token

These expire after **8 hours**.

## S3 Storage

### Pricing

| Tier | Cost |
|------|------|
| First 100 TB | Free |
| Beyond 100 TB | $3/TB/month |

### Common S3 Operations

```bash
# List buckets
aws s3 ls --profile <profile-name>

# List contents of a bucket
aws s3 ls s3://fh-pi-lastname-f-eco/ --profile <profile-name>

# Upload a file
aws s3 cp myfile.txt s3://fh-pi-lastname-f-eco/myfile.txt --profile <profile-name>

# Download a file
aws s3 cp s3://fh-pi-lastname-f-eco/myfile.txt . --profile <profile-name>

# Sync a directory
aws s3 sync ./local-dir s3://fh-pi-lastname-f-eco/remote-dir/ --profile <profile-name>

# Remove a file
aws s3 rm s3://fh-pi-lastname-f-eco/myfile.txt --profile <profile-name>
```

## Compute (AWS Batch)

- Free tier included with every lab account
- Pay-as-you-go beyond free tier
- 11% institutional discount applied automatically
- IT bills researchers monthly with itemized invoices assigned to grant Project IDs

## Account Administration

**Default Admin**: The PI owns the lab's AWS account.

**Delegated Admins**: Additional lab members can receive admin permissions with PI approval. Process:

1. Get PI approval
2. Submit an IAM ticket to helpdesk
3. User is added to the `Power User` group

## Cost Management

- Lab admins can configure **AWS Cost Anomaly Detection** per AWS documentation
- Actual Fred Hutch BizOps charges may differ from AWS console estimates
- Monitor via the **AWS Chargebacks Teams Channel**
- Use the AWS Pricing Calculator: https://calculator.aws/

## Using AWS from Rhino/Gizmo Jobs

```bash
# In your Slurm script or interactive session:
ml awscli

# Make sure you have an active SSO session
aws sso login --profile <profile-name>

# Then use AWS commands as normal
aws s3 cp s3://fh-pi-lastname-f-eco/data.tar.gz /hpc/temp/lastname_f/$USER/
```

**Important**: SSO sessions are time-limited. For long-running batch jobs, consider using the temporary credentials (Access Key ID, Secret Access Key, Session Token) as environment variables instead of relying on SSO session.

## Common Pitfalls

- **SSO credentials expire.** Run `aws sso login --profile <name>` to refresh.
- **BizOps charges differ from AWS console.** The institutional billing includes overhead and discounts that change the numbers.
- **Specialized Use accounts cannot delegate access.** Only the assigned user can access the account.
- **Proof-of-concept accounts are sandboxed** and tied to credit grant timelines.
- **Never share AWS credentials** via email, Slack, GitHub, or any unencrypted channel.
- **S3 bucket naming matters.** Lab buckets follow the `fh-pi-lastname-f` convention. Using the wrong bucket name means accessing someone else's data (or getting access denied).
- **Long-running Slurm jobs and SSO**: SSO sessions may expire during multi-hour jobs. Export temporary credentials as environment variables for reliability.

## Reference Links

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/access_aws/
- SciComp Wiki (Credentials): https://sciwiki.fredhutch.org/scicomputing/access_credentials/
- AWS Docs: https://docs.aws.amazon.com/
- AWS Pricing Calculator: https://calculator.aws/
- Slack: https://fhdata.slack.com/archives/CD3HGJHJT

# Access Credentials (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/access_credentials/

## Key Facts

- **HutchNet ID**: Standard login issued on hire. Used for network access, Rhino, Gizmo clusters.
- **Collaborator access**: Non-employees added via non-employee action forms.
- **SciComp Self-Service portal**: Add lab members, enable cluster access under PI's Slurm account, verify workshop access.
- **Slurm cluster access**: HutchNet ID must be associated with a PI account. Error "Invalid account or account/partition" means setup incomplete.
- **GitHub**: Fred Hutch org at github.com/FredHutch. Create account, email scicomp with username to join.
- **AWS credentials**: Each employee gets personal credentials via MyApps portal using HutchNet ID. Lab AWS accounts follow format `fh-pi-lastname-f`.

## Commands & Examples

### AWS CLI SSO Configuration (one-time setup)

```bash
# Step 1: SSH into rhino
ssh HutchID@rhino

# Step 2: Load AWS CLI module
ml awscli
aws --version

# Step 3: Configure SSO (interactive, one-time)
aws configure sso
# Provide: session name, SSO start URL (from MyApps), region us-west-2

# Step 4: Authenticate via browser (follow URL + verification code)

# Step 5: Select AWS account and role, set profile name

# Step 6: Refresh credentials when expired
aws sso login --profile <profile-name>
```

### Testing S3 Access

```bash
# Upload test
echo hello | aws s3 cp - s3://fh-pi-lastname-f-eco/hello.txt

# Download test
aws s3 cp s3://fh-pi-lastname-f-eco/hello.txt .
cat hello.txt

# Cleanup
aws s3 rm s3://fh-pi-lastname-f-eco/hello.txt
```

### Motuz Configuration

Use Temporary Security Credentials (STS) option with Access Key ID, Secret Access Key, and Session Token from SSO portal (Option 3). Credentials expire after 8 hours.

## Common Pitfalls

- Slurm jobs fail with "Invalid account or account/partition" if HutchNet ID is not linked to a PI account. Use SciComp Self-Service to fix.
- Never share AWS credentials via email or GitHub.
- Never commit secrets/credentials to GitHub repos. Use environment variables or external config files.
- Motuz STS credentials expire after 8 hours and must be refreshed.

## Cross-references

- /scicomputing/access_overview/ (parent)
- /scicomputing/access_aws/ (detailed AWS account info)
- /scicomputing/access_methods/ (SSH into rhino)

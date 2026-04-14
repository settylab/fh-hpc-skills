# AWS Accounts at Fred Hutch (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/access_aws/

## Key Facts

- Fred Hutch provides individual AWS accounts to labs with S3 storage, AWS Batch, and other services.
- Accounts come pre-configured with security rules and compute environments.

### Account Types

1. **Lab Account**: Granted to any PI via helpdesk ticket. Includes pre-configured S3 buckets and default AWS Batch environment.
2. **Specialized Use Account**: Near-unrestricted AWS access. Cannot grant account access to others. For software dev teams or research needing hosted websites/persistent services. Request via helpdesk.
3. **Proof-of-concept Account**: For labs with AWS Credit grants. Created in Sandbox environment. Requires Cloud and Data team configuration.

### SSO Login

- SSO Landing Page: `https://d-92674cb6d7.awsapps.com/start`
- Authenticate with Fred Hutch (HutchNet) credentials.
- Interface shows accessible accounts with console access or CLI credential retrieval options.

### Pricing

- **S3 Storage**: First 100TB free, then $3/TB/month.
- **Compute**: Free tier included, pay-as-you-go after (11% institutional discount).
- IT processes charges upfront, then bills researchers monthly with itemized invoices assigned to grant Project IDs.

### Account Administration

- Default admin: the PI.
- Delegated admins: Additional lab members can get admin permissions with PI approval. Submit IAM ticket to be added to `Power User` group.

### Cost Monitoring

- Lab admins can configure AWS Cost Anomaly Detection.
- Actual BizOps charges may differ from AWS estimates.
- AWS Chargebacks Teams Channel for details.

## Commands & Examples

```bash
# SSO login via CLI (after aws configure sso is done)
aws sso login --profile <profile-name>
```

## Common Pitfalls

- Users need AWS credentials configured before accessing resources. Do the SSO setup from the credentials page first.
- BizOps charges may differ from what the AWS console shows.
- Proof-of-concept accounts are sandboxed and have limited lifespans tied to credit grants.
- Specialized Use accounts cannot delegate access to others.

## Cross-references

- /scicomputing/access_credentials/ (AWS CLI SSO setup steps)
- /scicomputing/access_overview/ (parent)
- AWS Official Docs: https://docs.aws.amazon.com/
- AWS Pricing Calculator: https://calculator.aws/
- Slack: https://fhdata.slack.com/archives/CD3HGJHJT

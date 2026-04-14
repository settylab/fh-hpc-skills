# Cloud Computing (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/compute_cloud/

## Key Facts

Fred Hutch provides multiple methods for leveraging AWS cloud computing, ranging from beginner-friendly to advanced.

### WDL Workflows

- WDL (Workflow Description Language) is open-source and works across multiple compute infrastructures.
- Fred Hutch offers **PROOF** as a user-friendly interface that handles Cromwell server configuration automatically.
- Ideal for researchers who want cloud execution without deep AWS knowledge.

### Nextflow on AWS

- Nextflow can be configured to use AWS as the backend execution resource.
- This is an emerging service, not currently fully supported at Fred Hutch.

### AWS Batch

- Wraps around AWS EC2 resources for batch computing.
- Uses Docker containers.
- Features a queueing system for job management.
- Resources provision dynamically based on workload.
- Does NOT provide traditional file systems (no home directories, no fast-file, no temp).
- Typically uses S3 for data storage.
- Ideal for standard, repeatable processing workflows.

### CloudShell

- Browser-based shell native to AWS.
- AWS CLI integration built in.
- 1 GB persistent storage in home directory.
- No charges for CloudShell itself (enabled services may incur costs).
- Inherits user credentials from AWS Management Console.

## Common Pitfalls

- Expecting on-premise file systems (home, fast, scratch) to be available in AWS Batch.
- Not accounting for data transfer costs when moving data to/from S3.
- Using Nextflow on AWS without understanding it is not fully supported.

## Cross-references

- /scicomputing/compute_jobs/ (on-premise alternative)
- /scicomputing/access_aws/ (AWS account setup)

# AWS Batch at Fred Hutch

Source: https://sciwiki.fredhutch.org/compdemos/aws-batch/

## Overview

AWS Batch runs jobs consisting of a command, Docker image, and compute resources. The service finds machines, downloads the image, executes the command, and shuts down on completion. Data must be transferred to/from S3 (unlike gizmo's shared filesystem).

## Prerequisites

- AWS credentials configured
- Default queue pre-configured for AWS Genomics Pipeline workflows
- Custom compute environments require contacting SciComp

## Job Submission via CLI

```bash
# Generate job JSON skeleton
aws batch submit-job --generate-cli-skeleton > job.json
```

Example job.json:
```json
{
    "jobName": "jdoe-test-job",
    "jobQueue": "default",
    "jobDefinition": "myJobDef:7",
    "containerOverrides": {
        "command": ["echo", "hello world"],
        "environment": [
            {"name": "FAVORITE_COLOR", "value": "blue"}
        ]
    }
}
```

```bash
aws batch submit-job --cli-input-json file://job.json
```

## Job Submission via Python (boto3)

```python
import boto3
batch = boto3.client('batch')
response = batch.submit_job(
    jobName='jdoe-test-job',
    jobQueue='default',
    jobDefinition='myJobDef:7',
    containerOverrides={
        "command": ['echo', 'hello', 'world'],
        "environment": [{"name": "KEY", "value": "value"}]
    }
)
print("Job ID is {}.".format(response['jobId']))
```

## Scratch Space

Write all output to `/tmp` inside the container. This is an auto-scaling volume. Mount `/docker_scratch` on host to `/tmp` inside container.

## Monitoring

```bash
# Check job status
aws batch describe-jobs --jobs <job-id> | jq -r '.jobs[0].status'

# Get logs
aws batch describe-jobs --jobs <job-id> | jq -r '.jobs[0].container.logStreamName'
aws logs get-log-events --log-group-name /aws/batch/job --log-stream-name <stream-name> | jq -r '.events[]| .message'
```

Status values: SUBMITTED, PENDING, RUNNABLE, STARTING, RUNNING, FAILED, SUCCEEDED

## Key Notes

- Default vCPU limit is 128; request increase via AWS support
- SPOT instances cheaper but may be terminated
- Debug output increases CloudWatch costs
- Array jobs use `AWS_BATCH_JOB_ARRAY_INDEX` for task distinction
- Workflow managers (WDL/Cromwell, Nextflow) recommended for most users

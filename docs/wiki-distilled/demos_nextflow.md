# Nextflow on Fred Hutch HPC

Source: https://sciwiki.fredhutch.org/compdemos/nextflow/

## Overview

Nextflow is a workflow manager for complex bioinformatic analyses involving multiple steps with different software dependencies and resource needs. At Fred Hutch, Nextflow is commonly used with AWS Batch.

## Initial Setup

### Configuration File (`nextflow.config`)

```groovy
process.executor = 'awsbatch'
process.queue = 'default'
workDir = "s3://fh-pi-lastname-f-nextflow-scratch/delete10/nextflow/work/"

aws {
    region = 'us-west-2'
    batch {
        cliPath = '/home/ec2-user/miniconda/bin/aws'
        volumes = ['/var/lib/docker:/tmp:rw']
    }
    client {
        maxConnections = 4
    }
}
```

### Prerequisites

1. Obtain AWS credentials and request Batch access
2. Store input data in AWS S3
3. Prepare Nextflow workflow scripts

## Running Workflows

```bash
#!/bin/bash
set -e
BASE_BUCKET="s3://fh-pi-lastname-f-eco/lab/user_name/project_name"

ml nextflow

nextflow \
    -c ~/nextflow.config \
    run path-to-workflow.nf \
    --first_parameter ValueForFirstParameter \
    --input_folder $BASE_BUCKET/input/ \
    --output_folder $BASE_BUCKET/output/ \
    -with-report nextflow_report.html \
    -work-dir $BASE_BUCKET/work/ \
    -resume
```

**Execution location**: Use `grabnode` to run on a dedicated node, not rhino.

## Key Flags

- `--parameter value`: Pass parameters (accessed via `${params.parameter}`)
- `-with-report`: Generate HTML execution summary
- `-work-dir`: Temporary file location
- `-resume`: Resume from previous checkpoint

## Resource Configuration

Label-based:
```groovy
process {
    withLabel: 'io_limited' {
        cpus = 2
        memory = 8.GB
    }
}
```

Name-based:
```groovy
process {
    withName: 'trimmomatic' {
        cpus = 2
        memory = 8.GB
    }
}
```

Iterative retry with increasing resources:
```groovy
process {
    withName: 'process1' {
        cpus = 2
        maxRetries = 3
        errorStrategy = {task.attempt <= 3 ? 'retry' : 'finish'}
        memory = {4.GB * task.attempt}
    }
}
```

## Publishing Output

```groovy
publishDir "${params.output_folder}"
```

If results don't appear after success, rerun with `-resume` to copy outputs.

## Channel Synchronization

```groovy
Channel.fromPath("{params.input_folder}/*")
       .map { fp -> file(fp) }
       .into { input_ch_1; input_ch_2 }

// Join parallel process outputs by sample ID
output_ch_1.join(output_ch_2)
```

## Version Management

```bash
NXF_VER=19.10.0 nextflow run -c ~/nextflow.config repo/workflow --help
```

## Troubleshooting

- **Jobs stuck in RUNNABLE**: Queue congestion, incompatible CPU/memory, or resource limits. Contact SciComp.
- **Input file download failures**: Retry; add memory if files exceed process limits.
- **Container issues**: Verify Docker image accessibility and entrypoint configuration.
- **File paths as strings**: Use `path()` or `file()` functions for proper file handling.

## References

- [Fred Hutch Reproducible Workflows](https://github.com/FredHutch/reproducible-workflows/tree/master/nextflow)
- [Official Nextflow Documentation](https://www.nextflow.io/)

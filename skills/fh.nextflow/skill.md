---
description: "Nextflow workflow management on Fred Hutch Gizmo cluster and AWS Batch"
---

# Nextflow on Fred Hutch HPC

TRIGGER when: user mentions Nextflow, NF, workflow pipelines, nf-core, or running multi-step bioinformatics pipelines

## Context

Nextflow is a workflow manager for complex bioinformatic analyses with multiple steps, different software dependencies, and varying resource needs. At Fred Hutch, Nextflow is commonly run on dedicated gizmo nodes (via grabnode) submitting work to AWS Batch.

## Instructions

### Setup

1. Load Nextflow:
   ```bash
   ml nextflow
   ```

2. Create `~/nextflow.config` for AWS Batch execution:
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

3. Prerequisites: AWS credentials configured, input data in S3, Nextflow scripts prepared.

### Running Workflows

Always run from a `grabnode` session, never directly on rhino:

```bash
grabnode  # request resources first

ml nextflow
nextflow \
    -c ~/nextflow.config \
    run path-to-workflow.nf \
    --input_folder s3://bucket/input/ \
    --output_folder s3://bucket/output/ \
    -with-report nextflow_report.html \
    -work-dir s3://bucket/work/ \
    -resume
```

### Key Flags

- `--parameter value`: Pass to workflow as `${params.parameter}`
- `-with-report`: HTML execution summary
- `-work-dir`: Temporary file location (use S3)
- `-resume`: Resume from previous checkpoint (always use for reruns)

### Resource Configuration

```groovy
process {
    withName: 'my_process' {
        cpus = 2
        maxRetries = 3
        errorStrategy = {task.attempt <= 3 ? 'retry' : 'finish'}
        memory = {4.GB * task.attempt}
    }
}
```

### Output Publishing

Add `publishDir "${params.output_folder}"` to process blocks. If results missing after success, rerun with `-resume`.

### Version Pinning

```bash
NXF_VER=19.10.0 nextflow run -c ~/nextflow.config repo/workflow --help
```

### Troubleshooting

- **Jobs stuck RUNNABLE**: Queue congestion, incompatible CPU/memory, resource limits. Contact SciComp.
- **Input download failures**: Retry; increase memory if files are large.
- **Container issues**: Verify Docker image accessibility and entrypoint config.
- **File paths as strings**: Use `path()` or `file()` functions for proper file handling.

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/compdemos/nextflow/
- Fred Hutch Reproducible Workflows: https://github.com/FredHutch/reproducible-workflows/tree/master/nextflow
- Official Nextflow Docs: https://www.nextflow.io/

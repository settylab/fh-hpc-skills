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

### Configuration Profiles for Portability

Nextflow's profile system separates workflow logic from platform-specific settings. A single `nextflow.config` can define profiles for different execution environments, switched with a single flag:

```groovy
profiles {
    local {
        process.executor = 'local'
        docker.enabled = true
    }

    slurm {
        process.executor = 'slurm'
        singularity.enabled = true
        singularity.autoMounts = true
        process.queue = 'campus-new'
        process.clusterOptions = '--partition=campus-new'
    }

    slurm_gpu {
        process.executor = 'slurm'
        singularity.enabled = true
        singularity.autoMounts = true
        process.queue = 'chorus'
        process.clusterOptions = '--partition=chorus --gres=gpu:1'
    }

    awsbatch {
        process.executor = 'awsbatch'
        process.queue = 'default'
        aws.region = 'us-west-2'
        aws.batch.cliPath = '/home/ec2-user/miniconda/bin/aws'
    }
}
```

Usage:
```bash
nextflow run pipeline.nf -profile slurm      # Run on Gizmo
nextflow run pipeline.nf -profile awsbatch    # Burst to AWS
nextflow run pipeline.nf -profile local       # Test locally
```

**Gizmo partition mappings:**
- `campus-new` — default CPU jobs (up to 7 days)
- `short` — quick jobs under 12 hours
- `restart-new` — preemptible, for fault-tolerant workflows
- `chorus` — GPU jobs (L40S nodes)

Never hardcode paths, queue names, or resource requests in workflow logic. Keep them in profiles or params so they can be overridden per platform.

### Container Digest Pinning

Pin containers by SHA256 digest in process directives for reproducibility. Tags are mutable; digests guarantee identical bytes:

```groovy
process ALIGN {
    container 'quay.io/biocontainers/bwa:0.7.17--h7132678_9@sha256:abc123...'

    input:
    path reads

    script:
    """
    bwa mem -t ${task.cpus} ref.fa ${reads}
    """
}
```

For nf-core pipelines, containers are already pinned by digest in each release. When writing custom pipelines, always specify containers per process (not globally) and use digests for production runs.

### Pipeline Testing with nf-test

[nf-test](https://nf-co.re/docs/contributing/nf-test) is the standard testing framework for Nextflow pipelines. It supports snapshot testing and dependency analysis:

```bash
# Install nf-test — project-local via mamba (preferred)
# Requires project-local .condarc with channel_alias — see fh.python skill
export CONDARC="$(pwd)/.condarc"
mamba create --prefix ./envs/nf-test -c bioconda nf-test
mamba activate ./envs/nf-test

# Alternative: the official installer (installs to ~/.nf-test/ — not project-local)
# curl -fsSL https://code.askimed.com/install/nf-test | bash

# Initialize in your pipeline directory
nf-test init

# Generate a test for a process
nf-test generate process ALIGN

# Run tests
nf-test test
```

Example test file (`tests/processes/align.nf.test`):
```groovy
nextflow_process {
    name "Test ALIGN"
    script "modules/align.nf"
    process "ALIGN"

    test("Should align reads") {
        when {
            process {
                """
                input[0] = file("${projectDir}/tests/data/reads.fastq.gz")
                """
            }
        }
        then {
            assert process.success
            assert snapshot(process.out).match()
        }
    }
}
```

Snapshot testing captures process outputs and compares against stored snapshots, catching unintended changes. nf-test also performs dependency analysis to run only tests affected by code changes.

### The Portability Stack

A truly portable Nextflow pipeline has four layers:
1. **Workflow definition** — Nextflow DSL2 processes and workflows (the science logic).
2. **Containerized dependencies** — each process specifies a container with digest-pinned images (Apptainer SIF for HPC, Docker for cloud/local).
3. **Configuration profiles** — platform-specific settings (executor, queue, resources, container runtime) separated from workflow logic.
4. **Data access abstraction** — use URIs (`s3://`, `gs://`, local paths) via params rather than hardcoded filesystem paths.

This design lets you develop on a laptop, run on Gizmo, and burst to AWS Batch without changing a single line of pipeline code.

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

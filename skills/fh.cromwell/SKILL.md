---
description: "Cromwell/WDL workflow execution on Fred Hutch HPC and AWS Batch"
---

# Cromwell and WDL Workflows at Fred Hutch

TRIGGER when: user mentions Cromwell, WDL, Workflow Description Language, or WILDS Docker workflows

## Context

Cromwell is a WDL (Workflow Description Language) workflow engine used alongside Nextflow at Fred Hutch. WDL workflows use Docker containers for reproducibility and can execute on local HPC or AWS Batch. The SciComp wiki Cromwell page is currently a stub, but WDL container integration is documented in the Docker demo.

## Instructions

### WDL Task Structure

WDL tasks define a command, runtime environment (Docker image), and outputs:

```wdl
task runSTAR {
  input {
    File genome_fasta
    File reads_fastq
  }

  command {
    STAR --runMode genomeGenerate \
         --genomeDir genome_index \
         --genomeFastaFiles ${genome_fasta}
  }

  runtime {
    docker: "getwilds/star:2.7.6a"
  }

  output {
    Directory index = "genome_index"
  }
}
```

### Docker Image References

Format: `registry/namespace/repository:tag`
Example: `getwilds/star:2.7.6a`

Always use specific version tags, never `latest`.

### Running on Gizmo with Apptainer

Docker images specified in WDL are converted to Apptainer SIF format on the cluster:

```bash
ml Apptainer
apptainer exec docker://getwilds/samtools:1.19 samtools --version
```

### WILDS Docker Library

The Fred Hutch WILDS project provides pre-built bioinformatics containers with automated testing and security scanning. Prefer these over custom images when available.

### Best Practices

- Build containers on gizmo compute nodes (via `grabnode`), not rhino
- Mount large datasets rather than baking into images
- Keep containers minimal with only necessary dependencies
- Document with LABEL metadata in Dockerfiles
- Use `$TMPDIR` for temporary storage in batch jobs

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki Cromwell: https://sciwiki.fredhutch.org/compdemos/Cromwell/
- SciComp Wiki Docker: https://sciwiki.fredhutch.org/compdemos/Docker/
- WILDS Docker Library: https://github.com/getwilds

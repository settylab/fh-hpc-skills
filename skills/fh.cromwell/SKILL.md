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

### Cromwell on Google Batch API

As of June 2025, Cromwell runs on the **Google Batch API**, replacing the deprecated Cloud Life Sciences API. If you encounter documentation or configurations referencing Cloud Life Sciences (also known as PAPI v2), update them to target Google Batch. This applies to Terra platform deployments and standalone Cromwell instances.

At Fred Hutch, Cromwell is primarily used via the PROOF system for on-prem (Gizmo/Slurm) and AWS Batch execution. The Google Batch backend is relevant if collaborating with groups on Terra or GCP.

### WDL in Clinical and Regulated Settings

WDL/Cromwell has particular strengths in clinical genomics and regulated environments:

- **Audit trails** — Cromwell records detailed execution metadata (inputs, outputs, timing, container images) for every task, supporting compliance requirements.
- **Broad/Terra ecosystem** — WDL is the native workflow language for Terra, the primary platform for NHGRI/AnVIL, TOPMed, and other large genomics consortia.
- **Deterministic execution** — WDL's explicit input/output declarations and lack of implicit state make workflows easier to validate for clinical pipelines.
- **CromwellOnAzure** — Microsoft provides Azure deployment for WDL workflows, relevant for collaborations with institutions on Azure.

If your project involves Broad Institute collaboration, clinical genomics, or Terra-based data access, WDL is the right choice. For general bioinformatics at Fred Hutch, Nextflow is typically more practical.

### Best Practices

- Build containers on gizmo compute nodes (via `grabnode`), not rhino
- Mount large datasets rather than baking into images
- Keep containers minimal with only necessary dependencies
- Document with LABEL metadata in Dockerfiles
- Use `$TMPDIR` for temporary storage in batch jobs
- Pin container images by digest (SHA256) for reproducibility, not just tags

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

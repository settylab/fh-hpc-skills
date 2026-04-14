---
description: "Comparison of workflow managers (Nextflow, Snakemake, WDL/Cromwell, CWL) and the portability stack for Fred Hutch HPC"
---

# Workflow Managers Overview

TRIGGER when: user asks which workflow manager to use, compares Nextflow vs Snakemake vs WDL, asks about pipeline portability, cloud bursting, or how to structure a new bioinformatics pipeline.

## Context

Multiple workflow managers are used in bioinformatics, each with different strengths. This skill helps users choose the right one for their project and understand the portability patterns that make workflows survive infrastructure changes.

## Workflow Manager Comparison

### Nextflow

**Best for:** Most new bioinformatics projects, especially those needing cloud portability.

- Dataflow model with channel-based process communication, natural for parallel and streaming workloads.
- First-class executor abstraction: the same pipeline runs unchanged on a laptop, Slurm, AWS Batch, Google Cloud Batch, and Kubernetes. Switching is a single flag (`-profile slurm`).
- nf-core community: 124+ curated pipelines, 2,600+ contributors, 94% user satisfaction (2024 survey). Expanding beyond biology into astrophysics, earth science, and economics.
- Strong container integration with digest pinning in process directives.
- Groovy-based DSL has a learning curve for Python-native researchers.
- Backed by Seqera (commercial); governance depends on commercial incentives.

**At Fred Hutch:** Nextflow is the primary workflow manager. Runs on Gizmo via Slurm and bursts to AWS Batch. See `fh.nextflow` skill for setup.

### Snakemake

**Best for:** Python-heavy exploratory workflows and researchers who prefer staying in the Python ecosystem.

- Python-native syntax with low barrier for Python developers.
- Snakemake 8/9 plugin architecture: all execution backends (Slurm, Kubernetes, Google Cloud Batch, GA4GH TES) are plugins.
- File-based rule system: define inputs and outputs, Snakemake resolves the DAG.
- Academic project with transparent governance.
- Per-rule conda environments (optionally inside containers) provide fine-grained dependency management.
- Cloud execution story catching up but not as mature as Nextflow's.
- Declining market share (27% to 17% citation share, 2021-2024) suggests community momentum is shifting.

**At Fred Hutch:** Not officially supported by SciComp but works well on Gizmo with the Slurm executor plugin.

### WDL / Cromwell

**Best for:** Broad Institute collaborations, Terra platform, clinical/regulated genomics.

- Standard workflow language for Terra (NHGRI/AnVIL, TOPMed, AllOfUs).
- Strong audit trail support for clinical and regulated settings.
- Available at Fred Hutch via the PROOF system (Gizmo/Slurm and AWS Batch).
- As of June 2025, Cromwell runs on Google Batch API (Cloud Life Sciences is deprecated).
- CromwellOnAzure available for Azure deployments.
- Verbose syntax; less community diversity outside genomics.

**At Fred Hutch:** Use WDL when collaborating with Broad/Terra or when audit trails are required. See `fh.cromwell` skill.

### CWL (Common Workflow Language)

**Best for:** Consortia mandating strict cross-platform interoperability.

- Designed for platform-neutral workflow definitions and strict portability.
- Used by specific consortia (e.g., GA4GH) that require interoperability guarantees.
- Verbose, harder to write and debug than Nextflow or Snakemake.
- Smaller community, slower iteration.

**At Fred Hutch:** Only adopt if a specific consortium or collaboration requires it. Not the default choice for new projects.

## When to Use Which

| Scenario | Recommendation |
|---|---|
| New bioinformatics pipeline | Nextflow + nf-core |
| Python-centric exploratory analysis | Snakemake |
| Broad/Terra collaboration | WDL/Cromwell |
| Clinical/regulated pipeline | WDL/Cromwell |
| Consortium mandates interop standard | CWL |
| Existing pipeline in any manager | Keep it; switching has real cost |

## The Portability Stack

A truly portable workflow has four layers. Without any one of them, portability breaks down:

### 1. Workflow Definition

Use a manager with executor abstraction (Nextflow or Snakemake). The workflow defines the science: what processes run, what data flows between them, what the logic is. It should contain zero platform-specific settings.

### 2. Containerized Dependencies

Each process/rule specifies its own container. Pin images by SHA256 digest, not mutable tags. Use Apptainer SIF for HPC, Docker for cloud/local. Build from definition files (Dockerfile or `.def`), never interactive sandbox modifications.

```groovy
// Nextflow example
process ALIGN {
    container 'quay.io/biocontainers/bwa:0.7.17--h7132678_9@sha256:abc123...'
    // ...
}
```

### 3. Configuration Profiles

Separate platform-specific settings (executor, queue, resources, container runtime) from workflow logic. In Nextflow, use `profiles {}` blocks. In Snakemake, use executor plugins and config files.

```groovy
// nextflow.config
profiles {
    slurm {
        process.executor = 'slurm'
        process.queue = 'campus-new'
        singularity.enabled = true
    }
    awsbatch {
        process.executor = 'awsbatch'
        process.queue = 'default'
        aws.region = 'us-west-2'
    }
}
```

### 4. Data Access Abstraction

Use URIs (`s3://`, `gs://`, local paths) via parameters rather than hardcoded filesystem paths. Data location should be a runtime decision, not baked into the pipeline.

```bash
# Same pipeline, different data locations
nextflow run pipeline.nf -profile slurm --input /fh/fast/lab/data/
nextflow run pipeline.nf -profile awsbatch --input s3://bucket/data/
```

## Cloud-Burst Pattern

The practical hybrid pattern for Fred Hutch:

1. **Develop on Gizmo** — write and test the pipeline using Slurm on the local cluster with a small dataset.
2. **Validate locally** — run the full pipeline on a representative subset to confirm correctness.
3. **Burst to AWS** — switch to AWS Batch for peak demand, large-scale runs, or when specific cloud-native tools are needed. Change only the profile flag.
4. **Archive to S3** — store results in economy storage (S3) for long-term access.

This works because the portability stack keeps the science (workflow + containers) separate from the infrastructure (profiles + data URIs). The same code runs in both environments.

**When to burst:**
- Peak demand exceeds Gizmo capacity or queue wait times are unacceptable
- The workflow needs cloud-native services (e.g., specific instance types, GPU availability)
- Collaborators need to reproduce results in their own cloud environment

**When to stay on Gizmo:**
- Sustained, high-utilization workloads (on-prem is more cost-effective)
- Data gravity: large datasets already on `/fh/fast/` would be expensive to transfer
- Egress costs would dominate the bill

## Portability Checklist

- [ ] No hardcoded paths, queue names, or resource requests in workflow logic
- [ ] Container directives per process/rule, not global
- [ ] Containers pinned by SHA256 digest
- [ ] Memory, CPU, and time limits parameterized and overridable per platform
- [ ] Workflow-manager-native retry logic with increasing resources for OOM failures
- [ ] Tested on at least two platforms (local + cluster, or cluster + cloud)
- [ ] All software versions pinned in container definitions

## Principles

- Choose the simplest workflow manager that meets your needs
- Do not switch managers for an existing pipeline without a strong reason
- Invest in portability from the start; retrofitting is expensive
- Test before scaling: validate on a small dataset before committing cluster or cloud time
- Follow Fred Hutch data security policies for all data movement

## References

- Nextflow: https://www.nextflow.io/
- nf-core: https://nf-co.re/
- Snakemake: https://snakemake.readthedocs.io/
- WDL/OpenWDL: https://openwdl.org/
- Cromwell: https://cromwell.readthedocs.io/
- Fred Hutch SciComp Wiki: https://sciwiki.fredhutch.org/

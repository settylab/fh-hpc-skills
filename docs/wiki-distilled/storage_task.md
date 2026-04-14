# Task-Optimized Storage

Source: https://sciwiki.fredhutch.org/scicomputing/store_task/

## Core Concept

Task storage is for temporary data during computational workflows when primary storage is unsuitable for specific tasks.

**CRITICAL: Never store the primary or only copy of data in task/temp storage.**

## Storage Options

### Working (`/fh/working`)

- Available on all rhino/gizmo nodes
- Backups: None (snapshots available)
- Quota: 20TB default, expandable to 50TB (incurs costs)
- Purge policy: No automatic purge
- Access: PI/lab researchers only

### Temp (`/hpc/temp`)

- Available on rhino/gizmo nodes and managed workstations
- Backups: None (snapshots every 30 minutes)
- Purge policy: Files deleted 30 days after creation
- Cost: Free

### Job Local Storage

- Allocated during Slurm job execution only
- Storage type: Local node disk (directly-attached, fastest I/O)
- Duration: Job lifecycle only
- Cost: Free
- Data destroyed when job ends

### Cloud Scratch (S3)

- Bucket naming: `fh-pi-lastname-f-nextflow-scratch`
- Replication: Limited
- Cost: Charged
- Auto-deletion folders: `delete10/`, `delete30/`, `delete60/`

## Best Practices

1. Always ensure primary data exists in durable storage (Fast or Economy) before using task storage
2. Copy generated results to durable storage immediately after creation
3. Use workflow managers (Nextflow, Snakemake, Cromwell) to handle data staging and validation
4. Consider job-local storage for maximum I/O performance on single-node jobs

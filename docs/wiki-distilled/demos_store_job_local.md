# Job Local Storage ($TMPDIR)

Source: https://sciwiki.fredhutch.org/compdemos/store_job_local/

## Overview

Gizmo compute nodes provide temporary local SSD storage for each job, automatically removed on job completion.

## Key Details

- **Path**: `/loc/scratch/<jobid>` (accessed via `$TMPDIR`)
- **Capacity**: ~7TB on K class nodes
- **Ownership**: Job submitter
- **Scope**: Exclusive to processes on the allocated node; not shared between jobs or across nodes (no MPI sharing)

## Best Practices

Always use `$TMPDIR` instead of hardcoding paths. This ensures compatibility if the storage path changes.

Use `$TMPDIR` instead of `/tmp`. The `/tmp` directory has less space and is not automatically cleaned up.

## Java/GATK/Picard

Java does not follow standard `TMPDIR` conventions. The system sets `java.io.tmpdir` via the `JAVA_TOOL_OPTIONS` environment variable. User-specified temporary directory options in GATK or Picard override this default.

## Example Usage in Scripts

```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --cpus-per-task=4

# Copy input to local SSD for fast I/O
cp /fh/fast/lab/input.bam $TMPDIR/
cd $TMPDIR

# Run analysis with local I/O
samtools sort input.bam -o sorted.bam

# Copy results back to shared storage
cp sorted.bam /fh/fast/lab/output/
```

---
description: "Running AlphaFold 3 on Fred Hutch chorus GPU partition"
---

# AlphaFold 3 on Fred Hutch HPC

TRIGGER when: user mentions AlphaFold, AF3, protein structure prediction, or protein folding on the cluster

## Context

AlphaFold 3 runs on the chorus partition GPU nodes (harmony nodes) at Fred Hutch. Reference databases are pre-staged at `/shared/biodata/alphafold3`, accessible only on Chorus nodes via HPC Vast storage.

**Note:** Container and reference data paths are only accessible from chorus partition harmony nodes, not from rhino login nodes.

## Instructions

### Submission Script

Create a script (e.g., `af3.sh`):

```bash
#!/bin/bash
#SBATCH --cpus-per-task=8
#SBATCH --gpus=2
#SBATCH --mem=1024GB
#SBATCH --partition=chorus
#SBATCH --nodes=1

# User-defined variables
BASE=/path/to/working/directory
OUTPUT_DIR=$BASE/output
JSON_PATH=$BASE/input.json

# Container (no ml Apptainer needed on Chorus)
CONTAINER=/app/software/AlphaFold/containers/alphafold3.sif

apptainer exec --nv \
  --bind /shared/biodata/alphafold3:/root/public_databases \
  --bind $BASE:$BASE \
  $CONTAINER \
  python /app/alphafold/run_alphafold.py \
    --json_path=$JSON_PATH \
    --output_dir=$OUTPUT_DIR \
    --model_dir=/root/public_databases/parameter_models/
```

### Submit

```bash
sbatch af3.sh
```

### Key Details

- **Partition**: `chorus` (required, GPU-equipped harmony nodes)
- **GPUs**: 2 or 4 recommended (`--gpus=2` or `--gpus=4`)
- **CPUs**: Up to 32 CPUs per node on chorus (harmony nodes have 32 cores)
- **Memory**: 1024GB (1TB)
- **Container**: `/app/software/AlphaFold/containers/alphafold3.sif`
- **Reference data**: `/shared/biodata/alphafold3` (mounted as `/root/public_databases`)
- No `ml Apptainer` needed on Chorus partition
- `--nv` flag enables GPU passthrough to container

### Chorus Partition Limits

- 1-4 GPUs per job
- Maximum 32 CPUs per node
- Default time: 1 day, maximum: 7 days

### Input Format

AlphaFold 3 takes JSON input files specifying the protein/nucleic acid sequences and other parameters.

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## AlphaFold 2 (Module-Based)

Older AlphaFold versions are available as Lmod modules for use on campus-new/short partitions:

```bash
module spider AlphaFold
# Available: AlphaFold/2.1.1-fosscuda-2020b, AlphaFold/2.3.1-foss-2022a-CUDA-11.7.0

module load AlphaFold/2.3.1-foss-2022a-CUDA-11.7.0
```

These run on standard GPU nodes (j/k class with GTX 1080 Ti / RTX 2080 Ti). For AF3, use the container-based approach on chorus (above).

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/compdemos/alphafold3/

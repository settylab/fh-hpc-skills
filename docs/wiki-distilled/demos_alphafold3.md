# AlphaFold 3 on Fred Hutch HPC

Source: https://sciwiki.fredhutch.org/compdemos/alphafold3/

## Overview

AlphaFold 3 runs on the chorus partition GPU nodes (harmony nodes).

## Reference Data

Stored at `/shared/biodata/alphafold3`, available only on Chorus nodes via HPC Vast storage. The container expects public data mapped to `/root/public_databases`.

## Submission Script

```bash
#!/bin/bash
#SBATCH --cpus-per-task=8
#SBATCH --gpus=2          # or --gpus=4 recommended
#SBATCH --mem=1024GB
#SBATCH --partition=chorus
#SBATCH --nodes=1

# User-defined variables
BASE=/path/to/working/directory
OUTPUT_DIR=$BASE/output
JSON_PATH=$BASE/input.json

# Container location (no ml Apptainer needed on Chorus)
CONTAINER=/app/software/AlphaFold/containers/alpafold3.sif

# Run AlphaFold 3
apptainer exec --nv \
  --bind /shared/biodata/alphafold3:/root/public_databases \
  --bind $BASE:$BASE \
  $CONTAINER \
  python /app/alphafold/run_alphafold.py \
    --json_path=$JSON_PATH \
    --output_dir=$OUTPUT_DIR \
    --model_dir=/root/public_databases/parameter_models/
```

Submit with:
```bash
sbatch script.sh
```

## Key Details

- Max CPUs: 8 per task (current maximum on chorus)
- GPU: 2 or 4 recommended for AlphaFold 3
- Memory: 1024GB (1TB)
- Partition: chorus (required for GPU access)
- No Apptainer module loading needed on Chorus partition
- Container: `/app/software/AlphaFold/containers/alpafold3.sif`

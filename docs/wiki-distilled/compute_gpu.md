# GPU Computing (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/compute_gpu/

## Key Facts

### Available GPU Hardware

| Partition | Node Gen | GPU Model | GPUs/Node | GPU Memory |
|-----------|----------|-----------|-----------|------------|
| campus, short, new | j | NVIDIA GTX 1080ti | 1 | 10.92 GB |
| campus, short, new | k | NVIDIA RTX 2080ti | 1 | 10.76 GB |
| chorus | harmony | NVIDIA L40S | 4 | 44 GB |
| interactive | rhino | NVIDIA RTX 1080ti | -- | -- |

### Job Submission

**Standard partitions (campus, short, restart-new):**
```bash
# Request any GPU
sbatch --gpus=1 myscript.sh

# Request specific GPU type
sbatch --gpus=rtx2080ti:1 myscript.sh
```

**Chorus partition (harmony nodes with L40S GPUs):**
```bash
# Request one GPU on chorus
sbatch --partition=chorus --gpus=1 myscript.sh

# Request specific L40S GPU
sbatch --partition=chorus --gpus=l40s:1 myscript.sh

# Request multiple GPUs (up to 4 per harmony node)
sbatch --partition=chorus --gpus=3 myscript.sh
```

### CUDA Configuration

When Slurm allocates a GPU, it sets `CUDA_VISIBLE_DEVICES` automatically. Most CUDA-aware frameworks (TensorFlow, PyTorch, etc.) use this variable to restrict execution to assigned devices.

### Chorus Partition Requirements

Harmony nodes run a different OS and processor architecture (AMD EPYC) than standard gizmo nodes. Before submitting chorus jobs:
1. Run `module purge` to clear rhino/gizmo modules.
2. Load fresh modules within your job script.

## Common Pitfalls

- Requesting multiple GPUs without verifying the code can use them (most single-GPU code ignores extra GPUs).
- Not running `module purge` before chorus partition jobs, causing module conflicts.
- Expecting L40S GPUs on standard partitions (they are only on chorus).
- j/k nodes have only 1 GPU each, so multi-GPU jobs on standard partitions require multi-node allocation.

## Cross-references

- /scicomputing/compute_platforms/ (full node specifications)
- /scicomputing/compute_jobs/ (general job submission)
- /scicomputing/compute_environments/ (module management)

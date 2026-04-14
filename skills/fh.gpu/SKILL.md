---
description: "GPU computing on the Fred Hutch Gizmo cluster (requesting GPUs, CUDA, available GPU types, L40S, chorus partition)"
---

# Fred Hutch GPU Computing

TRIGGER when: user wants to run GPU jobs, asks about available GPUs, needs CUDA, TensorFlow/PyTorch on GPUs, or encounters GPU-related Slurm errors on the Gizmo cluster.

## Context

The Gizmo cluster has GPU nodes across multiple generations. Standard partitions (campus-new, short) have older GPUs (1 per node), while the chorus partition has newer NVIDIA L40S GPUs (4 per harmony node).

## Instructions

### Available GPUs

| Partition | Node Gen | GPU Model | GPUs/Node | GPU Memory | Best For |
|-----------|----------|-----------|-----------|------------|----------|
| campus-new, short | j | NVIDIA GTX 1080 Ti | 1 | 10.92 GB | Light inference, older CUDA code |
| campus-new, short | k | NVIDIA RTX 2080ti | 1 | 10.76 GB | Training small models, inference |
| chorus | harmony | NVIDIA L40S | 4 | 48 GB | Large model training, multi-GPU |
| interactive | j, k | NVIDIA GTX 1080 Ti / RTX 2080 Ti | 1 | 10.92 / 10.76 GB | Testing/debugging GPU code |

### Requesting GPUs

**Standard partitions (campus-new, short, restart-new):**
```bash
# Any available GPU
sbatch --gpus=1 myscript.sh

# Specific GPU type
sbatch --gpus=rtx2080ti:1 myscript.sh
```

**Chorus partition (L40S GPUs on harmony nodes):**
```bash
# One L40S GPU
sbatch --partition=chorus --gpus=1 myscript.sh

# Specific type
sbatch --partition=chorus --gpus=l40s:1 myscript.sh

# Multiple GPUs (up to 4 per node)
sbatch --partition=chorus --gpus=3 myscript.sh
```

**Interactive GPU session:**
```bash
# grabnode prompts "Do you need a GPU? [y/N]" — answer y
# This requests --gres=gpu on the interactive partition
grabnode
```

### CUDA Configuration

Slurm automatically sets `CUDA_VISIBLE_DEVICES` when it allocates GPUs. Most CUDA frameworks (TensorFlow, PyTorch, JAX) read this variable and restrict execution to assigned devices. You do NOT need to set it manually.

### Example GPU Job Script

```bash
#!/bin/bash
#SBATCH --job-name=gpu-training
#SBATCH --partition=chorus
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --time=1-00:00:00
#SBATCH --output=slurm-%j.out

# CRITICAL for chorus: purge old modules
module purge
source /app/lmod/lmod/init/profile

# Load GPU-compatible modules
module load CUDA/12.1.1
module load Python/3.11.3-GCCcore-12.3.0

# Verify GPU visibility
nvidia-smi
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"

python train.py
```

### Chorus Partition Requirements

Harmony nodes run a different OS and use AMD EPYC CPUs. You MUST:
1. Run `module purge` at the start of your job script.
2. Load fresh, chorus-compatible modules within the script.
3. Do not rely on modules loaded on rhino.

### Multi-GPU Considerations

Only request multiple GPUs if your code actually supports multi-GPU execution (e.g., PyTorch DistributedDataParallel, TensorFlow MirroredStrategy). Most single-GPU code silently ignores extra GPUs, wasting resources.

### Checkpointing GPU Jobs

Long training runs should save periodic checkpoints so they can resume after interruption (preemption, node failure, time limit). This is especially important on the `restart-new` partition where jobs can be killed at any time:

```python
# PyTorch example: save every N epochs
if epoch % save_every == 0:
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': loss,
    }, f'checkpoints/epoch_{epoch}.pt')
```

On job start, check for existing checkpoints and resume from the latest one instead of restarting from scratch.

## Principles

- Request only the GPUs you need. Most training jobs need 1 GPU.
- Verify multi-GPU support before requesting more than 1 GPU.
- Use appropriate partitions: chorus for L40S, campus-new for 1080ti/2080ti.
- Respect shared infrastructure and other users.
- Use versioned environments for reproducibility.
- Follow Fred Hutch data security policies.
- Review GPU scripts critically before submission. Verify CUDA module versions match your framework requirements, and confirm that `module purge` is present for chorus jobs. A wrong module combination can silently produce incorrect results or waste GPU hours on startup failures.

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_gpu/
- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_platforms/

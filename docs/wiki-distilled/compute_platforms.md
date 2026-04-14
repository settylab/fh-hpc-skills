# Compute Platforms (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/compute_platforms/

## Key Facts

- Fred Hutch provides on-premise HPC resources for researchers with computing needs exceeding desktop capabilities.
- Reasons to use the cluster: reproducible jobs, version-controlled software, increased compute capability, rapid access to large datasets.

### Access Points

- **Rhino**: CLI-based data and compute hub. 3 servers accessed via single hostname `rhino`.
- **Gizmo Cluster**: HPC cluster accessed via Rhino or NoMachine.
- **NoMachine (NX)**: Remote Linux desktop sessions on rhino01, rhino02, rhino03.

### Interactive Computing

- `grabnode` initiates interactive cluster sessions.
- Prompts for: number of cores, memory, time estimates.
- Accepts common sbatch options and flags.
- Must be run from a rhino host.

### Gizmo Node Configuration

**Standard Compute Nodes:**

| Generation | Count | CPU | Cores/Node | Memory/Node | Partitions |
|-----------|-------|-----|------------|-------------|------------|
| j | 42 | Intel Gold 6146 | 24 | 384 GB | campus, short, new |
| k | 170 | Intel Gold 6154 | 36 | 768 GB | campus, short, new |
| harmony | 8 | AMD EPYC 9354P | 32 | 1536 GB | chorus |

**GPU Nodes:**

| Generation | GPUs/Node | GPU Model | GPU Memory |
|-----------|-----------|-----------|------------|
| j | 1 | NVIDIA GTX 1080ti | 10.92 GB |
| k | 1 | NVIDIA RTX 2080ti | 10.76 GB |
| harmony | 4 | NVIDIA L40S | 44 GB |

### Local Storage (/loc)

All nodes have 10G networking. Per-node `/loc` scratch storage:
- j generation: 7 TB @ 300 MB/s
- k generation: 6 TB @ 300 MB/s
- harmony: 3 TB @ 300 MB/s
- rhino: 6 TB @ 300 MB/s

## Common Pitfalls

- "Invalid account" error means missing HutchNet ID or PI account association.
- Gizmo access requires both a HutchNet ID and PI account association.
- harmony nodes run a different OS and require separate environment modules (use `module purge` before loading).

## Cross-references

- /scicomputing/compute_jobs/ (job submission)
- /scicomputing/compute_gpu/ (GPU details)
- /scicomputing/compute_environments/ (modules and containers)

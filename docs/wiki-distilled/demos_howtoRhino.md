# How to Use Rhino Nodes

Source: https://sciwiki.fredhutch.org/compdemos/howtoRhino/

## Overview

The Rhino nodes are large-memory, shared computing systems for interactive work, prototyping, development, software compilation, and jobs requiring more than 48GB RAM. Four nodes are available via SSH with round-robin distribution.

## Usage Restrictions

These systems should NOT be used for intensive computational tasks unless the task requires significant memory (greater than 48GB). Other tasks should be limited in quantity and runtime. Do not run more than 10 jobs or exceed 1,000 CPU-seconds.

## Storage Access

Four storage types mount on Rhino nodes:
- `/fh/fast/` (fast storage)
- `/fh/economy/` (economy storage)
- `secure` storage
- `temp` storage

## Running Applications

```bash
# Load and run MATLAB
module load matlab/R2016b
matlab

# Run Firefox
firefox
```

## X11/GUI Applications

For X11 forwarding (required for GUI apps):
```bash
ssh -Y <hutchnetid>@rhino
```

Test X forwarding with `xeyes`.

## Monitoring and Enforcement

Processes accumulating more than 1,000 CPU-seconds receive warning emails. At 2,000 seconds, explanations are requested. At 4,000 seconds, processes are terminated. Combined TIME+ exceeding 1,000 across one user triggers alerts about core hogging.

## For Intensive Work

Use `grabnode` to reserve dedicated gizmo cluster nodes instead of running compute-intensive tasks on rhino.

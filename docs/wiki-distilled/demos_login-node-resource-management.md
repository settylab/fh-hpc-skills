# Login Node Resource Management (Arbiter)

Source: https://sciwiki.fredhutch.org/compdemos/login-node-resource-management/

## Overview

Arbiter manages CPU and memory allocation for individual users on shared interactive nodes (Rhino, Maestro) through background cgroup configuration. It throttles resource-intensive processes rather than terminating them.

## Versions

- Arbiter2 on Rhino systems
- Arbiter3 on newer systems like Maestro

## Resource Limits and Penalty Structure

| Stage | CPU Allocation | Memory | Duration |
|-------|---------------|--------|----------|
| Normal | 16 cores (1600%) | 86GB | Baseline |
| Penalty 1 | ~12 cores (1280%) | 86GB | 30 minutes |
| Penalty 2 | ~9 cores (960%) | 86GB | 60 minutes |

## Escalation Timeline

Exceeding normal limits for 5+ minutes triggers Penalty 1. Continuing beyond another 5 minutes triggers Penalty 2.

## Important Notes

- Memory limits are hard caps; exceeding them generates application errors (OOM kills)
- Email notifications alert users when penalties activate
- Use `grabnode` or `sbatch` to avoid login node restrictions for compute-intensive work

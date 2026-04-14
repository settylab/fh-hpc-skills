# Short Partition Usage

Source: https://sciwiki.fredhutch.org/compdemos/gizmo_short_partition/

## Overview

The short partition serves high-volume jobs requiring guaranteed execution, unlike the restart partition which offers no time guarantees.

## Time Committed Concept

Usage is calculated as remaining runtime multiplied by cores requested.

Example: An account has two jobs: one with 4 cores and 1 hour remaining, another with 2 cores and 10 minutes remaining. Total committed = 4 x 60 + 2 x 10 = 260 core-minutes.

## Limits

- Maximum time committed: 480,000 core-minutes per account
- Maximum wall time per job: 12 hours
- No specific core limit (theoretically up to 7,000 cores for 1 hour)
- Extensions are NOT available for short partition jobs
- Same priority and fairshare as campus partition

## Usage

```bash
sbatch -p short -t 1:00:00 myscript.sh
```

Default wall time is 1 hour. Requesting over 12 hours causes the job to be held.

## Error Messages

With srun:
```
srun: Requested partition configuration not available now
```

With sbatch (time limit exceeded):
```
$ squeue -u user -p short
  JOBID PARTITION  NAME  USER ST  TIME NODES NODELIST(REASON)
  27075194  short  wrap  user PD  0:00   1   (PartitionTimeLimit)
```

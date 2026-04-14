# MATLAB on Fred Hutch HPC

Source: https://sciwiki.fredhutch.org/compdemos/matlab/

## Interactive MATLAB

Requires NoMachine (NX) for remote display. Do NOT run on rhino nodes directly.

```bash
ssh rhino
grabnode          # request CPU and memory
module load MATLAB/R2022B
matlab
```

## Batch Job Submission

```bash
#!/bin/bash
#SBATCH --qos=matlab
#SBATCH --timelimit=3-0

. /app/lmod/lmod/init/profile
module load MATLAB/R2022B

matlab -nodisplay -nosplash -nodesktop -r "run('myAnalysisJob.m $1 $2'); exit;"
```

The `--qos=matlab` flag is MANDATORY for license management.

## License

Shared network licenses limited to 4 concurrent users.

## Parallel Computing

MATLAB Distributed Compute Engine enables parallelized operations across multiple cores/nodes.

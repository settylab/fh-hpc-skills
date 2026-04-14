# Introduction to rslurm

Source: https://sciwiki.fredhutch.org/compdemos/rslurm_intro/

## Overview

The `rslurm` R library distributes calculations across Slurm jobs, creating and managing self-contained tasks while aggregating outputs. Best for pleasantly-parallel computations where components do not communicate.

## Setup

```r
module purge
ml R
```

## Core Functions

- `slurm_apply()`: Distributes across multiple parameter sets
- `slurm_call()`: Single parameter set

## Workflow (Monte Carlo Pi Example)

```r
# 1. Define function
sim.pi <- function(iterations = 1000) {
  x.pos <- runif(iterations, min=-1, max=1)
  y.pos <- runif(iterations, min=-1, max=1)
  draw.pos <- ifelse(x.pos^2 + y.pos^2 <= 1, TRUE, FALSE)
  draws.in <- length(which(draw.pos == TRUE))
  result <- data.frame(iterations, draws.in)
  return(result)
}

# 2. Create parameter dataframe
params <- data.frame(iterations = rep(1000, 100))

# 3. Submit jobs
sjob1 <- slurm_apply(
  sim.pi, params,
  jobname = "rslurm-pi-example",
  nodes = 10,
  cpus_per_node = 1
)

# 4. Check status
get_job_status(sjob1)

# 5. Collect results
res <- get_slurm_out(sjob1, outtype = "table")

# 6. Use results
my_pi <- 4 / (sum(res$iterations) / sum(res$draws.in))

# 7. Cleanup
cleanup_files(sjob1)
```

## Notes

- `nodes` parameter is misleadingly named: it sets the task count, distributing parameter rows across tasks
- `cpus_per_node` sets cores per task

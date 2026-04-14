# Rslurm and Tximport Example

Source: https://sciwiki.fredhutch.org/compdemos/rslurm_example/

## Overview

Using rslurm to submit tximport RNA-seq processing jobs from interactive R to Gizmo cluster.

## Setup

```bash
module purge
ml R/3.4.3-foss-2016b-fh2
ml rstudio/1.1.383
```

## SLURM Options

```r
sopt <- list('nodes'='1',
             'cpus-per-task'='1',
             'partition'='campus',
             'mem'='6G',
             'time' = '24:00:00',
             'mail-type'='END,FAIL',
             'mail-user'='USER@fredhutch.org')
```

## Submit Job

```r
txi.geneLevel.job <- slurm_call(
    f = tximport,
    jobname = "tximport_Gene",
    params = list(files = files,
                  type = "kallisto",
                  tx2gene = tx2gene,
                  txIn = TRUE, txOut = FALSE,
                  countsFromAbundance = "scaledTPM"),
    slurm_options = sopt,
    submit = TRUE)

print_job_status(txi.geneLevel.job)
```

## Retrieve Results

```r
results <- get_slurm_out(txi.geneLevel.job)
# Or directly from RDS
results <- readRDS("_rslurm_tximport_Gene/results_0.RDS")
```

Key advantage: continue interactive R work while compute-intensive functions run on the cluster.

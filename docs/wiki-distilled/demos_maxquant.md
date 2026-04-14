# MaxQuant Proteomics on Gizmo

Source: https://sciwiki.fredhutch.org/compdemos/maxquant/

## Overview

MaxQuant is a quantitative proteomics software for analyzing mass-spectrometric data on Fred Hutch's Gizmo cluster.

## Workflow

1. Configure on local Windows machine, producing `mqpar.xml`
2. Place data files (.mzXML or .raw), FASTA files, and XML on `/fh/fast`
3. Edit XML: convert Windows paths to Linux paths (X: becomes /fh/fast)
4. Set `useDotNetCore` to `False` (MaxQuant 1.6.15.0+)
5. Set `<numThreads>` to match number of data files (max 36)

## Submission Script

```bash
#!/usr/bin/env bash
#SBATCH --mail-type=END
#SBATCH -n 1
#SBATCH -c 24
#SBATCH --mem 250G
#SBATCH -t 3-0

source /app/lmod/lmod/init/bash
module use /app/easybuild/modules/all
ulimit -n 655360
ml MaxQuant/1.6.10.43-foss-2018b
maxquantcmd mqpar.xml
```

```bash
sbatch submit.sh
```

## Monitoring

```bash
tail -f slurm-[jobid].out    # log output
squeue --job [jobid]          # status (R = running)
```

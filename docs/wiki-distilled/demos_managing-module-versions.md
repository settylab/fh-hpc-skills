# Managing Module Versions

Source: https://sciwiki.fredhutch.org/compdemos/managing-module-versions/

## Core Principle

Always specify full module versions rather than relying on defaults. Defaults may change over time, leading to unreproducible results.

## Best Practice

Specify modules directly in workflow files (Slurm scripts, Nextflow, Cromwell WDL) with versions tracked in source control.

## Method 1: Module RC File (~/.modulerc)

```
module-version Bowtie2/2.4.4-GCC-11.2.0 default
module-version cutadapt/4.1-GCCcore-11.2.0 default
module-version SAMtools/1.16.1-GCC-11.2.0 default
module-version BEDTools/2.30.0-GCC-11.2.0 default
```

## Method 2: Module Collections (Lmod)

```bash
# Load and save a collection
module load Bowtie2/2.4.4-GCC-11.2.0 cutadapt/4.1-GCCcore-11.2.0 SAMtools/1.16.1-GCC-11.2.0
module save mymodules

# View saved collections
module savelist

# Restore a collection
ml restore mymodules

# Create default collection (loads without specifying name)
module save
ml restore
```

## Warning

Do NOT load modules in shell startup files (~/.bashrc, ~/.zshrc). This causes unexpected results and slower login times.

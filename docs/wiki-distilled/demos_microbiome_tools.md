# Microbiome Analysis Tools

Source: https://sciwiki.fredhutch.org/compdemos/microbiome_tools/

## Overview

Nextflow-based workflows for microbiome research, all using Docker containers for dependency management.

## Available Tools

- **Bacterial Genome Annotation**: NCBI PGAP tool, FASTA input with metadata, hours per genome
- **16S Amplicon Analysis**: maliampi workflow (dada2 + pplacer), requires manifest.csv with specimen/read_1/read_2
- **Microbial Genome Assembly**: UniCycler, supports hybrid assembly (short + long reads)
- **Genome Circularization**: Circlator, converts linear to circular assemblies
- **Pan-Genome Analysis**: anvi'o via nf-anvio-pangenome
- **Microbial RNAseq**: Whole-genome shotgun alignment with rRNA filtering
- **Viral Metagenomics**: Read alignment against viral reference genomes by NCBI accession

## Infrastructure

All workflows use Nextflow for reproducibility. Docker containers manage dependencies. Reference data in Fred Hutch public S3 buckets.

## Contact

Sam Minot (sminot@fredhutch.org) for questions or additional functionality.

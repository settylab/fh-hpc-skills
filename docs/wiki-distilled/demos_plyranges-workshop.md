# plyranges Workshop (Bioconductor)

Source: https://sciwiki.fredhutch.org/compdemos/plyranges-workshop/

## Overview

plyranges applies dplyr-style operations to genomic range data (GRanges objects). Requires R >= 3.5.0.

## Setup

```r
install.packages("BiocManager")
BiocManager::install("plyranges")
```

On rhino:
```bash
ssh -X HutchID@rhino
ml R/3.5.0-foss-2016b-fh1
ml rstudio/1.1.383
rstudio &
```

## Core Verbs

- `mutate()`: Add/modify metadata columns
- `filter()`: Return ranges matching conditions
- `summarise()`: Aggregate operations
- `group_by()` / `ungroup()`: Group operations by metadata
- `select()`: Isolate specific columns

## Genomic Operations

- `anchor_start()`, `anchor_end()`, `anchor_center()`, `anchor_3p()`, `anchor_5p()`: Anchor points for range arithmetic
- `reduce_ranges()`: Aggregate nearby ranges
- `disjoin_ranges()`: Create union of all endpoints
- `filter_by_overlaps()`: Filter by overlapping ranges
- `join_overlap_inner()`, `join_overlap_left()`, `join_overlap_intersect()`: Overlap joins
- `bind_ranges()`: Combine multiple GRanges with `.id` column

## Example

```r
library(plyranges)
genes <- data.frame(seqnames = "VI",
                    start = c(3322, 3030), end = c(3846, 3338),
                    strand = c("-", "-"), gene_id = c("YFL064C", "YFL065C"))
gr <- as_granges(genes)
gr %>% mutate(gene_type = "ORF") %>% filter(width > 400)
```

# GDC Data Download with R

Source: https://sciwiki.fredhutch.org/compdemos/GDC_Data_Download/

## Overview

Accessing TCGA and TARGET next-generation sequencing data from GDC using R/Bioconductor GenomicDataCommons package.

## Setup

```r
BiocManager::install('GenomicDataCommons')
library(GenomicDataCommons)
GenomicDataCommons::status()
```

## Query and Download Gene Expression

```r
qfiles <- files(fields=desired_fields) %>%
  filter(~ type == 'gene_expression' &
         analysis.workflow_type == 'HTSeq - Counts' &
         cases.project.project_id == "TARGET-AML")

manifest_df <- qfiles %>% manifest()

dir.create("Expn_Data")
gdc_set_cache(directory = "Expn_Data/")
fnames <- gdcdata(manifest_df$id, progress=FALSE, access_method="api")
```

## Clinical Data

```r
case_ids <- cases() %>%
  filter(~ project.project_id == "TARGET-AML") %>%
  ids()

clin_res <- gdc_clinical(case_ids)
full_clin <- with(clin_res,
  main %>%
  left_join(demographic, by="case_id") %>%
  left_join(diagnoses, by="case_id"))
```

## Notes

- Default downloads "Harmonized" data (GRCh38), not legacy
- `results_all()` returns nested lists
- Filter out files with multiple associated IDs before processing

# R Matrix Operation Bug (foss/2018b)

Source: https://sciwiki.fredhutch.org/compdemos/r-2018b-matrix-errors/

## Bug Description

R installations built with the Easybuild toolchain `foss/2018b` produce inconsistent and varying results for matrix dot product calculations (`%*%` operator).

## At-Risk Scenarios

1. **Direct module loading**: R modules named with `foss-2018b` (e.g., "R/3.6.2-foss-2018b")
2. **RStudio dependency**: Loading newer R then rstudio module triggers foss/2018b
3. **Cascading toolchain loads**: Additional modules trigger foss/2018b reload

## Diagnostic Test

```r
M <- matrix(1:300^2, nrow = 300)
Mt <- t(M)
tmp <- M %*% Mt
max(tmp)
which(tmp == max(tmp), arr.ind = TRUE)
```

Expected: `max(tmp)` = 814054500000, at row 300, col 300.

## Mitigation

Test code with a newer toolchain and look for unexpected results.

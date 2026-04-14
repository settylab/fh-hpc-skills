# R Tips and Tricks

Source: https://sciwiki.fredhutch.org/compdemos/R_tips_tricks/

## Package Installation Sources

### CRAN vs Bioconductor

You cannot use CRAN instructions to install a Bioconductor package, but you CAN use Bioconductor's installer for CRAN packages. When installing from mixed sources, use Bioconductor's installation method for both.

### GitHub Packages

Two-step process recommended:
1. Install from official repository (CRAN or Bioconductor) first
2. Then upgrade with `devtools::install_github()`

GitHub installation methods may not automatically resolve all dependencies, so the initial official install provides stability.

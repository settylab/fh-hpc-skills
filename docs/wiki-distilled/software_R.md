# R and RStudio at Fred Hutch

Source: https://sciwiki.fredhutch.org/scicomputing/software_R/

## Local Installation

- Download R from CRAN (cran.r-project.org) or Fred Hutch Center IT Self Service Tools
- RStudio requires prior R installation; download from rstudio.com
- Updates require two-step process: update R, then RStudio separately

## Remote Access (Rhino/Gizmo)

- SSH or NoMachine connection to rhino machines
- **Open OnDemand (recommended)**: web-based interface for cluster RStudio access

## Module Management

```bash
module spider R
ml R/3.6.2-foss-2016b-fh1
ml R/
R
```

## RStudio Server on HPC

**Launch Options:**
- Fred Hutch RStudio Server (EasyBuild modules)
- RStudio Server/Apptainer (containerized, newer versions)

**Graphics fix for low resolution:**
Tools -> Global Options -> General -> Graphics tab -> Backend: AGG

**RMarkdown plotting enhancement:**
```r
knitr::opts_chunk$set(dev="CairoPNG")
```

## Jupyter Lab with R

**IRkernel Installation:**
```r
install.packages("IRkernel", repos="https://cran.r-project.org")
IRkernel::installspec()
```

**.Rprofile Configuration:**
```r
if (!is.na(Sys.getenv("JPY_PARENT_PID", unset = NA))) {
    options(bitmapType = 'cairo')
}
```

**Launch Command:**
```bash
jupyter lab --ip=$(hostname) --port=$(fhfreeport) --no-browser
```

## Package Sources

1. **Bioconductor** (bioconductor.org) -- curated bioinformatics packages
2. **CRAN** -- general R packages, less rigorous vetting
3. **GitHub** -- experimental packages, not peer-reviewed

## Key Libraries and Tools

- **Tidyverse**: group of coordinating R packages for data manipulation
- **Shiny**: interactive R-powered web applications, deployable via Shinyapps.io
- **RStudio features**: R Markdowns, git/SVN integration

## Support

- Seattle useR group, R-Ladies Seattle, Cascadia RConf
- Email scicomp for module requests or helpdesk for RStudio issues

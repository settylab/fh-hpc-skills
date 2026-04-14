# Scientific Software Modules (Distilled)

Source: https://sciwiki.fredhutch.org/scicomputing/compute_scientificSoftware/

## Key Facts

- Fred Hutch uses Environment Modules (Lmod) + EasyBuild for software management.
- Over 1,000 modules are already available on the gizmo cluster.

### Fred Hutch Custom Modules

- Prefixed with `fh.` to indicate Fred Hutch-specific builds.
- Contain libraries that users have requested.
- Inherit libraries from EasyBuild base R and Python.
- The `fhR` module includes many Bioconductor libraries.
- Recommended over standard versions due to included bioinformatics packages.

### Module Categories

- **R Modules**: Detailed at /rModules/
- **Python Modules**: Detailed at /pythonModules/
- **Life Science/Bio Software**: Detailed at /scicomputing/bio-modules-18.04/

### Software Requests

Users who cannot find needed software can:
- Email `scicomp` with specific requests (include source URL and version).
- Submit GitHub issues to https://github.com/FredHutch/easybuild-life-sciences

## Commands & Examples

```bash
# Search for available modules
module avail SAMtools

# Load Fred Hutch R with Bioconductor
module load fhR
```

## Common Pitfalls

- Not checking for existing modules before requesting new installations.
- Using base R/Python modules instead of the fh-prefixed versions that include bioinformatics packages.

## Cross-references

- /scicomputing/compute_environments/ (module system details)
- https://github.com/FredHutch/easybuild-life-sciences (software request repo)

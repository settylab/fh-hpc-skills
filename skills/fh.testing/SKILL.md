---
description: "Testing scientific code: pytest, testthat, nf-test, snapshot testing, CI with GitHub Actions, and practical priorities for academic software"
---

# Testing Scientific Code

TRIGGER when: user asks about testing bioinformatics code, writing tests for pipelines, pytest or testthat on the cluster, snapshot testing, CI/CD for scientific software, or how much testing is appropriate for academic code.

## Context

Scientific code has a fundamental testing challenge: for many analyses, there is no "known correct answer" to test against (the oracle problem). Despite this, testing remains essential. Untested code is unreliable code, and unreliable code produces unreliable science. The goal is not 100% coverage but strategic testing that catches the errors most likely to invalidate your results.

Most bioinformatics training does not cover testing. This skill provides practical, prioritized guidance for researchers at Fred Hutch.

## Instructions

### Testing Levels for Bioinformatics

#### 1. Unit Tests

Test individual functions with known inputs and outputs. Focus on:

- Data parsing and format conversion
- Statistical calculations (compare against hand-computed values or reference implementations)
- Edge cases: empty inputs, single-element inputs, missing values
- String/ID manipulation (off-by-one errors in genomic coordinates are common)

#### 2. Integration Tests

Verify that pipeline steps connect correctly:

- Output format from step A matches expected input format for step B
- Intermediate files are produced with expected structure
- Database/API connections work (if applicable)
- File paths resolve correctly across environments

#### 3. Regression Tests

Capture outputs from a "known good" run and compare future runs against them:

- Store checksums or key output values (not entire large files)
- Useful when you cannot derive expected outputs analytically
- Catches silent breakage from dependency updates or code changes
- Update baselines deliberately when expected behavior changes

#### 4. End-to-End Tests

Run the full pipeline on a small, curated test dataset:

- Dataset must be small enough to complete in minutes, not hours
- Include representative complexity (multiple samples, edge cases)
- Store test data in version control or a stable URL
- Validates the entire execution path including environment setup

#### 5. Negative Tests

Verify the pipeline fails gracefully on bad input:

- Malformed input files, missing columns, wrong formats
- Missing required files or directories
- Invalid parameter combinations
- Out-of-range values

### pytest (Python)

```python
# tests/test_analysis.py
import pytest
import numpy as np
from mypackage.analysis import normalize, differential_expression

def test_normalize_basic():
    """Known input/output pair."""
    raw = np.array([[10, 20], [30, 40]])
    result = normalize(raw)
    expected = np.array([[0.25, 0.5], [0.75, 1.0]])
    np.testing.assert_allclose(result, expected, rtol=1e-5)

def test_normalize_empty():
    """Edge case: empty input."""
    with pytest.raises(ValueError, match="empty"):
        normalize(np.array([]))

def test_normalize_single_sample():
    """Edge case: single sample."""
    raw = np.array([[5, 10]])
    result = normalize(raw)
    assert result.shape == (1, 2)

@pytest.fixture
def small_dataset(tmp_path):
    """Create a minimal test dataset."""
    data_file = tmp_path / "counts.csv"
    data_file.write_text("gene,sample1,sample2\nTP53,100,200\nBRCA1,50,75\n")
    return data_file

def test_differential_expression(small_dataset):
    """Integration test with fixture."""
    result = differential_expression(small_dataset)
    assert "pvalue" in result.columns
    assert all(result["pvalue"] >= 0)
    assert all(result["pvalue"] <= 1)
```

Run tests:

```bash
# Load Python on Gizmo
ml fhPython/3.11.3-foss-2023a

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mypackage --cov-report=term-missing

# Run a specific test
pytest tests/test_analysis.py::test_normalize_basic
```

#### pytest fixtures for scientific code

```python
@pytest.fixture(scope="session")
def reference_genome(tmp_path_factory):
    """Download or create a small reference genome for testing.
    Session-scoped so it's only created once per test run."""
    ref_dir = tmp_path_factory.mktemp("reference")
    ref_file = ref_dir / "chr22_subset.fa"
    # Create a minimal FASTA or copy from test data
    ref_file.write_text(">chr22\nACGTACGTACGT\n")
    return ref_file
```

### testthat (R)

```r
# tests/testthat/test-analysis.R
library(testthat)

test_that("normalize_counts returns expected values", {
  raw <- matrix(c(10, 30, 20, 40), nrow = 2)
  result <- normalize_counts(raw)
  expect_equal(dim(result), c(2, 2))
  expect_true(all(result >= 0 & result <= 1))
})

test_that("normalize_counts rejects empty input", {
  expect_error(normalize_counts(matrix(nrow = 0, ncol = 0)), "empty")
})

test_that("differential_expression returns valid p-values", {
  # Use a small built-in or bundled dataset
  result <- run_de(test_counts, test_metadata)
  expect_true(all(result$pvalue >= 0 & result$pvalue <= 1))
  expect_true("log2FoldChange" %in% colnames(result))
})
```

Run tests:

```r
# In R on Gizmo
ml R/4.4.1-foss-2023b
R -e 'testthat::test_dir("tests/testthat")'

# Or from within R
devtools::test()
```

### nf-test (Nextflow)

nf-test is purpose-built for testing Nextflow pipelines. It supports snapshot testing, dependency analysis, and parallelized execution.

```groovy
// tests/my_process.nf.test
nextflow_process {
    name "Test MY_PROCESS"
    script "../main.nf"
    process "MY_PROCESS"

    test("Should run with default parameters") {
        when {
            process {
                """
                input[0] = file("${projectDir}/tests/data/sample.bam")
                """
            }
        }
        then {
            assert process.success
            assert snapshot(process.out).match()
        }
    }

    test("Should fail on empty input") {
        when {
            process {
                """
                input[0] = file("${projectDir}/tests/data/empty.bam")
                """
            }
        }
        then {
            assert process.failed
        }
    }
}
```

Run tests:

```bash
# Install nf-test
nf-test test tests/

# Update snapshots after intentional changes
nf-test test tests/ --update-snapshot
```

nf-test's snapshot testing captures process outputs and compares against stored baselines. This is effective for regression testing when you cannot derive expected outputs analytically.

### Snapshot Testing for Pipeline Outputs

When full output comparison is impractical (large files, floating-point variation), test strategic properties:

```python
# Snapshot key properties, not entire files
def test_pipeline_output_structure(pipeline_output):
    """Regression test: output structure matches baseline."""
    import pandas as pd

    result = pd.read_csv(pipeline_output)

    # Structural checks
    assert result.shape[0] > 0, "Output is empty"
    assert set(result.columns) == {"gene", "pvalue", "log2fc", "padj"}

    # Statistical sanity
    assert result["pvalue"].between(0, 1).all()
    assert result["padj"].between(0, 1).all()
    assert (result["padj"] >= result["pvalue"]).all(), "Adjusted p-values should be >= raw"

    # Regression: compare against known-good summary stats
    assert abs(result["log2fc"].mean() - EXPECTED_MEAN) < 0.01
    assert result.shape[0] == EXPECTED_N_GENES
```

For checksums:

```bash
# Generate checksums for key outputs
md5sum results/*.csv > checksums.md5

# Verify against baseline
md5sum -c checksums.md5
```

### CI with GitHub Actions

A minimal CI workflow for a bioinformatics project:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest tests/ -v --cov=mypackage --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
```

For conda-based projects:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up conda
        uses: conda-incubator/setup-miniconda@v3
        with:
          environment-file: environment.yml
          activate-environment: myenv

      - name: Run tests
        shell: bash -el {0}
        run: pytest tests/ -v
```

For Nextflow pipelines:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Nextflow
        uses: nf-core/setup-nextflow@v2

      - name: Install nf-test
        uses: nf-core/setup-nf-test@v1

      - name: Run pipeline tests
        run: nf-test test tests/ --profile test,docker
```

### Practical Priorities for Academic Software

Comprehensive testing is aspirational. Here is a prioritized approach (Edmonds et al., 2022):

**Must have (day one):**
1. Test installation in a clean environment. If others cannot install your software, nothing else matters.
2. One end-to-end test with a small dataset that runs in under 5 minutes.
3. CI that runs on every push (even if it only runs the above two tests).

**Should have (before publication):**
4. Unit tests for core algorithms (the code that produces the numbers you report).
5. Regression tests for key outputs (snapshot checksums or summary statistics).
6. Negative tests for the most common user errors (wrong file format, missing columns).

**Nice to have (for maintained software):**
7. Coverage reporting with badges in README.
8. Integration tests for each pipeline step.
9. Performance benchmarks to detect regressions.
10. Property-based testing for statistical functions (hypothesis library in Python).

The gap between "no tests" and "one good test" is far larger than the gap between "one test" and "ten tests." Start with one.

### Testing on Gizmo

For tests that require cluster resources (GPU, large memory, specific software):

```bash
# Run tests in a Slurm job
sbatch --cpus-per-task=4 --mem=16G --time=1:00:00 --wrap="cd /fh/fast/pi_name/project && ml fhPython/3.11.3-foss-2023a && pytest tests/ -v"

# For GPU tests
sbatch --partition=chorus --gres=gpu:1 --time=1:00:00 --wrap="ml fhPython/3.11.3-foss-2023a && pytest tests/test_gpu.py -v"
```

Keep test datasets small. Store them in the repo under `tests/data/` or download them in a fixture. Do not store large test data in Git; use Git-LFS or download from a stable URL.

## Principles

- Start with one test. The marginal value of the first test is enormous.
- Test what matters most: the code that produces the numbers you publish.
- Use small, fast test datasets. Tests that take hours do not get run.
- Automate with CI. Tests that require manual execution get forgotten.
- Snapshot testing bridges the oracle problem for pipeline outputs.
- Clean-environment installation testing catches dependency issues early.
- Testing badges signal software maturity to reviewers and users.

## References

- Edmonds et al. (2022). "Software testing in microbial bioinformatics: a call to action." Microbial Genomics. https://pmc.ncbi.nlm.nih.gov/articles/PMC9176277/
- nf-test (2025). "Improving the reliability, quality, and maintainability of bioinformatics pipelines with nf-test." GigaScience. https://academic.oup.com/gigascience/article/doi/10.1093/gigascience/giaf130/8297140
- pytest: https://docs.pytest.org/
- testthat: https://testthat.r-lib.org/
- nf-test: https://www.nf-test.com/
- GitHub Actions: https://docs.github.com/en/actions

---
description: "FAIR data management, NIH DMSP compliance, data formats, versioning, and metadata standards for Fred Hutch HPC researchers"
---

# Data Management for Fred Hutch HPC Research

TRIGGER when: user asks about data management plans, FAIR principles, NIH DMSP, data sharing requirements, data formats for long-term storage, data versioning (DVC, Git-LFS), metadata standards, or how to organize research data on Fred Hutch storage for compliance and reproducibility

## Context

NIH requires a Data Management and Sharing Plan (DMSP) for all funded research (effective January 2023). The NIH Strategic Plan for Data Science 2025–2030 further emphasizes FAIR principles. Fred Hutch researchers generating data on Gizmo must make deliberate choices about formats, metadata, storage tiers, and sharing repositories to meet these requirements without extra effort at publication time.

This skill covers the full lifecycle: generating data on HPC, storing it in FAIR-compliant formats, versioning it alongside code, and depositing it in appropriate repositories.

## Instructions

### 1. NIH DMSP — What You Actually Need

A DMSP must address six elements. Here is what each means in practice for Fred Hutch computational work:

| DMSP Element | What to Write | Fred Hutch Action |
|---|---|---|
| **Data types** | Describe modalities (RNA-seq counts, imaging, clinical) and estimated volume | Inventory your pipeline outputs: BAM/CRAM, count matrices, processed objects |
| **Tools and software** | List analysis software, versions, and workflows | Pin module versions (`module load R/4.4.0`), use containers, commit `environment.yml` |
| **Standards** | Metadata schemas, ontologies, file formats | Use domain standards (MIAME, MINSEQE) and open formats (Parquet, AnnData, Zarr) |
| **Preservation and access** | Where data will live, for how long, under what access controls | Map to Fred Hutch tiers (Fast for active, Economy/S3 for archive) + public repositories |
| **Access and reuse** | Licenses, embargoes, controlled-access plans | Default to CC-BY-4.0 for data, CC0 for metadata; use dbGaP for controlled-access human genomics |
| **Oversight** | Who is responsible | Name the PI and a data steward; define review checkpoints |

**Practical tip:** Write the DMSP before starting analysis, not at manuscript submission. The plan shapes directory structure, naming conventions, and metadata capture from day one.

### 2. FAIR Principles on Fred Hutch HPC

#### Findable

- Assign persistent identifiers at deposition time (DOIs via Zenodo, accession numbers via GEO/SRA).
- Use consistent, descriptive directory naming on `/fh/fast/`: `{project}/{assay}/{YYYY-MM-DD}_{description}/`.
- Maintain a machine-readable sample sheet (Parquet or TSV with controlled column names) as the authoritative metadata index for every dataset.

#### Accessible

- Deposit in recognized repositories before or at publication (see Repository Guide below).
- For controlled-access human data, use dbGaP or controlled-access tiers of domain repositories.
- On Fred Hutch storage, set group permissions so lab members can access shared data: `chmod g+rX` on `/fh/fast/` directories.

#### Interoperable

- Use standard file formats (next section).
- Use controlled vocabularies: NCBI Taxonomy IDs for organisms, Ensembl/GENCODE gene IDs, Cell Ontology for cell types, EFO for experimental factors.
- Store metadata in structured formats (Parquet, JSON, YAML) rather than free-text README files.

#### Reusable

- Attach a license to every deposited dataset (CC-BY-4.0 is the NIH-recommended default).
- Document provenance: record the pipeline version (git commit SHA), input files (checksums), parameters, and software versions that produced each output.
- Include processing scripts alongside data deposits (archive code via Zenodo + GitHub integration).

### 3. Recommended Repositories by Data Type

| Data Type | Primary Repository | Accession Type | Notes |
|---|---|---|---|
| Raw sequencing reads | **SRA** (NCBI) | SRR/SRX accessions | Required for most genomics journals |
| Processed gene expression | **GEO** (NCBI) | GSE/GSM accessions | Accepts count matrices, metadata; links to SRA for raw |
| Proteomics/mass spec | **PRIDE** (EMBL-EBI) | PXD accessions | ProteomeXchange partner |
| Metabolomics | **MetaboLights** (EMBL-EBI) | MTBLS accessions | ISA-Tab metadata format |
| Immunology/flow cytometry | **ImmPort** | ImmPort study IDs | NIH/NIAID-funded studies often required here |
| Imaging | **BioImage Archive** (EMBL-EBI) | S-BIAD accessions | Replacing legacy Image Data Resource |
| Protein structures | **PDB** / **ModelArchive** | PDB IDs | AlphaFold predictions go to ModelArchive |
| Clinical/phenotype (controlled) | **dbGaP** (NCBI) | phs accessions | Controlled-access human genomics/phenotypes |
| General-purpose / code | **Zenodo** | DOI | Accepts any file type, GitHub integration, 50GB per record |
| Tabular supplementary data | **Dryad** or **figshare** | DOI | Good for processed results, figures, supplementary tables |

**Rule of thumb:** Use the domain-specific repository first. Fall back to Zenodo or Dryad for data types without a dedicated repository.

### 4. Data Format Longevity

Choose formats that are self-describing, language-agnostic, and performant at scale. Avoid formats that lock you into a single tool or degrade under concurrent access.

#### Tabular Data → Parquet

- **Use for:** QC metrics, sample metadata, variant tables, differential expression results, any rectangular data.
- **Why not CSV/TSV?** No type information, no compression, slow to parse at scale, ambiguous quoting/encoding. A 2GB CSV becomes ~200MB Parquet with full type fidelity.
- **Ecosystem:** Native support in Python (pandas, polars, pyarrow), R (arrow), Rust, Java, and every major query engine.

```python
# Python: save a DataFrame as Parquet
import pandas as pd
df.to_parquet("results/qc_metrics.parquet", engine="pyarrow")

# R: save a data frame as Parquet
library(arrow)
write_parquet(df, "results/qc_metrics.parquet")
```

#### N-Dimensional Arrays → Zarr v3

- **Use for:** Imaging stacks, spatial transcriptomics grids, tensor outputs, any chunked array data.
- **Why not HDF5?** HDF5 is a monolithic file that cannot be read in parallel from object storage, has a massive C library dependency, and suffers from file corruption on interrupted writes. Zarr stores each chunk as a separate object, enabling parallel cloud reads, sharding for very large arrays, and safe concurrent writes.
- **When HDF5 is acceptable:** Single-user, local-only workflows where cloud access and concurrent reads are not needed.

```python
import zarr
store = zarr.open("results/spatial_data.zarr", mode="w")
store.create_array("expression", data=matrix, chunks=(1000, 1000))
```

#### Single-Cell → AnnData + TileDB-SOMA

- **AnnData (.h5ad):** Standard interchange format for Scanpy/Python single-cell workflows. Use for sharing and publication.
- **TileDB-SOMA:** Cloud-optimized, scalable backend for datasets too large for in-memory AnnData. Supports both Python (tiledbsoma) and R (tiledbsoma) through the same on-disk format, eliminating the need to maintain separate h5ad and Seurat RDS copies.
- **Migration path:** Store working data in TileDB-SOMA for analysis, export to h5ad for repository deposition (GEO, CELLxGENE).

```python
import tiledbsoma
# Open a SOMA experiment for out-of-core analysis
exp = tiledbsoma.Experiment.open("my_atlas.soma")
query = exp.axis_query("RNA", obs_query=tiledbsoma.AxisQuery(value_filter="cell_type == 'T cell'"))
adata = query.to_anndata()
```

#### Summary Table

| Data Shape | Recommended Format | Avoid | Notes |
|---|---|---|---|
| Tabular / rectangular | **Parquet** | CSV, TSV, Excel | Arrow ecosystem, columnar compression |
| N-D arrays / images | **Zarr v3** | HDF5 (for cloud/shared) | Cloud-native, chunk-parallel |
| Single-cell objects | **AnnData** (interchange) / **TileDB-SOMA** (at scale) | Raw RDS, pickle | Cross-language via SOMA |
| Aligned reads | **CRAM** | BAM (for archival) | 40-60% smaller than BAM with reference |
| Variants | **VCF/BCF** | Custom text formats | BCF for programmatic access |
| Genomic intervals | **BED/BigBed** | CSV of coordinates | Indexed, standard tooling |

### 5. Version Control for Data

Code versioning (Git) is necessary but not sufficient. Data, parameters, and environments must be tracked together.

#### DVC (Data Version Control)

DVC tracks large files and datasets alongside Git. It stores lightweight pointer files (`.dvc`) in your Git repo while the actual data lives in remote storage.

```bash
# Initialize DVC in your project
dvc init

# Track a large file
dvc add data/raw_counts.h5ad
git add data/raw_counts.h5ad.dvc data/.gitignore
git commit -m "Track raw counts with DVC"

# Push data to remote storage (Fred Hutch S3)
dvc remote add -d hutch s3://fh-pi-setty-m-eco/dvc-cache
dvc push
```

**When to use DVC:**
- Datasets that change between pipeline versions (updated reference genomes, retrained models).
- ML experiment tracking alongside MLflow.
- When you need to reproduce exact dataset versions used in a paper.

#### Git-LFS

Git-LFS replaces large files in your repo with pointers, storing the actual content on a separate server.

```bash
# Track Parquet files with LFS
git lfs track "*.parquet"
git add .gitattributes
git add results/final_table.parquet
git commit -m "Add final results table"
```

**When to use Git-LFS:**
- Binary assets under ~2GB that are integral to the repo (trained model weights, reference files).
- When DVC's additional complexity is not warranted.
- GitHub free tier allows 1GB LFS storage, 1GB/month bandwidth.

#### Comparison

| Feature | DVC | Git-LFS |
|---|---|---|
| Storage backend | S3, GCS, SSH, local | Git hosting provider |
| Pipeline tracking | Yes (dvc.yaml) | No |
| Experiment tracking | Yes (with DVCLive) | No |
| Max file size | Unlimited (limited by backend) | ~2GB practical limit |
| Complexity | Medium | Low |
| Best for | Dataset versioning, ML pipelines | Binary assets in repos |

### 6. Fred Hutch Storage Tiers Mapped to FAIR

| FAIR Stage | Storage Tier | Path/Access | Rationale |
|---|---|---|---|
| **Active analysis** | Fast | `/fh/fast/lastname_f/` | Best I/O, daily backups, 5TB free per PI |
| **Job intermediates** | Temp/Scratch | `/hpc/temp/` | Free, auto-purged at 30 days, no backup |
| **Long-term archive** | Economy (S3) | `fh-pi-lastname-f-eco` | 100TB free, 60-day versioning, cheapest per TB |
| **Sharing / publication** | Public repository | GEO, SRA, Zenodo | Persistent IDs, globally accessible |
| **PHI / controlled** | Secure or Economy | `/fh/secure/` or S3 | Encryption + access auditing |

**Data lifecycle on Fred Hutch infrastructure:**

1. **Generate** on Gizmo → write intermediates to `/hpc/temp/`, results to `/fh/fast/`.
2. **Analyze** from `/fh/fast/` with versioned code + DVC pointers.
3. **Archive** finalized datasets to Economy/S3 (`aws s3 cp` or Motuz).
4. **Deposit** publication-ready data to domain repositories with metadata.
5. **Clean up** scratch and temp after verifying archive integrity (checksums).

**Checksumming critical transfers:**

```bash
# Generate checksums before archiving
sha256sum data/final_counts.h5ad > data/checksums.sha256

# Verify after transfer to S3
aws s3 cp s3://fh-pi-setty-m-eco/archive/final_counts.h5ad /tmp/verify.h5ad
sha256sum -c data/checksums.sha256
```

### 7. Metadata Standards for Bioinformatics

Good metadata is what makes data reusable by others (and by future-you). Use domain-specific minimum information standards.

#### By Assay Type

| Assay | Standard | Key Fields | Reference |
|---|---|---|---|
| Microarray | **MIAME** | Sample source, platform, normalization method | [FGED](https://www.fged.org/projects/miame/) |
| RNA-seq / sequencing | **MINSEQE** | Library prep, sequencing platform, read length, strandedness | [FGED](https://www.fged.org/projects/minseqe/) |
| Single-cell RNA-seq | **MINSEQE** + cell-level | Dissociation method, cell capture platform, doublet rate | [HCA metadata](https://data.humancellatlas.org/) |
| Mass spectrometry | **MIAPE** | Instrument, acquisition mode, search engine, FDR | [HUPO-PSI](https://www.psidev.info/) |
| Flow/mass cytometry | **MIFlowCyt** | Panel, gating strategy, compensation | [ISAC](https://isac-net.org/) |
| Imaging | **OME-XML** / **REMBI** | Acquisition parameters, pixel size, channel info | [OME](https://www.openmicroscopy.org/) |

#### Controlled Vocabularies to Use

- **Organisms:** NCBI Taxonomy IDs (e.g., `9606` for human, `10090` for mouse)
- **Genes:** Ensembl gene IDs or HGNC symbols (avoid mixing conventions within a project)
- **Cell types:** Cell Ontology (CL) terms
- **Diseases:** Disease Ontology (DO) or MONDO
- **Experimental factors:** Experimental Factor Ontology (EFO)
- **Anatomical sites:** Uberon

#### Practical Metadata Template

At minimum, maintain a sample sheet as a Parquet file (or TSV for simplicity) with these columns:

```
sample_id          — unique identifier, used in filenames
subject_id         — maps to patient/donor (for multi-sample subjects)
species            — NCBI Taxonomy ID
tissue             — Uberon term
disease            — DO or MONDO term
assay              — EFO term
library_prep       — protocol name and version
sequencing_platform — e.g., Illumina NovaSeq 6000
date_collected     — ISO 8601
batch              — processing batch identifier
file_r1            — path to raw FASTQ R1
file_r2            — path to raw FASTQ R2
notes              — free text for edge cases
```

Store this alongside your data in `/fh/fast/` and version-control it with Git (it is small enough).

## Principles

- Plan data management before starting analysis, not at publication time
- Use open, self-describing formats that outlive any single tool
- Apply the simplest versioning strategy that meets your needs (Git-LFS for small binaries, DVC for dataset pipelines)
- Capture metadata at the point of generation, not retroactively
- Follow Fred Hutch data security policies: PHI goes to Secure or Economy/S3 only
- Verify data integrity with checksums at every transfer boundary

## References

- NIH Data Management and Sharing Policy: https://sharing.nih.gov/data-management-and-sharing-policy
- NIH DMSP guidance: https://grants.nih.gov/grants/guide/notice-files/NOT-OD-21-013.html
- FAIR Principles: https://www.go-fair.org/fair-principles/
- Fred Hutch SciComp Wiki (Storage): https://sciwiki.fredhutch.org/scicomputing/store_overview/
- Fred Hutch SciComp Wiki (Economy/S3): https://sciwiki.fredhutch.org/scicomputing/store_objectstore/
- Apache Parquet: https://parquet.apache.org/
- Zarr v3: https://zarr.dev/
- TileDB-SOMA: https://github.com/single-cell-data/TileDB-SOMA
- DVC Documentation: https://dvc.org/doc
- Git-LFS: https://git-lfs.github.com/
- FAIR data management in multi-OMICS (PMC, 2025): https://pmc.ncbi.nlm.nih.gov/articles/PMC11788310/
- Ziemann et al. "Five pillars of computational reproducibility" (2023): https://pmc.ncbi.nlm.nih.gov/articles/PMC10591307/

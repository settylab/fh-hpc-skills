# Demos Agent Report

Agent: demos-agent
Date: 2026-04-13
Section: /compdemos/ (Resource Library)

## Summary

Processed all 45 compdemos wiki pages. Fetched content via WebFetch, distilled into structured knowledge files, and created 6 new skills.

## Pages Processed (45/45)

### Batch 1 -- Core HPC Demos (10 pages)
1. howtoRhino -- Rhino node usage, restrictions, enforcement
2. grabnode -- Interactive compute node allocation
3. gizmo_partition_index -- All partition types and limits
4. gizmo_short_partition -- Short partition time-committed model
5. login-node-resource-management -- Arbiter cgroup throttling
6. Apptainer -- Container usage on HPC (definition files, binds, cache)
7. Docker -- Docker/Apptainer workflow, Dockerfiles, image sharing
8. nextflow -- Nextflow with AWS Batch, config, resource management
9. Cromwell -- STUB PAGE (minimal content, placeholder only)
10. store_job_local -- $TMPDIR local SSD storage for jobs

### Batch 2 -- Software & Environment Demos (6 pages)
11. python_virtual_environments -- venv and Miniforge/conda setup
12. managing-module-versions -- Module RC files, collections, version pinning
13. VS-Code_lmod -- VS Code + LMOD integration script
14. rslurm_intro -- R-to-Slurm job distribution (Monte Carlo example)
15. shiny -- Shiny app deployment (SciComp pipeline and shinyapps.io)
16. alphafold3 -- AlphaFold 3 on chorus GPU partition

### Batch 3 -- Data & Cloud Demos (6 pages)
17. aws-s3 -- S3 access via CLI, Python (boto3), and R (aws.s3)
18. aws-batch -- AWS Batch job submission and monitoring
19. motuz -- Web-based data transfer tool
20. globus-personal -- Globus Connect Personal on rhino
21. snapshots -- File recovery via .snapshot directories
22. mydb -- Database-as-a-service (PostgreSQL, MariaDB, MongoDB, Neo4j)

### Batch 4 -- Remaining Demos (23 pages)
23. ssh_host_key_management -- SSH key removal and validation
24. git_tips -- Branch renaming, rebasing, GUI tools
25. python_logging -- Python logging module patterns
26. sharing-data-presigned-url -- S3 pre-signed URLs (no PHI)
27. onboard -- New user resources and support channels
28. matlab -- MATLAB on gizmo (--qos=matlab mandatory)
29. maxquant -- MaxQuant proteomics batch processing
30. microbiome_tools -- Nextflow-based microbiome analysis workflows
31. R_tips_tricks -- Package installation from mixed sources
32. ingest-Large-Data -- wget to /hpc/temp, then S3 sync
33. aws-credits -- Virtual credits and sandbox accounts
34. AWSCLI_WSL -- AWS CLI on Windows Subsystem for Linux
35. Mountain-CyberDuck -- GUI S3 clients
36. plyranges-workshop -- Bioconductor genomic range operations
37. rslurm_example -- Rslurm + tximport practical example
38. vscode_markdown_howto -- VS Code markdown editing plugins
39. github_pages-FHtheme -- Fred Hutch Jekyll theme
40. GDC_Data_Download -- GDC genomic data via R/Bioconductor
41. gdc-client-hints -- gdc-client optimization parameters
42. ucsc-track-s3 -- UCSC browser tracks via S3
43. aspera-change-destination -- Aspera download path config
44. aspera-on-nx -- Aspera Connect on NoMachine
45. r-2018b-matrix-errors -- foss/2018b matrix dot product bug

## Skills Created (6)

| Skill | Description | Source Pages |
|-------|-------------|-------------|
| fh.nextflow | Nextflow workflow management on Gizmo/AWS Batch | nextflow |
| fh.cromwell | Cromwell/WDL workflows (limited source content) | Cromwell, Docker |
| fh.alphafold | AlphaFold 3 on chorus GPU partition | alphafold3 |
| fh.vscode-remote | VS Code remote dev with LMOD modules | VS-Code_lmod, managing-module-versions, python_virtual_environments |
| fh.data-transfer | Data transfer tools (Motuz, Globus, S3, Aspera) | motuz, globus-personal, aws-s3, snapshots, ingest-Large-Data |
| fh.onboarding | New user onboarding checklist | onboard, howtoRhino, grabnode, gizmo_partition_index |

## Issues Found

1. **Cromwell page is a stub**: The wiki page at /compdemos/Cromwell/ contains no tutorial content, only navigation elements. The skill was built from Docker WDL integration content instead.
2. **Potential overlap with other agents**: Skills for containers (fh.containers), GPU (fh.gpu), grabnode (fh.grabnode), partitions (fh.partitions), storage-s3 (fh.storage-s3) already exist from other agents. My skills avoid duplicating those topics.
3. **Some demo pages are outdated**: r-2018b-matrix-errors (2018 bug), aspera pages reference old versions, plyranges uses R 3.5.0 modules. Content was distilled as-is with version context preserved.

## Completeness Assessment

100% of assigned pages processed. All 45 distilled docs written. All 6 skills created with proper frontmatter. All lockfiles cleaned up.

## Output Files

- Distilled docs: `docs/wiki-distilled/demos_*.md` (45 files)
- Skills: `skills/fh.{nextflow,cromwell,alphafold,vscode-remote,data-transfer,onboarding}/skill.md` (6 files)

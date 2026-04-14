---
description: "HPC resource descriptions and citation requirements for grant applications and publications"
---

# fh.grants

TRIGGER when: user asks about describing Fred Hutch computing resources in a grant, citing HPC infrastructure in a publication, NIH S10 grant acknowledgment, or getting cluster specs for grant writing.

## Context

Fred Hutch SciComp maintains a detailed, frequently updated document with current hardware specifications and infrastructure descriptions formatted for grant applications. This document includes non-public details not available on the wiki.

## Required Citation for Publications

Any publication using Fred Hutch computational resources must include:

> **"Fred Hutch Scientific Computing, NIH grants S10-OD-020069 and S10-OD-028685"**

This attribution is required because Fred Hutch computational resources are partially funded through the NIH S10 instrumentation grant program.

## Getting the Grant Description Document

Email SciComp at **scicomp@fredhutch.org** to request the latest version of:

**"Fred-Hutch-Computational-Resource-Description-for-Grant-Writers.docx"**

The document covers:
- Cluster hardware specifications (CPU types, core counts, memory per node)
- GPU resources (models, VRAM, availability)
- Storage infrastructure (Fast File capacity, Economy Cloud, Temp)
- Software environment and module system
- Support services and staffing
- Network and security infrastructure
- Historical investment and funding sources

## Quick Reference (Public Specs)

For context while waiting for the official document, the current Gizmo cluster includes approximately:
- ~209 compute nodes across multiple partitions
- J-class nodes: 24 cores, 350 GB RAM, GTX 1080 Ti GPU
- K-class nodes: 36 cores, 700 GB RAM, RTX 2080 Ti GPU
- Harmony nodes: 32 cores, ~1.5 TB RAM, 4x L40S GPUs (chorus partition)
- Fast File storage for active research data
- Economy Cloud (S3) for long-term archival

Always use the official SciComp document for grant submissions, as specs change and the document contains details not listed here.

## Principles

- Always request the latest document from SciComp before submitting a grant
- Never use outdated hardware specifications in grant applications
- Include the NIH S10 citation in every publication that used Fred Hutch compute resources
- Contact SciComp early in the grant-writing process for the most current information

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/compute_grants/
- Contact: scicomp@fredhutch.org

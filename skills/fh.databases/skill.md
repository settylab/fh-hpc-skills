---
description: "Database options at Fred Hutch: MyDB (Postgres, MariaDB, MongoDB, Neo4j), REDCap, and MS SQL"
---

# Fred Hutch Database Services

TRIGGER when: user asks about databases, MyDB, MariaDB, Postgres, MongoDB, Neo4j, REDCap, SQL Server, or structured data storage at Fred Hutch

## Context

Fred Hutch provides managed database services for researchers who need structured data storage beyond flat files. The primary self-service platform is MyDB, which supports four database engines. REDCap is available for clinical/survey data, and MS SQL Server for enterprise needs.

## MyDB (Self-Service)

URL: https://mydb.fredhutch.org/login (Hutch credentials)

### Available Engines

| Engine | Type | Best For |
|--------|------|----------|
| MariaDB | Relational (MySQL-compatible) | Traditional SQL workloads, web apps |
| Postgres | Relational | Complex queries, geospatial, high performance |
| MongoDB | NoSQL (document) | JSON document storage, flexible schemas |
| Neo4j | NoSQL (graph) | Network/graph data, relationship queries |

### Key Features

- Full admin rights on your databases
- Daily backups stored in Amazon cloud
- No shell access to the database system
- MariaDB supports encryption at rest and in transit
- Login with Hutch credentials

### Getting Started

1. Go to https://mydb.fredhutch.org/login
2. Authenticate with Hutch credentials
3. Create a new database instance (choose engine)
4. Use the provided connection string to connect from your code or tools

## REDCap

- Secure web application for clinical research forms (CRFs), surveys, and data collection
- HIPAA-compliant
- Features: logging, validation, branching logic, e-signatures, randomization, calculated fields
- Mobile app for offline data capture
- Export to Excel, SPSS, SAS, Stata, R
- API access for programmatic integration
- Managed by Collaborative Data Services (CDS)
- Training available through CDS REDCap Training page

## MS SQL Server

For MS SQL Server needs, contact IT Helpdesk or create a Cherwell ticket.

## Instructions

When helping users choose a database:

1. For clinical/survey data with HIPAA requirements: recommend **REDCap**
2. For general-purpose SQL with MySQL compatibility: recommend **MariaDB** via MyDB
3. For complex analytical queries or PostGIS geospatial: recommend **Postgres** via MyDB
4. For flexible document storage (JSON-heavy): recommend **MongoDB** via MyDB
5. For graph/network data: recommend **Neo4j** via MyDB
6. For enterprise SQL Server needs: direct to IT Helpdesk
7. For simple tabular data (a few CSVs, no concurrent access needed): a database may be overkill; suggest flat files

## Principles

- Request only the resources you need (CPUs, memory, time)
- Use appropriate partitions for your workload
- Respect shared infrastructure and other users
- Use versioned environments for reproducibility
- Follow Fred Hutch data security policies

## References

- SciComp Wiki: https://sciwiki.fredhutch.org/scicomputing/store_databases/
- MyDB docs: https://sciwiki.fredhutch.org/compdemos/mydb/
- MariaDB pathway: https://sciwiki.fredhutch.org/pathways/path-mydb-mariadb/

# Database Storage Options

Source: https://sciwiki.fredhutch.org/scicomputing/store_databases/

## When to Use a Database

Use a DBMS when you need structured data with complex access patterns, logging, fine-grained permissions, or backup/maintenance plans. For simple tabular data, flat files (CSV, TSV) may suffice.

## REDCap

- Secure web application for CRFs, data forms, and participant surveys
- HIPAA-compliant
- Features: logging, validation, branching logic, e-signatures, randomization, calculated fields
- Mobile app for offline data capture on tablets
- Export to Excel, SPSS, SAS, Stata, R
- API access available
- Managed by Collaborative Data Services (CDS) at Fred Hutch
- Training: CDS REDCap Training page

## MS SQL Server

- Contact IT Helpdesk or create a Cherwell ticket for administration

## MyDB (Self-Service)

- URL: https://mydb.fredhutch.org/login
- Login with Hutch credentials
- Users receive full admin rights
- Daily backups stored in Amazon cloud
- No shell access to database system

### Available Engines

| Engine | Type | Notes |
|--------|------|-------|
| MariaDB | Relational (MySQL-compatible) | Encryption at rest/in transit |
| Postgres | Relational | High-performance |
| MongoDB | NoSQL (document store) | JSON documents |
| Neo4j | NoSQL (graph database) | Graph data |

### Documentation Paths

- General MyDB docs: `/compdemos/mydb/`
- MariaDB pathway: `/pathways/path-mydb-mariadb/`

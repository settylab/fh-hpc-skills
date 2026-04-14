# MyDB Database Service

Source: https://sciwiki.fredhutch.org/compdemos/mydb/

## Overview

MyDB (https://MyDB.fredhutch.org/login) is a database-as-a-service offering form-based setup for PostgreSQL, MariaDB, MongoDB, and Neo4j. Login with HutchNet ID.

## Available Databases

| Database | Versions | Type |
|----------|----------|------|
| MariaDB | 10.3, 10.1 | Relational SQL (MySQL fork) |
| PostgreSQL | 13.2, 9.6 | Relational SQL |
| MongoDB | 4.2.2, 3.4 | NoSQL document store |
| Neo4j | 3.2.5 | Graph database |

## MariaDB Connection

```bash
ml MariaDB
mariadb --host mydb.fredhutch.org --port <port> --user <username> --password
```

## Configuration Options

- **DB/Container Name**: Alphanumeric, underscores, periods, dashes (max 128 chars)
- **Backup**: Weekly, daily, or never (backups go to AWS S3)
- **Data Storage**: Redundant NVMe drives, "standard" volume type

## Important

- Does NOT support PHI/PII storage
- MongoDB governed by SSPL license (source code disclosure may be required)

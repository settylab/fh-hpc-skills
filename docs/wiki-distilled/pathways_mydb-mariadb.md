# Configure and Use a MariaDB Database on MyDB

Source: https://sciwiki.fredhutch.org/pathways/path-mydb-mariadb/

## Key Facts

- MyDB (db4sci) is Fred Hutch's self-service database provisioning platform at https://mydb.fredhutch.org
- Supports MariaDB (MySQL-compatible) containers
- Access from rhino/gizmo nodes using the MariaDB module
- TLS/SSL is currently unsupported; contact SciComp for "in transit" encryption requirements
- MySQL Workbench and other graphical interfaces are also available

## Commands & Examples

```bash
# Log in to MyDB web interface
# Navigate to https://mydb.fredhutch.org/login with your HutchNet ID

# On rhino/gizmo, load the MariaDB module
ml MariaDB

# Connect using credentials from MyDB provisioning
# (use the command provided during database creation)
mysql -h mydb -u <username> -p --port <port> <database_name>
```

## Common Pitfalls

- Passing passwords as command-line arguments (visible in process table); use `-p` flag without value to get a prompt instead
- Not recording the username, password, and port securely during database creation
- Forgetting to load the MariaDB module before connecting
- Assuming TLS/SSL is available (it is not currently supported)

## Cross-references

- Full MyDB documentation: /compdemos/mydb#use
- Data storage overview: /scicomputing/store_overview/

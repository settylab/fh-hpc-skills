# Migrating Data from Fast File to Economy Cloud

Source: https://sciwiki.fredhutch.org/pathways/path-migrating-data-from-fast-to-cloud/

## Key Facts

- Economy Cloud is managed AWS S3 storage with buckets named `fh-pi-eco` and `fh-pi-eco-public`
- Fast File is the primary research data storage (accessible as X: drive or `\\center\fh\fast`, mounted at `/fh/fast/`)
- Temp is working storage for rhino/gizmo compute (not backed up, mounted at `/fh/temp/`)
- Motuz is the web-based file transfer tool at https://motuz.fredhutch.org
- Motuz copies files but does NOT delete source files; deletion must be done separately
- AWS credentials are required to access S3 Economy Cloud

## Steps

1. Obtain AWS credentials for S3 Economy Cloud access
2. Connect to campus network (on-site WiFi or VPN)
3. Access Motuz at https://motuz.fredhutch.org with HutchNet ID
4. Create a new cloud connection in Motuz for Economy Cloud
5. Copy files from Fast/Temp to Economy Cloud
6. Verify transfer success, then manually delete source files if desired

## Common Pitfalls

- Assuming Motuz deletes source files after transfer (it does not)
- Not having AWS credentials configured before starting
- Attempting to use Motuz from off-campus without VPN
- Not verifying transfer completion before deleting source data

## Cross-references

- AWS credentials: /scicomputing/access_credentials/
- Object storage (S3): /scicomputing/store_objectstore/
- Data storage overview: /scicomputing/store_overview/

# Ingesting Large External Datasets

Source: https://sciwiki.fredhutch.org/compdemos/ingest-Large-Data/

## Workflow

### 1. Download to Temporary Storage

```bash
cd /hpc/temp/lastname_f/
mkdir ingestedDataDir
cd ingestedDataDir
wget --recursive ftp://user@ftp.broadinstitute.org/bundle/
```

Use `--no-clobber` to skip existing files on repeated transfers.

### 2. Credential Options

```bash
# Command-line (least secure)
wget ftp://basil:password@site.example.org
wget --user=basil --password=password ftp://site.example.org

# File-based (~/.wgetrc, more secure)
# user=basil
# password=VeryStrongPassword
chmod u=rw,go-rwx $HOME/.wgetrc
```

### 3. Transfer to S3

```bash
aws s3 sync /ingestedDataDir/ s3://your-pi-bucket-name/theseData/
```

### 4. Cleanup

```bash
rm -rf /hpc/temp/ingestedDataDir
```

## Important Notes

- Do not transfer large temporary data into `/fh/fast` storage
- Passwords are "level III data"; never store HutchNet credentials
- Temporary storage is not backed up and has finite capacity
- Verify data before deletion

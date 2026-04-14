# GDC Client Download Optimization

Source: https://sciwiki.fredhutch.org/compdemos/gdc-client-hints/

## Basic Command

```bash
gdc-client --dir /path/to/download/ --log-file mydownload.log -n 4 -m my_manifest.tsv
```

## Optimization Tips

- **Workers (-n flag)**: 8-12 workers per node gives ~10MiB/s per worker. Beyond this, performance becomes erratic.
- **CPU allocation**: Match worker threads to assigned cores to prevent oversubscription
- **Exclusive node access**: Prevents contention for consistent performance on large datasets
- **Manifest splitting**: For 100+GB downloads, split manifests across multiple processes. Header must be retained in each chunk.
- **HTTP chunk size**: Default 1048576 bytes works well. Below 65536 bytes notably increases transfer time.
- **Data integrity**: `--no-file-md5sum` disables checksumming. Recommended to keep enabled despite overhead.

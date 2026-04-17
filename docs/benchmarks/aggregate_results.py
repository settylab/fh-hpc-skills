#!/usr/bin/env python3
"""Aggregate weekly-run storage benchmark outputs into a single TSV.

Scans ``results/*_summary.tsv`` and ``results/*_cluster.json``, joins
them by tag, and emits a wide TSV to stdout (or --output).

Use for post-hoc analysis: median per filesystem per load bucket,
variance over a week, etc.
"""

import argparse
import glob
import json
import os
import re
from collections import defaultdict


TAG_RE = re.compile(r"(\d{8}_\d{6})_([a-zA-Z0-9-]+)_(\d+|manual)")


def parse_summary(path):
    """Parse the 'metric\\tfs1\\tfs2\\t...' TSV block written by bench.sbatch."""
    rows = {}
    with open(path) as f:
        header = f.readline().rstrip("\n").split("\t")
        filesystems = header[1:]
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts or not parts[0]:
                continue
            metric = parts[0]
            for fs, val in zip(filesystems, parts[1:]):
                try:
                    rows[(fs, metric)] = float(val)
                except ValueError:
                    rows[(fs, metric)] = None
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results",
                    help="directory with *_summary.tsv files (default: results/)")
    ap.add_argument("--output", default="-", help="output TSV path, '-' for stdout")
    args = ap.parse_args()

    summaries = sorted(glob.glob(os.path.join(args.results, "*_summary.tsv")))
    if not summaries:
        raise SystemExit(f"no summary files in {args.results}/")

    rows = []
    all_metrics = set()
    all_fs = set()

    for sfile in summaries:
        base = os.path.basename(sfile).replace("_summary.tsv", "")
        m = TAG_RE.match(base)
        if not m:
            continue
        ts, host, jobid = m.groups()
        cstate_path = os.path.join(args.results, f"{base}_cluster.json")
        cstate = {}
        if os.path.exists(cstate_path):
            try:
                with open(cstate_path) as f:
                    cstate = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

        data = parse_summary(sfile)
        for (fs, metric), val in data.items():
            all_fs.add(fs)
            all_metrics.add(metric)
            rows.append({
                "timestamp": ts,
                "host": host,
                "jobid": jobid,
                "fs": fs,
                "metric": metric,
                "value": val,
                "slurm_cpus_alloc": cstate.get("slurm_cpus_alloc", ""),
                "slurm_cpus_total": cstate.get("slurm_cpus_total", ""),
                "this_node_load15": cstate.get("this_node_load15", ""),
            })

    cols = [
        "timestamp", "host", "jobid", "fs", "metric", "value",
        "slurm_cpus_alloc", "slurm_cpus_total", "this_node_load15",
    ]
    out = open(args.output, "w") if args.output != "-" else __import__("sys").stdout
    try:
        out.write("\t".join(cols) + "\n")
        for r in rows:
            out.write("\t".join(str(r.get(c, "")) for c in cols) + "\n")
    finally:
        if args.output != "-":
            out.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Storage throughput / latency benchmark for Fred Hutch HPC tiers.

Compares /fh/fast/, /hpc/temp/, and /fh/working/ on the host where this
script is run. Uses direct I/O (``O_DIRECT`` via ``dd``) to bypass the
page cache so results reflect actual NFS performance, not buffer hits.

Runs four tests per filesystem:
    1. Sequential write (2 GiB, bs=1M, direct)
    2. Sequential read  (2 GiB, bs=1M, direct)
    3. Metadata ops     (1000 create+stat+delete)
    4. Random small I/O (500 * 4 KiB random reads, direct)

Each test runs ``REPS`` times; median is reported. Total write budget is
about 6 GiB across the three filesystems (cleaned up at exit).

Run this on a gizmo node or rhino, not in the sandboxed agent. Results
vary with shared-filesystem load; rerun at different times for stable
medians.
"""

import argparse
import os
import random
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple


SEQ_SIZE_MB = 2048   # 2 GiB sequential file
RAND_SIZE_MB = 256   # 256 MiB random-read file
RAND_OPS = 500       # number of random 4 KiB reads
META_N = 1000        # number of small files for metadata test
REPS = 3


class Result(object):
    def __init__(self, label, values, unit):
        self.label = label
        self.values = values
        self.unit = unit

    @property
    def median(self):
        return statistics.median(self.values)

    @property
    def stdev(self):
        return statistics.pstdev(self.values) if len(self.values) > 1 else 0.0


def run(cmd):
    start = time.perf_counter()
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=True,
    )
    elapsed = time.perf_counter() - start
    return elapsed, proc.stderr


def seq_write(path, direct=True):
    cmd = [
        "dd", "if=/dev/zero", "of={0}".format(path),
        "bs=1M", "count={0}".format(SEQ_SIZE_MB),
        "conv=fdatasync",
    ]
    if direct:
        cmd.append("oflag=direct")
    elapsed, _ = run(cmd)
    return SEQ_SIZE_MB / elapsed  # MiB/s


def seq_read(path, direct=True):
    cmd = [
        "dd", "if={0}".format(path), "of=/dev/null",
        "bs=1M", "count={0}".format(SEQ_SIZE_MB),
    ]
    if direct:
        cmd.append("iflag=direct")
    elapsed, _ = run(cmd)
    return SEQ_SIZE_MB / elapsed


def metadata_test(dir_):
    """Return seconds to create + stat + delete META_N files."""
    start = time.perf_counter()
    files = [dir_ / "m{0}".format(i) for i in range(META_N)]
    for f in files:
        f.write_bytes(b"x")
    for f in files:
        f.stat()
    for f in files:
        f.unlink()
    return time.perf_counter() - start


def random_read(path, direct=True):
    """Return ops/sec for RAND_OPS random 4 KiB reads.

    Uses posix_fadvise(DONTNEED) to evict any cached pages before the
    test and POSIX_FADV_RANDOM to hint the kernel not to read ahead.
    This keeps the methodology consistent across filesystems (O_DIRECT
    has cross-fs alignment quirks). ``direct`` is kept for signature
    parity but no longer branches.
    """
    del direct  # noqa: unused
    fd = os.open(str(path), os.O_RDONLY)
    try:
        size = os.fstat(fd).st_size
        os.posix_fadvise(fd, 0, size, os.POSIX_FADV_DONTNEED)
        os.posix_fadvise(fd, 0, size, os.POSIX_FADV_RANDOM)
        max_off = (size // 4096) - 1
        offsets = [random.randint(0, max_off) * 4096 for _ in range(RAND_OPS)]
        start = time.perf_counter()
        for off in offsets:
            os.lseek(fd, off, os.SEEK_SET)
            _ = os.read(fd, 4096)
        elapsed = time.perf_counter() - start
    finally:
        os.close(fd)
    return RAND_OPS / elapsed


def _supports_direct_io(path):
    """Probe O_DIRECT support by writing a 1 MiB file with oflag=direct."""
    probe = path / ".directio_probe_{0}".format(os.getpid())
    try:
        subprocess.run(
            ["dd", "if=/dev/zero", "of={0}".format(probe),
             "bs=1M", "count=1", "oflag=direct"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        try:
            probe.unlink()
        except OSError:
            pass


def benchmark(label, root):
    work = root / "bench_{0}".format(os.getpid())
    work.mkdir(parents=True, exist_ok=True)
    seq = work / "seq.bin"
    rand = work / "rand.bin"

    direct = _supports_direct_io(work)
    if not direct:
        print("  [{0}] O_DIRECT unsupported; falling back to buffered I/O "
              "(read numbers may reflect page cache)".format(label), flush=True)

    results = {
        "seq_write_MiBs": [],
        "seq_read_MiBs": [],
        "metadata_s": [],
        "random_read_ops": [],
    }
    try:
        for rep in range(REPS):
            print("  [{0}] rep {1}/{2} seq write...".format(label, rep + 1, REPS), flush=True)
            results["seq_write_MiBs"].append(seq_write(seq, direct=direct))

            print("  [{0}] rep {1}/{2} seq read...".format(label, rep + 1, REPS), flush=True)
            results["seq_read_MiBs"].append(seq_read(seq, direct=direct))

            mdir = work / "meta_{0}".format(rep)
            mdir.mkdir()
            print("  [{0}] rep {1}/{2} metadata...".format(label, rep + 1, REPS), flush=True)
            results["metadata_s"].append(metadata_test(mdir))
            mdir.rmdir()

            print("  [{0}] rep {1}/{2} random write prep...".format(label, rep + 1, REPS), flush=True)
            prep_cmd = [
                "dd", "if=/dev/urandom", "of={0}".format(rand),
                "bs=1M", "count={0}".format(RAND_SIZE_MB),
                "conv=fdatasync",
            ]
            if direct:
                prep_cmd.append("oflag=direct")
            run(prep_cmd)
            print("  [{0}] rep {1}/{2} random read...".format(label, rep + 1, REPS), flush=True)
            results["random_read_ops"].append(random_read(rand, direct=direct))
            rand.unlink()
    finally:
        shutil.rmtree(work, ignore_errors=True)

    units = {
        "seq_write_MiBs": "MiB/s",
        "seq_read_MiBs": "MiB/s",
        "metadata_s": "s / 1000 files",
        "random_read_ops": "ops/s",
    }
    return {k: Result(k, v, units[k]) for k, v in results.items()}


def summarize(label, results):
    print("\n=== {0} ===".format(label))
    for k, r in results.items():
        print("  {0:22s}  median={1:10.2f}  stdev={2:8.2f}  ({3})".format(
            k, r.median, r.stdev, r.unit))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip", nargs="*", default=[],
                        help="labels to skip: fast, temp, working")
    args = parser.parse_args()

    user = os.environ["USER"]
    targets = {
        "fast": Path("/fh/fast/setty_m/user") / user,
        "temp": Path("/hpc/temp/setty_m") / user,
        "working": Path("/fh/working/setty_m") / user,
        "shm": Path("/dev/shm") / ("bench_" + user),
        "localtmp": Path("/tmp") / ("bench_" + user),
    }

    all_results = {}
    for label, root in targets.items():
        if label in args.skip:
            print("skipping {0}".format(label))
            continue
        if label in ("shm", "localtmp"):
            root.mkdir(parents=True, exist_ok=True)
        if not root.exists():
            print("skipping {0}: {1} does not exist".format(label, root))
            continue
        print("\n>>> benchmarking {0} at {1}".format(label, root))
        all_results[label] = benchmark(label, root)

    for label, results in all_results.items():
        summarize(label, results)

    print("\n--- tsv summary ---")
    print("metric\t" + "\t".join(all_results.keys()))
    metrics = list(next(iter(all_results.values())).keys()) if all_results else []
    for m in metrics:
        row = [m] + ["{0:.2f}".format(all_results[l][m].median) for l in all_results]
        print("\t".join(row))


if __name__ == "__main__":
    main()

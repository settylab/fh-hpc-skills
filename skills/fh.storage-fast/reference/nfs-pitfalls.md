# /fh/fast NFS behaviour that bites scripts

Detail behind "Behaviour that bites scripts" in `fh.storage-fast`. All items were measured on Gizmo in 2026.

## Client caching: what a single stat can tell you

`/fh/fast` is NFSv3 with default attribute caching (`acdirmin=30,acdirmax=60` as measured). Each compute node is a separate NFS client with its own caches, so a job on another node and your session can disagree for up to a minute.

- **A plain `lstat` of a DIRECTORY another node just changed returns cached mtime/size** (42 of 42 reads stale) even while a listing already shows the new child. `os.scandir(D)` then `lstat(D)`, or `open` + `fstat`, refreshed it (0 of 42 stale). A "did anything touch X" check stats each dir AFTER listing it, or starts ≥ 120 s after the last writer.
- **A path seen as ABSENT can keep returning ENOENT after another node creates it** (negative-lookup cache). Run a fresh readdir (`ls -la <parent>`) before any absence claim or any action that "repairs" a missing path.
- **A symlink flipped on node A reads stale on node B for seconds to ~60 s** (measured 4-36 s; same-node 0.2 s). Verify a cross-node swap by a bounded re-probe (e.g. every 5 s up to 150 s) on apply AND rollback, and record the node. A web viewer's refresh does not clear the client cache.

## Filesystem identity

- **`st_dev` differs per client node** (e.g. `0:152` on one, `0:159` on another) while `st_ino`, size and nlink agree. A record pinning `(st_dev, st_ino)` refuses an unchanged file on another node. Pin inode + size/sha + a filesystem identity (mountinfo source + root), and test the consumer on a node other than the one that wrote the record.
- **One NFS device appears as many mount entries.** `/proc/self/mountinfo` carried ~14 bind-mount entries for the same `major:minor` (on a compute node, and inside the agent-sandbox). Map a path to its mount by the LONGEST mount-point prefix, never by device number alone.
- **Lab directories are setgid**, and GNU `chmod 0555` keeps the bit, so a "read-only" dir reads `2555` (or `2550`). Assert the bits you mean (`mode & 0o222 == 0` for "no write bits"), not an exact mode.
- Run any function that parses mounts, modes or ownership once against the REAL target before relying on it: a `/tmp` test tree has one mount and no setgid.

## Hard-linked trees (`cp -al`)

- **`du` per directory overstates what a delete frees.** `du` counts a hard-linked inode in every directory that links it: a delete "sized" at ~3 TiB would have freed 4.2 GiB, because the variants shared one pool still linked from other trees. Size a delete by the bytes of inodes whose EVERY link lies inside the deletion set (`find SET -type f -printf '%i %n %s\n'`, comparing each inode's link count inside SET with `%n`), and report allocated vs apparent.
- **`cp -al` of a read-only tree copies its read-only DIRECTORY modes.** The copy's dirs are new inodes but inherit `a-w`, so the first file staged into the copy fails EACCES, possibly an hour in (a 300k-entry `cp -al` took ~54 min). After `cp -al`, `chmod u+w` only the directories you will write into (by `lstat` `S_ISDIR`), and have any rename/unlink job check the parent's `W_OK|X_OK` before its first change. Fixtures must use the live tree's modes.
- **Never chmod a file in a hard-linked copy:** a chmod is a write to the inode, so it changes every twin.
- **`cp -al` links metadata dot-files too.** A rehearsal copy of a live zarr store raised the live `.zmetadata`/`.zattrs` link count, so any nlink-guarded writer refused the live store until the copy was gone. Right after `cp -al`, replace dot-files with real copies (`cp f f.tmp && mv f.tmp f`) and assert no metadata inode is shared.

## Deletes and `.nfs*` files

- **`rm`/`shutil.rmtree` seconds after a job wrote the tree can fail `Errno 39`** on `.nfsXXXX` silly-rename files (unlinked while still open), which clear within minutes. An EXIT-trap `rm` can leave them too. Keep short-lived temp files node-local (`$TMPDIR`, `/loc/scratch`), or rename into a trash dir and purge later; never make a test depend on an immediate rmtree of fresh NFS output.
- Unlinking a tens-of-thousands-file tree runs at a few files per second (hours). To undo a `cp -al` rehearsal, unlink only the shared files; size large unlinks from a pilot.

## Metadata-heavy work is compute

- **Run tree-scale I/O in Slurm, not on a login node, even at low RSS.** `cp -al` farms, `rsync`/`copytree` of a large tree, `find … | wc -l` sizing walks and `rm -rf` of such trees are metadata storms. They hide inside tools: a "patch docs" script that rendered two pages in a minute then `cp -al`'d the whole published tree ran 40 min and was killed, and the `find` to size it ran an hour. Read whether a tool copies or walks a tree before running it; a bounded login-node check is `stat` of named files under `timeout`, never a walk.
- **Your own I/O confounds a benchmark on the same filer.** Venv builds (thousands of small files), smoke jobs importing from a venv there, and metadata walks all count: cold segments ran 2-7x slow while three venvs were built beside a measurement. Queue prep after the measurement (`--dependency=afterany:<job>`) or build on node-local disk, and keep a canary column per segment so overlap is visible.

## Measuring rates

- **A stat walk timed minutes after the same host touched the files reads ~10x fast** (cache, not filer). Age the tree ≥ 75 s, run 3+ walks ≥ 75 s apart, keep the rows, budget on the slow end.
- **Login-node probes err the other way:** a 60 s login-node walk read ~340 entries/s against ~2,800/s cold and ~5,000/s warm on a compute node (a 12M-entry tree took ~75 min cold). Size from compute-node measurements on the target tree itself; one tree's rate does not size another's (0.17 vs ~2 ms/entry).
- **A stat walk does not size a hashing pass:** 2.05M entries stat-walked in ~6 min, but hashing ran ~127 entries/s (~4.6 h).
- **A process per file costs ~0.2-0.3 s** (`bash -n`, `git ls-files --error-unmatch`): 858 files ≈ 4-5 min. Batch the call, scope to the files you need, or run it as a job.
- Give the job an in-job timeout ~3x the estimate, and treat a timeout as INCONCLUSIVE, never a pass.

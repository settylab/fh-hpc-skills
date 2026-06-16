#!/usr/bin/env bash
#
# bootstrap.sh — reliable, idempotent, interruption- and concurrency-safe
# setup of the three things a fresh Claude Code environment needs to use
# these skills on the Fred Hutch cluster:
#
#   1. the fh-hpc-skills clone     → $REPO_DIR        (settylab/fh-hpc-skills)
#   2. the skill symlinks          → $SKILLS_DIR/<skill> -> $REPO_DIR/skills/<skill>
#   3. the labsh CLI               → brew formula katosh/tools/labsh
#
# Design contract
# ---------------
# * Idempotent      — every step checks the desired end-state and acts only on
#                     the gap. A fully-installed re-run is a no-op; a partial
#                     re-run COMPLETES the install.
# * Atomic          — the clone lands via clone-to-temp + rename (never a
#                     half-cloned $REPO_DIR); symlinks are placed with `ln -sfn`
#                     (no clobber of a good link, no nesting footgun).
# * Recoverable     — a crash / close-restart that left a partial temp clone, a
#                     dangling symlink, or a non-repo directory is detected and
#                     cleaned/completed on the next run.
# * Concurrency-safe— the mutating section is guarded by an advisory flock on a
#                     LOCAL filesystem (flock over NFS is unreliable). Two
#                     simultaneous opens → one sets up, the other waits then
#                     sees it complete. No double-clone, no symlink race.
# * Verified        — ends with a health-check gate that asserts all three
#                     components are correctly present and FAILS LOUD otherwise,
#                     so a silent half-install cannot pass as success.
#
# Usage
# -----
#   bootstrap.sh              set up / repair all three components, then verify
#   bootstrap.sh --check      verify only; no mutation; nonzero exit if incomplete
#   bootstrap.sh --skip-labsh skip the labsh step (skills + symlinks only)
#   bootstrap.sh --quiet      suppress informational output (warnings/errors stay)
#   bootstrap.sh -h|--help    this help
#
# Overridable via environment (defaults target the live Claude config):
#   FHHS_REPO_DIR       default ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/fh-hpc-skills … see note
#   FHHS_SKILLS_DIR     default ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills
#   FHHS_REMOTE         default git@github.com:settylab/fh-hpc-skills.git
#   FHHS_REMOTE_HTTPS   default https://github.com/settylab/fh-hpc-skills.git
#   FHHS_LOCK_DIR       default ${XDG_RUNTIME_DIR:-/tmp}   (MUST be a local FS)
#   FHHS_LABSH_BIN      default labsh
#   FHHS_LABSH_INSTALL  default brew install katosh/tools/labsh
#
# Note: the clone defaults to $HOME/.claude/fh-hpc-skills (not CLAUDE_CONFIG_DIR)
# because ~/.claude is what the agent_sandbox mounts writable; the symlink dir
# honours CLAUDE_CONFIG_DIR to match Claude Code's own resolution.

set -euo pipefail

# ---------------------------------------------------------------- config -----
REPO_DIR="${FHHS_REPO_DIR:-$HOME/.claude/fh-hpc-skills}"
SKILLS_DIR="${FHHS_SKILLS_DIR:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills}"
REMOTE="${FHHS_REMOTE:-git@github.com:settylab/fh-hpc-skills.git}"
REMOTE_HTTPS="${FHHS_REMOTE_HTTPS:-https://github.com/settylab/fh-hpc-skills.git}"
LOCK_DIR="${FHHS_LOCK_DIR:-${XDG_RUNTIME_DIR:-/tmp}}"
LABSH_BIN="${FHHS_LABSH_BIN:-labsh}"
LABSH_INSTALL="${FHHS_LABSH_INSTALL:-brew install katosh/tools/labsh}"

CHECK_ONLY=""
: "${FHHS_SKIP_LABSH:=}"
: "${FHHS_QUIET:=}"

# ----------------------------------------------------------------- output ----
log()  { [ -n "$FHHS_QUIET" ] || printf '%s\n'    "$*" >&2; }
ok()   { [ -n "$FHHS_QUIET" ] || printf '  \xe2\x9c\x93 %s\n' "$*" >&2; }
warn() { printf '  ! %s\n' "$*" >&2; }
die()  { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
stamp(){ date +%Y%m%d-%H%M%S 2>/dev/null || echo "ts"; }

usage() { sed -n '2,/^set -euo/p' "$0" | sed 's/^# \{0,1\}//; s/^#$//' | head -n -1; }

# ------------------------------------------------------------------- args ----
parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --check)      CHECK_ONLY=1 ;;
            --skip-labsh) FHHS_SKIP_LABSH=1 ;;
            --quiet)      FHHS_QUIET=1 ;;
            -h|--help)    usage; exit 0 ;;
            *)            die "unknown argument: $1 (try --help)" ;;
        esac
        shift
    done
}

# ------------------------------------------------------------------- lock ----
# Advisory flock on a LOCAL fs. Kernel releases the lock when the holder dies,
# so a crashed bootstrap never deadlocks a subsequent one.
acquire_lock() {
    mkdir -p "$LOCK_DIR" 2>/dev/null || true
    local lock_file="$LOCK_DIR/fh-hpc-skills-bootstrap.$(id -u).lock"
    if ! exec 9>"$lock_file"; then
        warn "cannot open lock file $lock_file — proceeding without concurrency guard"
        return 0
    fi
    if ! command -v flock >/dev/null 2>&1; then
        warn "flock not available — proceeding without concurrency guard"
        return 0
    fi
    if ! flock -n 9; then
        log "Another fh-hpc-skills setup is in progress, waiting (up to 300s)…"
        flock -w 300 9 || die "timed out waiting for a concurrent bootstrap (lock: $lock_file). If stale, remove it and retry."
    fi
}

# ------------------------------------------------------------ component: repo -
repo_is_git()    { git -C "$REPO_DIR" rev-parse --git-dir >/dev/null 2>&1; }
repo_remote_ok() {
    repo_is_git || return 1
    local url; url="$(git -C "$REPO_DIR" config --get remote.origin.url 2>/dev/null || true)"
    case "$url" in *settylab/fh-hpc-skills*) return 0 ;; *) return 1 ;; esac
}
repo_healthy()   { repo_remote_ok && [ -d "$REPO_DIR/skills" ]; }

ensure_repo() {
    # Recovery: clear temp clones left by a crashed prior run (we hold the lock,
    # so no concurrent run owns these).
    local leftover
    for leftover in "${REPO_DIR}.bootstrap-tmp."*; do
        [ -e "$leftover" ] || continue
        warn "removing leftover temp clone $leftover"
        rm -rf "$leftover"
    done

    if repo_healthy; then ok "fh-hpc-skills present ($REPO_DIR)"; return 0; fi

    if [ -e "$REPO_DIR" ]; then
        if repo_is_git && ! repo_remote_ok; then
            die "refusing to overwrite $REPO_DIR — it is a git repo with an unexpected remote ($(git -C "$REPO_DIR" config --get remote.origin.url 2>/dev/null || echo none)). Move it aside manually and re-run."
        fi
        # partial clone, non-repo dir, or repo missing skills/ — move aside, don't destroy.
        local bak="${REPO_DIR}.broken.$(stamp)"
        warn "found partial/incomplete $REPO_DIR — moving aside to $bak"
        mv "$REPO_DIR" "$bak" || die "cannot move aside $REPO_DIR"
    fi

    # Atomic clone: into a temp sibling, then rename into place.
    local tmp="${REPO_DIR}.bootstrap-tmp.$$"
    rm -rf "$tmp"
    mkdir -p "$(dirname "$REPO_DIR")"
    log "Cloning fh-hpc-skills → $REPO_DIR"
    if ! git clone --quiet "$REMOTE" "$tmp" 2>/dev/null; then
        warn "ssh clone failed — retrying over https"
        rm -rf "$tmp"
        git clone --quiet "$REMOTE_HTTPS" "$tmp" || { rm -rf "$tmp"; die "git clone failed (ssh and https). Check network/credentials."; }
    fi
    if ! mv -T "$tmp" "$REPO_DIR" 2>/dev/null; then
        mv "$tmp" "$REPO_DIR" 2>/dev/null || { rm -rf "$tmp"; die "failed to move clone into place at $REPO_DIR"; }
    fi
    repo_healthy || { die "post-clone verification failed at $REPO_DIR"; }
    ok "cloned fh-hpc-skills"
}

# -------------------------------------------------------- component: symlinks -
ensure_symlinks() {
    mkdir -p "$SKILLS_DIR"
    local n_ok=0 n_fix=0 n_prune=0
    local skill name link target dest

    for skill in "$REPO_DIR"/skills/*/; do
        [ -d "$skill" ] || continue
        skill="${skill%/}"
        name="$(basename "$skill")"
        link="$SKILLS_DIR/$name"
        target="$skill"
        if [ -L "$link" ] && [ "$(readlink "$link" 2>/dev/null || true)" = "$target" ]; then
            n_ok=$((n_ok+1)); continue
        fi
        if [ -e "$link" ] && [ ! -L "$link" ]; then
            warn "$link exists and is NOT a symlink — leaving untouched (manual review)"
            continue
        fi
        # ln -sfn: replace atomically, never descend into an existing dir-symlink.
        ln -sfn "$target" "$link" || { warn "failed to link $link"; continue; }
        n_fix=$((n_fix+1))
    done

    # Prune dangling links that point into OUR repo's skills/ (renamed/removed
    # upstream). Untouched: real files, and links pointing elsewhere.
    for link in "$SKILLS_DIR"/*; do
        [ -L "$link" ] || continue
        dest="$(readlink "$link" 2>/dev/null || true)"
        case "$dest" in
            "$REPO_DIR"/skills/*)
                if [ ! -e "$link" ]; then   # -e dereferences: false ⇒ dangling
                    rm -f "$link" && n_prune=$((n_prune+1))
                fi
                ;;
        esac
    done

    ok "symlinks: $n_ok ok, $n_fix created/repaired, $n_prune pruned"
}

# ----------------------------------------------------------- component: labsh -
ensure_labsh() {
    if [ -n "$FHHS_SKIP_LABSH" ]; then ok "labsh: skipped (--skip-labsh)"; return 0; fi
    if command -v "$LABSH_BIN" >/dev/null 2>&1; then
        ok "labsh present ($(command -v "$LABSH_BIN"))"; return 0
    fi
    log "labsh not found — installing via: $LABSH_INSTALL"
    if [ "${LABSH_INSTALL%% *}" = "brew" ] && ! command -v brew >/dev/null 2>&1; then
        die "labsh missing and Homebrew not found. Install Homebrew (https://brew.sh), then re-run; or install labsh manually: $LABSH_INSTALL"
    fi
    if ! eval "$LABSH_INSTALL" >&2; then
        die "labsh install failed: $LABSH_INSTALL"
    fi
    command -v "$LABSH_BIN" >/dev/null 2>&1 || die "labsh still not on PATH after install — ensure brew's bin dir is on PATH and re-run."
    ok "installed labsh"
}

# ----------------------------------------------------------- verification gate -
verify_all() {
    local fail=0 skill name link dest expect=0 good=0

    if repo_healthy; then ok "[verify] fh-hpc-skills clone OK ($REPO_DIR)"
    else warn "[verify] fh-hpc-skills clone MISSING or BROKEN ($REPO_DIR)"; fail=1; fi

    for skill in "$REPO_DIR"/skills/*/; do
        [ -d "$skill" ] || continue
        expect=$((expect+1)); name="$(basename "${skill%/}")"; link="$SKILLS_DIR/$name"
        if [ -L "$link" ] && [ -d "$link" ]; then good=$((good+1))
        else warn "[verify] missing/invalid skill symlink: $link"; fail=1; fi
    done
    if [ "$expect" -eq 0 ]; then warn "[verify] no skills found under $REPO_DIR/skills"; fail=1
    elif [ "$fail" -eq 0 ]; then ok "[verify] skill symlinks OK ($good/$expect)"; fi

    for link in "$SKILLS_DIR"/*; do
        [ -L "$link" ] || continue
        dest="$(readlink "$link" 2>/dev/null || true)"
        case "$dest" in
            "$REPO_DIR"/skills/*) [ -e "$link" ] || { warn "[verify] dangling skill symlink: $link"; fail=1; } ;;
        esac
    done

    if [ -n "$FHHS_SKIP_LABSH" ]; then ok "[verify] labsh skipped"
    elif command -v "$LABSH_BIN" >/dev/null 2>&1; then ok "[verify] labsh OK ($(command -v "$LABSH_BIN"))"
    else warn "[verify] labsh MISSING"; fail=1; fi

    return "$fail"
}

# ------------------------------------------------------------------- main -----
main() {
    parse_args "$@"

    if [ -n "$CHECK_ONLY" ]; then
        verify_all || die "verification FAILED — run without --check to repair."
        log "✓ all three components verified."
        return 0
    fi

    acquire_lock
    ensure_repo
    ensure_symlinks
    ensure_labsh

    log "Verifying…"
    verify_all || die "bootstrap finished but verification FAILED — see warnings above."
    log "✓ fh-hpc-skills bootstrap complete."
}

main "$@"

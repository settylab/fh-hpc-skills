#!/usr/bin/env bash
#
# test_bootstrap.sh — robustness suite for bootstrap.sh.
#
# Everything runs against a throwaway $HOME and a LOCAL fake origin repo
# (path contains "settylab/fh-hpc-skills" so the remote-identity check passes).
# It NEVER touches the live ~/.claude, the live clone, brew, or labsh:
# the labsh step is exercised with a uniquely-named fake binary + fake installer.
#
# Usage: bash tests/test_bootstrap.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BOOTSTRAP="$SCRIPT_DIR/bootstrap.sh"
[ -x "$BOOTSTRAP" ] || { echo "FATAL: $BOOTSTRAP not executable"; exit 1; }

PASS=0 FAIL=0
ok()   { printf '  \033[32mPASS\033[0m %s\n' "$*"; PASS=$((PASS+1)); }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$*"; FAIL=$((FAIL+1)); }
chk()  { if eval "$2"; then ok "$1"; else bad "$1 — [$2]"; fi; }

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

# --- build a local fake upstream whose path contains settylab/fh-hpc-skills ---
UPSTREAM="$ROOT/remote/settylab/fh-hpc-skills"
mkdir -p "$UPSTREAM"
(
  cd "$UPSTREAM"
  git init -q
  git config user.email t@t.t; git config user.name t
  for s in fh.alpha fh.beta setty.labsh; do
    mkdir -p "skills/$s"; echo "# $s" > "skills/$s/SKILL.md"
  done
  git add -A; git commit -qm init
)

# fake labsh tooling (unique names: never collide with a real install)
FAKE_BIN="$ROOT/fakebin"; mkdir -p "$FAKE_BIN"
cat > "$FAKE_BIN/labsh_fake" <<'EOF'
#!/bin/sh
echo "labsh_fake 0.0.0"
EOF
chmod +x "$FAKE_BIN/labsh_fake"
cat > "$FAKE_BIN/install_labsh_fake" <<EOF
#!/bin/sh
cp "$FAKE_BIN/labsh_fake" "$FAKE_BIN/labsh_want"
EOF
chmod +x "$FAKE_BIN/install_labsh_fake"

# fresh env per case: isolated HOME + lock dir, fake origin, labsh skipped by default
new_home() {
  CASE_HOME="$ROOT/h$RANDOM$RANDOM"; mkdir -p "$CASE_HOME"
  export HOME="$CASE_HOME"
  unset CLAUDE_CONFIG_DIR
  export FHHS_REPO_DIR="$CASE_HOME/.claude/fh-hpc-skills"
  export FHHS_SKILLS_DIR="$CASE_HOME/.claude/skills"
  export FHHS_REMOTE="$UPSTREAM"
  export FHHS_REMOTE_HTTPS="$UPSTREAM"
  export FHHS_LOCK_DIR="$ROOT/locks"
  export FHHS_SKIP_LABSH=1
  export FHHS_QUIET=1
}
run() { bash "$BOOTSTRAP" "$@"; }   # returns exit code; stderr visible

echo "=== 1. fresh install ==="
new_home
run >/dev/null 2>&1; rc=$?
chk "exit 0" "[ $rc -eq 0 ]"
chk "repo cloned + .git present" "[ -d '$FHHS_REPO_DIR/.git' ]"
chk "remote identity correct" "git -C '$FHHS_REPO_DIR' config --get remote.origin.url | grep -q settylab/fh-hpc-skills"
chk "all 3 symlinks valid dirs" "[ -d '$FHHS_SKILLS_DIR/fh.alpha' ] && [ -d '$FHHS_SKILLS_DIR/fh.beta' ] && [ -d '$FHHS_SKILLS_DIR/setty.labsh' ]"
chk "symlink resolves to repo skill" "[ \"\$(readlink '$FHHS_SKILLS_DIR/fh.alpha')\" = '$FHHS_REPO_DIR/skills/fh.alpha' ]"
chk "no leftover temp clone" "! ls -d '$FHHS_REPO_DIR'.bootstrap-tmp.* >/dev/null 2>&1"
chk "--check passes" "run --check >/dev/null 2>&1"

echo "=== 2. idempotent re-run ==="
before="$(ls -la "$FHHS_SKILLS_DIR" | sort)"
run >/dev/null 2>&1; rc=$?
after="$(ls -la "$FHHS_SKILLS_DIR" | sort)"
chk "exit 0" "[ $rc -eq 0 ]"
chk "symlink set unchanged" "[ \"$before\" = \"$after\" ]"
chk "no nesting (ln -sfn): no skills/fh.alpha/fh.alpha" "! [ -e '$FHHS_REPO_DIR/skills/fh.alpha/fh.alpha' ]"
chk "no leftover temp clone" "! ls -d '$FHHS_REPO_DIR'.bootstrap-tmp.* >/dev/null 2>&1"

echo "=== 3a. crash: leftover temp clone + missing repo ==="
new_home
run >/dev/null 2>&1
rm -rf "$FHHS_REPO_DIR"
mkdir -p "$FHHS_REPO_DIR.bootstrap-tmp.999"; echo junk > "$FHHS_REPO_DIR.bootstrap-tmp.999/x"
run >/dev/null 2>&1; rc=$?
chk "exit 0" "[ $rc -eq 0 ]"
chk "leftover temp removed" "! ls -d '$FHHS_REPO_DIR'.bootstrap-tmp.* >/dev/null 2>&1"
chk "repo re-cloned healthy" "[ -d '$FHHS_REPO_DIR/.git' ] && [ -d '$FHHS_REPO_DIR/skills' ]"

echo "=== 3b. crash: partial non-repo dir at REPO_DIR ==="
new_home
run >/dev/null 2>&1
rm -rf "$FHHS_REPO_DIR/.git"          # leaves a non-git dir = partial state
run >/dev/null 2>&1; rc=$?
chk "exit 0" "[ $rc -eq 0 ]"
chk "moved partial aside (.broken.*)" "ls -d '$FHHS_REPO_DIR'.broken.* >/dev/null 2>&1"
chk "repo re-cloned healthy" "git -C '$FHHS_REPO_DIR' rev-parse --git-dir >/dev/null 2>&1"

echo "=== 4a. repair: deleted symlink ==="
new_home; run >/dev/null 2>&1
rm -f "$FHHS_SKILLS_DIR/fh.beta"
run >/dev/null 2>&1; rc=$?
chk "exit 0" "[ $rc -eq 0 ]"
chk "deleted link recreated" "[ -d '$FHHS_SKILLS_DIR/fh.beta' ]"

echo "=== 4b. repair: wrong symlink target ==="
ln -sfn /nonexistent/wrong "$FHHS_SKILLS_DIR/fh.alpha"
run >/dev/null 2>&1; rc=$?
chk "exit 0" "[ $rc -eq 0 ]"
chk "wrong link repaired" "[ \"\$(readlink '$FHHS_SKILLS_DIR/fh.alpha')\" = '$FHHS_REPO_DIR/skills/fh.alpha' ]"

echo "=== 4c. prune: dangling link to removed skill ==="
ln -sfn "$FHHS_REPO_DIR/skills/fh.removed" "$FHHS_SKILLS_DIR/fh.removed"   # dangling, points into our repo
chk "pre: dangling link exists" "[ -L '$FHHS_SKILLS_DIR/fh.removed' ]"
run >/dev/null 2>&1; rc=$?
chk "exit 0" "[ $rc -eq 0 ]"
chk "dangling link pruned" "! [ -L '$FHHS_SKILLS_DIR/fh.removed' ]"

echo "=== 4d. repair: corrupt clone (removed .git) ==="
new_home; run >/dev/null 2>&1
rm -rf "$FHHS_REPO_DIR/.git"
run >/dev/null 2>&1; rc=$?
chk "exit 0" "[ $rc -eq 0 ]"
chk "repo healthy again" "git -C '$FHHS_REPO_DIR' rev-parse --git-dir >/dev/null 2>&1 && [ -d '$FHHS_REPO_DIR/skills' ]"

echo "=== 4e. untouched: foreign (non-our) symlink left alone ==="
ln -sfn /etc/hostname "$FHHS_SKILLS_DIR/my.custom"
run >/dev/null 2>&1
chk "foreign link preserved" "[ -L '$FHHS_SKILLS_DIR/my.custom' ] && [ \"\$(readlink '$FHHS_SKILLS_DIR/my.custom')\" = '/etc/hostname' ]"

echo "=== 5. concurrency: two simultaneous bootstraps ==="
new_home
run >/dev/null 2>&1; rm -rf "$FHHS_REPO_DIR"   # force both to attempt a clone
( run >/dev/null 2>&1; echo $? > "$ROOT/c1.rc" ) &
p1=$!
( run >/dev/null 2>&1; echo $? > "$ROOT/c2.rc" ) &
p2=$!
wait $p1; wait $p2
chk "both exit 0" "[ \"\$(cat $ROOT/c1.rc)\" = 0 ] && [ \"\$(cat $ROOT/c2.rc)\" = 0 ]"
chk "repo healthy, single clone" "git -C '$FHHS_REPO_DIR' rev-parse --git-dir >/dev/null 2>&1 && [ -d '$FHHS_REPO_DIR/skills' ]"
chk "no leftover temp clone" "! ls -d '$FHHS_REPO_DIR'.bootstrap-tmp.* >/dev/null 2>&1"
chk "no broken-aside dirs" "! ls -d '$FHHS_REPO_DIR'.broken.* >/dev/null 2>&1"

echo "=== 5b. lock genuinely blocks: held lock makes bootstrap wait ==="
new_home
run >/dev/null 2>&1                       # establish a healthy install first
LOCKF="$FHHS_LOCK_DIR/fh-hpc-skills-bootstrap.$(id -u).lock"
mkdir -p "$FHHS_LOCK_DIR"
( exec 9>"$LOCKF"; flock 9; sleep 2 ) &   # hold the lock for ~2s
holder=$!
sleep 0.3                                 # ensure holder grabbed it first
t0=$(date +%s)
run >/dev/null 2>&1; rc=$?
t1=$(date +%s)
wait $holder
chk "blocked-then-succeeded exit 0" "[ $rc -eq 0 ]"
chk "waited for the held lock (>=1s)" "[ $((t1 - t0)) -ge 1 ]"

echo "=== 6. labsh present ==="
new_home; unset FHHS_SKIP_LABSH
export FHHS_LABSH_BIN=labsh_fake
export PATH="$FAKE_BIN:$PATH"
run >/dev/null 2>&1; rc=$?
chk "exit 0 with labsh present" "[ $rc -eq 0 ]"
chk "--check passes (labsh on PATH)" "run --check >/dev/null 2>&1"

echo "=== 7. labsh repair (fake installer) ==="
new_home; unset FHHS_SKIP_LABSH
export FHHS_LABSH_BIN=labsh_want
export FHHS_LABSH_INSTALL="install_labsh_fake"
rm -f "$FAKE_BIN/labsh_want"
export PATH="$FAKE_BIN:$PATH"
chk "pre: labsh_want absent" "! command -v labsh_want >/dev/null 2>&1"
run >/dev/null 2>&1; rc=$?
chk "exit 0 after install" "[ $rc -eq 0 ]"
chk "labsh_want now on PATH" "command -v labsh_want >/dev/null 2>&1"

echo "=== 8. labsh install failure → fail loud ==="
new_home; unset FHHS_SKIP_LABSH
export FHHS_LABSH_BIN=labsh_never
export FHHS_LABSH_INSTALL="false"
err="$(run 2>&1)"; rc=$?
chk "nonzero exit" "[ $rc -ne 0 ]"
chk "actionable error mentions labsh install" "printf '%s' \"\$err\" | grep -qi 'labsh install failed'"

echo "=== 9. --check on incomplete env → nonzero ==="
new_home   # never ran bootstrap; repo absent
rc=0; run --check >/dev/null 2>&1 || rc=$?
chk "--check nonzero on empty env" "[ $rc -ne 0 ]"

echo
echo "================  $PASS passed, $FAIL failed  ================"
[ "$FAIL" -eq 0 ]

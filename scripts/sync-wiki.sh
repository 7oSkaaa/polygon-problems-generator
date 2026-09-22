#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WIKI_DIR="${REPO_ROOT}/wiki"
WIKI_REPO_SSH="git@github.com:7oSkaaa/polygon-problems-generator.wiki.git"
WIKI_REPO_HTTPS="https://github.com/7oSkaaa/polygon-problems-generator.wiki.git"

if [ ! -d "${WIKI_DIR}" ]; then
  echo "Error: Wiki source directory '${WIKI_DIR}' does not exist." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "==> Checking GitHub Wiki repository..."
# Test if wiki repository exists and can be cloned
export GIT_TERMINAL_PROMPT=0
if ! git clone "${WIKI_REPO_SSH}" "${TMP_DIR}/wiki" 2>/dev/null; then
  if ! git clone "${WIKI_REPO_HTTPS}" "${TMP_DIR}/wiki" 2>/dev/null; then
    cat >&2 <<EOF

[!] GitHub Wiki repository is not yet initialized.

GitHub requires the Wiki repository to be initialized once via the web UI:
  1. Open: https://github.com/7oSkaaa/polygon-problems-generator/wiki
  2. Click "Create the first page"
  3. Click "Save Page" (any content is fine, this script will overwrite it)

Once done, re-run this script:
  ./scripts/sync-wiki.sh

EOF
    exit 1
  fi
fi

echo "==> Synchronizing wiki documentation..."
cd "${TMP_DIR}/wiki"

# Determine default branch (usually master for GitHub wikis)
DEFAULT_BRANCH="$(git rev-parse --abbrev-ref HEAD || echo "master")"

# Remove old files except .git
find . -maxdepth 1 ! -name ".git" ! -name "." -exec rm -rf {} +

# Copy all files from wiki/
cp -r "${WIKI_DIR}/." .

# Check for git changes
if [ -z "$(git status --porcelain)" ]; then
  echo "==> Wiki is already up to date. Nothing to commit."
  exit 0
fi

git add -A
git commit -m "docs: sync wiki documentation from main repo [$(date -u +"%Y-%m-%d %H:%M:%S UTC")]"
echo "==> Pushing updates to GitHub Wiki (${DEFAULT_BRANCH})..."
git push origin "${DEFAULT_BRANCH}"

echo "==> Successfully synchronized GitHub Wiki!"
echo "    Visit: https://github.com/7oSkaaa/polygon-problems-generator/wiki"

#!/usr/bin/env bash
# Build a clean, shareable archive of the plugin (skill + engine) for a client.
#
# Produces, under dist/:
#   ms-dropshipping-market-research-<version>.zip
#   ms-dropshipping-market-research-<version>.tar.gz
#   ms-dropshipping-market-research-<version>.sha256   (checksums)
#
# Excludes secrets (.env), build cruft, venvs, caches, and generated briefs.
# The version is read from .claude-plugin/plugin.json (single source of truth).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="ms-dropshipping-market-research"
MANIFEST="$ROOT/.claude-plugin/plugin.json"

VERSION="$(grep -E '"version"' "$MANIFEST" | head -1 | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')"
[[ -n "$VERSION" ]] || { echo "Could not read version from $MANIFEST" >&2; exit 1; }

DIST="$ROOT/dist"
STAGE="$DIST/${NAME}-${VERSION}"
ZIP="$DIST/${NAME}-${VERSION}.zip"
TGZ="$DIST/${NAME}-${VERSION}.tar.gz"
SUMS="$DIST/${NAME}-${VERSION}.sha256"

echo "Packaging ${NAME} v${VERSION}…"
rm -rf "$STAGE" "$ZIP" "$TGZ" "$SUMS"
mkdir -p "$STAGE"

# Stage a clean copy. rsync excludes keep secrets and cruft out of the artifact.
rsync -a \
  --exclude '.git' \
  --exclude 'dist' \
  --exclude '.verifyenv' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '*.egg-info' \
  --exclude '.env' \
  --exclude 'engine/.env' \
  --exclude 'uv.lock' \
  --exclude '.DS_Store' \
  --exclude 'briefs' \
  "$ROOT"/ "$STAGE"/

# Guard: fail loudly if a secret slipped into the staging dir.
if find "$STAGE" -name '.env' -type f | grep -q .; then
  echo "REFUSING TO PACKAGE: a .env file is present in the staging dir." >&2
  exit 1
fi

( cd "$DIST" && zip -rq "$(basename "$ZIP")" "${NAME}-${VERSION}" )
( cd "$DIST" && tar -czf "$(basename "$TGZ")" "${NAME}-${VERSION}" )
( cd "$DIST" && shasum -a 256 "$(basename "$ZIP")" "$(basename "$TGZ")" > "$(basename "$SUMS")" )

echo
echo "Built:"
ls -lh "$ZIP" "$TGZ"
echo
echo "Checksums ($SUMS):"
cat "$SUMS"
echo
echo "File count in archive: $(find "$STAGE" -type f | wc -l | tr -d ' ')"
echo "Share the .zip (or .tar.gz) + the .sha256 with your client."
echo "Client steps are in VALIDATION.md."

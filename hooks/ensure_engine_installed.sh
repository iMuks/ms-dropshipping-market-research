#!/usr/bin/env bash
# SessionStart hook for the ms-dropshipping-market-research plugin.
#
# Idempotent. On each session start it:
#   1. Checks whether the bundled niche-research CLI is already installed
#      and up-to-date (by comparing the plugin's manifest version against
#      a marker stored in the user's data dir).
#   2. If not, installs the bundled engine as an isolated tool using `uv`
#      (preferred) or `pipx` as a fallback.
#   3. Prints a one-line status to stderr and exits 0. Never blocks the
#      session if install fails — it just degrades to Path B (skill-only)
#      mode and tells the user how to fix it.

set -u
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
if [[ -z "${PLUGIN_ROOT}" || ! -d "${PLUGIN_ROOT}/engine" ]]; then
    # Hook fired in an unexpected context — silently no-op.
    exit 0
fi

PLUGIN_NAME="ms-dropshipping-market-research"
MARKER_DIR="${HOME}/.local/share/${PLUGIN_NAME}"
MARKER_FILE="${MARKER_DIR}/installed-version"
MANIFEST="${PLUGIN_ROOT}/.claude-plugin/plugin.json"

# Parse current version from manifest without requiring jq.
CURRENT_VERSION=$(grep -E '"version"\s*:' "${MANIFEST}" 2>/dev/null \
    | head -n1 | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')
INSTALLED_VERSION=$( [[ -f "${MARKER_FILE}" ]] && cat "${MARKER_FILE}" || echo "" )

cli_works() { command -v niche-research >/dev/null 2>&1; }

if cli_works && [[ "${INSTALLED_VERSION}" == "${CURRENT_VERSION}" ]]; then
    # Already installed at the right version. Quiet success.
    exit 0
fi

mkdir -p "${MARKER_DIR}"

note() { printf '[%s] %s\n' "${PLUGIN_NAME}" "$*" 1>&2; }

install_with_uv() {
    if ! command -v uv >/dev/null 2>&1; then
        return 1
    fi
    note "installing niche-research via uv tool install (v${CURRENT_VERSION})..."
    if uv tool install --force --reinstall "${PLUGIN_ROOT}/engine" >/dev/null 2>&1; then
        echo "${CURRENT_VERSION}" > "${MARKER_FILE}"
        note "engine CLI installed. Try: niche-research demand \"<niche>\""
        return 0
    fi
    return 1
}

install_with_pipx() {
    if ! command -v pipx >/dev/null 2>&1; then
        return 1
    fi
    note "installing niche-research via pipx (v${CURRENT_VERSION})..."
    if pipx install --force "${PLUGIN_ROOT}/engine" >/dev/null 2>&1; then
        echo "${CURRENT_VERSION}" > "${MARKER_FILE}"
        note "engine CLI installed via pipx."
        return 0
    fi
    return 1
}

if install_with_uv; then exit 0; fi
if install_with_pipx; then exit 0; fi

# Couldn't install — explain how to fix without breaking the session.
note "could not auto-install the niche-research CLI."
note "install one of these and re-open Claude Code:"
note "   brew install uv     # recommended"
note "   brew install pipx   # alternative"
note "the skill still works in fallback mode (WebSearch + WebFetch only)."
exit 0

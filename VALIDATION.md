# Validation & Sharing Guide

How to **package** this plugin for a client, how the **client installs and
validates** it, and the **pre-ship checklist** to run before you send it.

---

## A. Package it (you, the author)

```bash
./package.sh
```

This builds, under `dist/`:

- `ms-dropshipping-market-research-<version>.zip`
- `ms-dropshipping-market-research-<version>.tar.gz`
- `ms-dropshipping-market-research-<version>.sha256` (checksums)

Secrets (`.env`), venvs, caches, and generated briefs are excluded automatically;
the script aborts if a `.env` ever slips into the archive.

**Two ways to share:**

1. **File** — send the `.zip` (or `.tar.gz`) + the `.sha256`. The client unzips
   it and adds it as a local marketplace (see B-1 below).
2. **Git/GitHub** — push the repo and have the client run
   `/plugin marketplace add <owner>/ms-dropshipping-market-research`
   then `/plugin install ms-dropshipping-market-research`.

> Bump the version (`.claude-plugin/plugin.json` + `marketplace.json` +
> `engine/pyproject.toml` + `engine/src/niche_research/__init__.py`, kept in sync)
> on every release — the SessionStart hook only reinstalls the engine when the
> version changes.

---

## B. Install & validate (your client)

### Prerequisites

- macOS or Linux, and either [`uv`](https://docs.astral.sh/uv/) (recommended) or
  [`pipx`](https://pipx.pypa.io/): `brew install uv`
- A **Claude Pro/Max subscription** (the engine reuses the Claude Code login — no
  separate API key needed) **or** an Anthropic API key for pay-per-token billing.

### B-1. Install from the archive (file share)

```text
unzip ms-dropshipping-market-research-<version>.zip
```

In Claude Code:

```text
/plugin marketplace add /absolute/path/to/ms-dropshipping-market-research-<version>
/plugin install ms-dropshipping-market-research
```

Then **restart Claude Code**. The SessionStart hook installs the `niche-research`
engine and prints a one-line confirmation.

### B-2. Validate (free — no tokens, no API call)

From the extracted folder, or anywhere after install:

```bash
niche-research verify
# or, without installing the CLI globally:
./research.sh            # runs verify first, then discovery
```

A healthy install prints all ✓ and ends with **`All checks passed`**, including:

- `Auth: Claude subscription` (or `Auth: API key`) — confirms login is wired
- `pipeline.yaml loads … runnable specialists: demand, competition, community`

If the auth line is ✗, sign in once and re-run:

```text
! claude /login      # choose the Pro/Max account
```

### B-3. Smoke-test for real (uses your plan/credits)

```bash
./research.sh                              # suggest high-ticket products (lightest)
./research.sh "ergonomic standing desks"   # full opportunity brief
```

Discovery (`suggest`) is the cheapest real test. A full `run` is heavier (3
specialists). Briefs are written to `~/niche-research/briefs/`.

---

## C. Pre-ship checklist (run before sending)

- [ ] Versions match across `plugin.json`, `marketplace.json`, `pyproject.toml`,
      `__init__.py`.
- [ ] `./package.sh` builds without the secret-guard tripping.
- [ ] Fresh install from the archive: `niche-research verify` exits 0.
- [ ] `niche-research --help` lists: `demand`, `competition`, `community`,
      `run`, `suggest`, `verify`.
- [ ] `pipeline.yaml` loads with the intended engines + enabled specialists.
- [ ] No `.env` (or any secret) in the archive — `unzip -l <zip> | grep -i env`
      shows only `.env.example`.
- [ ] README + this guide reflect the current commands.

When every box is checked, the artifact in `dist/` is safe to share.

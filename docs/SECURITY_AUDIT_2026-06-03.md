# Security Audit — robotics-platform-template
**Date**: 2026-06-03
**Auditor**: SEC-Template (Claude opus 4.7, Plan agent)
**Scope**: code (HEAD), CI workflows, deps lockfile, git history, pre-commit config

## Executive summary
Verdict: **LOW RISK**. Repo is a clean public Apache-2.0 template with pure-Python type/Protocol code, zero network surface, no secrets in history, and a working anti-leak hook. Main gaps are CI hygiene (missing `permissions:`, floating-tag actions), missing `SECURITY.md`, and one runtime-side-effect `assert` at module import in `sim_adapter.py`. Findings: 0 Critical / 0 High / 3 Medium / 4 Low / 2 Info.

## Findings

| ID | Severity | Surface | Finding | Recommended fix | Effort |
|----|----------|---------|---------|-----------------|--------|
| TPL-001 | Medium | CI | `.github/workflows/ci.yaml` declares no top-level or per-job `permissions:` block, so jobs inherit the repo-level default `GITHUB_TOKEN` scope. For a public repo a least-privilege baseline is mandatory. | Add `permissions: contents: read` at workflow top level; widen only where needed. | S |
| TPL-002 | Medium | CI | GitHub Actions are pinned to floating tags (`actions/checkout@v4`, `astral-sh/setup-uv@v5`) rather than full commit SHAs. A compromised tag would inject code in CI. | Pin to full 40-char commit SHAs and add a comment with the human-readable tag. Optionally enable Dependabot for `github-actions` ecosystem. | S |
| TPL-003 | Medium | Docs | No `SECURITY.md` at repo root. For a public Apache-2.0 template that is meant to be reused, a coordinated-disclosure policy is expected by GitHub and downstream consumers. | Add `SECURITY.md` (root) with supported versions, a private contact (e.g. GitHub Security Advisories), and SLA. Reference it from `README.md`. | S |
| TPL-004 | Low | Validation | `src/robotics_platform/hal/sim_adapter.py` lines 153–159 instantiate `SimRobotAdapter()` and run `assert isinstance(...)` at module import. (a) `assert` is stripped under `python -O`, defeating the check; (b) the side-effect runs on every import, including in security-sensitive contexts. | Move the Protocol conformance check into the test suite (e.g. `tests/hal/test_sim_adapter.py`); remove the module-level assert. | S |
| TPL-005 | Low | CI | No dependency vulnerability scan in CI (no `pip-audit`, `osv-scanner`, or `safety` job). `uv.lock` is pinned (good) but unscanned. | Add a `security` job to `ci.yaml` running `uv run pip-audit --strict` (and/or `osv-scanner --lockfile=uv.lock`) on push/PR and weekly schedule. | M |
| TPL-006 | Low | Pre-commit | The `anti-leak` hook is invoked via `bash .git-hooks/pre-commit-anti-leak.sh`. On Windows-only contributor machines without WSL/Git-Bash on PATH the hook will silently fail to execute, defeating the IP guard. Also the script is not exercised by CI (no smoke test). | Add a tiny CI job that runs the hook against a synthetic staged diff containing each `BLOCKED_PATTERNS` entry and asserts exit code 1. Document Bash requirement in `docs/CONTRIBUTING.md`. | M |
| TPL-007 | Low | Pre-commit | `.pre-commit-config.yaml` pins `ruff-pre-commit@v0.9.0` and `mirrors-mypy@v1.10.0` (May 2024) while `uv.lock` resolves `ruff==0.15.14` and `mypy==2.1.0`. The version drift means pre-commit checks differ from CI/local runs, weakening the guarantee. | Bump pre-commit revs to match `uv.lock`, or switch to the `pre-commit/mirrors-mypy` `language: python` form pulling from project requirements. | S |
| TPL-008 | Info | Deps | `pip-audit` not executed in this read-only audit (cannot install). Manual review of `uv.lock` shows only well-known maintained packages (`numpy 2.4.6`, `loguru 0.7.3`, `typing-extensions 4.15.0`, `mujoco 3.5.0`, dev: `ruff`, `mypy`, `pytest`, `pre-commit`). No deprecated/abandoned packages, no `requests`/HTTP libs, no native auth libs. | Defer to fix phase: run `uv run pip-audit` and capture output once writable env is available. | S |
| TPL-009 | Info | Secrets | History scan `git log -p --all -S` for `TOKEN`, `SECRET`, `password`, `api_key`, `private_key`, `BEGIN RSA`, `ghp_`, `AWS_` returned no real hits (one false positive on the docs phrase "single source of truth"). `.gitignore` covers `.env`, `secrets/`, `_private/`, `my-robot-stack/`, `proprietary_*`. No `.env*` or `*.key`/`*.pem` glob — add for defense in depth. | Extend `.gitignore`: `.env.*`, `*.pem`, `*.key`, `*.p12`, `id_rsa*`. | S |
| TPL-010 | Low | IP | `CLAUDE.md` and `docs/CONTRIBUTING.md` reference the private-layer ban but `README.md` does not surface the Apache-2.0 / no-proprietary-layer commitment for outside contributors. | Add a one-paragraph "Contributing & IP boundary" section to `README.md` linking to `LICENSE`, `NOTICE`, and `docs/CONTRIBUTING.md`. | S |

Severity = Critical / High / Medium / Low / Info
Effort = S (<1h) / M (1-4h) / L (>4h)
Surface = Pre-commit / CI / Deps / Secrets / Validation / Network / SPDX / IP / Docs

### Positive controls verified
- **SPDX coverage**: 17/17 `.py` files under `src/` and `tests/` carry `SPDX-License-Identifier: Apache-2.0`. 100% coverage.
- **Anti-leak hook exists**: `.git-hooks/pre-commit-anti-leak.sh` is present (the inventory's "not found" note was incorrect). Logic correctly checks filenames AND staged diff content for 5 blocked patterns, exits 1 on hit.
- **No proprietary leak in code**: `LicenseRef-Proprietary` / `All Rights Reserved` strings appear only in guard files (`.git-hooks/`, `CLAUDE.md`, `docs/CONTRIBUTING.md`).
- **Zero network surface**: no `socket`/`requests`/`urllib`/`http`/`aiohttp`/`fastapi`/`flask`/`grpc` import anywhere in `src/`. Confirmed.
- **No unsafe primitives**: no `eval`/`exec`/`pickle`/`subprocess`/`os.system`/`shell=True`/`__import__` in `src/`.
- **Deps pinned**: `uv.lock` present, runtime deps are 3 (numpy, loguru, typing-extensions); sim is optional (mujoco 3.5.0).
- **Git history clean**: no committed secrets/tokens/keys found in `--all` history.
- **CI uses safe trigger**: `pull_request` (not `pull_request_target`), so PR forks cannot exfiltrate the workflow token.

## Out of scope
- Runtime security of downstream consumers that implement `EnvAdapter` / `RobotInterface` (their `step`/`reset` may exec user-supplied code, but that is a consumer-layer concern).
- Hardware-facing safety (the template explicitly forbids hardware-specific code; real-robot `is_safe()` impls live in private adapters).
- `mujoco_playground` security posture (installed off-PyPI from a GitHub URL by consumers — not a template responsibility, but worth a note in `docs/ADD_A_ROBOT.md`).
- `.venv/` contents under the repo (caching artefact; not committed).

## Recommandations transverses
- Add a small `security:` CI job running `pip-audit` + `osv-scanner` + a synthetic invocation of `pre-commit-anti-leak.sh` (covers TPL-005, TPL-006 in one PR).
- Adopt full-SHA pinning for all GitHub Actions and enable Dependabot for `github-actions`, `pip`, and `pre-commit` ecosystems (covers TPL-002 and surfaces TPL-007 automatically).
- Promote the IP-boundary contract from `CLAUDE.md` to user-facing docs (`README.md` + `SECURITY.md`) so external contributors see it without reading the agent rules.

### Critical Files for Implementation (for the fix phase)
- `.github/workflows/ci.yaml`
- `.pre-commit-config.yaml`
- `src/robotics_platform/hal/sim_adapter.py`
- `.gitignore`
- `.git-hooks/pre-commit-anti-leak.sh`

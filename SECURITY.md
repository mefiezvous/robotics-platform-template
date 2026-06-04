<!--
SPDX-FileCopyrightText: 2026 Arthur Mouraud
SPDX-License-Identifier: Apache-2.0
-->
# Security Policy

## Supported Versions
The `main` branch (latest release tag) is the only supported version.

## Reporting a Vulnerability
Please report security issues privately via GitHub Security Advisories: https://github.com/mefiezvous/robotics-platform-template/security/advisories/new

Expected first response: 7 days. Coordinated disclosure window: 90 days.

## Scope
- In scope: code under `src/robotics_platform/`, CI workflows, pre-commit hooks.
- Out of scope: downstream consumer implementations of `RobotInterface` / `EnvAdapter` (their own security boundary).
- Out of scope: `mujoco_playground` and other third-party deps (report upstream).

## Threat Model
This is a generic HAL template; it has no network surface, no eval/exec, no pickle.load. Primary risks are:
- CI supply-chain (GitHub Actions, deps). Mitigated by SHA-pinning + Dependabot + pip-audit.
- IP boundary leak (downstream private impls accidentally pushed here). Mitigated by anti-leak pre-commit hook + CI smoke test.

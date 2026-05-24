# CLAUDE.md — robotics-platform-template

## Identity
Generic Hardware Abstraction Layer (HAL) + Environment Adapter Protocols for robotics.
Apache-2.0, Python 3.12+. Author: Arthur Mouraud. Package name: `robotics_platform`.

## Critical Rules
1. NEVER add hardware-specific code — this layer is 100% generic.
2. NEVER reference specific robots, clients, projects, or `_private/`.
3. NEVER use `LicenseRef-Proprietary` or `All Rights Reserved`.
4. SPDX header required at top of every `.py`:
   `# SPDX-FileCopyrightText: 2026 Arthur Mouraud`
   `# SPDX-License-Identifier: Apache-2.0`
5. Coverage 100% on `src/robotics_platform/hal/` and `src/robotics_platform/envs/` — non-negotiable.

## Code Standards
- `typing.Protocol` (`@runtime_checkable`), no ABCs.
- Type hints everywhere, mypy strict.
- Google-style docstrings on public API.
- `from loguru import logger` — no `print()`.

## Documentation enfant
- [README.md](README.md) — purpose, install, quickstart
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Protocol design, modules, consumers
- [docs/ROADMAP.md](docs/ROADMAP.md) — forward-looking
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) — workflow, strict rules

## Workspace context (non committé)
- Cross-repo rules & memory : `../CLAUDE.md` racine workspace
- État volatile (branche active, P0) : `memory/project_state.md`

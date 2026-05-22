# Claude Code — robotics-platform-template

## Purpose
Generic Hardware Abstraction Layer (HAL) for robotics projects.
Defines the RobotInterface Protocol and supporting types used by all adapter implementations.
License: Apache-2.0. Python 3.12+. Author: Arthur Mouraud.

## Absolute Rules
1. NEVER add hardware-specific code here — this layer is 100% generic
2. NEVER reference specific robots, clients, or projects
3. NEVER reference `_private/`, `my-robot-stack/`, or `LicenseRef-Proprietary`
4. SPDX header required at top of every .py file:
   `# SPDX-FileCopyrightText: 2026 Arthur Mouraud`
   `# SPDX-License-Identifier: Apache-2.0`
5. HAL coverage is non-negotiable: 100% on `src/robotics_platform/hal/`

## What Belongs Here
- RobotInterface Protocol (abstract contract)
- Observation, Action, RobotCapabilities types
- SimRobotAdapter (generic MuJoCo backend — no hardware deps)
- AdapterRegistry (lookup by name)
- Generic Hydra config templates

## What Does NOT Belong Here
- Robot brand names or model numbers
- Hardware-specific safety limits
- Production configs
- Anything from `_private/`

## Code Standards
- Type hints everywhere, mypy strict
- Google-style docstrings for all public API
- Protocol-based design (structural subtyping, no ABC inheritance required)
- Tests: 100% coverage on src/robotics_platform/hal/ (enforced by --cov-fail-under=100)

## Workflow
- Conventional commits: feat:, fix:, docs:, chore:, refactor:, test:
- Feature branches, PRs required
- No direct commits to main

## État du projet
Voir **STATUS.md** — ce qui est implémenté, ce qui reste, les consommateurs du layer.

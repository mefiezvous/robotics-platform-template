# Contributing — robotics-platform-template

This repo is a generic Hardware Abstraction Layer template. Contributions must preserve its genericity and 100% coverage discipline.

## Strict rules

1. **No hardware-specific code.** No robot brand names (Franka, UR5, Panda, etc.), no model numbers, no production configs.
2. **No proprietary references.** No mention of `_private/`, `my-robot-stack/`, `LicenseRef-Proprietary`, or `All Rights Reserved`.
3. **Protocol-based.** Public contracts are `typing.Protocol` with `@runtime_checkable`. No ABCs, no inheritance requirements.
4. **SPDX header** on every `.py`:
   ```
   # SPDX-FileCopyrightText: 2026 Arthur Mouraud
   # SPDX-License-Identifier: Apache-2.0
   ```
5. **100% coverage** on `src/robotics_platform/hal/` and `src/robotics_platform/envs/` — enforced by `--cov-fail-under=100`. PRs that lower coverage are rejected.

## Workflow

- Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`
- Feature branches only — no direct commits to `main`.
- PR required (even solo). CI must be green before merge.

## Local checks

```bash
make lint        # ruff check + format
make typecheck   # mypy strict
make test        # pytest --cov-fail-under=100
```

Pre-commit hooks (`ruff`, `mypy`, `anti-leak`) run on every commit.

## Code standards

- Type hints everywhere; mypy strict mode.
- Google-style docstrings on every public API.
- `from loguru import logger` — never `print()`.
- No direct `os.environ` access.

## What does NOT belong here

Anything tied to a specific robot, simulator instance, or training task. Those go in `ml-core`, `lerobot-playground-portfolio`, or `_private/my-robot-stack`.

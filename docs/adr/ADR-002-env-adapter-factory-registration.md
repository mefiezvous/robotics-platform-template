<!--
SPDX-FileCopyrightText: 2026 Arthur Mouraud
SPDX-License-Identifier: Apache-2.0
-->

# ADR-002 — EnvAdapterRegistry: accept zero-arg factory callables

- **Status**: Implemented 2026-06-10
- **Deciders**: Arthur Mouraud
- **Scope**: `robotics-platform-template` (`robotics_platform.envs.registry`), consumed by `lerobot-playground-portfolio`. Cross-reference: `ml-core/docs/adr/ADR-001-yaml-spec-loader.md`, `lerobot-playground-portfolio/docs/adr/ADR-001-robot-specs-yaml-registry.md`.

## Context

`EnvAdapterRegistry` (`_REGISTRY: dict[str, type]`) only accepted classes registered via the `@register("name")` decorator, each instantiated with `cls()`. Adding a new MuJoCo Playground env required hand-writing a thin adapter subclass per env:

```python
@register("cube_reach_v1")
class CubeReachV1Adapter(MujocoPlaygroundAdapter):
    def __init__(self) -> None:
        super().__init__(env_name="CubeReachV1", task_description="Reach the cube")
```

The new data-driven YAML robot-spec registry (ADR-001 in `ml-core` and `lerobot-playground-portfolio`) needs to register an env under a name with constructor arguments baked in from YAML (`env_name`, `task_description`), without generating a Python class per robot.

## Decision

Widen `_REGISTRY` to `dict[str, type | Callable[[], EnvAdapter]]` and add `register_factory(name: str, factory: Callable[[], EnvAdapter]) -> None`, an imperative alternative to the `@register` decorator for zero-arg callables (typically `functools.partial(MujocoPlaygroundAdapter, env_name=..., task_description=...)`). `EnvAdapterRegistry.get(name)` now returns `type[EnvAdapter] | Callable[[], EnvAdapter]`; existing callers already do `EnvAdapterRegistry.get(name)()`, which works identically for a class or a `functools.partial`. Both `register` and `register_factory` log a warning on overwrite, so a YAML-driven registration that collides with a hand-written `@register`'d class is visible but non-fatal — the later registration wins.

## Alternatives considered

1. **Dynamic `type()` generation** — synthesize an adapter subclass at runtime from YAML fields. Rejected: harder to debug (no source location, opaque `__name__`), and `functools.partial` already gives the same zero-arg-callable contract with full introspection (`factory.func`, `factory.keywords`).
2. **Separate registry for factories** (`_FACTORY_REGISTRY` alongside `_REGISTRY`). Rejected: callers (`EnvAdapterRegistry.get(name)()`) would need to check two registries; a single widened registry keeps the lookup contract unchanged.
3. **Require all adapters to go through factories** (deprecate the `@register` class decorator). Rejected: breaking change for no benefit — class-based registration remains the right tool for hand-written, non-MuJoCo-Playground (hardware) adapters.

## Consequences

**Positive**:
- Additive, fully backward-compatible: existing `@register`'d classes and `EnvAdapterRegistry.get(name)()` call sites are unchanged (`type.__call__()` and `functools.partial.__call__()` both satisfy the zero-arg contract).
- Unblocks data-driven registration (`lerobot-playground-portfolio/src/playground/envs/yaml_registrations.py`) without per-robot Python source generation.

**Negative**:
- `EnvAdapterRegistry.get(name)` callers that previously assumed a `type` (e.g. introspecting `cls.__name__`) must now handle `functools.partial` too. One such case was found and fixed: `lerobot-playground-portfolio/tests/test_registrations.py`'s nomenclature guardian test now skips the class-naming check for non-`type` (factory) registry entries, since data-driven entries intentionally all map to the same `MujocoPlaygroundAdapter` class regardless of registry key.

**Verification**: `tests/test_envs_registry.py` covers `register_factory` (registration, retrieval, overwrite warning) at 100% coverage on `src/robotics_platform/envs/registry.py`; `mypy --strict` clean.

# robotics-platform-template

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)

> Hardware Abstraction Layer (HAL) template for robotics projects.
> Protocol-based contracts between robot hardware/simulation and algorithm code.

## What this is

A small, generic, reusable template providing:
- `RobotInterface` — Python Protocol for all robot adapters (sim or hardware)
- `Observation`, `Action`, `RobotCapabilities` — typed data structures
- `SimRobotAdapter` — generic MuJoCo Playground wrapper
- `AdapterRegistry` — runtime adapter lookup by name
- `EnvAdapter` — gym-style environment Protocol (5-tuple step)
- `EnvAdapterRegistry` — runtime env adapter lookup

Zero hardware-specific code, zero opinions about training algorithms. 100% test coverage on the entire public surface.

## Install

As a local path dependency in your `pyproject.toml`:

```toml
[tool.uv.sources]
robotics-platform-template = { path = "../robotics-platform-template", editable = true }
```

## Quickstart

Implement the Protocol for your robot — no inheritance required:

```python
from robotics_platform.hal.interfaces import RobotInterface
from robotics_platform.hal.types import Observation, Action, RobotCapabilities

class MyRobotAdapter:
    def get_capabilities(self) -> RobotCapabilities: ...
    def reset(self) -> Observation: ...
    def step(self, action: Action) -> tuple[Observation, float, bool, dict]: ...
    def close(self) -> None: ...
    def is_safe(self, action: Action) -> bool: ...

assert isinstance(MyRobotAdapter(), RobotInterface)  # structural check
```

For an environment adapter, use the `EnvAdapter` Protocol from `robotics_platform.envs.interfaces`.

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Protocol design, module layout, consumers
- [docs/ROADMAP.md](docs/ROADMAP.md) — forward-looking
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) — workflow & strict rules

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
Copyright 2026 Arthur Mouraud.

> Future major versions may carry more restrictive license terms. See [NOTICE](NOTICE).

# robotics-platform-template

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)

> Hardware Abstraction Layer (HAL) template for robotics projects.
> Provides a clean Protocol-based interface between robot hardware/simulation and algorithm code.

## What This Is

A reusable architecture template defining:
- `RobotInterface` — Python Protocol for all robot adapters
- `Observation`, `Action`, `RobotCapabilities` — typed data structures
- `SimRobotAdapter` — generic MuJoCo Playground adapter
- `AdapterRegistry` — runtime adapter lookup

## Usage

Add as a local path dependency in your `pyproject.toml`:

```toml
[tool.uv.sources]
robotics-platform-template = { path = "../robotics-platform-template", editable = true }
```

Then implement the Protocol for your robot:

```python
from platform.hal.interfaces import RobotInterface
from platform.hal.types import Observation, Action, RobotCapabilities

class MyRobotAdapter:
    def get_capabilities(self) -> RobotCapabilities: ...
    def reset(self) -> Observation: ...
    def step(self, action: Action) -> tuple[Observation, float, bool, dict]: ...
    def close(self) -> None: ...
    def is_safe(self, action: Action) -> bool: ...
```

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
Copyright 2026 Arthur Mouraud.

> **Note:** Future major versions may carry more restrictive license terms. See NOTICE for details.

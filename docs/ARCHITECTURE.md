# Architecture — robotics-platform-template

Generic, Protocol-based abstraction layer for robotics. Zero hardware-specific code, zero dependencies beyond `numpy` and `loguru`.

## Design principle: structural subtyping

All contracts are defined as `typing.Protocol` (with `@runtime_checkable`). Implementers don't inherit — they just need to match the method signatures. This decouples the consumer code from the adapter library.

```python
from robotics_platform.hal.interfaces import RobotInterface

class MyAdapter:                           # no "extends RobotInterface"
    def get_capabilities(self) -> RobotCapabilities: ...
    def reset(self) -> Observation: ...
    def step(self, action: Action) -> tuple[Observation, float, bool, dict]: ...
    def close(self) -> None: ...
    def is_safe(self, action: Action) -> bool: ...

assert isinstance(MyAdapter(), RobotInterface)  # True via Protocol
```

## Layout

```
src/robotics_platform/
├── hal/                              # Hardware Abstraction Layer
│   ├── interfaces.py    RobotInterface Protocol (5 methods)
│   ├── types.py         Observation, Action, RobotCapabilities dataclasses
│   ├── registry.py      AdapterRegistry + @register decorator
│   └── sim_adapter.py   SimRobotAdapter — generic MuJoCo Playground wrapper
└── envs/                             # Environment Adapter Layer
    ├── interfaces.py    EnvAdapter Protocol (gym-style 5-tuple step)
    └── registry.py      EnvAdapterRegistry + @register decorator
```

## HAL layer — what each module provides

### `hal/interfaces.py` — `RobotInterface`

5 methods every robot adapter must expose (sim or hardware):

| Method | Returns | Used for |
|---|---|---|
| `get_capabilities()` | `RobotCapabilities` | DOF, gripper, joint limits, control freq |
| `reset()` | `Observation` | Episode start |
| `step(action)` | `(Observation, reward, done, info)` | Per-step |
| `close()` | `None` | Cleanup |
| `is_safe(action)` | `bool` | Pre-step safety gate |

### `hal/types.py` — typed data containers

| Type | Key fields |
|---|---|
| `Observation` | `joint_positions`, `joint_velocities`, `ee_pose`, `images`, `proprioceptive` |
| `Action` | `joint_targets` OR `ee_target` + `gripper_state` |
| `RobotCapabilities` | `n_dof`, `has_gripper`, `joint_limits`, `max_control_hz` |

`Action.__post_init__` raises `ValueError` if both `joint_targets` and `ee_target` are `None`.

### `hal/registry.py` — `AdapterRegistry`

```python
from robotics_platform.hal.registry import register, AdapterRegistry

@register("my_adapter")
class MyAdapter: ...

AdapterRegistry.get("my_adapter")()      # instantiate
AdapterRegistry.list_adapters()          # ["sim_panda", "my_adapter", ...]
```

### `hal/sim_adapter.py` — `SimRobotAdapter`

Generic MuJoCo Playground wrapper. Reusable for any robot exposed through a Playground env. ~150 lines, fully tested.

## Environment Adapter layer (`envs/`)

Separate from HAL. The `EnvAdapter` Protocol abstracts gym-style environments (MuJoCo Playground, LIBERO, real-robot wrappers) so the pipeline layer in downstream repos doesn't import simulator code directly.

Key difference vs `hal/`:
- HAL wraps a **robot** (low-level: joints, end-effector, safety).
- `envs/` wraps an **environment** (high-level: task, observation dict, gym 5-tuple).

```python
from robotics_platform.envs.interfaces import EnvAdapter
from robotics_platform.envs.registry import register, EnvAdapterRegistry

@register("playground_cube_reach")
class PlaygroundCubeReachAdapter:
    def reset(self, seed: int) -> tuple[dict, dict]: ...
    def step(self, action) -> tuple[dict, float, bool, bool, dict]: ...
    def close(self) -> None: ...
    @property
    def obs_space_keys(self) -> list[str]: ...
    @property
    def action_dim(self) -> int: ...
    @property
    def task_description(self) -> str: ...
```

## Hydra config template

```yaml
# configs/hal/sim_adapter.yaml
hal:
  adapter: sim_panda
  sim_adapter:
    env_name: CubeReachV1
    seed: 42
    joint_limit_scale: 0.9
```

## Coverage policy

`--cov-fail-under=100` enforced on both `src/robotics_platform/hal/` and `src/robotics_platform/envs/`. Any uncovered line fails CI.

## Consumers

| Repo | Imports |
|---|---|
| `lerobot-playground-portfolio` | `robotics_platform.hal.*`, `robotics_platform.envs.*` |
| `ml-core` | `robotics_platform.hal.types` (re-exports) |
| `_private/my-robot-stack` | `robotics_platform.hal.interfaces` (RobotInterface contract) |

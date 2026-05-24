# Roadmap — robotics-platform-template

Forward-looking only. For volatile state (current branch, in-progress fixes), see workspace memory.

## Current release: v0.1.0

HAL layer + Environment Adapter layer, both at 100% coverage. Published on GitHub. CI green.

## Stable surface (v0.1)

- `robotics_platform.hal.interfaces.RobotInterface` — 5-method Protocol
- `robotics_platform.hal.types` — `Observation`, `Action`, `RobotCapabilities`
- `robotics_platform.hal.registry.AdapterRegistry` — name → class lookup
- `robotics_platform.hal.sim_adapter.SimRobotAdapter` — MuJoCo Playground generic wrapper
- `robotics_platform.envs.interfaces.EnvAdapter` — gym-style 5-tuple Protocol
- `robotics_platform.envs.registry.EnvAdapterRegistry`

## v0.2 candidates (not committed)

| Item | Rationale |
|---|---|
| Async safety hook in `RobotInterface` | Real hardware needs non-blocking `is_safe` for high control rates |
| `ObservationProcessor` Protocol | Standardize obs normalization across consumers |
| Hydra config schemas (typed) | Catch config typos at instantiation |
| Reference docs (Sphinx or mkdocs) | Currently README + this docs/ folder only |

These are candidates — none planned until a consumer (`lerobot-playground` or `_private/my-robot-stack`) requires them. The template stays small on purpose.

## Maintenance discipline

- No breaking changes to public Protocols without a major version bump.
- Coverage stays at 100% on `hal/` and `envs/`. No exceptions.
- No hardware-specific code, no robot names, no proprietary terms — checked by anti-leak pre-commit and CI.

## Downstream consumers (informational)

| Repo | Current usage |
|---|---|
| `lerobot-playground-portfolio` | Imports `hal.*` and `envs.*` |
| `ml-core` | Re-exports a subset of `hal.types` |
| `_private/my-robot-stack` | Implements `RobotInterface` for hardware adapter |

Changes to public APIs require coordination with these consumers.

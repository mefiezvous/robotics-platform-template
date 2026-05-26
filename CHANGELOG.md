# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Deprecated
- `robotics_platform.hal.types.Observation` — use `dict[str, np.ndarray]` + `RobotSpec` (ml-core) instead. Removed in v0.2.0. See [ADR-001](docs/adr/ADR-001-unify-on-envadapter.md).
- `robotics_platform.hal.types.Action` — use `np.ndarray` directly, with shape described by `RobotSpec.action_dim`. Removed in v0.2.0.
- `robotics_platform.hal.sim_adapter.SimRobotAdapter` — implement `robotics_platform.envs.interfaces.EnvAdapter` directly. Removed in v0.2.0.
- `robotics_platform.hal.interfaces.RobotInterface` — soft-deprecated (still implemented by hardware adapters during migration). Removed in v0.2.0.

## [0.1.0] — 2026-05-20 (initial release)
- HAL Protocol (`RobotInterface`) + structured types (`Observation`, `Action`, `RobotCapabilities`).
- `SimRobotAdapter` generic MuJoCo Playground wrapper.
- `EnvAdapter` Protocol + registry for gym-style environments.

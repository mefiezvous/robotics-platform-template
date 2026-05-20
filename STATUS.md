# Status — robotics-platform-template
_Dernière mise à jour : 2026-05-20 · Session 1_

## Ce qui est fait

### HAL Layer (complet)
- [x] `src/platform/hal/interfaces.py` — `RobotInterface` Protocol (`@runtime_checkable`)
- [x] `src/platform/hal/types.py` — `Observation`, `Action`, `RobotCapabilities` dataclasses
- [x] `src/platform-hal/registry.py` — `AdapterRegistry` + `@register` decorator
- [x] `src/platform/hal/sim_adapter.py` — `SimRobotAdapter` (150 lignes, wraps mujoco_playground)
- [x] `tests/hal/test_interfaces.py` — 6 tests Protocol structural subtyping
- [x] `tests/hal/test_registry.py` — tests lookup registry
- [x] `tests/hal/test_sim_adapter.py` — tests comportement SimRobotAdapter
- [x] `tests/hal/test_types.py` — tests validation types
- [x] Coverage 100% sur `platform.hal` (enforced par `--cov-fail-under=100`)
- [x] Pre-commit hooks : ruff, mypy strict, anti-leak
- [x] `NOTICE` file (Apache-2.0 + "may become restrictive")
- [x] `configs/hal/sim_adapter.yaml` — Hydra config adapter

## Ce qui reste

- [ ] Publier le repo sur GitHub (`mefiezvous/robotics-platform-template`) — actuellement local only
- [ ] GitHub Actions CI (copier le pattern du layer public)
- [ ] Versionner via tags git (v0.1.0) avant publication

## Dépendances
```
numpy>=1.26 · loguru>=0.7
# optionnel (sim) : mujoco==3.5.0 · mujoco_playground==0.2.0
```

## Consommateurs
| Repo | Import |
|------|--------|
| `lerobot-playground-portfolio` | `from platform.hal.interfaces import RobotInterface` |
| `_private/my-robot-stack` | `from platform.hal.interfaces import RobotInterface` |

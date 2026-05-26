<!--
SPDX-FileCopyrightText: 2026 Arthur Mouraud
SPDX-License-Identifier: Apache-2.0
-->

# Glossary

Definitions for terms used across `robotics-platform-template` and its consumers.

## Abstractions

### EnvAdapter (canonique)
Protocol gym-style défini dans `src/robotics_platform/envs/interfaces.py`. Toute environnement (sim ou hardware) implémente :

- `reset(seed: int) -> tuple[dict, dict]` — retourne `(obs, info)` où `obs: dict[str, np.ndarray]`.
- `step(action: np.ndarray) -> tuple[dict, float, bool, bool, dict]` — gym 5-tuple : `(obs, reward, terminated, truncated, info)`.
- `close() -> None`.
- Properties : `obs_space_keys: list[str]`, `action_dim: int`, `task_description: str`.

C'est l'**abstraction canonique** du workspace depuis ADR-001 (2026-05-25). Le schéma exact des `obs` est décrit par un `RobotSpec` (voir ci-dessous).

### RobotInterface (deprecated, à supprimer en v0.2.0)
Ancien Protocol HAL avec types structurés `Observation`/`Action`. Conservé en place avec `@deprecated` jusqu'à la migration de `MyRobotAdapter`. Voir [ADR-001](adr/ADR-001-unify-on-envadapter.md).

### RobotSpec (ml-core)
Dataclass définie dans `ml-core/src/mlcore/robots/spec.py`. Décrit déclarativement :
- `obs_keys: list[str]` — les clés de l'`obs` dict à concaténer pour former le state.
- `relational_features: list[RelationalFeature]` — features dérivées (ex : `ee_to_cube`).
- `action_dim: int`, `joint_names: list[str]`, `gripper: bool`.

`RobotSpec` est la **source de vérité du schéma observation/action** pour un robot donné. Couplé à `mlcore.observation.ObservationBuilder`, il génère le vecteur d'état consommé par les policies.

### ObservationBuilder (ml-core)
`mlcore.observation.ObservationBuilder.build(obs: dict) -> np.ndarray` — applique un `RobotSpec` à un `obs` dict (provenant d'un `EnvAdapter`) et retourne le vecteur d'état 1-D float32 stocké dans le dataset.

## Adapters

### MujocoPlaygroundAdapter
Adapter d'environnement de simulation MuJoCo Playground (`lerobot-playground-portfolio/src/playground/envs/mujoco_playground_adapter.py`). Implémente `EnvAdapter`.

### CubeReachV1Adapter
Sous-classe spécifique de `MujocoPlaygroundAdapter` pour la tâche `CubeReachV1` (registry key : `cube_reach_v1`).

### MyRobotAdapter (private)
Adapter hardware dans `_private/my-robot-stack/src/my_robot/adapters/my_robot_adapter.py`. **Phase 3 en cours** : migration de `RobotInterface` vers `EnvAdapter`.

### SimRobotAdapter (deprecated, à supprimer en v0.2.0)
Ancien adapter sim qui retournait des `Observation` HAL. Remplacé par `MujocoPlaygroundAdapter` + `EnvAdapter`.

## Nomenclature

| Niveau | Format | Exemple |
|---|---|---|
| Registry key (`EnvAdapterRegistry`) | snake_case | `cube_reach_v1` |
| Class name | PascalCase | `CubeReachV1Adapter` |
| Upstream MuJoCo Playground env ID | tel quel (imposé upstream) | `CubeReachV1` |
| Robot spec name (`RobotSpec.name`) | snake_case identique au registry key | `cube_reach_v1` |

**Règle** : pour chaque registry key snake_case, la classe correspondante doit avoir le nom PascalCase équivalent avec le suffixe `Adapter`. Vérifié par `tests/test_registrations.py` (test gardien, Phase 5b).

## Observations / actions — schémas exercés

| Concept | Forme exercée par le pipeline chaud |
|---|---|
| Observation brute (sortie `EnvAdapter.reset/step`) | `dict[str, np.ndarray]` libre |
| Vecteur d'état (entrée policy / dataset) | `np.ndarray` 1-D float32, layout défini par `RobotSpec` (pour cube_reach_v1 : 16-dim = ee_pos(3) + cube_pos(3) + joints(7) + ee_to_cube(3)) |
| Action (sortie policy / entrée `EnvAdapter.step`) | `np.ndarray` 1-D float32, dim = `RobotSpec.action_dim` (pour cube_reach_v1 : 8 = 7 joints + 1 gripper) |

<!--
SPDX-FileCopyrightText: 2026 Arthur Mouraud
SPDX-License-Identifier: Apache-2.0
-->

# ADR-001 — Unify on EnvAdapter, deprecate RobotInterface/Observation/Action

- **Status**: Accepted 2026-05-25
- **Deciders**: Arthur Mouraud
- **Scope**: `robotics-platform-template` (cœur), `_private/my-robot-stack` (consumer), `ml-core` + `lerobot-playground-portfolio` (références doc uniquement).

## Context

Deux abstractions parallèles coexistent dans `robotics-platform-template` :

| Abstraction | Module | Forme | Exercée par |
|---|---|---|---|
| `RobotInterface` Protocol + `Observation`/`Action` dataclasses | `hal/` | Types structurés (joint_pos/vel/ee_pose 21-dim ; Action joint_targets\|ee_target + gripper) | `SimRobotAdapter` (template), `MyRobotAdapter` (private) — **0 usages dans le code chaud du pipeline ML** |
| `EnvAdapter` Protocol | `envs/` | Gym-style : `reset()/step()` → `dict[str, np.ndarray]` + `np.ndarray` action ; schéma déclaratif via `RobotSpec` (ml-core) | `MujocoPlaygroundAdapter` + pipeline complet (collect/train/eval), 100 % du chemin chaud |

Investigation 2026-05-25 confirme :
- La `Observation` HAL 21-dim n'est jamais consommée en aval — `MujocoPlaygroundAdapter` retourne directement des `dict`. Le pipeline construit un état 16-dim ad-hoc (`ee_pos + cube_pos + joints + ee_to_cube`) via `mlcore.observation.ObservationBuilder`, configuré déclarativement par `RobotSpec.obs_keys + relational_features`. Le 16-dim est strictement plus expressif (couvre `cube_pos` et features relationnelles que la HAL ne sait pas exprimer).
- La structure `Action` HAL n'est jamais instanciée par une policy ; toutes les policies (ACT, Diffusion, ScriptedPolicy) retournent `np.ndarray` (8,) float32.
- `SimRobotAdapter` est du code mort : 0 imports dans `lerobot-playground-portfolio`, 0 imports dans `_private/my-robot-stack`. Encore couvert par 26 tests qui ne reflètent aucun chemin de production.

Garder deux abstractions parallèles génère de la dette : double maintenance, ambiguïté pour les futurs adapters, gap conceptuel entre HAL (hardware) et EnvAdapter (sim/ML) sans bridge.

## Decision

**Unifier sur `EnvAdapter` + `RobotSpec`.** `RobotInterface`, `Observation`, `Action`, `SimRobotAdapter` sont marqués `@deprecated` (PEP 702) puis supprimés en `v0.2.0`. Tout consommateur hardware (notamment `_private/my-robot-stack/MyRobotAdapter`) bascule vers une implémentation native d'`EnvAdapter`. Le schéma observation/action reste décrit déclarativement par `RobotSpec` (ml-core).

## Alternatives considered

1. **Unifier autour de la HAL (refactor inverse)** — refactor `MujocoPlaygroundAdapter` pour retourner `Observation` HAL, refactor des policies pour produire `Action` structurée. Rejeté : la HAL force un schéma figé (joint_pos/vel/ee_pose) qui ne couvre pas les features relationnelles, et imposerait un refactor profond du pipeline déjà mature.
2. **Documenter explicitement les 2 mondes (statu quo + clarification)** — EnvAdapter pour sim/ML, RobotInterface pour hardware. Rejeté : perpétue la friction, double la maintenance, n'apporte pas de bridge utilisable.
3. **Bridge explicite `Observation ↔ dict` + `Action ↔ ndarray`** — convertisseurs triviaux exposés en utilitaire. Rejeté : ajoute du code sans résoudre la question "quelle est l'abstraction canonique" et conserve l'ambiguïté.

## Consequences

**Positifs** :
- Une seule abstraction à maintenir, déjà exercée par 100 % du pipeline.
- Suppression de ~200 LoC de code mort + tests associés.
- Élimine les frictions #1 (HAL↔dataset bridge) et #2 (Action incohérent) documentées dans `memory/arch_decisions.md` — elles disparaissent mécaniquement.
- `MyRobotAdapter` (hardware) bénéficie de la même abstraction que `MujocoPlaygroundAdapter` (sim), facilitant la sym2real future.

**Négatifs** :
- Migration `MyRobotAdapter` (private) requise — Phase 3 du plan de rollout.
- Tag `v0.2.0` BREAKING pour les consommateurs externes du template (mefiezvous-only à ce jour — risque limité).

**Migration plan** (rollout en 6 phases — voir `memory/arch_unification.md`) :
1. ADR + glossaire + suivi mémoire.
2. Décoration `@deprecated` sans suppression (additif zéro-risque).
3. Migration `_private/my-robot-stack/MyRobotAdapter` vers `EnvAdapter`.
4. Suppression effective dans `v0.2.0` du template.
5. Couplages latents (`WORKSPACE_ROOT` paramétrable, test gardien nomenclature).
6. Pattern ADR généralisé aux autres repos.

**Critère "Implemented"** : Phase 4 mergée, `git grep RobotInterface` retourne ≤1 hit (cette ADR), `v0.2.0` tagué.

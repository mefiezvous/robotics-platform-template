<!-- SPDX-License-Identifier: Apache-2.0 -->

# Add a robot — canonical tutorial

> Onboard a new 3D robot into the pipeline in 3 commands: scaffold, collect, train.

This guide walks through every contract a new robot must satisfy, the scaffolder
that generates them, and the end-to-end data → training → eval loop. The
worked example onboards a fictional `dummy_arm` in under 10 minutes.

---

## 1. The contract — three layers, three Protocols

A "robot" in this pipeline is the intersection of three independent Protocols.
None of them inherit from anything: they are structural (`typing.Protocol`,
`@runtime_checkable`). Implementers only need to match signatures.

### `RobotInterface` — the HAL contract

Lives in [robotics_platform/hal/interfaces.py](../src/robotics_platform/hal/interfaces.py).
Five methods: `get_capabilities`, `reset`, `step`, `close`, `is_safe`. This is the
low-level contract — joints, end-effector, safety. Every sim adapter and every
hardware adapter must satisfy it. For the public pipeline you rarely write this
by hand: `SimRobotAdapter` already wraps any MuJoCo Playground env.

### `EnvAdapter` — the environment contract

Lives in [robotics_platform/envs/interfaces.py](../src/robotics_platform/envs/interfaces.py).
Gym-style 5-tuple `step()` plus three properties: `obs_space_keys`,
`action_dim`, `task_description`. This is the surface the training/collection
loops actually consume — task semantics, observation dict, episode boundaries.
Adapters are registered through `EnvAdapterRegistry`.

### `RobotSpec` — the declarative descriptor

Lives in `ml-core` under `mlcore/robots/specs/`. A small dataclass declaring
`name`, `n_joints`, `action_dim`, `obs_keys`, `task_description`, `fps`,
`episode_length`. It is the single source of truth that connects an env to a
policy. At pipeline startup, `validate_spec_against_env(spec, env)` cross-checks
the spec against the env's introspectable properties and fails fast on
mismatch. See [section 4](#4-runtime-validation).

---

## 2. Quick reference — naming and required fields

**Golden rule:** use one `<name>` in `lower_snake_case` everywhere. No
`mujoco_pgnd:` prefix, no `CamelCase`. The same string is the env config name,
the dataset config name, the RobotSpec key, and the EnvAdapterRegistry key.

| Field            | Where it lives                                        | Owner               |
|------------------|--------------------------------------------------------|---------------------|
| `name`           | `configs/env/<name>.yaml`, `RobotSpec.name`            | scaffolder          |
| `n_joints`       | `RobotSpec.n_joints`                                   | user                |
| `action_dim`     | `RobotSpec.action_dim` + `EnvAdapter.action_dim`       | must agree          |
| `obs_keys`       | `RobotSpec.obs_keys` + `EnvAdapter.obs_space_keys`     | must agree          |
| `task_description` | `RobotSpec.task_description`                         | user                |
| `fps`            | `configs/env/<name>.yaml`                              | env config          |
| `episode_length` | `configs/dataset/<name>.yaml`                          | dataset config      |
| Adapter class    | `src/playground/envs/<name>.py`                        | scaffolder, then user fills `compute_reward()` |
| Spec class       | `ml-core/src/mlcore/robots/specs/<name>.py`            | scaffolder          |
| Registry entry   | `src/playground/envs/registrations.py`                 | scaffolder          |

---

## 3. Walkthrough — onboard `dummy_arm`

A 6-DoF arm reaching for a target. We will scaffold, write the reward, collect,
train, eval.

### Step 1 — Scaffold

From `lerobot-playground-portfolio/`:

```bash
uv run python -m playground.scripts.add_robot dummy_arm \
    --n-joints 6 --action-dim 6 \
    --obs-keys "ee_pos,target_pos,joints" \
    --task-description "Reach a target" \
    --fps 20 --episode-length 200
```

This creates exactly five files and appends one registration:

| File                                                             | Role                                         |
|------------------------------------------------------------------|----------------------------------------------|
| `configs/env/dummy_arm.yaml`                                     | env config (`name: dummy_arm`, `fps: 20`)    |
| `configs/dataset/dummy_arm.yaml`                                 | dataset config (`episode_length: 200`)       |
| `configs/robot/dummy_arm.yaml`                                   | robot config (links spec by name)            |
| `src/playground/envs/dummy_arm.py`                               | `EnvAdapter` subclass with `# TODO` reward   |
| `ml-core/src/mlcore/robots/specs/dummy_arm.py`                   | `RobotSpec` dataclass instance               |

Plus an append in `src/playground/envs/registrations.py`:

```python
EnvAdapterRegistry.register("dummy_arm", DummyArmEnvAdapter)
```

The scaffolder is idempotent — rerunning with the same args is a no-op (or
patches diffs if you tweak flags). Pass `--dry-run` to preview without writing.

### Step 2 — Implement `compute_reward()`

Open `src/playground/envs/dummy_arm.py` and find the `# TODO: implement reward`
line. Replace with a distance-based shaped reward:

```python
import numpy as np

def compute_reward(self, obs: dict) -> float:
    """Negative Euclidean distance from end-effector to target."""
    ee_pos = np.asarray(obs["ee_pos"], dtype=np.float32)
    target_pos = np.asarray(obs["target_pos"], dtype=np.float32)
    distance = float(np.linalg.norm(ee_pos - target_pos))
    return -distance
```

That's the only line of "physics" you write in the easy path. The
`EnvAdapter.step()` boilerplate (action clipping, obs dict assembly, done flag)
is already generated.

### Step 3 — Place the asset

There are two paths:

**Easy path (recommended)** — subclass an existing MuJoCo Playground env
(e.g. `PandaPickCube`) inside `src/playground/envs/dummy_arm.py`. No MJCF, no
URDF. You inherit the robot model, scene, contacts, sensors. You only override
the task layer: target sampling, reward, success criterion.

**Hard path (custom robot model)** — MJCF/URDF authoring is non-trivial and
out of scope for this guide. You need a valid MJCF in `assets/<name>/scene.xml`,
register it via `mujoco_playground.registry.register("<name>", ...)`, and
ensure all referenced meshes and textures resolve. Plan for a separate
debugging session — sim convergence on a fresh MJCF rarely works first try.

### Step 4 — Collect a dataset

```bash
uv run python collect.py env=dummy_arm dataset=dummy_arm episodes=200 push_to_hub=true
```

Under the hood `collect.py`:
1. Builds the env via `EnvAdapterRegistry.get("dummy_arm")()`
2. Fetches the spec via `mlcore.robots.get("dummy_arm")`
3. Runs `validate_spec_against_env(spec, env)` — fails fast on mismatch
4. Instantiates `ScriptedReachPolicy` → `ScriptedCollector` → `HubSink`
5. Writes a LeRobotDataset v3.0 (Parquet + MP4) and optionally pushes to the Hub

### Step 5 — Train

```bash
uv run python train.py env=dummy_arm policy=act
```

Same validation runs at the top of `train.py`. Checkpoints land at
`checkpoints/dummy_arm/act/checkpoint_XXXXXXXX.ckpt`, MLflow at
`mlruns/dummy_arm_act/`.

### Step 6 — Eval

```bash
uv run python eval.py env=dummy_arm policy=act \
    +eval.checkpoint_path=checkpoints/dummy_arm/act/checkpoint_00010000.ckpt \
    +eval.n_episodes=50
```

This wraps `mlcore.eval.Evaluator`, which rolls out the policy in the env,
computes success rate / reward distribution, and writes a namespaced report at
`eval_reports/dummy_arm/act/eval_report.json`.

---

## 4. Runtime validation

`validate_spec_against_env(spec, env)` is called at the top of `train.py` and
`collect.py`. It raises `RobotSpecMismatch` (subclass of `ValueError`) on the
first inconsistency. Two failure modes:

**Action-dim mismatch:**

```
RobotSpecMismatch: Action dim mismatch for 'dummy_arm':
    spec.action_dim = 6
    env.action_dim  = 7
```

**Missing observation keys:**

```
RobotSpecMismatch: Missing obs keys for 'dummy_arm':
    spec.obs_keys      = ['ee_pos', 'target_pos', 'joints']
    env.obs_space_keys = ['ee_pos', 'joints']
    missing            = ['target_pos']
```

Implementation: `mlcore.robots.validate_spec_against_env`.

---

## 5. Troubleshooting

| Symptom                                       | Cause                                                                 | Fix                                                                                          |
|----------------------------------------------|-----------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| `RobotSpecMismatch: Action dim mismatch`      | Spec and env disagree on `action_dim`.                                | Edit either `RobotSpec.action_dim` (in `mlcore/robots/specs/<name>.py`) or the env's action space until they agree. |
| `RobotSpecMismatch: Missing obs keys`         | Env does not expose what the spec declares.                           | Edit `spec.obs_keys` so it is a subset of `env.obs_space_keys`. The env is authoritative.    |
| **Name mismatch across configs / registry**   | Same robot referenced under different names in env config, dataset config, RobotSpec, EnvAdapterRegistry key. | Use one `lower_snake_case` `<name>` everywhere — no `mujoco_pgnd:` prefix, no `CamelCase`. Fix any leftover variant. |
| `fps` incompatible                            | Env's internal control rate ≠ `cfg.env.fps`.                          | Edit `configs/env/<name>.yaml` to match the env's true control rate, or expose `fps` in the env adapter. |
| Hub push fails with 401                       | `HUGGINGFACE_TOKEN` not in env / not write-scope.                     | Re-issue a write-scoped token; never pass it through CLI args.                               |

---

## 6. Multi-robot workflow

**Mode A — sequential training (supported today).** Loop over names; each run
gets its own namespaced checkpoint and MLflow run automatically:

```bash
for r in dummy_arm cube_reach_v1 panda_pick; do
    uv run python collect.py env=$r dataset=$r episodes=200
    uv run python train.py   env=$r policy=act
    uv run python eval.py    env=$r policy=act +eval.n_episodes=50
done
```

No code change required — the path namespacing
`{robot_name}/{policy_type}/` keeps artifacts isolated.

---

## 7. What's next

**Mode C — cross-embodiment mixed-batch training** (one policy across several
robots, batched together via padding + embodiment ID) is a future evolution.
It is documented in workspace memory and in private design notes; it requires
changes to `Trainer`, `RobotSpec` (embodiment token), and the dataloader
sampling strategy. Not in scope here.

For the contract evolution itself (new `RobotInterface` methods, new
`EnvAdapter` properties), see
[ROADMAP.md](ROADMAP.md) in this repo.

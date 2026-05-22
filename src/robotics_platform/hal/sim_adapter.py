# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""SimRobotAdapter — generic MuJoCo Playground adapter implementing RobotInterface."""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger

from robotics_platform.hal.interfaces import RobotInterface
from robotics_platform.hal.types import Action, Observation, RobotCapabilities


class SimRobotAdapter:
    """Generic simulation adapter wrapping a MuJoCo Playground environment.

    Implements RobotInterface via structural subtyping (no explicit inheritance).
    Translates between Playground obs dicts and HAL typed dataclasses.

    Args:
        env_name: Registered mujoco_playground environment name.
        seed: Random seed for reproducibility.
        joint_limit_scale: Safety margin applied to joint limits (0.9 = 10% margin).
    """

    def __init__(
        self,
        env_name: str = "CubeReachV1",
        seed: int = 42,
        joint_limit_scale: float = 0.9,
    ) -> None:
        self._env_name = env_name
        self._seed = seed
        self._joint_limit_scale = joint_limit_scale
        self._env: Any = None
        self._capabilities: RobotCapabilities | None = None
        logger.debug(f"SimRobotAdapter initialized for env={env_name}, seed={seed}")

    def _ensure_env(self) -> None:
        if self._env is None:
            try:
                import mujoco_playground as mp  # type: ignore[import-not-found]

                self._env = mp.make(self._env_name)
            except ImportError as e:
                raise RuntimeError(
                    "mujoco_playground not installed. Install from: "
                    "pip install git+https://github.com/google-deepmind/mujoco_playground"
                ) from e

    def get_capabilities(self) -> RobotCapabilities:
        """Return sim robot capabilities (7-DOF Panda, wrist cam, sim-only)."""
        if self._capabilities is None:
            self._capabilities = RobotCapabilities(
                n_dof=7,
                has_gripper=True,
                has_cameras=["wrist_cam"],
                sim_only=True,
                max_control_hz=50.0,
                joint_limits=np.array(
                    [
                        [-2.8973, 2.8973],
                        [-1.7628, 1.7628],
                        [-2.8973, 2.8973],
                        [-3.0718, -0.0698],
                        [-2.8973, 2.8973],
                        [-0.0175, 3.7525],
                        [-2.8973, 2.8973],
                    ]
                )
                * self._joint_limit_scale,
            )
        return self._capabilities

    def reset(self) -> Observation:
        """Reset simulation and return first observation."""
        self._ensure_env()
        obs_dict, _ = self._env.reset(seed=self._seed)
        return self._dict_to_observation(obs_dict)

    def step(self, action: Action) -> tuple[Observation, float, bool, dict[str, object]]:
        """Apply action to simulation and return (obs, reward, done, info)."""
        self._ensure_env()
        raw_action = self._action_to_array(action)
        obs_dict, reward, terminated, truncated, info = self._env.step(raw_action)
        done = bool(terminated or truncated)
        return self._dict_to_observation(obs_dict), float(reward), done, dict(info)

    def close(self) -> None:
        """Release simulation resources."""
        if self._env is not None:
            self._env.close()
            self._env = None
            logger.debug("SimRobotAdapter: env closed")

    def is_safe(self, action: Action) -> bool:
        """Check if action respects joint limits."""
        caps = self.get_capabilities()
        if action.joint_targets is not None:
            limits = caps.joint_limits
            within = np.all(
                (action.joint_targets >= limits[:, 0]) & (action.joint_targets <= limits[:, 1])
            )
            return bool(within)
        return True

    def _dict_to_observation(self, obs_dict: dict[str, Any]) -> Observation:
        return Observation(
            timestamp=float(obs_dict.get("time", 0.0)),
            joint_positions=np.asarray(
                obs_dict.get("joint_positions", np.zeros(7)), dtype=np.float32
            ),
            joint_velocities=np.asarray(
                obs_dict.get("joint_velocities", np.zeros(7)), dtype=np.float32
            ),
            ee_pose=np.asarray(obs_dict.get("ee_pose", np.zeros(7)), dtype=np.float32),
            images={
                k: np.asarray(v, dtype=np.uint8)
                for k, v in obs_dict.items()
                if isinstance(v, np.ndarray) and v.ndim == 3
            },
        )

    def _action_to_array(self, action: Action) -> np.ndarray:
        if action.joint_targets is not None:
            return np.concatenate(
                [
                    action.joint_targets.astype(np.float32),
                    np.array([action.gripper_state], dtype=np.float32),
                ]
            )
        if action.ee_target is not None:
            return np.concatenate(
                [
                    action.ee_target.astype(np.float32),
                    np.array([action.gripper_state], dtype=np.float32),
                ]
            )
        raise ValueError("Action has neither joint_targets nor ee_target")


assert isinstance(SimRobotAdapter(), RobotInterface), (
    "SimRobotAdapter must satisfy RobotInterface Protocol"
)

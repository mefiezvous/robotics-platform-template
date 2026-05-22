# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""HAL data types — Observation, Action, RobotCapabilities."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Observation:
    """Sensor observation from a robot at a single timestep.

    Attributes:
        timestamp: Monotonic timestamp in seconds.
        joint_positions: Joint angles in radians, shape (n_dof,).
        joint_velocities: Joint angular velocities in rad/s, shape (n_dof,).
        ee_pose: End-effector pose [x, y, z, qw, qx, qy, qz], shape (7,).
        images: Named RGB images, shape (H, W, 3) each, uint8.
        proprioceptive: Scalar proprioceptive readings (e.g., gripper force).
    """

    timestamp: float = 0.0
    joint_positions: np.ndarray = field(default_factory=lambda: np.zeros(7))
    joint_velocities: np.ndarray = field(default_factory=lambda: np.zeros(7))
    ee_pose: np.ndarray = field(default_factory=lambda: np.zeros(7))
    images: dict[str, np.ndarray] = field(default_factory=dict)
    proprioceptive: dict[str, float] = field(default_factory=dict)


@dataclass
class Action:
    """Control action to apply to a robot.

    Exactly one of joint_targets or ee_target should be set.

    Attributes:
        joint_targets: Target joint positions in radians, shape (n_dof,).
        ee_target: Target EE pose [x, y, z, qw, qx, qy, qz], shape (7,).
        gripper_state: Normalized gripper opening [0.0=closed, 1.0=open].
    """

    joint_targets: np.ndarray | None = None
    ee_target: np.ndarray | None = None
    gripper_state: float = 0.0

    def __post_init__(self) -> None:
        if self.joint_targets is None and self.ee_target is None:
            raise ValueError("Action must specify either joint_targets or ee_target")


@dataclass
class RobotCapabilities:
    """Static description of a robot's capabilities.

    Attributes:
        n_dof: Number of degrees of freedom (joints).
        has_gripper: Whether the robot has a gripper.
        has_cameras: List of camera names available.
        sim_only: True if this adapter only works in simulation.
        max_control_hz: Maximum control frequency in Hz.
        joint_limits: Per-joint limits [(min, max), ...], shape (n_dof, 2).
    """

    n_dof: int = 7
    has_gripper: bool = True
    has_cameras: list[str] = field(default_factory=lambda: ["wrist_cam"])
    sim_only: bool = True
    max_control_hz: float = 50.0
    joint_limits: np.ndarray = field(default_factory=lambda: np.array([[-2.9, 2.9]] * 7))

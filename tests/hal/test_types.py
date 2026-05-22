# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""Tests for HAL data types."""

import numpy as np
import pytest

from robotics_platform.hal.types import Action, Observation, RobotCapabilities


class TestObservation:
    def test_default_construction(self) -> None:
        obs = Observation()
        assert obs.timestamp == 0.0
        assert obs.joint_positions.shape == (7,)
        assert obs.joint_velocities.shape == (7,)
        assert obs.ee_pose.shape == (7,)
        assert obs.images == {}
        assert obs.proprioceptive == {}

    def test_custom_values(self) -> None:
        positions = np.ones(7) * 0.5
        obs = Observation(timestamp=1.23, joint_positions=positions)
        assert obs.timestamp == 1.23
        np.testing.assert_array_equal(obs.joint_positions, positions)

    def test_with_images(self) -> None:
        img = np.zeros((64, 64, 3), dtype=np.uint8)
        obs = Observation(images={"wrist_cam": img})
        assert "wrist_cam" in obs.images
        assert obs.images["wrist_cam"].shape == (64, 64, 3)


class TestAction:
    def test_joint_targets_action(self) -> None:
        targets = np.zeros(7)
        action = Action(joint_targets=targets)
        assert action.gripper_state == 0.0

    def test_ee_target_action(self) -> None:
        pose = np.array([0.5, 0.0, 0.5, 1.0, 0.0, 0.0, 0.0])
        action = Action(ee_target=pose)
        assert action.ee_target is not None

    def test_raises_without_target(self) -> None:
        with pytest.raises(ValueError, match="must specify"):
            Action()

    def test_gripper_state_range(self) -> None:
        action = Action(joint_targets=np.zeros(7), gripper_state=1.0)
        assert action.gripper_state == 1.0


class TestRobotCapabilities:
    def test_default_construction(self) -> None:
        caps = RobotCapabilities()
        assert caps.n_dof == 7
        assert caps.has_gripper is True
        assert "wrist_cam" in caps.has_cameras
        assert caps.sim_only is True
        assert caps.max_control_hz == 50.0
        assert caps.joint_limits.shape == (7, 2)

    def test_custom_dof(self) -> None:
        caps = RobotCapabilities(n_dof=6, has_gripper=False, has_cameras=[])
        assert caps.n_dof == 6
        assert caps.has_gripper is False

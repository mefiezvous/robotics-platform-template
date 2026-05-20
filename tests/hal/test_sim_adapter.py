# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""Tests for SimRobotAdapter (mocked mujoco_playground — no GPU required)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from platform.hal.interfaces import RobotInterface
from platform.hal.sim_adapter import SimRobotAdapter
from platform.hal.types import Action, Observation, RobotCapabilities


def make_mock_env() -> MagicMock:
    """Create a mock mujoco_playground env with realistic return values."""
    env = MagicMock()
    obs_dict = {
        "time": 0.0,
        "joint_positions": np.zeros(7, dtype=np.float32),
        "joint_velocities": np.zeros(7, dtype=np.float32),
        "ee_pose": np.array([0.5, 0.0, 0.5, 1.0, 0.0, 0.0, 0.0], dtype=np.float32),
    }
    env.reset.return_value = (obs_dict, {})
    env.step.return_value = (obs_dict, 0.5, False, False, {"success": False})
    return env


class TestSimRobotAdapterProtocol:
    def test_satisfies_robot_interface(self) -> None:
        adapter = SimRobotAdapter()
        assert isinstance(adapter, RobotInterface)


class TestSimRobotAdapterCapabilities:
    def test_default_capabilities(self) -> None:
        adapter = SimRobotAdapter()
        caps = adapter.get_capabilities()
        assert isinstance(caps, RobotCapabilities)
        assert caps.n_dof == 7
        assert caps.has_gripper is True
        assert caps.sim_only is True
        assert caps.max_control_hz == 50.0

    def test_capabilities_cached(self) -> None:
        adapter = SimRobotAdapter()
        caps1 = adapter.get_capabilities()
        caps2 = adapter.get_capabilities()
        assert caps1 is caps2

    def test_joint_limits_shape(self) -> None:
        adapter = SimRobotAdapter()
        caps = adapter.get_capabilities()
        assert caps.joint_limits.shape == (7, 2)


class TestSimRobotAdapterLifecycle:
    def test_reset_returns_observation(self) -> None:
        adapter = SimRobotAdapter()
        mock_env = make_mock_env()
        with patch("mujoco_playground.make", return_value=mock_env):
            obs = adapter.reset()
        assert isinstance(obs, Observation)
        assert obs.joint_positions.shape == (7,)

    def test_step_returns_tuple(self) -> None:
        adapter = SimRobotAdapter()
        mock_env = make_mock_env()
        action = Action(joint_targets=np.zeros(7))
        with patch("mujoco_playground.make", return_value=mock_env):
            adapter.reset()
            obs, reward, done, info = adapter.step(action)
        assert isinstance(obs, Observation)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(info, dict)

    def test_close_releases_env(self) -> None:
        adapter = SimRobotAdapter()
        mock_env = make_mock_env()
        with patch("mujoco_playground.make", return_value=mock_env):
            adapter.reset()
            assert adapter._env is not None
            adapter.close()
            assert adapter._env is None
            mock_env.close.assert_called_once()

    def test_close_without_reset_is_safe(self) -> None:
        adapter = SimRobotAdapter()
        adapter.close()


class TestSimRobotAdapterSafety:
    def test_safe_joint_action(self) -> None:
        adapter = SimRobotAdapter()
        action = Action(joint_targets=np.zeros(7))
        assert adapter.is_safe(action) is True

    def test_unsafe_joint_action_exceeds_limits(self) -> None:
        adapter = SimRobotAdapter()
        action = Action(joint_targets=np.ones(7) * 10.0)
        assert adapter.is_safe(action) is False

    def test_ee_target_action_accepted(self) -> None:
        adapter = SimRobotAdapter()
        action = Action(ee_target=np.array([0.5, 0.0, 0.5, 1.0, 0.0, 0.0, 0.0]))
        assert adapter.is_safe(action) is True


class TestSimRobotAdapterActionConversion:
    def test_joint_action_conversion(self) -> None:
        adapter = SimRobotAdapter()
        mock_env = make_mock_env()
        targets = np.ones(7) * 0.1
        action = Action(joint_targets=targets, gripper_state=0.5)
        with patch("mujoco_playground.make", return_value=mock_env):
            adapter.reset()
            adapter.step(action)
        call_args = mock_env.step.call_args[0][0]
        assert call_args.shape == (8,)
        np.testing.assert_array_almost_equal(call_args[:7], targets)
        assert call_args[7] == pytest.approx(0.5)

    def test_ee_action_conversion(self) -> None:
        adapter = SimRobotAdapter()
        mock_env = make_mock_env()
        pose = np.array([0.5, 0.0, 0.5, 1.0, 0.0, 0.0, 0.0])
        action = Action(ee_target=pose, gripper_state=1.0)
        with patch("mujoco_playground.make", return_value=mock_env):
            adapter.reset()
            adapter.step(action)
        call_args = mock_env.step.call_args[0][0]
        assert call_args.shape == (8,)


class TestSimRobotAdapterMissingDep:
    def test_raises_on_missing_mujoco_playground(self) -> None:
        adapter = SimRobotAdapter()
        with patch.dict("sys.modules", {"mujoco_playground": None}):
            with pytest.raises(RuntimeError, match="mujoco_playground not installed"):
                adapter.reset()

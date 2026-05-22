# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""Tests for SimRobotAdapter (mocked mujoco_playground — no GPU required)."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from robotics_platform.hal.interfaces import RobotInterface
from robotics_platform.hal.sim_adapter import SimRobotAdapter
from robotics_platform.hal.types import Action, Observation, RobotCapabilities


def _make_fake_mp(mock_env: MagicMock) -> ModuleType:
    """Return a fake mujoco_playground module whose make() returns mock_env."""
    fake = ModuleType("mujoco_playground")
    fake.make = MagicMock(return_value=mock_env)  # type: ignore[attr-defined]
    return fake


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
        fake_mp = _make_fake_mp(mock_env)
        with patch.dict(sys.modules, {"mujoco_playground": fake_mp}):
            obs = adapter.reset()
        assert isinstance(obs, Observation)
        assert obs.joint_positions.shape == (7,)

    def test_step_returns_tuple(self) -> None:
        adapter = SimRobotAdapter()
        mock_env = make_mock_env()
        fake_mp = _make_fake_mp(mock_env)
        action = Action(joint_targets=np.zeros(7))
        with patch.dict(sys.modules, {"mujoco_playground": fake_mp}):
            adapter.reset()
            obs, reward, done, info = adapter.step(action)
        assert isinstance(obs, Observation)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(info, dict)

    def test_close_releases_env(self) -> None:
        adapter = SimRobotAdapter()
        mock_env = make_mock_env()
        fake_mp = _make_fake_mp(mock_env)
        with patch.dict(sys.modules, {"mujoco_playground": fake_mp}):
            adapter.reset()
            assert adapter._env is not None
            adapter.close()
            assert adapter._env is None
            mock_env.close.assert_called_once()

    def test_close_without_reset_is_safe(self) -> None:
        adapter = SimRobotAdapter()
        adapter.close()

    def test_ensure_env_not_called_twice(self) -> None:
        """Second reset should reuse the existing env (no double-make)."""
        adapter = SimRobotAdapter()
        mock_env = make_mock_env()
        fake_mp = _make_fake_mp(mock_env)
        with patch.dict(sys.modules, {"mujoco_playground": fake_mp}):
            adapter.reset()
            adapter.reset()
        assert fake_mp.make.call_count == 1  # type: ignore[attr-defined]


class TestSimRobotAdapterSafety:
    def test_safe_joint_action(self) -> None:
        adapter = SimRobotAdapter()
        # Joint 4 (index 3) limits are [-3.07, -0.07]*0.9 — must be negative.
        safe_targets = np.array([0.0, -0.5, 0.0, -2.0, 0.0, 1.5, 0.5])
        action = Action(joint_targets=safe_targets)
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
        fake_mp = _make_fake_mp(mock_env)
        targets = np.ones(7) * 0.1
        action = Action(joint_targets=targets, gripper_state=0.5)
        with patch.dict(sys.modules, {"mujoco_playground": fake_mp}):
            adapter.reset()
            adapter.step(action)
        call_args = mock_env.step.call_args[0][0]
        assert call_args.shape == (8,)
        np.testing.assert_array_almost_equal(call_args[:7], targets)
        assert call_args[7] == pytest.approx(0.5)

    def test_ee_action_conversion(self) -> None:
        adapter = SimRobotAdapter()
        mock_env = make_mock_env()
        fake_mp = _make_fake_mp(mock_env)
        pose = np.array([0.5, 0.0, 0.5, 1.0, 0.0, 0.0, 0.0])
        action = Action(ee_target=pose, gripper_state=1.0)
        with patch.dict(sys.modules, {"mujoco_playground": fake_mp}):
            adapter.reset()
            adapter.step(action)
        call_args = mock_env.step.call_args[0][0]
        assert call_args.shape == (8,)

    def test_dict_to_observation_with_image(self) -> None:
        """Cover the image extraction branch in _dict_to_observation."""
        adapter = SimRobotAdapter()
        mock_env = make_mock_env()
        # Add a 3D array to obs_dict so the image-extraction branch runs
        img = np.zeros((64, 64, 3), dtype=np.uint8)
        obs_dict_with_img = {
            "time": 0.0,
            "joint_positions": np.zeros(7, dtype=np.float32),
            "joint_velocities": np.zeros(7, dtype=np.float32),
            "ee_pose": np.zeros(7, dtype=np.float32),
            "wrist_cam": img,
        }
        mock_env.reset.return_value = (obs_dict_with_img, {})
        fake_mp = _make_fake_mp(mock_env)
        with patch.dict(sys.modules, {"mujoco_playground": fake_mp}):
            obs = adapter.reset()
        assert "wrist_cam" in obs.images
        assert obs.images["wrist_cam"].shape == (64, 64, 3)

    def test_action_with_no_targets_raises(self) -> None:
        adapter = SimRobotAdapter()
        mock_action = MagicMock()
        mock_action.joint_targets = None
        mock_action.ee_target = None
        with pytest.raises(ValueError, match="neither joint_targets nor ee_target"):
            adapter._action_to_array(mock_action)


class TestSimRobotAdapterMissingDep:
    def test_raises_on_missing_mujoco_playground(self) -> None:
        adapter = SimRobotAdapter()
        # Setting the module to None in sys.modules makes Python raise ImportError
        # when "import mujoco_playground" is executed inside _ensure_env.
        with patch.dict(sys.modules, {"mujoco_playground": None}):  # type: ignore[dict-item]
            with pytest.raises(RuntimeError, match="mujoco_playground not installed"):
                adapter.reset()

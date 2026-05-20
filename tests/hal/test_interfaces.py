# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""Tests for RobotInterface Protocol structural subtyping."""

import numpy as np

from platform.hal.interfaces import RobotInterface
from platform.hal.types import Action, Observation, RobotCapabilities


class MinimalAdapter:
    """Minimal class satisfying RobotInterface without inheriting from it."""

    def get_capabilities(self) -> RobotCapabilities:
        return RobotCapabilities()

    def reset(self) -> Observation:
        return Observation()

    def step(self, action: Action) -> tuple[Observation, float, bool, dict]:
        return Observation(), 0.0, False, {}

    def close(self) -> None:
        pass

    def is_safe(self, action: Action) -> bool:
        return True


class IncompleteAdapter:
    """Class missing some Protocol methods — should NOT satisfy RobotInterface."""

    def get_capabilities(self) -> RobotCapabilities:
        return RobotCapabilities()


class TestRobotInterfaceProtocol:
    def test_minimal_adapter_satisfies_protocol(self) -> None:
        adapter = MinimalAdapter()
        assert isinstance(adapter, RobotInterface)

    def test_incomplete_adapter_fails_protocol(self) -> None:
        adapter = IncompleteAdapter()
        assert not isinstance(adapter, RobotInterface)

    def test_protocol_is_runtime_checkable(self) -> None:
        assert isinstance(MinimalAdapter(), RobotInterface)

    def test_minimal_adapter_reset(self) -> None:
        adapter = MinimalAdapter()
        obs = adapter.reset()
        assert isinstance(obs, Observation)

    def test_minimal_adapter_step(self) -> None:
        adapter = MinimalAdapter()
        action = Action(joint_targets=np.zeros(7))
        obs, reward, done, info = adapter.step(action)
        assert isinstance(obs, Observation)
        assert isinstance(reward, float)
        assert isinstance(done, bool)
        assert isinstance(info, dict)

    def test_minimal_adapter_is_safe(self) -> None:
        adapter = MinimalAdapter()
        action = Action(joint_targets=np.zeros(7))
        assert adapter.is_safe(action) is True

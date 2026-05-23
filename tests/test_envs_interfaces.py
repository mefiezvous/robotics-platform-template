# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""Tests for EnvAdapter Protocol structural subtyping."""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from robotics_platform.envs.interfaces import EnvAdapter


class MinimalEnvAdapter:
    """Minimal class satisfying EnvAdapter without inheriting from it."""

    def reset(self, seed: int) -> tuple[dict[str, NDArray[np.floating[Any]]], dict[str, Any]]:
        return {"state": np.zeros(3, dtype=np.float32)}, {"seed": seed}

    def step(
        self, action: NDArray[np.floating[Any]]
    ) -> tuple[
        dict[str, NDArray[np.floating[Any]]],
        float,
        bool,
        bool,
        dict[str, Any],
    ]:
        return {"state": np.zeros(3, dtype=np.float32)}, 0.0, False, False, {}

    def close(self) -> None:
        pass

    @property
    def obs_space_keys(self) -> list[str]:
        return ["state"]

    @property
    def action_dim(self) -> int:
        return 7

    @property
    def task_description(self) -> str:
        return "do the thing"


class IncompleteEnvAdapter:
    """Class missing some Protocol methods — should NOT satisfy EnvAdapter."""

    def reset(self, seed: int) -> tuple[dict[str, NDArray[np.floating[Any]]], dict[str, Any]]:
        return {}, {}


class TestEnvAdapterProtocol:
    def test_minimal_adapter_satisfies_protocol(self) -> None:
        adapter = MinimalEnvAdapter()
        assert isinstance(adapter, EnvAdapter)

    def test_incomplete_adapter_fails_protocol(self) -> None:
        adapter = IncompleteEnvAdapter()
        assert not isinstance(adapter, EnvAdapter)

    def test_protocol_is_runtime_checkable(self) -> None:
        # If the Protocol were not @runtime_checkable, isinstance would raise TypeError.
        assert isinstance(MinimalEnvAdapter(), EnvAdapter)

    def test_all_six_contract_methods_present(self) -> None:
        """The Protocol must expose exactly the documented public surface."""
        expected = {
            "reset",
            "step",
            "close",
            "obs_space_keys",
            "action_dim",
            "task_description",
        }
        for name in expected:
            assert hasattr(EnvAdapter, name), f"EnvAdapter missing required member: {name}"

    def test_minimal_adapter_reset_returns_obs_and_info(self) -> None:
        adapter = MinimalEnvAdapter()
        obs, info = adapter.reset(seed=42)
        assert isinstance(obs, dict)
        assert isinstance(info, dict)
        assert info["seed"] == 42

    def test_minimal_adapter_step_returns_five_tuple(self) -> None:
        adapter = MinimalEnvAdapter()
        action = np.zeros(7, dtype=np.float32)
        obs, reward, terminated, truncated, info = adapter.step(action)
        assert isinstance(obs, dict)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)

    def test_minimal_adapter_properties(self) -> None:
        adapter = MinimalEnvAdapter()
        assert adapter.obs_space_keys == ["state"]
        assert adapter.action_dim == 7
        assert adapter.task_description == "do the thing"

    def test_minimal_adapter_close(self) -> None:
        adapter = MinimalEnvAdapter()
        # close() must not raise on a fresh adapter.
        adapter.close()

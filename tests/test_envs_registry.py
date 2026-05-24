# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""Tests for EnvAdapterRegistry."""

from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from robotics_platform.envs.registry import EnvAdapterRegistry, register


class DummyEnvAdapter:
    """Minimal stand-in implementing the EnvAdapter contract."""

    def reset(self, seed: int) -> tuple[dict[str, NDArray[np.floating[Any]]], dict[str, Any]]:
        return {}, {}

    def step(
        self, action: NDArray[np.floating[Any]]
    ) -> tuple[
        dict[str, NDArray[np.floating[Any]]],
        float,
        bool,
        bool,
        dict[str, Any],
    ]:
        return {}, 0.0, False, False, {}

    def close(self) -> None:
        pass

    @property
    def obs_space_keys(self) -> list[str]:
        return []

    @property
    def action_dim(self) -> int:
        return 0

    @property
    def task_description(self) -> str:
        return ""


class TestEnvAdapterRegistry:
    def test_register_returns_class_unchanged(self) -> None:
        @register("test_unchanged_env")
        class MyAdapter(DummyEnvAdapter):
            pass

        # The decorator returns the class identity unchanged.
        assert MyAdapter.__name__ == "MyAdapter"
        assert EnvAdapterRegistry.get("test_unchanged_env") is MyAdapter

    def test_register_and_get(self) -> None:
        @register("test_dummy_env_adapter")
        class TestAdapter(DummyEnvAdapter):
            pass

        cls = EnvAdapterRegistry.get("test_dummy_env_adapter")
        assert cls is TestAdapter

    def test_get_unknown_raises_key_error_with_available_listing(self) -> None:
        with pytest.raises(KeyError, match="No env adapter registered"):
            EnvAdapterRegistry.get("nonexistent_env_adapter_xyz")

        # Error message must list available adapters for discoverability.
        with pytest.raises(KeyError, match=r"Available: \["):
            EnvAdapterRegistry.get("still_nonexistent")

    def test_list_adapters_includes_registered(self) -> None:
        @register("test_list_env_adapter")
        class TestListAdapter(DummyEnvAdapter):
            pass

        adapters = EnvAdapterRegistry.list_adapters()
        assert "test_list_env_adapter" in adapters

    def test_list_adapters_returns_list(self) -> None:
        adapters = EnvAdapterRegistry.list_adapters()
        assert isinstance(adapters, list)

    def test_register_overwrite_warns(self, caplog: pytest.LogCaptureFixture) -> None:
        """Registering the same name twice should log a warning (not raise)."""
        from loguru import logger

        # Bridge loguru to caplog so pytest can assert on warning messages.
        handler_id = logger.add(caplog.handler, format="{message}", level="WARNING")
        try:

            @register("test_overwrite_env_adapter")
            class First(DummyEnvAdapter):
                pass

            with caplog.at_level("WARNING"):

                @register("test_overwrite_env_adapter")
                class Second(DummyEnvAdapter):
                    pass

            # Second registration wins.
            cls = EnvAdapterRegistry.get("test_overwrite_env_adapter")
            assert cls is Second
            # A warning was emitted on overwrite.
            assert any("overwriting" in rec.message for rec in caplog.records)
        finally:
            logger.remove(handler_id)

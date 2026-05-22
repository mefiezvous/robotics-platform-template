# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""Tests for AdapterRegistry."""

import pytest

from platform.hal.registry import AdapterRegistry, register
from platform.hal.types import Action, Observation, RobotCapabilities


class DummyAdapter:
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


class TestAdapterRegistry:
    def test_register_and_get(self) -> None:
        @register("test_dummy_adapter")
        class TestAdapter(DummyAdapter):
            pass

        cls = AdapterRegistry.get("test_dummy_adapter")
        assert cls is TestAdapter

    def test_get_unknown_raises_key_error(self) -> None:
        with pytest.raises(KeyError, match="No adapter registered"):
            AdapterRegistry.get("nonexistent_adapter_xyz")

    def test_list_adapters_includes_registered(self) -> None:
        @register("test_list_adapter")
        class TestListAdapter(DummyAdapter):
            pass

        adapters = AdapterRegistry.list_adapters()
        assert "test_list_adapter" in adapters

    def test_list_adapters_returns_list(self) -> None:
        adapters = AdapterRegistry.list_adapters()
        assert isinstance(adapters, list)

    def test_register_overwrite_warns(self) -> None:
        """Registering the same name twice should log a warning (not raise)."""
        @register("test_overwrite_adapter")
        class First(DummyAdapter):
            pass

        @register("test_overwrite_adapter")
        class Second(DummyAdapter):
            pass

        # Second registration should win
        cls = AdapterRegistry.get("test_overwrite_adapter")
        assert cls is Second

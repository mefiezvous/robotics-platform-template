# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""AdapterRegistry — runtime lookup of RobotInterface implementations."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from robotics_platform.hal.interfaces import RobotInterface

_REGISTRY: dict[str, type] = {}


def register(name: str) -> Callable[[type], type]:
    """Class decorator to register an adapter by name.

    Args:
        name: Unique adapter name (e.g., "sim_panda", "my_robot").

    Returns:
        The decorated class unchanged.
    """

    def decorator(cls: type) -> type:
        if name in _REGISTRY:
            logger.warning(f"AdapterRegistry: overwriting existing adapter '{name}'")
        _REGISTRY[name] = cls
        logger.debug(f"AdapterRegistry: registered '{name}' -> {cls.__name__}")
        return cls

    return decorator


class AdapterRegistry:
    """Lookup registered RobotInterface adapters by name."""

    @staticmethod
    def get(name: str) -> type[RobotInterface]:
        """Return the adapter class registered under the given name.

        Args:
            name: Adapter name as passed to @register().

        Returns:
            The adapter class.

        Raises:
            KeyError: If no adapter is registered under that name.
        """
        if name not in _REGISTRY:
            available = list(_REGISTRY.keys())
            raise KeyError(f"No adapter registered as '{name}'. Available: {available}")
        return _REGISTRY[name]

    @staticmethod
    def list_adapters() -> list[str]:
        """Return names of all registered adapters."""
        return list(_REGISTRY.keys())

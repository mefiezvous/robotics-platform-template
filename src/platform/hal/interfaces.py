# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""RobotInterface Protocol — the HAL contract."""

from typing import Protocol, runtime_checkable

from platform.hal.types import Action, Observation, RobotCapabilities


@runtime_checkable
class RobotInterface(Protocol):
    """Protocol defining the contract for all robot adapters.

    Any class implementing these methods is structurally compatible,
    regardless of inheritance. Use isinstance(obj, RobotInterface)
    to verify at runtime.
    """

    def get_capabilities(self) -> RobotCapabilities:
        """Return hardware/sim capabilities of this robot."""
        ...

    def reset(self) -> Observation:
        """Reset environment to initial state, return first observation."""
        ...

    def step(self, action: Action) -> tuple[Observation, float, bool, dict[str, object]]:
        """Apply action and return (observation, reward, done, info)."""
        ...

    def close(self) -> None:
        """Release all resources (sim handles, hardware connections)."""
        ...

    def is_safe(self, action: Action) -> bool:
        """Return True if the action is within safe operating bounds.

        Must fail-safe: when in doubt, return False.
        """
        ...

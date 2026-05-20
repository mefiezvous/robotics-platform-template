# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""Hardware Abstraction Layer — public API."""

from platform.hal.interfaces import RobotInterface
from platform.hal.registry import AdapterRegistry
from platform.hal.types import Action, Observation, RobotCapabilities

__all__ = [
    "RobotInterface",
    "Observation",
    "Action",
    "RobotCapabilities",
    "AdapterRegistry",
]

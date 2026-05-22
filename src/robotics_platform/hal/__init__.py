# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""Hardware Abstraction Layer — public API."""

from robotics_platform.hal.interfaces import RobotInterface
from robotics_platform.hal.registry import AdapterRegistry
from robotics_platform.hal.types import Action, Observation, RobotCapabilities

__all__ = [
    "RobotInterface",
    "Observation",
    "Action",
    "RobotCapabilities",
    "AdapterRegistry",
]

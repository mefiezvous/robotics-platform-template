# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""Environment adapters — public API.

EnvAdapter is the gym-style 5-tuple Protocol used to plug arbitrary
simulation or real-robot environments into training/evaluation pipelines.
Mirrors the HAL pattern but is intentionally a separate registry: the
two namespaces hold different contracts (RobotInterface vs EnvAdapter).
"""

from robotics_platform.envs.interfaces import EnvAdapter
from robotics_platform.envs.registry import EnvAdapterRegistry, register

__all__ = [
    "EnvAdapter",
    "EnvAdapterRegistry",
    "register",
]

# SPDX-FileCopyrightText: 2026 Arthur Mouraud
# SPDX-License-Identifier: Apache-2.0
"""EnvAdapter Protocol — the gym-style environment contract.

Any class implementing these methods is structurally compatible with
the training/evaluation pipelines, regardless of inheritance. The
5-tuple ``step`` signature matches the Gymnasium / MuJoCo Playground
convention (``terminated`` and ``truncated`` are returned separately).
"""

from typing import Any, Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray


@runtime_checkable
class EnvAdapter(Protocol):
    """Protocol defining the contract for all environment adapters.

    Third-party adapters (MuJoCo Playground, LIBERO, real-robot wrappers)
    implement this Protocol to be consumable by the pipeline layer.
    Use ``isinstance(obj, EnvAdapter)`` to verify at runtime.
    """

    def reset(self, seed: int) -> tuple[dict[str, NDArray[np.floating[Any]]], dict[str, Any]]:
        """Reset environment to an initial state.

        Args:
            seed: Seed for deterministic initialisation.

        Returns:
            Tuple of (observation dict, info dict).
        """
        ...

    def step(
        self, action: NDArray[np.floating[Any]]
    ) -> tuple[
        dict[str, NDArray[np.floating[Any]]],
        float,
        bool,
        bool,
        dict[str, Any],
    ]:
        """Apply an action and return the gym-style 5-tuple.

        Args:
            action: Action vector matching ``action_dim``.

        Returns:
            Tuple of (observation, reward, terminated, truncated, info).
        """
        ...

    def close(self) -> None:
        """Release all underlying resources (sim handles, sockets, ...)."""
        ...

    @property
    def obs_space_keys(self) -> list[str]:
        """Names of the keys present in the observation dict returned by ``reset``/``step``."""
        ...

    @property
    def action_dim(self) -> int:
        """Dimensionality of the action vector accepted by ``step``."""
        ...

    @property
    def task_description(self) -> str:
        """Natural-language instruction describing the task (used by LLM-conditioned policies)."""
        ...

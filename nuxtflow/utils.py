"""Helper utilities and configuration for NuxtFlow, including anti-detection settings."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Coroutine, Optional, TypeVar

T = TypeVar("T")


@dataclass
class StealthConfig:
    """
    Configuration options for anti-detection and human-like browser behavior.

    Attributes:
        enabled: If True, apply stealth measures (default: True).
        random_delays: Introduce random pauses between actions (default: True).
        min_action_delay_ms: Minimum delay in milliseconds (default: 100).
        max_action_delay_ms: Maximum delay in milliseconds (default: 3000).
        human_typing: Simulate realistic typing speed and typos (default: True).
        typing_speed_wpm: Words per minute for typing simulation (default: 65).
        typo_chance: Probability of a typo (0.0 to 1.0, default: 0.02).
        pause_chance: Probability of a longer pause during typing (0.0 to 1.0, default: 0.05).
        mouse_movement: Simulate realistic mouse movements before clicks (default: True).
        randomize_viewport: Randomize browser viewport size (default: True).
        realistic_user_agent: Use a random realistic user agent string (default: True).
        # Add more stealth options here as needed
    """

    enabled: bool = True
    random_delays: bool = True
    min_action_delay_ms: int = 100
    max_action_delay_ms: int = 3000
    human_typing: bool = True
    typing_speed_wpm: int = 65
    typo_chance: float = 0.02
    pause_chance: float = 0.05
    mouse_movement: bool = True
    randomize_viewport: bool = True
    realistic_user_agent: bool = True

    # Internal field to hold the chosen user agent if randomized
    _resolved_user_agent: Optional[str] = field(init=False, repr=False, default=None)
    _resolved_viewport: Optional[tuple[int, int]] = field(init=False, repr=False, default=None)


def merge_stealth_configs(base: StealthConfig, override: Optional[StealthConfig]) -> StealthConfig:
    """
    Merges an override StealthConfig into a base StealthConfig.

    Args:
        base: The base configuration.
        override: An optional override configuration. Only non-None fields will override.

    Returns:
        A new StealthConfig instance with merged values.
    """
    if override is None:
        return base

    merged = StealthConfig()
    for field_name, field_value in base.__dict__.items():
        if not field_name.startswith("_"): # Skip internal fields
            override_value = getattr(override, field_name, None)
            if override_value is not None:
                setattr(merged, field_name, override_value)
            else:
                setattr(merged, field_name, field_value)
    return merged


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run an async coroutine from synchronous code.
    Uses asyncio.run(); creates a new event loop.
    """
    return asyncio.run(coro)

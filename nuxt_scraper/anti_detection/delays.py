"""Human-like delay utilities for anti-detection."""

from __future__ import annotations

import asyncio
import random


async def human_delay(min_ms: int = 100, max_ms: int = 2000) -> None:
    """
    Introduces a random delay to simulate human pauses.

    Args:
        min_ms: Minimum delay in milliseconds.
        max_ms: Maximum delay in milliseconds.
    """
    delay_s = random.uniform(min_ms, max_ms) / 1000.0
    await asyncio.sleep(delay_s)

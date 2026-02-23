"""Helper utilities for NuxtFlow."""

from __future__ import annotations

import asyncio
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run an async coroutine from synchronous code.
    Uses asyncio.run(); creates a new event loop.
    """
    return asyncio.run(coro)

"""Pytest configuration and shared fixtures for NuxtFlow tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from nuxtflow.steps import NavigationStep, StepType
from nuxtflow.utils import StealthConfig


@pytest.fixture
def mock_page() -> MagicMock:
    """A mock Playwright Page with async methods."""
    page = MagicMock()
    page.wait_for_selector = AsyncMock(return_value=None)
    page.click = AsyncMock(return_value=None)
    page.fill = AsyncMock(return_value=None)
    page.select_option = AsyncMock(return_value=None)
    page.hover = AsyncMock(return_value=None)
    page.evaluate = AsyncMock(return_value=None)
    page.goto = AsyncMock(return_value=None)
    page.close = AsyncMock(return_value=None)
    page.focus = AsyncMock(return_value=None) # Added for human_type
    page.keyboard = MagicMock() # Added for human_type
    page.keyboard.press = AsyncMock(return_value=None)
    page.keyboard.type = AsyncMock(return_value=None)

    locator = MagicMock()
    locator.scroll_into_view_if_needed = AsyncMock(return_value=None)
    page.locator = MagicMock(return_value=locator)
    
    page.mouse = MagicMock() # Added for simulate_mouse_movement
    page.mouse.move = AsyncMock(return_value=None)

    return page


@pytest.fixture
def sample_nuxt_json() -> str:
    """Sample raw JSON string as would be in __NUXT_DATA__."""
    return '{"data": [{"id": 1, "name": "Item 1"}], "state": {}}'


@pytest.fixture
def click_step() -> NavigationStep:
    """A simple click step."""
    return NavigationStep.click("button.submit", timeout=3000)


@pytest.fixture
def fill_step() -> NavigationStep:
    """A fill step."""
    return NavigationStep.fill("input#search", "widgets", timeout=5000)


@pytest.fixture
def wait_step() -> NavigationStep:
    """A wait step."""
    return NavigationStep.wait("div.content-loaded", timeout=10000)


@pytest.fixture
def default_stealth_config() -> StealthConfig:
    """A default StealthConfig instance."""
    return StealthConfig()


@pytest.fixture
def disabled_stealth_config() -> StealthConfig:
    """A StealthConfig instance with stealth disabled."""
    return StealthConfig(enabled=False)


@pytest.fixture
def custom_stealth_config() -> StealthConfig:
    """A StealthConfig instance with custom values."""
    return StealthConfig(
        random_delays=False,
        human_typing=True,
        typing_speed_wpm=30,
        mouse_movement=False,
    )

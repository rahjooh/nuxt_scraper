"""Pytest configuration and shared fixtures for NuxtFlow tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from nuxtflow.steps import NavigationStep, StepType


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
    locator = MagicMock()
    locator.scroll_into_view_if_needed = AsyncMock(return_value=None)
    page.locator = MagicMock(return_value=locator)
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

"""Tests for NuxtFlow anti_detection module utilities."""

from __future__ import annotations

import asyncio
import random
from unittest.mock import AsyncMock, patch

import pytest

from nuxtflow.anti_detection.delays import human_delay
from nuxtflow.anti_detection.mouse_movement import simulate_mouse_movement
from nuxtflow.anti_detection.typing import human_type
from nuxtflow.anti_detection.user_agents import get_realistic_user_agent, REALISTIC_USER_AGENTS
from nuxtflow.anti_detection.viewports import get_random_viewport, REALISTIC_VIEWPORTS
from nuxtflow.anti_detection.stealth_scripts import STEALTH_SCRIPTS


@pytest.mark.asyncio
async def test_human_delay_introduces_random_sleep() -> None:
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with patch.object(random, "uniform", return_value=0.5): # Mock random value
            await human_delay(min_ms=100, max_ms=1000)
            mock_sleep.assert_called_once_with(0.5)
        with patch.object(random, "uniform", return_value=0.1): # Mock random value
            await human_delay(min_ms=100, max_ms=1000)
            mock_sleep.assert_called_once_with(0.1)


@pytest.mark.asyncio
async def test_simulate_mouse_movement_moves_mouse(mock_page: object) -> None:
    mock_page.locator.return_value.bounding_box.return_value = {
        "x": 100, "y": 100, "width": 50, "height": 50
    }
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        await simulate_mouse_movement(mock_page, "#target")
        mock_page.mouse.move.assert_called()
        assert mock_sleep.call_count > 0


@pytest.mark.asyncio
async def test_human_type_simulates_typing(mock_page: object) -> None:
    with patch('nuxtflow.anti_detection.typing.human_delay', new_callable=AsyncMock) as mock_delay:
        await human_type(mock_page, "#input", "test")
        mock_page.focus.assert_called_once_with("#input")
        mock_page.keyboard.press.assert_called_with('Backspace')
        mock_page.keyboard.type.assert_called()
        mock_delay.assert_called()


def test_get_realistic_user_agent_returns_from_list() -> None:
    user_agent = get_realistic_user_agent()
    assert user_agent in REALISTIC_USER_AGENTS


def test_get_random_viewport_returns_from_list() -> None:
    viewport = get_random_viewport()
    assert viewport in REALISTIC_VIEWPORTS


def test_stealth_scripts_are_list_of_strings() -> None:
    assert isinstance(STEALTH_SCRIPTS, list)
    for script in STEALTH_SCRIPTS:
        assert isinstance(script, str)
        assert "Object.defineProperty(navigator, 'webdriver'" in script or \
               "window.chrome.runtime" in script or \
               "window.navigator.permissions.query" in script or \
               "navigator.plugins" in script or \
               "console.debug" in script or \
               "WebGLRenderingContext.prototype.getParameter" in script or \
               "Element.prototype.getClientRects" in script

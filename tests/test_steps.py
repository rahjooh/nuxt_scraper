"""Tests for navigation steps and their execution."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from playwright.async_api import Page

from nuxt_scraper.exceptions import (
    DateNotFoundInCalendarError,
    NavigationStepFailed,
)
from nuxt_scraper.steps import NavigationStep, StepType, execute_step
from nuxt_scraper.utils import StealthConfig


@pytest.fixture
def mock_page() -> Page:
    """Mock Playwright Page object."""
    page = AsyncMock(spec=Page)
    # Mock common methods that steps might call
    page.click = AsyncMock()
    page.fill = AsyncMock()
    page.select_option = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.locator = MagicMock(return_value=AsyncMock())
    page.locator.return_value.click = AsyncMock()
    page.locator.return_value.fill = AsyncMock()
    page.locator.return_value.select_option = AsyncMock()
    page.locator.return_value.wait_for = AsyncMock()
    page.locator.return_value.scroll_into_view_if_needed = AsyncMock()
    page.locator.return_value.hover = AsyncMock()
    page.keyboard = AsyncMock()
    page.mouse = AsyncMock()
    return page


@pytest.fixture
def mock_anti_detection_functions() -> None:
    """Patches anti-detection functions to prevent actual delays/movements during tests."""
    with (
        patch("nuxt_scraper.anti_detection.delays.human_delay", new=AsyncMock()),
        patch("nuxt_scraper.anti_detection.mouse_movement.simulate_mouse_movement", new=AsyncMock()),
        patch("nuxt_scraper.anti_detection.typing.human_type", new=AsyncMock()),
    ):
        yield


@pytest.fixture
def stealth_config_enabled() -> StealthConfig:
    """StealthConfig with all features enabled."""
    return StealthConfig(enabled=True)


@pytest.fixture
def stealth_config_disabled() -> StealthConfig:
    """StealthConfig with all features disabled."""
    return StealthConfig(enabled=False)


# --- NavigationStep factory methods tests ---

def test_click_step_creation() -> None:
    step = NavigationStep.click("#btn")
    assert step.type == StepType.CLICK
    assert step.selector == "#btn"
    assert step.timeout == 5000
    assert step.wait_after_selector is None


def test_fill_step_creation() -> None:
    step = NavigationStep.fill("#input", "test_value")
    assert step.type == StepType.FILL
    assert step.selector == "#input"
    assert step.value == "test_value"


def test_select_step_creation() -> None:
    step = NavigationStep.select("select#dropdown", "option_value")
    assert step.type == StepType.SELECT
    assert step.selector == "select#dropdown"
    assert step.value == "option_value"


def test_wait_step_creation() -> None:
    step = NavigationStep.wait(".content-loaded")
    assert step.type == StepType.WAIT
    assert step.selector == ".content-loaded"
    assert step.timeout == 10000


def test_scroll_step_creation() -> None:
    step = NavigationStep.scroll("footer")
    assert step.type == StepType.SCROLL
    assert step.selector == "footer"


def test_hover_step_creation() -> None:
    step = NavigationStep.hover("#menu-item")
    assert step.type == StepType.HOVER
    assert step.selector == "#menu-item"


def test_select_date_step_creation() -> None:
    step = NavigationStep.select_date(
        target_date="2026-03-15",
        calendar_selector="div.calendar",
        prev_month_selector="button.prev",
        next_month_selector="button.next",
        month_year_display_selector="div.month-year",
        date_cell_selector="div.day",
        view_results_selector="button.view-results",
        timeout=15000,
        wait_after_selector=".results-loaded",
    )
    assert step.type == StepType.SELECT_DATE
    assert step.target_date == "2026-03-15"
    assert step.calendar_selector == "div.calendar"
    assert step.prev_month_selector == "button.prev"
    assert step.next_month_selector == "button.next"
    assert step.month_year_display_selector == "div.month-year"
    assert step.date_cell_selector == "div.day"
    assert step.view_results_selector == "button.view-results"
    assert step.timeout == 15000
    assert step.wait_after_selector == ".results-loaded"


# --- execute_step tests ---

async def test_execute_click_step(mock_page: Page) -> None:
    step = NavigationStep.click("#button")
    await execute_step(mock_page, step)
    mock_page.wait_for_selector.assert_awaited_with("#button", timeout=5000)
    mock_page.click.assert_awaited_with("#button", timeout=5000)


async def test_execute_fill_step(mock_page: Page) -> None:
    step = NavigationStep.fill("#input", "test_value")
    await execute_step(mock_page, step)
    mock_page.wait_for_selector.assert_awaited_with("#input", timeout=5000)
    mock_page.fill.assert_awaited_with("#input", "test_value", timeout=5000)


async def test_execute_select_step(mock_page: Page) -> None:
    step = NavigationStep.select("select#dropdown", "option_value")
    await execute_step(mock_page, step)
    mock_page.wait_for_selector.assert_awaited_with("select#dropdown", timeout=5000)
    mock_page.select_option.assert_awaited_with(
        "select#dropdown", "option_value", timeout=5000
    )


async def test_execute_wait_step(mock_page: Page) -> None:
    step = NavigationStep.wait(".content-loaded")
    await execute_step(mock_page, step)
    mock_page.wait_for_selector.assert_awaited_with(
        ".content-loaded", timeout=10000
    )
    # No other actions should be performed for a WAIT step
    mock_page.click.assert_not_awaited()
    mock_page.fill.assert_not_awaited()


async def test_execute_scroll_step(mock_page: Page) -> None:
    step = NavigationStep.scroll("footer")
    await execute_step(mock_page, step)
    mock_page.wait_for_selector.assert_awaited_with("footer", timeout=5000)
    mock_page.locator.return_value.scroll_into_view_if_needed.assert_awaited_with(
        timeout=5000
    )


async def test_execute_hover_step(mock_page: Page) -> None:
    step = NavigationStep.hover("#menu-item")
    await execute_step(mock_page, step)
    mock_page.wait_for_selector.assert_awaited_with("#menu-item", timeout=5000)
    mock_page.hover.assert_awaited_with("#menu-item", timeout=5000)


async def test_execute_step_with_wait_after_selector(mock_page: Page) -> None:
    step = NavigationStep.click("#btn", wait_after_selector=".modal-open")
    await execute_step(mock_page, step)
    mock_page.click.assert_awaited_once()
    assert mock_page.wait_for_selector.call_count == 2
    mock_page.wait_for_selector.assert_awaited_with(".modal-open", timeout=5000)


async def test_execute_step_raises_navigation_step_failed(mock_page: Page) -> None:
    step = NavigationStep.click("#non-existent")
    mock_page.wait_for_selector.side_effect = TimeoutError("Element not found")
    with pytest.raises(NavigationStepFailed) as exc_info:
        await execute_step(mock_page, step)
    assert isinstance(exc_info.value.original_error, TimeoutError)


# --- Anti-detection integration tests ---

async def test_execute_step_applies_human_delay(mock_page: Page, mock_anti_detection_functions: None) -> None:
    step = NavigationStep.click("#button")
    config = StealthConfig(enabled=True, random_delays=True)
    await execute_step(mock_page, step, stealth_config=config)
    from nuxt_scraper.anti_detection.delays import human_delay
    assert human_delay.call_count == 2 # Before and after action


async def test_execute_step_applies_mouse_movement(mock_page: Page, mock_anti_detection_functions: None) -> None:
    step = NavigationStep.click("#button")
    config = StealthConfig(enabled=True, mouse_movement=True)
    await execute_step(mock_page, step, stealth_config=config)
    from nuxt_scraper.anti_detection.mouse_movement import simulate_mouse_movement
    simulate_mouse_movement.assert_awaited_with(mock_page, "#button")


async def test_execute_step_applies_human_typing(mock_page: Page, mock_anti_detection_functions: None) -> None:
    step = NavigationStep.fill("#input", "text")
    config = StealthConfig(enabled=True, human_typing=True)
    await execute_step(mock_page, step, stealth_config=config)
    from nuxt_scraper.anti_detection.typing import human_type
    human_type.assert_awaited_with(mock_page, "#input", "text", wpm=config.typing_speed_wpm, typo_chance=config.typo_chance, pause_chance=config.pause_chance)
    mock_page.fill.assert_not_awaited()


# --- SELECT_DATE specific tests ---

@patch("nuxt_scraper.steps.human_delay", new_callable=AsyncMock)
async def test_handle_select_date_current_month(
    mock_human_delay: AsyncMock, mock_page: Page, stealth_config_enabled: StealthConfig
) -> None:
    target_date = "2026-02-23"
    step = NavigationStep.select_date(
        target_date=target_date,
        calendar_selector="div.calendar",
        prev_month_selector="button.prev",
        next_month_selector="button.next",
        month_year_display_selector="div.month-year",
        date_cell_selector="div.day",
    )

    # Mock the current month/year display to match target
    mock_page.locator.return_value.text_content.side_effect = ["Feb 2026"]
    mock_page.locator.return_value.wait_for.return_value = None # For date cell locator
    mock_page.locator.return_value.click.return_value = None # For date cell click

    await execute_step(mock_page, step, stealth_config=stealth_config_enabled)

    mock_page.wait_for_selector.assert_awaited_with(step.calendar_selector, timeout=step.timeout)
    mock_page.locator.assert_any_call(step.month_year_display_selector)
    mock_page.locator.assert_any_call("div.day:has-text(\"23\")")
    mock_page.locator.return_value.click.assert_awaited_once()
    mock_page.click.assert_not_awaited() # ensure direct page.click not used for nav buttons
    assert mock_human_delay.call_count >= 1 # Initial delay + delay for calendar visibility

@patch("nuxt_scraper.steps.human_delay", new_callable=AsyncMock)
@patch("nuxt_scraper.anti_detection.mouse_movement.simulate_mouse_movement", new_callable=AsyncMock)
async def test_handle_select_date_navigate_forward(
    mock_simulate_mouse_movement: AsyncMock, mock_human_delay: AsyncMock, mock_page: Page, stealth_config_enabled: StealthConfig
) -> None:
    target_date = "2026-04-10"
    step = NavigationStep.select_date(
        target_date=target_date,
        calendar_selector="div.calendar",
        prev_month_selector="button.prev",
        next_month_selector="button.next",
        month_year_display_selector="div.month-year",
        date_cell_selector="div.day",
    )

    # Mock text_content to simulate navigating forward
    mock_page.locator.return_value.text_content.side_effect = [
        "Feb 2026", # Initial
        "Mar 2026", # After first next click
        "Apr 2026", # After second next click
    ]
    mock_page.locator.return_value.wait_for.return_value = None
    mock_page.locator.return_value.click.return_value = None

    await execute_step(mock_page, step, stealth_config=stealth_config_enabled)

    mock_page.wait_for_selector.assert_awaited_with(step.calendar_selector, timeout=step.timeout)
    mock_page.click.assert_awaited_with(step.next_month_selector) # Should click next twice
    assert mock_page.click.call_count == 2
    mock_page.locator.assert_any_call("div.day:has-text(\"10\")")
    mock_page.locator.return_value.click.assert_awaited_once()
    assert mock_human_delay.call_count >= 3 # Initial, after each nav, and before final click
    mock_simulate_mouse_movement.assert_awaited_with(mock_page, "div.day:has-text(\"10\")")

@patch("nuxt_scraper.steps.human_delay", new_callable=AsyncMock)
@patch("nuxt_scraper.anti_detection.mouse_movement.simulate_mouse_movement", new_callable=AsyncMock)
async def test_handle_select_date_navigate_backward(
    mock_simulate_mouse_movement: AsyncMock, mock_human_delay: AsyncMock, mock_page: Page, stealth_config_enabled: StealthConfig
) -> None:
    target_date = "2025-12-05"
    step = NavigationStep.select_date(
        target_date=target_date,
        calendar_selector="div.calendar",
        prev_month_selector="button.prev",
        next_month_selector="button.next",
        month_year_display_selector="div.month-year",
        date_cell_selector="div.day",
    )

    # Mock text_content to simulate navigating backward
    mock_page.locator.return_value.text_content.side_effect = [
        "Feb 2026", # Initial
        "Jan 2026", # After first prev click
        "Dec 2025", # After second prev click
    ]
    mock_page.locator.return_value.wait_for.return_value = None
    mock_page.locator.return_value.click.return_value = None

    await execute_step(mock_page, step, stealth_config=stealth_config_enabled)

    mock_page.wait_for_selector.assert_awaited_with(step.calendar_selector, timeout=step.timeout)
    mock_page.click.assert_awaited_with(step.prev_month_selector) # Should click prev twice
    assert mock_page.click.call_count == 2
    mock_page.locator.assert_any_call("div.day:has-text(\"5\")")
    mock_page.locator.return_value.click.assert_awaited_once()
    assert mock_human_delay.call_count >= 3 # Initial, after each nav, and before final click
    mock_simulate_mouse_movement.assert_awaited_with(mock_page, "div.day:has-text(\"5\")")


async def test_handle_select_date_view_results_button(mock_page: Page, stealth_config_enabled: StealthConfig) -> None:
    target_date = "2026-02-23"
    step = NavigationStep.select_date(
        target_date=target_date,
        calendar_selector="div.calendar",
        prev_month_selector="button.prev",
        next_month_selector="button.next",
        month_year_display_selector="div.month-year",
        date_cell_selector="div.day",
        view_results_selector="button.view-results",
    )

    mock_page.locator.return_value.text_content.side_effect = ["Feb 2026"]
    mock_page.locator.return_value.wait_for.return_value = None
    mock_page.locator.return_value.click.return_value = None

    await execute_step(mock_page, step, stealth_config=stealth_config_enabled)

    mock_page.click.assert_awaited_with(step.view_results_selector, timeout=step.timeout) # After date click


async def test_handle_select_date_raises_date_not_found(mock_page: Page, stealth_config_enabled: StealthConfig) -> None:
    target_date = "2028-01-01"
    step = NavigationStep.select_date(
        target_date=target_date,
        calendar_selector="div.calendar",
        prev_month_selector="button.prev",
        next_month_selector="button.next",
        month_year_display_selector="div.month-year",
        date_cell_selector="div.day",
    )

    # Mock text_content to loop indefinitely (or up to limit)
    mock_page.locator.return_value.text_content.side_effect = ["Feb 2026"] * 30 # Will never reach target

    with pytest.raises(DateNotFoundInCalendarError) as exc_info:
        await execute_step(mock_page, step, stealth_config=stealth_config_enabled)
    assert target_date in str(exc_info.value)


async def test_handle_select_date_day_not_clickable(mock_page: Page, stealth_config_enabled: StealthConfig) -> None:
    target_date = "2026-02-23"
    step = NavigationStep.select_date(
        target_date=target_date,
        calendar_selector="div.calendar",
        prev_month_selector="button.prev",
        next_month_selector="button.next",
        month_year_display_selector="div.month-year",
        date_cell_selector="div.day",
    )

    mock_page.locator.return_value.text_content.side_effect = ["Feb 2026"]
    mock_page.locator.return_value.wait_for.side_effect = TimeoutError("Day not visible")

    with pytest.raises(DateNotFoundInCalendarError) as exc_info:
        await execute_step(mock_page, step, stealth_config=stealth_config_enabled)
    assert f"Failed to click day {23}" in str(exc_info.value)

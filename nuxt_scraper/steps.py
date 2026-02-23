"""Navigation step definitions and step executor for Nuxt Scraper."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, TYPE_CHECKING

from nuxt_scraper.anti_detection.delays import human_delay
from nuxt_scraper.anti_detection.mouse_movement import simulate_mouse_movement
from nuxt_scraper.anti_detection.typing import human_type
from nuxt_scraper.exceptions import DateNotFoundInCalendarError, NavigationStepFailed
from nuxt_scraper.utils import StealthConfig

if TYPE_CHECKING:
    from playwright.async_api import Page

logger = logging.getLogger(__name__)


class StepType(str, Enum):
    """Supported navigation step types."""

    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    WAIT = "wait"
    SCROLL = "scroll"
    HOVER = "hover"
    SELECT_DATE = "select_date"


@dataclass
class NavigationStep:
    """
    A single navigation step (click, fill, wait, etc.).

    Attributes:
        type: The kind of action to perform.
        selector: CSS selector (or other selector) for the target element.
        value: Optional value for fill/select steps.
        timeout: Max time to wait for the element/action (milliseconds).
        wait_after_selector: Optional selector to wait for after the action.
        target_date: Target date for SELECT_DATE step (format: YYYY-MM-DD).
        calendar_selector: Selector for the calendar pop-up.
        prev_month_selector: Selector for the 'previous month' button.
        next_month_selector: Selector for the 'next month' button.
        month_year_display_selector: Selector for the current month/year display.
        date_cell_selector: Common selector for individual date cells.
        view_results_selector: Selector for the 'View Results' button after date selection.
    """

    type: StepType
    selector: Optional[str] = None
    value: Optional[str] = None
    timeout: int = 5000
    wait_after_selector: Optional[str] = None

    # Date selection specific attributes
    target_date: Optional[str] = None  # Format: YYYY-MM-DD
    calendar_selector: Optional[str] = None
    prev_month_selector: Optional[str] = None
    next_month_selector: Optional[str] = None
    month_year_display_selector: Optional[str] = None
    date_cell_selector: Optional[str] = None
    view_results_selector: Optional[str] = None

    @classmethod
    def click(
        cls,
        selector: str,
        timeout: int = 5000,
        wait_after_selector: Optional[str] = None,
    ) -> NavigationStep:
        """Create a click step."""
        return cls(
            type=StepType.CLICK,
            selector=selector,
            timeout=timeout,
            wait_after_selector=wait_after_selector,
        )

    @classmethod
    def fill(
        cls,
        selector: str,
        value: str,
        timeout: int = 5000,
        wait_after_selector: Optional[str] = None,
    ) -> NavigationStep:
        """Create a fill step (input/textarea)."""
        return cls(
            type=StepType.FILL,
            selector=selector,
            value=value,
            timeout=timeout,
            wait_after_selector=wait_after_selector,
        )

    @classmethod
    def select(
        cls,
        selector: str,
        value: str,
        timeout: int = 5000,
        wait_after_selector: Optional[str] = None,
    ) -> NavigationStep:
        """Create a select step (dropdown)."""
        return cls(
            type=StepType.SELECT,
            selector=selector,
            value=value,
            timeout=timeout,
            wait_after_selector=wait_after_selector,
        )

    @classmethod
    def wait(
        cls,
        selector: str,
        timeout: int = 10000,
        wait_after_selector: Optional[str] = None,
    ) -> NavigationStep:
        """Create a wait step (wait for selector to be visible)."""
        return cls(
            type=StepType.WAIT,
            selector=selector,
            timeout=timeout,
            wait_after_selector=wait_after_selector,
        )

    @classmethod
    def scroll(
        cls,
        selector: str,
        timeout: int = 5000,
        wait_after_selector: Optional[str] = None,
    ) -> NavigationStep:
        """Create a scroll step (scroll element into view)."""
        return cls(
            type=StepType.SCROLL,
            selector=selector,
            timeout=timeout,
            wait_after_selector=wait_after_selector,
        )

    @classmethod
    def hover(
        cls,
        selector: str,
        timeout: int = 5000,
        wait_after_selector: Optional[str] = None,
    ) -> NavigationStep:
        """Create a hover step."""
        return cls(
            type=StepType.HOVER,
            selector=selector,
            timeout=timeout,
            wait_after_selector=wait_after_selector,
        )

    @classmethod
    def select_date(
        cls,
        target_date: str,
        calendar_selector: str,
        prev_month_selector: str,
        next_month_selector: str,
        month_year_display_selector: str,
        date_cell_selector: str,
        view_results_selector: Optional[str] = None,
        timeout: int = 15000,
        wait_after_selector: Optional[str] = None,
    ) -> NavigationStep:
        """Create a step to select a specific date from a calendar pop-up."""
        return cls(
            type=StepType.SELECT_DATE,
            target_date=target_date,
            calendar_selector=calendar_selector,
            prev_month_selector=prev_month_selector,
            next_month_selector=next_month_selector,
            month_year_display_selector=month_year_display_selector,
            date_cell_selector=date_cell_selector,
            view_results_selector=view_results_selector,
            timeout=timeout,
            wait_after_selector=wait_after_selector,
        )


async def _handle_select_date(
    page: Page, step: NavigationStep, stealth_config: StealthConfig
) -> None:
    """
    Handles the selection of a date from a calendar pop-up.
    """
    if not all([
        step.target_date,
        step.calendar_selector,
        step.prev_month_selector,
        step.next_month_selector,
        step.month_year_display_selector,
        step.date_cell_selector,
    ]):
        raise NavigationStepFailed(step, ValueError("Missing required date selection parameters"))

    target_datetime = datetime.strptime(step.target_date, "%Y-%m-%d")
    current_month_year_selector = step.month_year_display_selector
    prev_button_selector = step.prev_month_selector
    next_button_selector = step.next_month_selector
    date_cell_base_selector = step.date_cell_selector
    
    # Ensure calendar is visible
    await page.wait_for_selector(step.calendar_selector, timeout=step.timeout)
    if stealth_config.enabled and stealth_config.random_delays:
        await human_delay(config.min_action_delay_ms, config.max_action_delay_ms)

    # Iterate to find the correct month
    for _ in range(24): # Max 24 months (2 years) to prevent infinite loop
        current_month_year_text = await page.locator(current_month_year_selector).text_content()
        if not current_month_year_text:
            raise NavigationStepFailed(step, ValueError("Could not read current month/year display"))

        current_display_date = datetime.strptime(current_month_year_text.strip(), "%b %Y")

        if (
            current_display_date.year == target_datetime.year
            and current_display_date.month == target_datetime.month
        ):
            break # Correct month found

        if target_datetime < current_display_date:
            await page.click(prev_button_selector)
        else:
            await page.click(next_button_selector)
        
        if stealth_config.enabled and stealth_config.random_delays:
            await human_delay(
                stealth_config.min_action_delay_ms // 2,
                stealth_config.max_action_delay_ms // 2,
            )

    else: # Loop exhausted, date not found after 24 attempts
        raise DateNotFoundInCalendarError(step.target_date, "Target month not reached in calendar")

    # Month is now correct, find and click the day
    target_day_selector = f"{date_cell_base_selector}:has-text(\"{target_datetime.day}\")"
    day_locator = page.locator(target_day_selector)
    
    try:
        await day_locator.wait_for(state="visible", timeout=step.timeout)
        if stealth_config.enabled and stealth_config.mouse_movement:
            await simulate_mouse_movement(page, target_day_selector)
            await human_delay(50, 200)
        await day_locator.click()
    except Exception as e:
        raise DateNotFoundInCalendarError(step.target_date, f"Failed to click day {target_datetime.day}: {e!s}") from e

    # Optionally click View Results button
    if step.view_results_selector:
        if stealth_config.enabled and stealth_config.random_delays:
            await human_delay(
                stealth_config.min_action_delay_ms, stealth_config.max_action_delay_ms
            )
        await page.click(step.view_results_selector, timeout=step.timeout)


async def execute_step(page: Page, step: NavigationStep, stealth_config: Optional[StealthConfig] = None) -> None:
    """
    Execute one navigation step on a Playwright page with optional anti-detection.

    Args:
        page: Playwright Page object.
        step: The step to execute.
        stealth_config: Optional configuration for human-like behavior.

    Raises:
        NavigationStepFailed: When the step fails.
    """
    config = stealth_config or StealthConfig()  # Use default if not provided

    try:
        # Initial random delay before action if enabled
        if config.enabled and config.random_delays:
            await human_delay(config.min_action_delay_ms, config.max_action_delay_ms)

        if step.type == StepType.SELECT_DATE:
            await _handle_select_date(page, step, config)
            # No need for general wait_for_selector here, _handle_select_date handles it
        else:
            # For other step types, we still need to wait for the selector to be present
            # before attempting to interact with it, unless the selector is optional.
            # We check if step.selector is not None to avoid waiting for a non-existent selector
            # in steps like WAIT where the selector is purely for waiting.
            if step.selector:
                await page.wait_for_selector(step.selector, timeout=step.timeout)

            if step.type == StepType.CLICK:
                if config.enabled and config.mouse_movement:
                    await simulate_mouse_movement(page, step.selector)
                    await human_delay(50, 200)  # Short pause after mouse movement
                await page.click(step.selector, timeout=step.timeout)

            elif step.type == StepType.FILL:
                if config.enabled and config.human_typing:
                    await human_type(
                        page,
                        step.selector,
                        step.value or "",
                        wpm=config.typing_speed_wpm,
                        typo_chance=config.typo_chance,
                        pause_chance=config.pause_chance,
                    )
                else:
                    await page.fill(step.selector, step.value or "", timeout=step.timeout)

            elif step.type == StepType.SELECT:
                await page.select_option(step.selector, step.value or "", timeout=step.timeout)

            elif step.type == StepType.WAIT:
                # Already waited for selector at the start, just ensuring it's still there
                pass

            elif step.type == StepType.SCROLL:
                # Scroll into view, potentially triggers lazy loading
                await page.locator(step.selector).scroll_into_view_if_needed(timeout=step.timeout)

            elif step.type == StepType.HOVER:
                await page.hover(step.selector, timeout=step.timeout)

            else:
                raise NavigationStepFailed(
                    step, ValueError(f"Unknown step type: {step.type}")
                )

        # Optional wait after action if specified in the step
        if step.wait_after_selector:
            await page.wait_for_selector(step.wait_after_selector, timeout=step.timeout)

        # Final random delay after action if enabled
        if config.enabled and config.random_delays:
            await human_delay(config.min_action_delay_ms, config.max_action_delay_ms)

    except Exception as e:
        raise NavigationStepFailed(step, e) from e


async def execute_steps(
    page: Page, steps: List[NavigationStep], stealth_config: Optional[StealthConfig] = None
) -> None:
    """
    Execute a list of navigation steps in order with optional anti-detection measures.

    Args:
        page: Playwright Page object.
        steps: List of steps to execute.
        stealth_config: Optional configuration for human-like behavior.
    """
    for step in steps:
        logger.debug("Executing step: %s on %s", step.type.value, step.selector)
        await execute_step(page, step, stealth_config)

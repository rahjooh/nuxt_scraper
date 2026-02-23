"""Navigation step definitions and step executor for NuxtFlow."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, TYPE_CHECKING

from nuxtflow.anti_detection.delays import human_delay
from nuxtflow.anti_detection.mouse_movement import simulate_mouse_movement
from nuxtflow.anti_detection.typing import human_type
from nuxtflow.exceptions import NavigationStepFailed

if TYPE_CHECKING:
    from playwright.async_api import Page
    from nuxtflow.utils import StealthConfig

logger = logging.getLogger(__name__)


class StepType(str, Enum):
    """Supported navigation step types."""

    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    WAIT = "wait"
    SCROLL = "scroll"
    HOVER = "hover"


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
    """

    type: StepType
    selector: str
    value: Optional[str] = None
    timeout: int = 5000
    wait_after_selector: Optional[str] = None

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


async def execute_step(page: Page, step: NavigationStep, stealth_config: Optional[StealthConfig] = None) -> None:
    """
    Execute a single navigation step on a Playwright page with optional anti-detection measures.

    Args:
        page: Playwright Page object.
        step: The step to execute.
        stealth_config: Optional configuration for human-like behavior.

    Raises:
        NavigationStepFailed: When the step fails.
    """
    config = stealth_config or StealthConfig() # Use default if not provided

    try:
        # Initial random delay before action if enabled
        if config.enabled and config.random_delays:
            await human_delay(config.min_action_delay_ms, config.max_action_delay_ms)

        await page.wait_for_selector(step.selector, timeout=step.timeout)

        if step.type == StepType.CLICK:
            if config.enabled and config.mouse_movement:
                await simulate_mouse_movement(page, step.selector)
                await human_delay(50, 200) # Short pause after mouse movement
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
            raise NavigationStepFailed(step, ValueError(f"Unknown step type: {step.type}"))

        # Optional wait after action if specified in the step
        if step.wait_after_selector:
            await page.wait_for_selector(step.wait_after_selector, timeout=step.timeout)

        # Final random delay after action if enabled
        if config.enabled and config.random_delays:
            await human_delay(config.min_action_delay_ms, config.max_action_delay_ms)

    except Exception as e:
        raise NavigationStepFailed(step, e) from e


async def execute_steps(page: Page, steps: List[NavigationStep], stealth_config: Optional[StealthConfig] = None) -> None:
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

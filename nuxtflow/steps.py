"""Navigation step definitions and step executor for NuxtFlow."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional

from nuxtflow.exceptions import NavigationStepFailed

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


async def execute_step(page: Any, step: NavigationStep) -> None:
    """
    Execute a single navigation step on a Playwright page.

    Args:
        page: Playwright Page object.
        step: The step to execute.

    Raises:
        NavigationStepFailed: When the step fails.
    """
    try:
        if step.type == StepType.CLICK:
            await page.wait_for_selector(step.selector, timeout=step.timeout)
            await page.click(step.selector, timeout=step.timeout)
        elif step.type == StepType.FILL:
            await page.wait_for_selector(step.selector, timeout=step.timeout)
            await page.fill(step.selector, step.value or "", timeout=step.timeout)
        elif step.type == StepType.SELECT:
            await page.wait_for_selector(step.selector, timeout=step.timeout)
            await page.select_option(step.selector, step.value or "", timeout=step.timeout)
        elif step.type == StepType.WAIT:
            await page.wait_for_selector(step.selector, timeout=step.timeout)
        elif step.type == StepType.SCROLL:
            await page.wait_for_selector(step.selector, timeout=step.timeout)
            await page.locator(step.selector).scroll_into_view_if_needed(timeout=step.timeout)
        elif step.type == StepType.HOVER:
            await page.wait_for_selector(step.selector, timeout=step.timeout)
            await page.hover(step.selector, timeout=step.timeout)
        else:
            raise NavigationStepFailed(step, ValueError(f"Unknown step type: {step.type}"))

        if step.wait_after_selector:
            await page.wait_for_selector(step.wait_after_selector, timeout=step.timeout)
    except Exception as e:
        raise NavigationStepFailed(step, e) from e


async def execute_steps(page: Any, steps: List[NavigationStep]) -> None:
    """
    Execute a list of navigation steps in order.

    Args:
        page: Playwright Page object.
        steps: List of steps to execute.
    """
    for step in steps:
        logger.debug("Executing step: %s on %s", step.type.value, step.selector)
        await execute_step(page, step)

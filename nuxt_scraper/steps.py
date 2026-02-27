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
    DISMISS_POPUPS = "dismiss_popups"


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

    @classmethod
    def dismiss_popups(
        cls,
        timeout: int = 5000,
        wait_after_selector: Optional[str] = None,
    ) -> NavigationStep:
        """Create a step to dismiss common advertisement popups and modals."""
        return cls(
            type=StepType.DISMISS_POPUPS,
            timeout=timeout,
            wait_after_selector=wait_after_selector,
        )


async def _handle_select_date(
    page: Page, step: NavigationStep, stealth_config: StealthConfig
) -> None:
    """
    Handles the selection of a date from a calendar pop-up.
    Uses robust selector fallbacks and month parsing similar to legacy implementations.
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

    # Parse target date
    target_datetime = datetime.strptime(step.target_date, "%Y-%m-%d")
    ty, tm, td = target_datetime.year, target_datetime.month, target_datetime.day
    day_str = str(td)
    
    # Month names for comparison (full and abbreviated)
    mn_full = ["", "January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", "December"]
    mn_abbrev = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    tm_full, tm_abbrev = mn_full[tm], mn_abbrev[tm]
    
    # Split selectors into fallback lists (support comma-separated selectors)
    month_year_selectors = [s.strip() for s in step.month_year_display_selector.split(",")]
    prev_selectors = [s.strip() for s in step.prev_month_selector.split(",")]
    next_selectors = [s.strip() for s in step.next_month_selector.split(",")]
    
    # Try to find calendar - use visibility check instead of strict wait_for_selector
    calendar_found = False
    for sel in [s.strip() for s in step.calendar_selector.split(",")]:
        try:
            locator = page.locator(sel).first
            if await locator.is_visible(timeout=500):
                calendar_found = True
                break
        except Exception:
            continue
    
    if not calendar_found:
        raise NavigationStepFailed(step, ValueError("Calendar not visible"))
    
    if stealth_config.enabled and stealth_config.random_delays:
        await human_delay(stealth_config.min_action_delay_ms, stealth_config.max_action_delay_ms)

    # Navigate to correct month/year (up to 120 attempts like legacy code)
    for attempt in range(120):
        cur_m, cur_y = "", 0
        
        # Try multiple selectors for month/year display
        for sel in month_year_selectors:
            try:
                locator = page.locator(sel).first
                if await locator.is_visible(timeout=500):
                    text = await locator.text_content()
                    if text:
                        parts = text.strip().split()
                        if len(parts) >= 2:
                            cur_m = parts[0]
                            try:
                                cur_y = int(parts[-1])
                            except ValueError:
                                continue
                            break
            except Exception:
                continue
        
        if not cur_m or not cur_y:
            # Could not read month/year, try to continue
            if attempt < 5:  # Give it a few tries
                await human_delay(200, 500)
                continue
            else:
                raise NavigationStepFailed(step, ValueError("Could not read current month/year display"))
        
        # Check if we're at the target month
        if cur_m in (tm_full, tm_abbrev) and cur_y == ty:
            break  # Correct month found
        
        # Calculate which direction to navigate
        cur_num = next((i for i, n in enumerate(mn_full) if n == cur_m), 0) or \
                  next((i for i, n in enumerate(mn_abbrev) if n == cur_m), 0)
        if cur_num == 0:
            raise NavigationStepFailed(step, ValueError(f"Could not parse month name: {cur_m}"))
        
        cur_tot = cur_y * 12 + cur_num
        tgt_tot = ty * 12 + tm
        
        # Click prev or next button with fallback selectors
        button_clicked = False
        button_selectors = prev_selectors if cur_tot > tgt_tot else next_selectors
        
        for sel in button_selectors:
            try:
                locator = page.locator(sel).first
                if await locator.is_visible(timeout=500):
                    await locator.click(force=True)
                    button_clicked = True
                    break
            except Exception:
                continue
        
        if not button_clicked:
            raise NavigationStepFailed(step, ValueError("Could not find or click prev/next button"))
        
        # Small delay after navigation
        if stealth_config.enabled and stealth_config.random_delays:
            await human_delay(200, 500)
        else:
            await human_delay(200, 500)  # Always add small delay for calendar updates

    else:  # Loop exhausted, date not found after 120 attempts
        raise DateNotFoundInCalendarError(step.target_date, "Target month not reached in calendar")

    # Month is now correct, find and click the day
    # Try multiple selector strategies like legacy code
    day_clicked = False
    
    # Build day selectors - try exact text match first, then has-text
    day_selectors = [
        f'span.cell.day:text-is("{day_str}")',
        f'[class*="day"]:has-text("{day_str}")'
    ]
    
    # Also try with the base selector if it's different
    if step.date_cell_selector not in day_selectors[0] and step.date_cell_selector not in day_selectors[1]:
        day_selectors.append(f'{step.date_cell_selector}:has-text("{day_str}")')
    
    for selector in day_selectors:
        try:
            cells = page.locator(selector)
            count = await cells.count()
            for i in range(count):
                cell = cells.nth(i)
                try:
                    txt = await cell.text_content()
                    if txt and txt.strip() == day_str and await cell.is_visible(timeout=500):
                        if stealth_config.enabled and stealth_config.mouse_movement:
                            # Get selector for mouse movement simulation
                            cell_selector = await cell.evaluate("el => el.className || el.tagName")
                            if cell_selector:
                                await simulate_mouse_movement(page, selector)
                                await human_delay(50, 200)
                        await cell.click(force=True)
                        day_clicked = True
                        break
                except Exception:
                    continue
            if day_clicked:
                break
        except Exception:
            continue
    
    if not day_clicked:
        raise DateNotFoundInCalendarError(step.target_date, f"Failed to find or click day {day_str}")
    
    # Small delay after day click
    await human_delay(500, 1000)

    # Optionally click View Results button
    if step.view_results_selector:
        if stealth_config.enabled and stealth_config.random_delays:
            await human_delay(
                stealth_config.min_action_delay_ms, stealth_config.max_action_delay_ms
            )
        else:
            await human_delay(1000, 2000)
        
        # Try to find and click view results button
        view_results_found = False
        for sel in [s.strip() for s in step.view_results_selector.split(",")]:
            try:
                locator = page.locator(sel).first
                if await locator.is_visible(timeout=2000):
                    await locator.click(force=True, timeout=step.timeout)
                    view_results_found = True
                    break
            except Exception:
                continue
        
        if view_results_found:
            # Wait for page to load after clicking view results
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            await human_delay(2000, 3000)


async def _handle_dismiss_popups(
    page: Page, step: NavigationStep, stealth_config: StealthConfig
) -> None:
    """
    Handles dismissing common advertisement popups and modals.
    """
    popup_selectors = [
        'button[aria-label="Close"]', 'button[aria-label="close"]', '.close-button', '.popup-close',
        '.modal-close', '[data-dismiss="modal"]', '.ad-close', '.advertisement-close',
        'button:has-text("×")', 'button:has-text("✕")', 'span:has-text("×")', 'span:has-text("✕")',
        '[class*="close"]:visible', '[id*="close"]:visible', 'button:has-text("Skip")',
        'button:has-text("Skip Ad")', 'button:has-text("Continue")', 'button:has-text("No Thanks")',
        '.overlay', '.modal-backdrop',
    ]
    
    dismissed_count = 0
    for selector in popup_selectors:
        try:
            element = page.locator(selector).first
            if await element.is_visible(timeout=1000):
                await element.click(timeout=2000)
                dismissed_count += 1
                if stealth_config.enabled and stealth_config.random_delays:
                    await human_delay(500, 1500)
        except Exception:
            continue
    
    if dismissed_count > 0 and stealth_config.enabled and stealth_config.random_delays:
        await human_delay(1000, 2000)


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
        elif step.type == StepType.DISMISS_POPUPS:
            await _handle_dismiss_popups(page, step, config)
            # No need for selector wait, dismiss_popups handles its own selectors
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

"""Human-like mouse movement simulation for anti-detection."""

from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Page


async def simulate_mouse_movement(page: Page, target_selector: str) -> None:
    """
    Simulates human-like mouse movement to a target element.

    Args:
        page: Playwright Page object.
        target_selector: CSS selector for the target element.
    """
    try:
        element = page.locator(target_selector)
        box = await element.bounding_box()

        if not box:
            return  # Element not found, cannot simulate movement

        # Random start point (could be outside the element)
        start_x = random.uniform(max(0, box["x"] - 50), box["x"] + box["width"] + 50)
        start_y = random.uniform(max(0, box["y"] - 50), box["y"] + box["height"] + 50)

        # Target center of the element
        target_x = box["x"] + box["width"] / 2
        target_y = box["y"] + box["height"] / 2

        await page.mouse.move(start_x, start_y)
        await asyncio.sleep(random.uniform(0.1, 0.3)) # Initial pause

        # Simulate curved movement with multiple intermediate points
        num_steps = random.randint(5, 15) # More steps for smoother curves
        for i in range(num_steps + 1):
            progress = i / num_steps
            
            # Introduce some curve/randomness
            x_offset = random.uniform(-10, 10) * (1 - abs(progress - 0.5) * 2)
            y_offset = random.uniform(-10, 10) * (1 - abs(progress - 0.5) * 2)

            current_x = start_x + (target_x - start_x) * progress + x_offset
            current_y = start_y + (target_y - start_y) * progress + y_offset

            await page.mouse.move(current_x, current_y)
            await asyncio.sleep(random.uniform(0.01, 0.08)) # Small delays between moves

        # Final small adjustment to the exact center (or near center)
        await page.mouse.move(target_x, target_y)

    except Exception as e:
        # Log the error but don't fail the extraction if mouse movement fails
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to simulate mouse movement to {target_selector}: {e}")

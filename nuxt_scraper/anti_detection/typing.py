"""Human-like typing simulation for anti-detection."""

from __future__ import annotations

import asyncio
import random
import string
from typing import TYPE_CHECKING

from nuxt_scraper.anti_detection.delays import human_delay

if TYPE_CHECKING:
    from playwright.async_api import Page


async def human_type(
    page: Page,
    selector: str,
    text: str,
    wpm: int = 65,
    typo_chance: float = 0.02,
    pause_chance: float = 0.05,
) -> None:
    """
    Types text into a field with human-like speed and occasional typos.

    Args:
        page: Playwright Page object.
        selector: CSS selector for the target input field.
        text: The text to type.
        wpm: Typing speed in words per minute.
        typo_chance: Probability of making a typo (0.0 to 1.0).
        pause_chance: Probability of making a longer pause (0.0 to 1.0).
    """
    await page.wait_for_selector(selector)  # Ensure element is visible
    await page.focus(selector)  # Focus the input field

    # Clear field first for human-like behavior (e.g., Ctrl+A, Backspace/Delete)
    # Check platform to use 'Meta+a' for macOS or 'Control+a' for others
    await page.keyboard.press("Control+A")  # Select all text
    await human_delay(50, 150)
    await page.keyboard.press("Backspace")  # Delete selected text
    await human_delay(100, 200)

    # Calculate delay per character based on WPM
    chars_per_second = (wpm * 5) / 60.0  # Average 5 chars per word
    base_delay_s = 1.0 / chars_per_second if chars_per_second > 0 else 0.1

    for i, char in enumerate(text):
        # Introduce random variance to typing speed
        delay = base_delay_s * random.uniform(0.7, 1.3)  # +/- 30% speed variance

        # Occasionally pause longer (simulating thinking)
        if random.random() < pause_chance:
            delay *= random.uniform(2, 5)  # Longer pause

        # Simulate occasional typos and corrections
        if random.random() < typo_chance and i > 0 and char.isalnum():
            # Choose a random incorrect character (alphanumeric)
            wrong_char = random.choice(string.ascii_letters + string.digits)
            await page.keyboard.type(wrong_char)
            await asyncio.sleep(delay * 0.3)  # Short pause after typo
            await page.keyboard.press("Backspace")
            await asyncio.sleep(delay * 0.2)  # Short pause after backspace

        await page.keyboard.type(char)
        await asyncio.sleep(delay)

    await human_delay(50, 300)  # Small delay after typing finishes

"""
Advanced navigation examples: multiple steps before extracting Nuxt data.

Run with: python -m examples.advanced_navigation
"""

from __future__ import annotations

import asyncio
from nuxt_scraper import NuxtDataExtractor, NavigationStep
from nuxt_scraper.utils import StealthConfig


async def extract_after_clicking_tab() -> None:
    """Click a tab, then wait for content, then extract."""
    steps = [
        NavigationStep.click("button[data-tab='products']"),
        NavigationStep.wait("div.products-loaded", timeout=10000),
    ]
    async with NuxtDataExtractor(headless=False, timeout=30000) as extractor:
        data = await extractor.extract(
            "https://shop.example.com",
            steps=steps,
            wait_for_nuxt=True,
        )
    print("Data keys:", list(data.keys()) if isinstance(data, dict) else data)


async def extract_after_fill_and_submit() -> None:
    """Fill a search box, optionally click submit, then extract."""
    steps = [
        NavigationStep.fill("input[name='search']", "widgets"),
        NavigationStep.click("button[type='submit']"),
        NavigationStep.wait("div.search-results", timeout=15000),
    ]
    async with NuxtDataExtractor(timeout=30000) as extractor:
        data = await extractor.extract(
            "https://catalog.example.com",
            steps=steps,
        )
    return data


async def extract_after_scroll_and_wait() -> None:
    """Scroll to load lazy content, then extract."""
    steps = [
        NavigationStep.scroll("footer"),
        NavigationStep.wait("div.lazy-loaded-section", timeout=8000),
    ]
    async with NuxtDataExtractor() as extractor:
        data = await extractor.extract(
            "https://infinite-scroll.example.com",
            steps=steps,
        )
    return data


async def extract_with_select_dropdown() -> None:
    """Change a dropdown, wait for update, then extract."""
    steps = [
        NavigationStep.select("select#region", "US"),
        NavigationStep.wait("div.region-content", timeout=5000),
    ]
    async with NuxtDataExtractor() as extractor:
        data = await extractor.extract(
            "https://region.example.com",
            steps=steps,
        )
    return data


async def select_date_example() -> None:
    """Demonstrates selecting a date from a calendar pop-up."""
    # First, click the input that opens the calendar
    open_calendar_step = NavigationStep.click("input#date-picker-input")

    # Then, define the date selection step
    select_specific_date = NavigationStep.select_date(
        target_date="2026-03-15",  # March 15, 2026
        calendar_selector="div.calendar-popup",
        prev_month_selector="button.prev-month",
        next_month_selector="button.next-month",
        month_year_display_selector="div.month-year-display",  # e.g. "Feb 2026"
        date_cell_selector="div.day-cell",
        view_results_selector="button:has-text('View Results')",
        timeout=20000,
    )

    async with NuxtDataExtractor(headless=False, stealth_config=StealthConfig()) as extractor:
        data = await extractor.extract(
            "https://your-site-with-calendar.com",
            steps=[open_calendar_step, select_specific_date],
        )
    print("Data after date selection:", data)


if __name__ == "__main__":
    print("Advanced navigation examples (replace URLs to run)")
    # asyncio.run(extract_after_clicking_tab())
    # asyncio.run(select_date_example())

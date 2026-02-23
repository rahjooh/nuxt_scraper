"""
Advanced navigation examples: multiple steps before extracting Nuxt data.

Run with: python -m examples.advanced_navigation
"""

from __future__ import annotations

import asyncio
from nuxtflow import NuxtDataExtractor, NavigationStep


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


if __name__ == "__main__":
    print("Advanced navigation examples (replace URLs to run)")
    # asyncio.run(extract_after_clicking_tab())

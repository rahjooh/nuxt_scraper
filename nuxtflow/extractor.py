"""Main NuxtDataExtractor class for extracting __NUXT_DATA__ via Playwright."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, List, Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from nuxtflow.exceptions import ExtractionTimeout, NuxtDataNotFound
from nuxtflow.parser import (
    EXTRACT_NUXT_DATA_SCRIPT,
    NUXT_DATA_ELEMENT_ID,
    parse_nuxt_json,
    validate_extracted_result,
)
from nuxtflow.steps import NavigationStep, execute_steps

logger = logging.getLogger(__name__)


class NuxtDataExtractor:
    """
    Extract __NUXT_DATA__ from Nuxt.js applications using Playwright.

    Supports optional navigation steps (click, fill, wait, etc.) before extraction.
    Can be used as an async context manager or with explicit start/stop.
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        browser_type: str = "chromium",
        ignore_https_errors: bool = False,
        viewport_width: int = 1280,
        viewport_height: int = 720,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Initialize the extractor.

        Args:
            headless: Run browser in headless mode.
            timeout: Default timeout for navigation and extraction (ms).
            browser_type: One of "chromium", "firefox", "webkit".
            ignore_https_errors: Ignore HTTPS certificate errors.
            viewport_width: Viewport width in pixels.
            viewport_height: Viewport height in pixels.
            user_agent: Optional custom user agent string.
        """
        self.headless = headless
        self.timeout = timeout
        self.browser_type_name = browser_type
        self.ignore_https_errors = ignore_https_errors
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.user_agent = user_agent

        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

    async def __aenter__(self) -> NuxtDataExtractor:
        """Start Playwright and browser."""
        await self._start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop browser and Playwright."""
        await self._stop()

    async def _start(self) -> None:
        """Launch Playwright and browser."""
        self._playwright = await async_playwright().start()
        browser_launcher = getattr(self._playwright, self.browser_type_name)
        self._browser = await browser_launcher.launch(headless=self.headless)
        opts: Any = {
            "ignore_https_errors": self.ignore_https_errors,
            "viewport": {"width": self.viewport_width, "height": self.viewport_height},
        }
        if self.user_agent:
            opts["user_agent"] = self.user_agent
        self._context = await self._browser.new_context(**opts)
        self._context.set_default_timeout(self.timeout)

    async def _stop(self) -> None:
        """Close browser and stop Playwright."""
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    def _ensure_started(self) -> None:
        if not self._context:
            raise RuntimeError(
                "Extractor not started. Use 'async with NuxtDataExtractor()' or call start() first."
            )

    async def extract(
        self,
        url: str,
        steps: Optional[List[NavigationStep]] = None,
        wait_for_nuxt: bool = True,
        wait_for_nuxt_timeout: Optional[int] = None,
    ) -> Any:
        """
        Navigate to the URL, optionally run steps, then extract __NUXT_DATA__.

        Args:
            url: Target page URL.
            steps: Optional list of navigation steps to run before extraction.
            wait_for_nuxt: If True, wait for #__NUXT_DATA__ to be present.
            wait_for_nuxt_timeout: Timeout in ms for waiting for Nuxt data (default: self.timeout).

        Returns:
            Parsed Nuxt data (typically a dict).
        """
        self._ensure_started()
        timeout_ms = wait_for_nuxt_timeout if wait_for_nuxt_timeout is not None else self.timeout

        page = await self._context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)

            if steps:
                await execute_steps(page, steps)

            if wait_for_nuxt:
                try:
                    await page.wait_for_selector(f"#{NUXT_DATA_ELEMENT_ID}", timeout=timeout_ms)
                except Exception as e:
                    raise ExtractionTimeout(
                        f"Timed out waiting for #{NUXT_DATA_ELEMENT_ID}: {e!s}"
                    ) from e

            raw = await page.evaluate(EXTRACT_NUXT_DATA_SCRIPT)
            validate_extracted_result(raw)
            return parse_nuxt_json(raw)
        finally:
            await page.close()

    def extract_sync(
        self,
        url: str,
        steps: Optional[List[NavigationStep]] = None,
        wait_for_nuxt: bool = True,
        wait_for_nuxt_timeout: Optional[int] = None,
    ) -> Any:
        """
        Synchronous wrapper for extract(). Runs the async extract in the event loop.
        """
        return asyncio.run(
            self.extract(
                url,
                steps=steps,
                wait_for_nuxt=wait_for_nuxt,
                wait_for_nuxt_timeout=wait_for_nuxt_timeout,
            )
        )


def extract_nuxt_data(
    url: str,
    steps: Optional[List[NavigationStep]] = None,
    headless: bool = True,
    timeout: int = 30000,
    wait_for_nuxt: bool = True,
) -> Any:
    """
    Convenience function: create an extractor, extract once, return data.

    Args:
        url: Target page URL.
        steps: Optional navigation steps.
        headless: Run browser headless.
        timeout: Timeout in ms.
        wait_for_nuxt: Wait for __NUXT_DATA__ element.

    Returns:
        Parsed Nuxt data.
    """
    async def _run() -> Any:
        async with NuxtDataExtractor(headless=headless, timeout=timeout) as extractor:
            return await extractor.extract(
                url,
                steps=steps,
                wait_for_nuxt=wait_for_nuxt,
            )

    return asyncio.run(_run())

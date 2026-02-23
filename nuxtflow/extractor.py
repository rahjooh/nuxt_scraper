"""Main NuxtDataExtractor class for extracting __NUXT_DATA__ via Playwright."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, List, Optional, Dict

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from nuxtflow.anti_detection.stealth_scripts import STEALTH_SCRIPTS
from nuxtflow.anti_detection.user_agents import get_realistic_user_agent
from nuxtflow.anti_detection.viewports import get_random_viewport
from nuxtflow.exceptions import BrowserError, ExtractionTimeout, NuxtDataNotFound, ProxyError
from nuxtflow.parser import (
    EXTRACT_NUXT_DATA_SCRIPT,
    NUXT_DATA_ELEMENT_ID,
    parse_nuxt_json,
    validate_extracted_result,
)
from nuxtflow.steps import NavigationStep, execute_steps
from nuxtflow.utils import StealthConfig

logger = logging.getLogger(__name__)


class NuxtDataExtractor:
    """
    Extract __NUXT_DATA__ from Nuxt.js applications using Playwright.

    Supports optional navigation steps (click, fill, wait, etc.) before extraction.
    Can be used as an async context manager or with explicit start/stop.
    Incorporates anti-detection measures and proxy support.
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        browser_type: str = "chromium",
        ignore_https_errors: bool = False,
        viewport_width: Optional[int] = 1280,
        viewport_height: Optional[int] = 720,
        user_agent: Optional[str] = None,
        stealth_config: Optional[StealthConfig] = None,
        proxy: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize the extractor.

        Args:
            headless: Run browser in headless mode.
            timeout: Default timeout for navigation and extraction (ms).
            browser_type: One of "chromium", "firefox", "webkit".
            ignore_https_errors: Ignore HTTPS certificate errors.
            viewport_width: Viewport width in pixels. If randomize_viewport is True in StealthConfig, this is ignored.
            viewport_height: Viewport height in pixels. If randomize_viewport is True in StealthConfig, this is ignored.
            user_agent: Optional custom user agent string. If realistic_user_agent is True in StealthConfig, this is ignored.
            stealth_config: Configuration for anti-detection features. Defaults to StealthConfig().
            proxy: Dictionary for proxy settings, e.g., {"server": "http://ip:port", "username": "user", "password": "pass"}.
        """
        self.headless = headless
        self.timeout = timeout
        self.browser_type_name = browser_type
        self.ignore_https_errors = ignore_https_errors
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.user_agent = user_agent
        self.stealth_config = stealth_config or StealthConfig()
        self.proxy = proxy

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
        """Launch Playwright and browser with anti-detection measures and proxy."""
        try:
            self._playwright = await async_playwright().start()
            browser_launcher = getattr(self._playwright, self.browser_type_name)

            launch_args = []
            if self.stealth_config.enabled:
                launch_args.extend([
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                ])
            
            self._browser = await browser_launcher.launch(headless=self.headless, args=launch_args)

            # Resolve viewport and user agent based on stealth config
            if self.stealth_config.enabled and self.stealth_config.randomize_viewport:
                resolved_width, resolved_height = get_random_viewport()
                self.stealth_config._resolved_viewport = (resolved_width, resolved_height)
            else:
                resolved_width, resolved_height = self.viewport_width or 1280, self.viewport_height or 720

            if self.stealth_config.enabled and self.stealth_config.realistic_user_agent:
                resolved_user_agent = get_realistic_user_agent()
                self.stealth_config._resolved_user_agent = resolved_user_agent
            else:
                resolved_user_agent = self.user_agent

            context_opts: Dict[str, Any] = {
                "ignore_https_errors": self.ignore_https_errors,
                "viewport": {"width": resolved_width, "height": resolved_height},
            }
            if resolved_user_agent:
                context_opts["user_agent"] = resolved_user_agent
            if self.proxy:
                context_opts["proxy"] = self.proxy

            self._context = await self._browser.new_context(**context_opts)
            self._context.set_default_timeout(self.timeout)

            # Inject stealth scripts
            if self.stealth_config.enabled:
                for script in STEALTH_SCRIPTS:
                    await self._context.add_init_script(script)

        except Exception as e:
            if self.proxy:
                raise ProxyError(f"Failed to launch browser with proxy {self.proxy}: {e!s}", original_error=e) from e
            raise BrowserError(f"Failed to launch browser: {e!s}", original_error=e) from e

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
                await execute_steps(page, steps, self.stealth_config)

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
    stealth_config: Optional[StealthConfig] = None,
    proxy: Optional[Dict[str, str]] = None,
) -> Any:
    """
    Convenience function: create an extractor, extract once, return data.

    Args:
        url: Target page URL.
        steps: Optional navigation steps.
        headless: Run browser headless.
        timeout: Timeout in ms.
        wait_for_nuxt: Wait for __NUXT_DATA__ element.
        stealth_config: Configuration for anti-detection features.
        proxy: Dictionary for proxy settings.

    Returns:
        Parsed Nuxt data.
    """
    async def _run() -> Any:
        async with NuxtDataExtractor(
            headless=headless,
            timeout=timeout,
            stealth_config=stealth_config,
            proxy=proxy,
        ) as extractor:
            return await extractor.extract(
                url,
                steps=steps,
                wait_for_nuxt=wait_for_nuxt,
            )

    return asyncio.run(_run())

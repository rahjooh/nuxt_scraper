"""Main NuxtDataExtractor class for extracting __NUXT_DATA__ via Playwright."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Playwright,
    async_playwright,
)

from nuxt_scraper.anti_detection.stealth_scripts import STEALTH_SCRIPTS
from nuxt_scraper.anti_detection.user_agents import get_realistic_user_agent
from nuxt_scraper.anti_detection.viewports import get_random_viewport
from nuxt_scraper.exceptions import (
    BrowserError,
    ExtractionTimeout,
    ProxyError,
)
from nuxt_scraper.parser import (
    EXTRACT_NUXT_DATA_SCRIPT,
    EXTRACT_NUXT_COMBINED_SCRIPT,
    NUXT_DATA_ELEMENT_ID,
    parse_nuxt_json,
    parse_nuxt_result,
    validate_extracted_result,
    validate_combined_result,
    deserialize_nuxt3_data,
)
from nuxt_scraper.steps import NavigationStep, execute_steps
from nuxt_scraper.utils import StealthConfig

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
            viewport_width: Viewport width (px). Ignored when randomize_viewport.
            viewport_height: Viewport height (px). Ignored when randomize_viewport.
            user_agent: Custom user agent. Ignored when realistic_user_agent.
            stealth_config: Anti-detection config. Defaults to StealthConfig().
            proxy: Proxy dict e.g. {"server": "http://ip:port"}.
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
                launch_args.extend(
                    [
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                    ]
                )

            self._browser = await browser_launcher.launch(
                headless=self.headless, args=launch_args
            )

            # Resolve viewport and user agent based on stealth config
            if self.stealth_config.enabled and self.stealth_config.randomize_viewport:
                resolved_width, resolved_height = get_random_viewport()
                self.stealth_config._resolved_viewport = (
                    resolved_width,
                    resolved_height,
                )
            else:
                resolved_width, resolved_height = (
                    self.viewport_width or 1280,
                    self.viewport_height or 720,
                )

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
                raise ProxyError(
                    f"Failed to launch browser with proxy {self.proxy}: {e!s}",
                    original_error=e,
                ) from e
            raise BrowserError(
                f"Failed to launch browser: {e!s}", original_error=e
            ) from e

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
                "Extractor not started. Use async with NuxtDataExtractor() or start()."
            )

    async def extract(
        self,
        url: str,
        steps: Optional[List[NavigationStep]] = None,
        wait_for_nuxt: bool = True,
        wait_for_nuxt_timeout: Optional[int] = None,
        use_combined_extraction: bool = True,
        deserialize_nuxt3: bool = True,
    ) -> Any:
        """
        Navigate to the URL, optionally run steps, then extract Nuxt data.

        Args:
            url: Target page URL.
            steps: Optional list of navigation steps to run before extraction.
            wait_for_nuxt: If True, wait for #__NUXT_DATA__ to be present (legacy mode only).
            wait_for_nuxt_timeout: Timeout (ms) for Nuxt data. Default: self.timeout.
            use_combined_extraction: If True, try both #__NUXT_DATA__ and window.__NUXT__.
            deserialize_nuxt3: If True, deserialize Nuxt 3 reactive references.

        Returns:
            Parsed Nuxt data (typically a dict).
        """
        self._ensure_started()
        timeout_ms = (
            wait_for_nuxt_timeout if wait_for_nuxt_timeout is not None else self.timeout
        )

        page = await self._context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)

            if steps:
                await execute_steps(page, steps, self.stealth_config)

            if use_combined_extraction:
                # New combined approach: try both methods
                return await self._extract_combined(page, timeout_ms, deserialize_nuxt3)
            else:
                # Legacy approach: only try #__NUXT_DATA__ element
                return await self._extract_legacy(page, timeout_ms, wait_for_nuxt, deserialize_nuxt3)
        finally:
            await page.close()

    async def _extract_combined(self, page, timeout_ms: int, deserialize_nuxt3: bool = True) -> Any:
        """
        Extract Nuxt data using the combined approach (both element and window methods).
        
        Args:
            page: Playwright page object
            timeout_ms: Timeout in milliseconds
            deserialize_nuxt3: Whether to deserialize Nuxt 3 reactive references
            
        Returns:
            Parsed Nuxt data
        """
        # Wait a bit for the page to fully load
        await asyncio.sleep(2)
        
        # Try the combined extraction script
        extraction_result = await page.evaluate(EXTRACT_NUXT_COMBINED_SCRIPT)
        
        # If no data found immediately, wait a bit more and try again
        if not extraction_result or not extraction_result.get('data'):
            logger.debug("No Nuxt data found on first attempt, waiting and retrying...")
            await asyncio.sleep(3)
            extraction_result = await page.evaluate(EXTRACT_NUXT_COMBINED_SCRIPT)
        
        validate_combined_result(extraction_result)
        data, method = parse_nuxt_result(extraction_result, deserialize_nuxt3=deserialize_nuxt3)
        
        logger.info(f"Successfully extracted Nuxt data using {method} method")
        return data

    async def _extract_legacy(self, page, timeout_ms: int, wait_for_nuxt: bool, deserialize_nuxt3: bool = True) -> Any:
        """
        Extract Nuxt data using the legacy approach (only #__NUXT_DATA__ element).
        
        Args:
            page: Playwright page object
            timeout_ms: Timeout in milliseconds
            wait_for_nuxt: Whether to wait for the element
            deserialize_nuxt3: Whether to deserialize Nuxt 3 reactive references
            
        Returns:
            Parsed Nuxt data
        """
        if wait_for_nuxt:
            try:
                await page.wait_for_selector(
                    f"#{NUXT_DATA_ELEMENT_ID}", timeout=timeout_ms
                )
            except Exception as e:
                raise ExtractionTimeout(
                    f"Timed out waiting for #{NUXT_DATA_ELEMENT_ID}: {e!s}"
                ) from e

        raw = await page.evaluate(EXTRACT_NUXT_DATA_SCRIPT)
        validate_extracted_result(raw)
        return parse_nuxt_json(raw, deserialize_nuxt3=deserialize_nuxt3)

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
                use_combined_extraction=True,
                deserialize_nuxt3=True,
            )
        )

    async def extract_from_current_page(self, use_combined_extraction: bool = True, deserialize_nuxt3: bool = True) -> Any:
        """
        Extract Nuxt data from the currently loaded page without navigation.
        
        Args:
            use_combined_extraction: If True, try both #__NUXT_DATA__ and window.__NUXT__.
            deserialize_nuxt3: If True, deserialize Nuxt 3 reactive references.
            
        Returns:
            Parsed Nuxt data
        """
        self._ensure_started()
        
        # Get the current page (assuming there's one active)
        pages = self._context.pages
        if not pages:
            raise BrowserError("No active pages found")
        
        page = pages[0]  # Use the first/main page
        
        if use_combined_extraction:
            return await self._extract_combined(page, self.timeout, deserialize_nuxt3)
        else:
            return await self._extract_legacy(page, self.timeout, wait_for_nuxt=False, deserialize_nuxt3=deserialize_nuxt3)

    async def navigate(self, url: str) -> None:
        """
        Navigate to a URL without extracting data.
        
        Args:
            url: Target page URL
        """
        self._ensure_started()
        
        pages = self._context.pages
        if pages:
            page = pages[0]
        else:
            page = await self._context.new_page()
        
        await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)

    async def execute_step(self, step: NavigationStep) -> None:
        """
        Execute a single navigation step on the current page.
        
        Args:
            step: Navigation step to execute
        """
        self._ensure_started()
        
        pages = self._context.pages
        if not pages:
            raise BrowserError("No active pages found")
        
        page = pages[0]
        await execute_steps(page, [step], self.stealth_config)

    async def extract_with_api_capture(
        self,
        url: str,
        steps: Optional[List[NavigationStep]] = None,
        api_filter: Optional[callable] = None,
        wait_for_nuxt: bool = True,
        wait_for_nuxt_timeout: Optional[int] = None,
        use_combined_extraction: bool = True,
        deserialize_nuxt3: bool = True,
    ) -> tuple[Any, List[Dict[str, Any]]]:
        """
        Extract Nuxt data AND capture API responses during navigation.
        
        This is useful for calendar navigation or dynamic content where
        window.__NUXT__ doesn't update but API calls contain the new data.
        
        The response handler is attached BEFORE navigation to ensure all
        API calls are captured, including those during initial page load.
        
        Args:
            url: Target page URL.
            steps: Optional list of navigation steps to run before extraction.
            api_filter: Optional function to filter which API responses to capture.
                       Receives response object, returns True to capture.
                       Default: captures all JSON responses from puntapi.com or graphql.
            wait_for_nuxt: If True, wait for #__NUXT_DATA__ to be present (legacy mode only).
            wait_for_nuxt_timeout: Timeout (ms) for Nuxt data. Default: self.timeout.
            use_combined_extraction: If True, try both #__NUXT_DATA__ and window.__NUXT__.
            deserialize_nuxt3: If True, deserialize Nuxt 3 reactive references.
            
        Returns:
            Tuple of (nuxt_data, api_responses) where api_responses is a list of dicts
            with 'url' and 'data' keys.
            
        Example:
            async with NuxtDataExtractor() as extractor:
                nuxt_data, api_responses = await extractor.extract_with_api_capture(
                    "https://racenet.com.au/results/harness",
                    steps=[
                        NavigationStep.click("a.tab:has-text('Select Date')"),
                        NavigationStep.select_date(
                            target_date="2025-02-20",
                            calendar_selector=".calendar",
                            ...
                        )
                    ]
                )
                # Find specific API response
                meetings_data = extractor.find_api_response(
                    api_responses, 
                    "meetingsGroupedByStartEndDate"
                )
        """
        self._ensure_started()
        timeout_ms = (
            wait_for_nuxt_timeout if wait_for_nuxt_timeout is not None else self.timeout
        )
        
        # Set up API response capture
        api_responses: List[Dict[str, Any]] = []
        
        # Default filter: capture JSON responses from puntapi.com or graphql
        if api_filter is None:
            def default_filter(response) -> bool:
                return (
                    ("puntapi.com" in response.url or "graphql" in response.url.lower())
                    and response.status == 200
                )
            api_filter = default_filter
        
        async def handle_response(response):
            try:
                if api_filter(response):
                    try:
                        data = await response.json()
                        api_responses.append({"url": response.url, "data": data})
                    except Exception:
                        # Response might not be JSON
                        pass
            except Exception:
                # Filter function might raise exception
                pass
        
        # Get or create page and attach handler BEFORE navigation
        pages = self._context.pages
        if pages:
            page = pages[0]
        else:
            page = await self._context.new_page()
        
        page.on("response", handle_response)
        
        try:
            # Navigate to URL
            await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
            
            # Execute navigation steps if provided
            if steps:
                await execute_steps(page, steps, self.stealth_config)
            
            # Extract Nuxt data
            if use_combined_extraction:
                nuxt_data = await self._extract_combined(page, timeout_ms, deserialize_nuxt3)
            else:
                nuxt_data = await self._extract_legacy(page, timeout_ms, wait_for_nuxt, deserialize_nuxt3)
            
            return nuxt_data, api_responses
            
        finally:
            # Remove response handler to avoid memory leaks
            try:
                page.remove_listener("response", handle_response)
            except Exception:
                pass

    def find_api_response(
        self,
        api_responses: List[Dict[str, Any]],
        url_pattern: str,
        fallback_to_first: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Find a specific API response by URL pattern.
        
        Args:
            api_responses: List of captured API responses from extract_with_api_capture().
            url_pattern: String to search for in response URLs.
            fallback_to_first: If True, return first response if pattern not found.
            
        Returns:
            Response data dict (with 'url' and 'data' keys) or None if not found.
            
        Example:
            meetings_response = extractor.find_api_response(
                api_responses,
                "meetingsGroupedByStartEndDate"
            )
            if meetings_response:
                meetings_data = meetings_response["data"]
        """
        # Search for matching URL pattern
        for response in api_responses:
            if url_pattern in response["url"]:
                return response
        
        # Fallback to first response if requested
        if fallback_to_first and api_responses:
            return api_responses[0]
        
        return None


def extract_nuxt_data(
    url: str,
    steps: Optional[List[NavigationStep]] = None,
    headless: bool = True,
    timeout: int = 30000,
    wait_for_nuxt: bool = True,
    use_combined_extraction: bool = True,
    deserialize_nuxt3: bool = True,
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
        wait_for_nuxt: Wait for __NUXT_DATA__ element (legacy mode only).
        use_combined_extraction: Try both #__NUXT_DATA__ and window.__NUXT__.
        deserialize_nuxt3: Deserialize Nuxt 3 reactive references.
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
                use_combined_extraction=use_combined_extraction,
                deserialize_nuxt3=deserialize_nuxt3,
            )

    return asyncio.run(_run())

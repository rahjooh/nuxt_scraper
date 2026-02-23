"""Tests for NuxtFlow extractor module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from nuxtflow.exceptions import BrowserError, NuxtDataNotFound, ProxyError, ExtractionTimeout
from nuxtflow.extractor import NuxtDataExtractor
from nuxtflow.steps import NavigationStep
from nuxtflow.utils import StealthConfig

# Mock anti-detection functions globally for these tests unless specifically testing them
@pytest.fixture(autouse=True)
def mock_anti_detection_externals():
    with (
        patch('nuxtflow.anti_detection.user_agents.get_realistic_user_agent', return_value="MockUserAgent") as mock_ua,
        patch('nuxtflow.anti_detection.viewports.get_random_viewport', return_value=(800, 600)) as mock_vp,
        patch('nuxtflow.anti_detection.stealth_scripts.STEALTH_SCRIPTS', new_callable=MagicMock) as mock_scripts,
        patch('nuxtflow.steps.human_delay', new_callable=AsyncMock) as mock_delay,
        patch('nuxtflow.steps.simulate_mouse_movement', new_callable=AsyncMock) as mock_mouse_move,
        patch('nuxtflow.steps.human_type', new_callable=AsyncMock) as mock_human_type,
    ):
        yield mock_ua, mock_vp, mock_scripts, mock_delay, mock_mouse_move, mock_human_type


@pytest.fixture
def mock_context() -> MagicMock:
    """Mock browser context with a new_page that returns a mock page."""
    context = MagicMock()
    page = MagicMock()
    page.goto = AsyncMock(return_value=None)
    page.wait_for_selector = AsyncMock(return_value=None)
    page.evaluate = AsyncMock(return_value='{"data": "test"}')
    page.close = AsyncMock(return_value=None)
    context.new_page = AsyncMock(return_value=page)
    context.set_default_timeout = MagicMock()
    context.add_init_script = AsyncMock(return_value=None) # Added for stealth scripts
    return context


@pytest.fixture
def mock_browser(mock_context: MagicMock) -> MagicMock:
    """Mock browser that returns mock context."""
    browser = MagicMock()
    browser.new_context = AsyncMock(return_value=mock_context)
    browser.close = AsyncMock(return_value=None)
    return browser


@pytest.fixture
def mock_playwright(mock_browser: MagicMock) -> MagicMock:
    """Mock Playwright with chromium launcher."""
    pw = MagicMock()
    pw.chromium.launch = AsyncMock(return_value=mock_browser)
    pw.stop = AsyncMock(return_value=None)
    return pw


@pytest.mark.asyncio
async def test_extractor_initializes_with_default_stealth_config(mock_playwright: MagicMock) -> None:
    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)
        async with NuxtDataExtractor() as extractor:
            assert isinstance(extractor.stealth_config, StealthConfig)
            assert extractor.stealth_config.enabled is True


@pytest.mark.asyncio
async def test_extract_returns_parsed_data(
    mock_playwright: MagicMock,
    mock_context: MagicMock,
) -> None:
    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)

        async with NuxtDataExtractor() as extractor:
            result = await extractor.extract("https://example.com")

        assert result == {"data": "test"}
        mock_playwright.chromium.launch.assert_called_once()
        mock_context.new_page.assert_called_once()
        mock_context.add_init_script.assert_called()


@pytest.mark.asyncio
async def test_extractor_applies_stealth_options(
    mock_playwright: MagicMock,
    mock_context: MagicMock,
    mock_anti_detection_externals,
) -> None:
    mock_ua, mock_vp, mock_scripts, *_ = mock_anti_detection_externals
    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)

        custom_config = StealthConfig(
            randomize_viewport=True,
            realistic_user_agent=True,
        )
        async with NuxtDataExtractor(stealth_config=custom_config) as extractor:
            await extractor.extract("https://example.com")

        mock_ua.assert_called_once() # get_realistic_user_agent should be called
        mock_vp.assert_called_once() # get_random_viewport should be called
        mock_context.add_init_script.assert_called() # Stealth scripts should be added
        # Assert that user_agent and viewport are passed to new_context
        new_context_kwargs = mock_playwright.chromium.launch.return_value.new_context.call_args[1]
        assert "user_agent" in new_context_kwargs
        assert new_context_kwargs["viewport"] == {"width": 800, "height": 600}


@pytest.mark.asyncio
async def test_extractor_handles_proxy_configuration(
    mock_playwright: MagicMock,
    mock_context: MagicMock,
) -> None:
    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)

        proxy_settings = {"server": "http://myproxy.com:8080"}
        async with NuxtDataExtractor(proxy=proxy_settings) as extractor:
            await extractor.extract("https://example.com")
        
        new_context_kwargs = mock_playwright.chromium.launch.return_value.new_context.call_args[1]
        assert new_context_kwargs["proxy"] == proxy_settings


@pytest.mark.asyncio
async def test_extractor_raises_browser_error_on_launch_failure(
    mock_playwright: MagicMock,
) -> None:
    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch.side_effect = Exception("Launch failed")
        with pytest.raises(BrowserError):
            async with NuxtDataExtractor():
                pass


@pytest.mark.asyncio
async def test_extractor_raises_proxy_error_on_proxy_launch_failure(
    mock_playwright: MagicMock,
) -> None:
    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch.side_effect = Exception("Proxy failed")
        with pytest.raises(ProxyError):
            async with NuxtDataExtractor(proxy={"server": "http://bad.proxy:8080"}):
                pass


@pytest.mark.asyncio
async def test_extract_raises_when_nuxt_data_missing(
    mock_playwright: MagicMock,
    mock_context: MagicMock,
) -> None:
    page = mock_context.new_page.return_value
    page.evaluate = AsyncMock(return_value=None)

    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)

        async with NuxtDataExtractor() as extractor:
            with pytest.raises(NuxtDataNotFound):
                await extractor.extract("https://example.com")


@pytest.mark.asyncio
async def test_extract_uses_extract_script(
    mock_playwright: MagicMock,
    mock_context: MagicMock,
) -> None:
    page = mock_context.new_page.return_value
    page.evaluate = AsyncMock(return_value='{"x": 1}')

    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)

        async with NuxtDataExtractor() as extractor:
            await extractor.extract("https://example.com")
            page.evaluate.assert_called_once()
            call_arg = page.evaluate.call_args[0][0]
            assert "getElementById" in call_arg and "__NUXT_DATA__" in call_arg


@pytest.mark.asyncio
async def test_extract_requires_started_extractor() -> None:
    extractor = NuxtDataExtractor()
    with pytest.raises(RuntimeError, match="not started"):
        await extractor.extract("https://example.com")


@pytest.mark.asyncio
async def test_extract_with_steps_calls_execute_steps(
    mock_playwright: MagicMock,
    mock_context: MagicMock,
    mock_anti_detection_externals,
) -> None:
    _, _, _, mock_delay, mock_mouse_move, mock_human_type = mock_anti_detection_externals
    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)
        
        mock_execute_steps = AsyncMock()
        with patch('nuxtflow.extractor.execute_steps', new=mock_execute_steps):
            test_steps = [NavigationStep.click("button")]
            async with NuxtDataExtractor() as extractor:
                await extractor.extract("https://example.com", steps=test_steps)
            
            mock_execute_steps.assert_called_once()
            # Check if stealth_config is passed to execute_steps
            assert isinstance(mock_execute_steps.call_args[0][2], StealthConfig)


@pytest.mark.asyncio
async def test_extract_nuxt_data_convenience_function(
    mock_playwright: MagicMock,
    mock_context: MagicMock,
    sample_nuxt_json: str,
    mock_anti_detection_externals,
) -> None:
    mock_context.new_page.return_value.evaluate.return_value = sample_nuxt_json
    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)

        result = await NuxtDataExtractor().extract_sync("https://example.com")
        assert result == {"data": [{"id": 1, "name": "Item 1"}], "state": {}}


@pytest.mark.asyncio
async def test_extract_sync_calls_extract_async(
    mock_playwright: MagicMock,
    mock_context: MagicMock,
    sample_nuxt_json: str,
    mock_anti_detection_externals,
) -> None:
    mock_context.new_page.return_value.evaluate.return_value = sample_nuxt_json
    
    with patch("nuxtflow.extractor.NuxtDataExtractor.extract", new_callable=AsyncMock) as mock_extract:
        mock_extract.return_value = parse_nuxt_json(sample_nuxt_json)
        extractor = NuxtDataExtractor()
        result = extractor.extract_sync("https://example.com")
        mock_extract.assert_called_once()
        assert result == parse_nuxt_json(sample_nuxt_json)

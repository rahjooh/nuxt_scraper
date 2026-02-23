"""Tests for NuxtFlow extractor module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from nuxtflow.exceptions import NuxtDataNotFound
from nuxtflow.extractor import NuxtDataExtractor
from nuxtflow.steps import NavigationStep


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
async def test_extract_returns_parsed_data(
    mock_playwright: MagicMock,
    mock_context: MagicMock,
) -> None:
    with patch("nuxtflow.extractor.async_playwright") as p:
        p.return_value.start = AsyncMock(return_value=mock_playwright)

        async with NuxtDataExtractor() as extractor:
            result = await extractor.extract("https://example.com")

        assert result == {"data": "test"}


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

"""Tests for different extraction methods and configurations."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
import json

import pytest

from nuxt_scraper.extractor import NuxtDataExtractor, extract_nuxt_data
from nuxt_scraper.exceptions import NuxtDataNotFound, DataParsingError
from nuxt_scraper.utils import StealthConfig


@pytest.fixture
def mock_playwright_setup():
    """Setup mock playwright with configurable responses."""
    with patch("nuxt_scraper.extractor.async_playwright") as mock_async_playwright:
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        # Setup the chain
        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.set_default_timeout = MagicMock()
        mock_context.add_init_script = AsyncMock()
        mock_browser.close = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        yield {
            "playwright": mock_playwright,
            "browser": mock_browser,
            "context": mock_context,
            "page": mock_page
        }


class TestExtractionMethods:
    """Test different extraction methods (combined vs legacy)."""
    
    @pytest.mark.asyncio
    async def test_combined_extraction_tries_both_methods(self, mock_playwright_setup):
        """Test that combined extraction tries both element and window methods."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock the combined extraction script to return both methods
        extraction_result = {
            "data": json.dumps([{"state": 1}, {"name": "test"}]),
            "method": "element",
            "raw": "raw_data"
        }
        page.evaluate = AsyncMock(return_value=extraction_result)
        
        async with NuxtDataExtractor() as extractor:
            result = await extractor.extract(
                "https://test.com",
                use_combined_extraction=True
            )
        
        assert result == {"name": "test"}
        page.evaluate.assert_called_once()
        # Should use the combined script
        call_args = page.evaluate.call_args[0][0]
        assert "getElementById" in call_args
        assert "window.__NUXT__" in call_args
    
    @pytest.mark.asyncio
    async def test_legacy_extraction_element_only(self, mock_playwright_setup):
        """Test legacy extraction (element method only)."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock element extraction
        page.evaluate = AsyncMock(return_value=json.dumps([{"state": 1}, {"name": "legacy"}]))
        
        async with NuxtDataExtractor() as extractor:
            result = await extractor.extract(
                "https://test.com",
                use_combined_extraction=False,
                wait_for_nuxt=True
            )
        
        assert result == {"name": "legacy"}
        page.evaluate.assert_called_once()
        # Should use the element-only script
        call_args = page.evaluate.call_args[0][0]
        assert "getElementById" in call_args
        assert "__NUXT_DATA__" in call_args
    
    @pytest.mark.asyncio
    async def test_extraction_with_deserialization_enabled(self, mock_playwright_setup):
        """Test extraction with Nuxt 3 deserialization enabled."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock Nuxt 3 serialized data
        nuxt3_data = [
            {"state": 1},
            {"user": 2, "created": {"$d": 1672531200000}},
            {"name": "Alice", "id": 123}
        ]
        
        extraction_result = {
            "data": json.dumps(nuxt3_data),
            "method": "element",
            "raw": json.dumps(nuxt3_data)
        }
        page.evaluate = AsyncMock(return_value=extraction_result)
        
        async with NuxtDataExtractor() as extractor:
            result = await extractor.extract(
                "https://test.com",
                deserialize_nuxt3=True  # Enable deserialization
            )
        
        # Should deserialize the data
        assert result["user"]["name"] == "Alice"
        assert result["user"]["id"] == 123
        assert hasattr(result["created"], "year")  # Date object
    
    @pytest.mark.asyncio
    async def test_extraction_with_deserialization_disabled(self, mock_playwright_setup):
        """Test extraction with Nuxt 3 deserialization disabled."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock Nuxt 3 serialized data
        nuxt3_data = [
            {"state": 1},
            {"user": 2, "created": {"$d": 1672531200000}},
            {"name": "Alice", "id": 123}
        ]
        
        extraction_result = {
            "data": json.dumps(nuxt3_data),
            "method": "element",
            "raw": json.dumps(nuxt3_data)
        }
        page.evaluate = AsyncMock(return_value=extraction_result)
        
        async with NuxtDataExtractor() as extractor:
            result = await extractor.extract(
                "https://test.com",
                deserialize_nuxt3=False  # Disable deserialization
            )
        
        # Should return raw serialized data
        assert result == nuxt3_data
        assert isinstance(result, list)
        assert len(result) == 3
    
    @pytest.mark.asyncio
    async def test_window_method_extraction(self, mock_playwright_setup):
        """Test extraction via window.__NUXT__ method."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock window method response
        window_data = {"page": "data", "state": {"user": "test"}}
        extraction_result = {
            "data": window_data,
            "method": "window",
            "raw": json.dumps(window_data)
        }
        page.evaluate = AsyncMock(return_value=extraction_result)
        
        async with NuxtDataExtractor() as extractor:
            result = await extractor.extract("https://test.com")
        
        assert result == window_data
        assert result["page"] == "data"
        assert result["state"]["user"] == "test"
    
    @pytest.mark.asyncio
    async def test_extraction_fallback_behavior(self, mock_playwright_setup):
        """Test fallback behavior when primary method fails."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock combined extraction returning fallback to window method
        extraction_result = {
            "data": {"fallback": "data"},
            "method": "window",
            "raw": '{"fallback": "data"}'
        }
        page.evaluate = AsyncMock(return_value=extraction_result)
        
        async with NuxtDataExtractor() as extractor:
            result = await extractor.extract("https://test.com")
        
        assert result == {"fallback": "data"}


class TestExtractionErrorHandling:
    """Test error handling in extraction methods."""
    
    @pytest.mark.asyncio
    async def test_extraction_no_data_found(self, mock_playwright_setup):
        """Test handling when no Nuxt data is found."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock no data found
        extraction_result = {
            "data": None,
            "method": None,
            "raw": None
        }
        page.evaluate = AsyncMock(return_value=extraction_result)
        
        with pytest.raises(NuxtDataNotFound):
            async with NuxtDataExtractor() as extractor:
                await extractor.extract("https://test.com")
    
    @pytest.mark.asyncio
    async def test_extraction_invalid_json_data(self, mock_playwright_setup):
        """Test handling of invalid JSON data."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock invalid JSON
        extraction_result = {
            "data": "invalid json {",
            "method": "element",
            "raw": "invalid json {"
        }
        page.evaluate = AsyncMock(return_value=extraction_result)
        
        with pytest.raises(DataParsingError):
            async with NuxtDataExtractor() as extractor:
                await extractor.extract("https://test.com")
    
    @pytest.mark.asyncio
    async def test_extraction_script_evaluation_error(self, mock_playwright_setup):
        """Test handling of script evaluation errors."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock script evaluation error
        page.evaluate = AsyncMock(side_effect=Exception("Script error"))
        
        with pytest.raises(Exception):
            async with NuxtDataExtractor() as extractor:
                await extractor.extract("https://test.com")
    
    @pytest.mark.asyncio
    async def test_extraction_empty_result(self, mock_playwright_setup):
        """Test handling of empty extraction result."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock empty result
        page.evaluate = AsyncMock(return_value=None)
        
        with pytest.raises(NuxtDataNotFound):
            async with NuxtDataExtractor() as extractor:
                await extractor.extract("https://test.com")


class TestConvenienceFunction:
    """Test the extract_nuxt_data convenience function."""
    
    @patch("nuxt_scraper.extractor.NuxtDataExtractor")
    def test_extract_nuxt_data_basic_usage(self, mock_extractor_class):
        """Test basic usage of extract_nuxt_data function."""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor.__aenter__ = AsyncMock(return_value=mock_extractor)
        mock_extractor.__aexit__ = AsyncMock(return_value=None)
        mock_extractor.extract = AsyncMock(return_value={"test": "data"})
        mock_extractor_class.return_value = mock_extractor
        
        # Test the function
        result = extract_nuxt_data("https://test.com")
        
        assert result == {"test": "data"}
        mock_extractor_class.assert_called_once()
        mock_extractor.extract.assert_called_once_with(
            "https://test.com",
            steps=None,
            wait_for_nuxt=True,
            wait_for_nuxt_timeout=None,
            use_combined_extraction=True,
            deserialize_nuxt3=True
        )
    
    @patch("nuxt_scraper.extractor.NuxtDataExtractor")
    def test_extract_nuxt_data_with_options(self, mock_extractor_class):
        """Test extract_nuxt_data with various options."""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor.__aenter__ = AsyncMock(return_value=mock_extractor)
        mock_extractor.__aexit__ = AsyncMock(return_value=None)
        mock_extractor.extract = AsyncMock(return_value={"test": "data"})
        mock_extractor_class.return_value = mock_extractor
        
        # Test with options
        stealth_config = StealthConfig(random_delays=True)
        proxy_config = {"server": "http://proxy.com:8080"}
        
        result = extract_nuxt_data(
            "https://test.com",
            headless=False,
            timeout=45000,
            deserialize_nuxt3=False,
            stealth_config=stealth_config,
            proxy=proxy_config
        )
        
        assert result == {"test": "data"}
        
        # Check extractor was created with correct options
        mock_extractor_class.assert_called_once_with(
            headless=False,
            timeout=45000,
            stealth_config=stealth_config,
            proxy=proxy_config
        )
        
        # Check extract was called with correct options
        mock_extractor.extract.assert_called_once_with(
            "https://test.com",
            steps=None,
            wait_for_nuxt=True,
            wait_for_nuxt_timeout=None,
            use_combined_extraction=True,
            deserialize_nuxt3=False
        )


class TestExtractFromCurrentPage:
    """Test extraction from current page without navigation."""
    
    @pytest.mark.asyncio
    async def test_extract_from_current_page_success(self, mock_playwright_setup):
        """Test successful extraction from current page."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock extraction result
        extraction_result = {
            "data": json.dumps([{"state": 1}, {"current": "page"}]),
            "method": "element",
            "raw": "raw_data"
        }
        page.evaluate = AsyncMock(return_value=extraction_result)
        
        async with NuxtDataExtractor() as extractor:
            # Navigate first
            await extractor.navigate("https://test.com")
            
            # Extract from current page
            result = await extractor.extract_from_current_page()
        
        assert result == {"current": "page"}
        # Should not call goto again
        assert page.goto.call_count == 1
    
    @pytest.mark.asyncio
    async def test_extract_from_current_page_with_deserialization_options(self, mock_playwright_setup):
        """Test extraction from current page with different deserialization options."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        # Mock Nuxt 3 data
        nuxt3_data = [{"state": 1}, {"test": "data"}]
        extraction_result = {
            "data": json.dumps(nuxt3_data),
            "method": "element",
            "raw": json.dumps(nuxt3_data)
        }
        page.evaluate = AsyncMock(return_value=extraction_result)
        
        async with NuxtDataExtractor() as extractor:
            await extractor.navigate("https://test.com")
            
            # Test with deserialization enabled
            result1 = await extractor.extract_from_current_page(deserialize_nuxt3=True)
            assert result1 == {"test": "data"}
            
            # Test with deserialization disabled
            result2 = await extractor.extract_from_current_page(deserialize_nuxt3=False)
            assert result2 == nuxt3_data
    
    @pytest.mark.asyncio
    async def test_extract_from_current_page_no_navigation(self, mock_playwright_setup):
        """Test extraction from current page without prior navigation."""
        async with NuxtDataExtractor() as extractor:
            with pytest.raises(RuntimeError, match="not started"):
                await extractor.extract_from_current_page()


class TestNavigationMethod:
    """Test the navigate method."""
    
    @pytest.mark.asyncio
    async def test_navigate_success(self, mock_playwright_setup):
        """Test successful navigation."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        async with NuxtDataExtractor() as extractor:
            await extractor.navigate("https://test.com")
        
        page.goto.assert_called_once_with("https://test.com", timeout=30000)
    
    @pytest.mark.asyncio
    async def test_navigate_with_custom_timeout(self, mock_playwright_setup):
        """Test navigation with custom timeout."""
        mocks = mock_playwright_setup
        page = mocks["page"]
        
        async with NuxtDataExtractor(timeout=60000) as extractor:
            await extractor.navigate("https://test.com")
        
        page.goto.assert_called_once_with("https://test.com", timeout=60000)
    
    @pytest.mark.asyncio
    async def test_navigate_not_started(self):
        """Test navigation when extractor not started."""
        extractor = NuxtDataExtractor()
        
        with pytest.raises(RuntimeError, match="not started"):
            await extractor.navigate("https://test.com")
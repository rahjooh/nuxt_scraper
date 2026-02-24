"""Integration tests for nuxt_scraper functionality."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

import pytest

from nuxt_scraper import extract_nuxt_data, NuxtDataExtractor, NavigationStep
from nuxt_scraper.utils import StealthConfig
from nuxt_scraper.exceptions import NavigationStepFailed, NuxtDataNotFound


class TestEndToEndIntegration:
    """Test complete end-to-end workflows."""
    
    @patch("nuxt_scraper.extractor.async_playwright")
    @patch("nuxt_scraper.anti_detection.delays.human_delay", new_callable=AsyncMock)
    @patch("nuxt_scraper.anti_detection.mouse_movement.simulate_mouse_movement", new_callable=AsyncMock)
    @patch("nuxt_scraper.anti_detection.typing.human_type", new_callable=AsyncMock)
    def test_complete_workflow_with_navigation_and_deserialization(
        self, mock_human_type, mock_mouse_move, mock_human_delay, mock_async_playwright
    ):
        """Test complete workflow: navigation steps + extraction + deserialization."""
        # Setup mocks
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.set_default_timeout = MagicMock()
        mock_context.add_init_script = AsyncMock()
        mock_browser.close = AsyncMock()
        
        # Setup page mocks
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.click = AsyncMock()
        mock_page.fill = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock Nuxt 3 data extraction
        nuxt3_data = [
            {"state": 1},
            {
                "products": [2, 3],
                "user": 4,
                "timestamp": {"$d": 1672531200000}
            },
            {"id": 1, "name": "Product A", "price": 99.99},
            {"id": 2, "name": "Product B", "price": 149.99},
            {"name": "Alice", "role": "admin"}
        ]
        
        extraction_result = {
            "data": json.dumps(nuxt3_data),
            "method": "element",
            "raw": json.dumps(nuxt3_data)
        }
        mock_page.evaluate = AsyncMock(return_value=extraction_result)
        
        # Define navigation steps
        steps = [
            NavigationStep.click("button[data-accept-cookies]"),
            NavigationStep.fill("input[name='search']", "products"),
            NavigationStep.click("button[type='submit']"),
            NavigationStep.wait(".search-results", timeout=10000)
        ]
        
        # Execute workflow
        result = extract_nuxt_data(
            "https://ecommerce-site.com",
            steps=steps,
            headless=True,
            timeout=45000,
            deserialize_nuxt3=True
        )
        
        # Verify navigation was executed
        mock_page.goto.assert_called_once_with("https://ecommerce-site.com", timeout=45000)
        mock_page.wait_for_selector.assert_called()
        mock_page.click.assert_called()
        mock_page.fill.assert_called_with("input[name='search']", "products", timeout=5000)
        
        # Verify anti-detection was applied
        mock_human_delay.assert_called()
        
        # Verify data was deserialized correctly
        assert len(result["products"]) == 2
        assert result["products"][0]["name"] == "Product A"
        assert result["products"][1]["name"] == "Product B"
        assert result["user"]["name"] == "Alice"
        assert hasattr(result["timestamp"], "year")  # Date object
    
    @patch("nuxt_scraper.extractor.async_playwright")
    def test_stealth_configuration_integration(self, mock_async_playwright):
        """Test integration with stealth configuration."""
        # Setup mocks
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.set_default_timeout = MagicMock()
        mock_context.add_init_script = AsyncMock()
        mock_browser.close = AsyncMock()
        
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value={
            "data": '{"test": "data"}',
            "method": "element",
            "raw": '{"test": "data"}'
        })
        
        # Custom stealth config
        stealth_config = StealthConfig(
            random_delays=True,
            human_typing=True,
            mouse_movement=True,
            randomize_viewport=True,
            realistic_user_agent=True
        )
        
        with patch("nuxt_scraper.anti_detection.user_agents.get_realistic_user_agent") as mock_ua:
            with patch("nuxt_scraper.anti_detection.viewports.get_random_viewport") as mock_vp:
                mock_ua.return_value = "CustomUserAgent"
                mock_vp.return_value = (1920, 1080)
                
                result = extract_nuxt_data(
                    "https://protected-site.com",
                    stealth_config=stealth_config,
                    headless=True
                )
        
        # Verify stealth features were applied
        mock_ua.assert_called_once()
        mock_vp.assert_called_once()
        mock_context.add_init_script.assert_called()  # Stealth scripts
        
        # Verify context was created with stealth options
        context_kwargs = mock_browser.new_context.call_args[1]
        assert context_kwargs["user_agent"] == "CustomUserAgent"
        assert context_kwargs["viewport"] == {"width": 1920, "height": 1080}
        
        assert result == {"test": "data"}
    
    @patch("nuxt_scraper.extractor.async_playwright")
    def test_proxy_configuration_integration(self, mock_async_playwright):
        """Test integration with proxy configuration."""
        # Setup mocks
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.set_default_timeout = MagicMock()
        mock_context.add_init_script = AsyncMock()
        mock_browser.close = AsyncMock()
        
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value={
            "data": '{"proxy": "test"}',
            "method": "element",
            "raw": '{"proxy": "test"}'
        })
        
        # Proxy configuration
        proxy_config = {
            "server": "http://proxy.example.com:8080",
            "username": "user",
            "password": "pass"
        }
        
        result = extract_nuxt_data(
            "https://geo-restricted-site.com",
            proxy=proxy_config,
            headless=True
        )
        
        # Verify proxy was configured
        context_kwargs = mock_browser.new_context.call_args[1]
        assert context_kwargs["proxy"] == proxy_config
        
        assert result == {"proxy": "test"}


class TestErrorHandlingIntegration:
    """Test error handling across different components."""
    
    @patch("nuxt_scraper.extractor.async_playwright")
    @patch("nuxt_scraper.steps.execute_step")
    def test_navigation_step_failure_handling(self, mock_execute_step, mock_async_playwright):
        """Test handling of navigation step failures."""
        # Setup mocks
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.set_default_timeout = MagicMock()
        mock_context.add_init_script = AsyncMock()
        mock_browser.close = AsyncMock()
        
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock navigation step failure
        mock_execute_step.side_effect = NavigationStepFailed(
            NavigationStep.click("button.missing"),
            TimeoutError("Element not found")
        )
        
        steps = [NavigationStep.click("button.missing")]
        
        with pytest.raises(NavigationStepFailed):
            extract_nuxt_data(
                "https://test.com",
                steps=steps,
                headless=True
            )
    
    @patch("nuxt_scraper.extractor.async_playwright")
    def test_no_nuxt_data_found_handling(self, mock_async_playwright):
        """Test handling when no Nuxt data is found."""
        # Setup mocks
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.set_default_timeout = MagicMock()
        mock_context.add_init_script = AsyncMock()
        mock_browser.close = AsyncMock()
        
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock no data found
        mock_page.evaluate = AsyncMock(return_value={
            "data": None,
            "method": None,
            "raw": None
        })
        
        with pytest.raises(NuxtDataNotFound):
            extract_nuxt_data("https://no-nuxt-site.com", headless=True)


class TestRealWorldScenarios:
    """Test scenarios that mimic real-world usage."""
    
    @patch("nuxt_scraper.extractor.async_playwright")
    def test_ecommerce_product_scraping_scenario(self, mock_async_playwright):
        """Test e-commerce product scraping scenario."""
        # Setup mocks
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.set_default_timeout = MagicMock()
        mock_context.add_init_script = AsyncMock()
        mock_browser.close = AsyncMock()
        
        # Setup page interactions
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.click = AsyncMock()
        mock_page.fill = AsyncMock()
        mock_page.select_option = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock e-commerce data
        ecommerce_data = [
            {"state": 1},
            {
                "products": [2, 3, 4],
                "filters": {"category": "electronics", "priceRange": "100-500"},
                "pagination": {"page": 1, "totalPages": 5}
            },
            {
                "id": 1,
                "name": "Gaming Laptop",
                "price": 1299.99,
                "category": "electronics",
                "inStock": True,
                "lastUpdated": {"$d": 1672531200000}
            },
            {
                "id": 2,
                "name": "Wireless Mouse",
                "price": 49.99,
                "category": "electronics",
                "inStock": True,
                "lastUpdated": {"$d": 1672617600000}
            },
            {
                "id": 3,
                "name": "Mechanical Keyboard",
                "price": 149.99,
                "category": "electronics",
                "inStock": False,
                "lastUpdated": {"$d": 1672704000000}
            }
        ]
        
        mock_page.evaluate = AsyncMock(return_value={
            "data": json.dumps(ecommerce_data),
            "method": "element",
            "raw": json.dumps(ecommerce_data)
        })
        
        # Define e-commerce navigation steps
        steps = [
            NavigationStep.click("button[data-accept-cookies]"),
            NavigationStep.fill("input[name='search']", "gaming laptop"),
            NavigationStep.select("select[name='category']", "electronics"),
            NavigationStep.select("select[name='price-range']", "1000-2000"),
            NavigationStep.click("button[type='submit']"),
            NavigationStep.wait(".product-results", timeout=15000)
        ]
        
        result = extract_nuxt_data(
            "https://electronics-store.com",
            steps=steps,
            headless=True,
            timeout=60000,
            deserialize_nuxt3=True
        )
        
        # Verify the structure
        assert len(result["products"]) == 3
        assert result["products"][0]["name"] == "Gaming Laptop"
        assert result["products"][0]["price"] == 1299.99
        assert result["products"][0]["inStock"] is True
        assert hasattr(result["products"][0]["lastUpdated"], "year")
        
        assert result["filters"]["category"] == "electronics"
        assert result["pagination"]["totalPages"] == 5
        
        # Verify navigation was executed
        mock_page.fill.assert_called_with("input[name='search']", "gaming laptop", timeout=5000)
        mock_page.select_option.assert_any_call("select[name='category']", "electronics", timeout=5000)
        mock_page.select_option.assert_any_call("select[name='price-range']", "1000-2000", timeout=5000)
    
    @patch("nuxt_scraper.extractor.async_playwright")
    def test_racing_data_collection_scenario(self, mock_async_playwright):
        """Test racing data collection scenario."""
        # Setup mocks
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.set_default_timeout = MagicMock()
        mock_context.add_init_script = AsyncMock()
        mock_browser.close = AsyncMock()
        
        # Setup page interactions for calendar
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.click = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock locator for calendar interactions
        mock_locator = MagicMock()
        mock_locator.text_content = AsyncMock(return_value="Mar 2026")
        mock_locator.wait_for = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        # Mock racing data
        racing_data = [
            {"state": 1},
            {
                "meeting": 2,
                "races": [3, 4],
                "date": "2026-03-15"
            },
            {
                "venue": "Albion Park",
                "weather": "Fine",
                "track": "Good 4"
            },
            {
                "raceNumber": 1,
                "name": "Maiden Pace",
                "distance": 1660,
                "startTime": {"$d": 1672531200000},
                "runners": [5, 6]
            },
            {
                "raceNumber": 2,
                "name": "Open Pace",
                "distance": 2138,
                "startTime": {"$d": 1672534800000},
                "runners": [7, 8]
            },
            {"number": 1, "name": "Fast Horse", "barrier": 1, "odds": 3.50},
            {"number": 2, "name": "Quick Runner", "barrier": 2, "odds": 4.20},
            {"number": 1, "name": "Speed Demon", "barrier": 1, "odds": 2.80},
            {"number": 2, "name": "Lightning Bolt", "barrier": 2, "odds": 5.10}
        ]
        
        mock_page.evaluate = AsyncMock(return_value={
            "data": json.dumps(racing_data),
            "method": "element",
            "raw": json.dumps(racing_data)
        })
        
        # Define racing calendar navigation steps
        steps = [
            NavigationStep.click("input[data-date-picker]"),
            NavigationStep.select_date(
                target_date="2026-03-15",
                calendar_selector=".calendar-popup",
                prev_month_selector=".calendar-prev",
                next_month_selector=".calendar-next",
                month_year_display_selector=".calendar-month-year",
                date_cell_selector=".calendar-day",
                view_results_selector="button.view-results",
                timeout=20000
            )
        ]
        
        result = extract_nuxt_data(
            "https://racenet.com.au/form-guide/",
            steps=steps,
            headless=False,  # Calendar interaction often needs visible browser
            timeout=90000,
            deserialize_nuxt3=True
        )
        
        # Verify racing data structure
        assert result["meeting"]["venue"] == "Albion Park"
        assert result["meeting"]["track"] == "Good 4"
        assert len(result["races"]) == 2
        
        race1 = result["races"][0]
        assert race1["name"] == "Maiden Pace"
        assert race1["distance"] == 1660
        assert hasattr(race1["startTime"], "year")
        assert len(race1["runners"]) == 2
        assert race1["runners"][0]["name"] == "Fast Horse"
        
        # Verify calendar interaction
        mock_page.click.assert_any_call("input[data-date-picker]")
        mock_locator.click.assert_called()  # Date cell click


class TestDataPersistence:
    """Test data persistence and file operations."""
    
    @patch("nuxt_scraper.extractor.async_playwright")
    def test_data_extraction_and_save(self, mock_async_playwright):
        """Test extracting data and saving to file."""
        # Setup mocks
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.set_default_timeout = MagicMock()
        mock_context.add_init_script = AsyncMock()
        mock_browser.close = AsyncMock()
        
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        
        # Mock data with special types
        test_data = [
            {"state": 1},
            {
                "timestamp": {"$d": 1672531200000},
                "tags": {"$s": [2, 3]},
                "metadata": {"$m": [[4, 5]]},
                "count": {"$b": "123456789"},
                "pattern": {"$r": "/test/gi"}
            },
            "important",
            "urgent",
            "version",
            "1.0.0"
        ]
        
        mock_page.evaluate = AsyncMock(return_value={
            "data": json.dumps(test_data),
            "method": "element",
            "raw": json.dumps(test_data)
        })
        
        # Extract data
        result = extract_nuxt_data(
            "https://test-site.com",
            deserialize_nuxt3=True
        )
        
        # Verify deserialized structure
        assert hasattr(result["timestamp"], "year")
        assert isinstance(result["tags"], set)
        assert result["tags"] == {"important", "urgent"}
        assert isinstance(result["metadata"], dict)
        assert result["metadata"]["version"] == "1.0.0"
        assert isinstance(result["count"], int)
        assert result["count"] == 123456789
        assert hasattr(result["pattern"], "pattern")
        
        # Test saving to file (mock file operations)
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(result, f, default=str, indent=2)
            temp_file = f.name
        
        # Verify file was created and contains data
        temp_path = Path(temp_file)
        assert temp_path.exists()
        
        # Clean up
        temp_path.unlink()


class TestConcurrentExtractions:
    """Test concurrent extraction scenarios."""
    
    @patch("nuxt_scraper.extractor.async_playwright")
    async def test_multiple_extractors_concurrent(self, mock_async_playwright):
        """Test running multiple extractors concurrently."""
        import asyncio
        
        # Setup mocks
        mock_playwright = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        
        mock_async_playwright.return_value.start = AsyncMock(return_value=mock_playwright)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.set_default_timeout = MagicMock()
        mock_context.add_init_script = AsyncMock()
        mock_browser.close = AsyncMock()
        
        # Create separate pages for each extractor
        pages = []
        for i in range(3):
            mock_page = MagicMock()
            mock_page.goto = AsyncMock()
            mock_page.close = AsyncMock()
            mock_page.evaluate = AsyncMock(return_value={
                "data": json.dumps([{"state": 1}, {"site": i, "data": f"test_{i}"}]),
                "method": "element",
                "raw": "raw_data"
            })
            pages.append(mock_page)
        
        mock_context.new_page = AsyncMock(side_effect=pages)
        
        async def extract_from_site(site_id: int):
            """Extract data from a specific site."""
            async with NuxtDataExtractor() as extractor:
                return await extractor.extract(f"https://site{site_id}.com")
        
        # Run concurrent extractions
        tasks = [extract_from_site(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Verify results
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["site"] == i
            assert result["data"] == f"test_{i}"
        
        # Verify all pages were used
        assert mock_context.new_page.call_count == 3
        for page in pages:
            page.goto.assert_called_once()
            page.evaluate.assert_called_once()
"""
Error Handling and Debugging Examples

This example demonstrates comprehensive error handling, debugging techniques,
and recovery strategies for robust data extraction.
"""

import asyncio
import logging
from nuxt_scraper import (
    NuxtDataExtractor, extract_nuxt_data, NavigationStep,
    NuxtDataNotFound, NavigationStepFailed, ExtractionTimeout,
    DataParsingError, BrowserError, ProxyError
)


def setup_detailed_logging():
    """Configure detailed logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable specific loggers
    loggers = [
        'nuxt_scraper.extractor',
        'nuxt_scraper.parser', 
        'nuxt_scraper.steps',
        'playwright'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    print("🔍 Detailed logging enabled")


def basic_error_handling():
    """Basic error handling with try-catch."""
    print("🛡️ Basic Error Handling Example")
    
    urls_to_test = [
        "https://working-site.com",           # Should work
        "https://non-existent-site.xyz",     # DNS error
        "https://site-without-nuxt.com",     # No Nuxt data
        "https://very-slow-site.com"         # Timeout
    ]
    
    for url in urls_to_test:
        print(f"   Testing: {url}")
        
        try:
            data = extract_nuxt_data(
                url,
                headless=True,
                timeout=10000  # Short timeout for demo
            )
            print(f"   ✅ Success: {type(data).__name__}")
            
        except NuxtDataNotFound as e:
            print(f"   ⚠️ No Nuxt data found: {e}")
            
        except ExtractionTimeout as e:
            print(f"   ⏱️ Timeout occurred: {e}")
            
        except DataParsingError as e:
            print(f"   📝 Data parsing failed: {e}")
            
        except BrowserError as e:
            print(f"   🌐 Browser error: {e}")
            
        except Exception as e:
            print(f"   ❌ Unexpected error: {type(e).__name__}: {e}")


async def advanced_error_handling():
    """Advanced error handling with retry logic."""
    print("\n🔄 Advanced Error Handling with Retries")
    
    async def extract_with_retries(url, max_retries=3):
        """Extract data with automatic retry logic."""
        for attempt in range(max_retries):
            try:
                print(f"   Attempt {attempt + 1}/{max_retries}: {url}")
                
                async with NuxtDataExtractor(
                    headless=True,
                    timeout=30000
                ) as extractor:
                    data = await extractor.extract(url)
                    print(f"   ✅ Success on attempt {attempt + 1}")
                    return data
                    
            except ExtractionTimeout:
                print(f"   ⏱️ Timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except NuxtDataNotFound:
                print(f"   ⚠️ No Nuxt data found - no retry needed")
                break
                
            except BrowserError as e:
                print(f"   🌐 Browser error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"   ❌ Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
        
        print(f"   💥 All {max_retries} attempts failed")
        return None
    
    # Test retry logic
    test_urls = [
        "https://sometimes-slow-site.com",
        "https://unreliable-site.com"
    ]
    
    for url in test_urls:
        result = await extract_with_retries(url)
        if result:
            print(f"   📊 Final result type: {type(result).__name__}")


async def navigation_error_handling():
    """Handle errors in navigation steps."""
    print("\n🧭 Navigation Error Handling")
    
    async with NuxtDataExtractor(headless=False, timeout=45000) as extractor:
        try:
            # Steps that might fail
            steps = [
                NavigationStep.click("button.might-not-exist", timeout=5000),
                NavigationStep.fill("input.also-might-not-exist", "test"),
                NavigationStep.wait(".element-that-never-loads", timeout=10000)
            ]
            
            data = await extractor.extract(
                "https://problematic-site.com",
                steps=steps
            )
            
            print("   ✅ All navigation steps succeeded")
            
        except NavigationStepFailed as e:
            print(f"   🚫 Navigation step failed: {e}")
            print(f"   Failed step: {e.step}")
            print(f"   Error details: {e.original_error}")
            
            # Try to continue with current page state
            try:
                print("   🔄 Attempting extraction from current page...")
                data = await extractor.extract_from_current_page()
                print("   ✅ Partial extraction successful")
                
            except Exception as fallback_error:
                print(f"   ❌ Fallback extraction failed: {fallback_error}")


def proxy_error_handling():
    """Handle proxy-related errors."""
    print("\n🌐 Proxy Error Handling")
    
    # Test with various proxy configurations
    proxy_configs = [
        {"server": "http://working-proxy.com:8080"},
        {"server": "http://bad-proxy.com:8080"},
        {"server": "http://slow-proxy.com:8080"},
        None  # No proxy
    ]
    
    for i, proxy_config in enumerate(proxy_configs):
        proxy_desc = f"Proxy {i+1}" if proxy_config else "No proxy"
        print(f"   Testing {proxy_desc}...")
        
        try:
            data = extract_nuxt_data(
                "https://test-site.com",
                proxy=proxy_config,
                timeout=15000
            )
            print(f"   ✅ {proxy_desc}: Success")
            
        except ProxyError as e:
            print(f"   🌐 {proxy_desc}: Proxy error - {e}")
            
        except ExtractionTimeout as e:
            print(f"   ⏱️ {proxy_desc}: Timeout (possibly proxy issue)")
            
        except Exception as e:
            print(f"   ❌ {proxy_desc}: Other error - {e}")


async def debugging_techniques():
    """Demonstrate debugging techniques."""
    print("\n🔍 Debugging Techniques")
    
    # Enable detailed logging
    setup_detailed_logging()
    
    async with NuxtDataExtractor(
        headless=False,  # Visible browser for debugging
        timeout=60000
    ) as extractor:
        try:
            # Navigate to page
            await extractor.navigate("https://debug-target-site.com")
            
            # Take screenshot for debugging
            page = extractor._current_page
            if page:
                await page.screenshot(path="debug_screenshot.png")
                print("   📸 Screenshot saved: debug_screenshot.png")
                
                # Get page content for analysis
                content = await page.content()
                print(f"   📄 Page content length: {len(content):,} characters")
                
                # Check for Nuxt data elements
                nuxt_element = await page.query_selector("#__NUXT_DATA__")
                if nuxt_element:
                    print("   ✅ #__NUXT_DATA__ element found")
                    text_content = await nuxt_element.text_content()
                    print(f"   📊 Nuxt data length: {len(text_content or ''):,} characters")
                else:
                    print("   ⚠️ #__NUXT_DATA__ element not found")
                
                # Check for window.__NUXT__
                window_nuxt = await page.evaluate("() => window.__NUXT__")
                if window_nuxt:
                    print("   ✅ window.__NUXT__ found")
                else:
                    print("   ⚠️ window.__NUXT__ not found")
            
            # Attempt extraction
            data = await extractor.extract_from_current_page()
            print("   ✅ Extraction successful")
            
        except Exception as e:
            print(f"   ❌ Debugging session failed: {e}")
            
            # Additional debugging info
            if hasattr(e, '__dict__'):
                print("   🔍 Error details:")
                for key, value in e.__dict__.items():
                    print(f"     {key}: {value}")


async def graceful_degradation():
    """Implement graceful degradation strategies."""
    print("\n🛟 Graceful Degradation Strategies")
    
    url = "https://challenging-site.com"
    
    # Strategy 1: Try different extraction methods
    extraction_strategies = [
        ("Combined extraction", {"use_combined_extraction": True}),
        ("Legacy extraction", {"use_combined_extraction": False}),
        ("No deserialization", {"deserialize_nuxt3": False}),
        ("Extended timeout", {"timeout": 60000})
    ]
    
    for strategy_name, options in extraction_strategies:
        print(f"   Trying {strategy_name}...")
        
        try:
            async with NuxtDataExtractor(headless=True, **options) as extractor:
                data = await extractor.extract(url)
                print(f"   ✅ {strategy_name}: Success")
                return data
                
        except Exception as e:
            print(f"   ❌ {strategy_name}: Failed - {e}")
    
    # Strategy 2: Fallback to manual page content
    print("   Trying manual page content extraction...")
    
    try:
        async with NuxtDataExtractor(headless=True) as extractor:
            await extractor.navigate(url)
            page = extractor._current_page
            
            if page:
                # Get raw page content as fallback
                content = await page.content()
                print(f"   ✅ Manual extraction: Got {len(content):,} chars of HTML")
                return {"fallback_content": content[:1000] + "..."}
                
    except Exception as e:
        print(f"   ❌ Manual extraction failed: {e}")
    
    print("   💥 All strategies failed - no data available")
    return None


async def error_reporting_and_monitoring():
    """Implement error reporting and monitoring."""
    print("\n📊 Error Reporting and Monitoring")
    
    error_stats = {
        "total_attempts": 0,
        "successful": 0,
        "timeout_errors": 0,
        "nuxt_not_found": 0,
        "navigation_errors": 0,
        "other_errors": 0
    }
    
    test_urls = [
        "https://good-site.com",
        "https://slow-site.com", 
        "https://no-nuxt-site.com",
        "https://broken-site.com"
    ]
    
    for url in test_urls:
        error_stats["total_attempts"] += 1
        
        try:
            data = extract_nuxt_data(url, timeout=15000)
            error_stats["successful"] += 1
            print(f"   ✅ {url}: Success")
            
        except ExtractionTimeout:
            error_stats["timeout_errors"] += 1
            print(f"   ⏱️ {url}: Timeout")
            
        except NuxtDataNotFound:
            error_stats["nuxt_not_found"] += 1
            print(f"   ⚠️ {url}: No Nuxt data")
            
        except NavigationStepFailed:
            error_stats["navigation_errors"] += 1
            print(f"   🧭 {url}: Navigation failed")
            
        except Exception as e:
            error_stats["other_errors"] += 1
            print(f"   ❌ {url}: {type(e).__name__}")
    
    # Generate error report
    print(f"\n📈 Error Statistics:")
    print(f"   Total attempts: {error_stats['total_attempts']}")
    print(f"   Successful: {error_stats['successful']} ({error_stats['successful']/error_stats['total_attempts']*100:.1f}%)")
    print(f"   Timeouts: {error_stats['timeout_errors']}")
    print(f"   No Nuxt data: {error_stats['nuxt_not_found']}")
    print(f"   Navigation errors: {error_stats['navigation_errors']}")
    print(f"   Other errors: {error_stats['other_errors']}")
    
    success_rate = error_stats['successful'] / error_stats['total_attempts'] * 100
    if success_rate > 80:
        print("   ✅ Good success rate")
    elif success_rate > 50:
        print("   ⚠️ Moderate success rate - consider optimizations")
    else:
        print("   ❌ Low success rate - review extraction strategy")


async def main():
    """Run all error handling examples."""
    print("🛡️ Error Handling and Debugging Examples")
    print("=" * 50)
    
    basic_error_handling()
    await advanced_error_handling()
    await navigation_error_handling()
    proxy_error_handling()
    await debugging_techniques()
    await graceful_degradation()
    await error_reporting_and_monitoring()
    
    print("\n✨ All error handling examples completed!")
    print("💡 Key takeaways:")
    print("   - Always handle specific exceptions")
    print("   - Implement retry logic for transient failures")
    print("   - Use logging for debugging complex issues")
    print("   - Have fallback strategies for critical applications")
    print("   - Monitor error rates to improve reliability")


if __name__ == "__main__":
    asyncio.run(main())
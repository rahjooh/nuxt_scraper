"""
Navigation Steps Examples

This example shows how to interact with web pages before extracting Nuxt data.
Covers clicking, filling forms, waiting, scrolling, and other navigation actions.
"""

import asyncio
from nuxt_scraper import NuxtDataExtractor, NavigationStep


async def click_and_extract():
    """Click elements before extracting data."""
    print("🖱️ Click Navigation Example")
    
    async with NuxtDataExtractor(headless=False) as extractor:
        try:
            steps = [
                # Click a tab or button
                NavigationStep.click("button[data-tab='products']"),
                
                # Wait for content to load after clicking
                NavigationStep.wait(".products-loaded", timeout=10000),
            ]
            
            data = await extractor.extract(
                "https://your-ecommerce-site.com",
                steps=steps
            )
            
            print(f"✅ Data extracted after navigation")
            print(f"📊 Result type: {type(data)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def form_filling_example():
    """Fill forms before extracting data."""
    print("\n📝 Form Filling Example")
    
    async with NuxtDataExtractor(headless=False) as extractor:
        try:
            steps = [
                # Fill search form
                NavigationStep.fill("input[name='search']", "racing results"),
                
                # Select dropdown option
                NavigationStep.select("select[name='category']", "sports"),
                
                # Click search button
                NavigationStep.click("button[type='submit']"),
                
                # Wait for results to load
                NavigationStep.wait(".search-results", timeout=15000),
            ]
            
            data = await extractor.extract(
                "https://your-search-site.com",
                steps=steps
            )
            
            print(f"✅ Data extracted after form submission")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def scroll_and_hover_example():
    """Scroll and hover interactions."""
    print("\n📜 Scroll and Hover Example")
    
    async with NuxtDataExtractor(headless=False) as extractor:
        try:
            steps = [
                # Scroll to trigger lazy loading
                NavigationStep.scroll("footer", timeout=5000),
                
                # Hover over menu to show dropdown
                NavigationStep.hover(".menu-item", wait_after_selector=".dropdown-menu"),
                
                # Click item in dropdown
                NavigationStep.click(".dropdown-menu a[href='/data']"),
                
                # Wait for page to load
                NavigationStep.wait(".data-loaded", timeout=10000),
            ]
            
            data = await extractor.extract(
                "https://your-site-with-lazy-content.com",
                steps=steps
            )
            
            print(f"✅ Data extracted after scroll and hover")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def complex_navigation_flow():
    """Complex multi-step navigation example."""
    print("\n🔄 Complex Navigation Flow Example")
    
    async with NuxtDataExtractor(headless=False, timeout=60000) as extractor:
        try:
            steps = [
                # Accept cookies
                NavigationStep.click("button[data-accept-cookies]"),
                
                # Navigate to login
                NavigationStep.click("a[href='/login']"),
                NavigationStep.wait("form[name='login']"),
                
                # Fill login form
                NavigationStep.fill("input[name='username']", "demo_user"),
                NavigationStep.fill("input[name='password']", "demo_pass"),
                NavigationStep.click("button[type='submit']"),
                
                # Wait for dashboard
                NavigationStep.wait(".dashboard-loaded"),
                
                # Navigate to data section
                NavigationStep.click("nav a[href='/dashboard/data']"),
                NavigationStep.wait(".data-table"),
                
                # Apply filters
                NavigationStep.select("select[name='date_range']", "last_week"),
                NavigationStep.click("button[data-action='apply-filters']"),
                
                # Wait for filtered results
                NavigationStep.wait(".filtered-results", timeout=20000),
            ]
            
            data = await extractor.extract(
                "https://your-dashboard-app.com",
                steps=steps
            )
            
            print(f"✅ Data extracted after complex navigation")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run all navigation examples."""
    print("🧭 Navigation Steps Examples")
    print("=" * 50)
    
    await click_and_extract()
    await form_filling_example()
    await scroll_and_hover_example()
    await complex_navigation_flow()
    
    print("\n✨ All navigation examples completed!")
    print("💡 Customize the selectors and URLs for your target sites.")


if __name__ == "__main__":
    asyncio.run(main())
"""Example: Using dismiss_popups NavigationStep to handle advertisements and modals

This example demonstrates how to use the dismiss_popups step to automatically
handle common popup advertisements, cookie banners, and modal overlays that
might interfere with data extraction.
"""

import asyncio
from nuxt_scraper import NuxtDataExtractor, NavigationStep
from nuxt_scraper.utils import StealthConfig


async def basic_popup_dismissal():
    """Basic example of dismissing popups on page load."""
    
    stealth_config = StealthConfig(
        random_delays=True,
        min_action_delay_ms=500,
        max_action_delay_ms=2000,
    )
    
    async with NuxtDataExtractor(
        headless=False,
        stealth_config=stealth_config
    ) as extractor:
        
        # Navigate to a site and immediately dismiss any popups
        steps = [
            NavigationStep.dismiss_popups(timeout=5000),  # Handle initial popups
            NavigationStep.wait(".main-content", timeout=10000),  # Wait for main content
        ]
        
        data = await extractor.extract(
            "https://example-site-with-ads.com",
            steps=steps,
            wait_for_nuxt=True,
            timeout=30000
        )
        
        print("✅ Data extracted successfully after dismissing popups")
        return data


async def racenet_with_popup_handling():
    """Example: Enhanced racenet scraping with popup dismissal."""
    
    stealth_config = StealthConfig(
        random_delays=True,
        min_action_delay_ms=1000,
        max_action_delay_ms=3000,
        human_typing=True,
        mouse_movement=True,
    )
    
    async with NuxtDataExtractor(
        headless=False,
        timeout=60000,
        stealth_config=stealth_config
    ) as extractor:
        
        steps = [
            # Step 1: Dismiss any initial popups/ads
            NavigationStep.dismiss_popups(timeout=5000),
            
            # Step 2: Click on a tab (e.g., Tomorrow)
            NavigationStep.click("a:has-text('Tomorrow')", timeout=5000),
            
            # Step 3: Dismiss any popups that appear after navigation
            NavigationStep.dismiss_popups(timeout=3000),
            
            # Step 4: Wait for content to load
            NavigationStep.wait(".selection-result", timeout=10000),
        ]
        
        data = await extractor.extract(
            "https://www.racenet.com.au/form-guide/harness",
            steps=steps,
            use_combined_extraction=True,
            wait_for_nuxt=True,
            wait_for_nuxt_timeout=20000
        )
        
        print("✅ Racenet data extracted with popup handling")
        return data


async def calendar_navigation_with_popups():
    """Example: Calendar navigation with comprehensive popup handling."""
    
    stealth_config = StealthConfig(
        random_delays=True,
        min_action_delay_ms=800,
        max_action_delay_ms=2500,
        human_typing=True,
        mouse_movement=True,
    )
    
    async with NuxtDataExtractor(
        headless=False,
        timeout=60000,
        stealth_config=stealth_config
    ) as extractor:
        
        steps = [
            # Step 1: Initial popup dismissal
            NavigationStep.dismiss_popups(timeout=5000),
            
            # Step 2: Click to open calendar
            NavigationStep.click("a.tab:has-text('Select Date')", timeout=5000),
            
            # Step 3: Dismiss any popups that appear after clicking
            NavigationStep.dismiss_popups(timeout=3000),
            
            # Step 4: Navigate calendar to specific date
            NavigationStep.select_date(
                target_date="2021-02-20",
                calendar_selector=".vdp-datepicker__calendar",
                prev_month_selector=".vdp-datepicker__calendar .prev",
                next_month_selector=".vdp-datepicker__calendar .next",
                month_year_display_selector=".vdp-datepicker__calendar header span.up",
                date_cell_selector="span.cell.day",
                view_results_selector="button:has-text('View Results')",
                timeout=30000
            ),
            
            # Step 5: Final popup dismissal after calendar navigation
            NavigationStep.dismiss_popups(timeout=3000),
            
            # Step 6: Wait for results to load
            NavigationStep.wait(".selection-result", timeout=15000),
        ]
        
        data = await extractor.extract(
            "https://www.racenet.com.au/results/harness",
            steps=steps,
            use_combined_extraction=True,
            wait_for_nuxt=True,
            wait_for_nuxt_timeout=20000
        )
        
        print("✅ Historical data extracted with calendar navigation and popup handling")
        return data


async def advanced_popup_handling_workflow():
    """Advanced example showing popup handling in a complex workflow."""
    
    stealth_config = StealthConfig(
        random_delays=True,
        min_action_delay_ms=1000,
        max_action_delay_ms=3000,
        human_typing=True,
        typing_speed_wpm=65,
        typo_chance=0.02,
        mouse_movement=True,
    )
    
    async with NuxtDataExtractor(
        headless=False,
        timeout=90000,
        stealth_config=stealth_config
    ) as extractor:
        
        # Multi-step workflow with popup handling at each stage
        workflow_steps = [
            # Initial page load
            NavigationStep.dismiss_popups(timeout=5000),
            NavigationStep.wait("body", timeout=5000),
            
            # Navigation to specific section
            NavigationStep.click("a[href='/specific-section']", timeout=5000),
            NavigationStep.dismiss_popups(timeout=3000),  # Handle navigation popups
            
            # Form interaction
            NavigationStep.fill("input[name='search']", "harness racing", timeout=5000),
            NavigationStep.dismiss_popups(timeout=2000),  # Handle search popups
            
            # Submit and wait for results
            NavigationStep.click("button[type='submit']", timeout=5000),
            NavigationStep.dismiss_popups(timeout=3000),  # Handle result popups
            NavigationStep.wait(".results-loaded", timeout=15000),
            
            # Final cleanup
            NavigationStep.dismiss_popups(timeout=2000),
        ]
        
        data = await extractor.extract(
            "https://example-complex-site.com",
            steps=workflow_steps,
            use_combined_extraction=True,
            wait_for_nuxt=True,
            wait_for_nuxt_timeout=25000
        )
        
        print("✅ Complex workflow completed with comprehensive popup handling")
        return data


if __name__ == "__main__":
    print("🚀 Popup Dismissal Examples")
    print("=" * 50)
    
    # Run basic example
    print("\n1. Basic popup dismissal example...")
    try:
        asyncio.run(basic_popup_dismissal())
    except Exception as e:
        print(f"❌ Basic example failed: {e}")
    
    # Run racenet example
    print("\n2. Racenet with popup handling...")
    try:
        asyncio.run(racenet_with_popup_handling())
    except Exception as e:
        print(f"❌ Racenet example failed: {e}")
    
    # Run calendar example
    print("\n3. Calendar navigation with popups...")
    try:
        asyncio.run(calendar_navigation_with_popups())
    except Exception as e:
        print(f"❌ Calendar example failed: {e}")
    
    print("\n✅ All examples completed!")
    print("\n💡 Key takeaways:")
    print("   - Use dismiss_popups() at page load and after major navigation")
    print("   - Combine with appropriate timeouts (3-5 seconds usually sufficient)")
    print("   - Place before critical interactions to ensure clean page state")
    print("   - Can be used multiple times in a single workflow")

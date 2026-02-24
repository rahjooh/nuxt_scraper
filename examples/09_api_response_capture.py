"""Generic API Response Capture Pattern

This example demonstrates the general pattern for capturing API responses
during navigation, which is essential when:
- Calendar navigation or tab clicks trigger API calls
- window.__NUXT__ doesn't update after user interactions
- You need to access the freshest data from API responses

This pattern is applicable to any Nuxt site with dynamic content loading.
"""

import asyncio
from nuxt_scraper import NuxtDataExtractor, NavigationStep, validate_meeting_date
from nuxt_scraper.utils import StealthConfig


async def example_with_default_filter():
    """Example using the default API filter (puntapi.com and graphql)."""
    print("=" * 70)
    print("Example 1: Using Default API Filter")
    print("=" * 70)
    
    async with NuxtDataExtractor(headless=False) as extractor:
        # extract_with_api_capture returns (nuxt_data, api_responses)
        nuxt_data, api_responses = await extractor.extract_with_api_capture(
            "https://www.racenet.com.au/results/harness",
            steps=[
                NavigationStep.click("a.tab:has-text('Select Date')"),
                NavigationStep.select_date(
                    target_date="2025-02-20",
                    calendar_selector=".vdp-datepicker__calendar",
                    prev_month_selector=".vdp-datepicker__calendar .prev",
                    next_month_selector=".vdp-datepicker__calendar .next",
                    month_year_display_selector=".vdp-datepicker__calendar header span.up",
                    date_cell_selector=".cell.day",
                    view_results_selector="button:has-text('View Results')",
                    timeout=20000
                )
            ]
        )
        
        print(f"\n📊 Results:")
        print(f"  - Captured {len(api_responses)} API responses")
        print(f"  - window.__NUXT__ available: {nuxt_data is not None}")
        
        # Find specific API response
        meetings_response = extractor.find_api_response(
            api_responses,
            "meetingsGroupedByStartEndDate"
        )
        
        if meetings_response:
            print(f"\n✅ Found target API response:")
            print(f"  - URL: {meetings_response['url'][:80]}...")
            
            # Validate the data
            if validate_meeting_date(meetings_response["data"], "2025-02-20"):
                print(f"  - Date validation: ✅ PASSED")
            else:
                print(f"  - Date validation: ❌ FAILED")
        else:
            print(f"\n⚠️  Target API response not found")


async def example_with_custom_filter():
    """Example using a custom API filter."""
    print("\n" + "=" * 70)
    print("Example 2: Using Custom API Filter")
    print("=" * 70)
    
    # Define custom filter to capture all JSON responses from any API
    def custom_api_filter(response):
        """Capture all successful JSON responses containing 'api' in URL."""
        return (
            response.status == 200
            and "api" in response.url.lower()
        )
    
    async with NuxtDataExtractor(headless=False) as extractor:
        nuxt_data, api_responses = await extractor.extract_with_api_capture(
            "https://example-nuxt-site.com",
            api_filter=custom_api_filter  # Use custom filter
        )
        
        print(f"\n📊 Captured {len(api_responses)} API responses with custom filter")
        
        # Print all captured URLs
        for i, resp in enumerate(api_responses, 1):
            print(f"  {i}. {resp['url'][:80]}...")


async def example_finding_responses():
    """Example demonstrating different ways to find API responses."""
    print("\n" + "=" * 70)
    print("Example 3: Finding Specific API Responses")
    print("=" * 70)
    
    async with NuxtDataExtractor(headless=False) as extractor:
        nuxt_data, api_responses = await extractor.extract_with_api_capture(
            "https://www.racenet.com.au/form-guide/harness"
        )
        
        print(f"\n📊 Captured {len(api_responses)} API responses")
        
        # Method 1: Find by URL pattern
        print("\n🔍 Method 1: Find by URL pattern")
        meetings_resp = extractor.find_api_response(api_responses, "meetings")
        if meetings_resp:
            print(f"  ✅ Found: {meetings_resp['url'][:80]}...")
        else:
            print(f"  ❌ Not found")
        
        # Method 2: Find with fallback
        print("\n🔍 Method 2: Find with fallback to first response")
        any_resp = extractor.find_api_response(
            api_responses,
            "nonexistent-pattern",
            fallback_to_first=True
        )
        if any_resp:
            print(f"  ✅ Fallback used: {any_resp['url'][:80]}...")
        
        # Method 3: Manual search with custom logic
        print("\n🔍 Method 3: Manual search with custom logic")
        for resp in api_responses:
            if "graphql" in resp["url"].lower():
                print(f"  ✅ Found GraphQL: {resp['url'][:80]}...")
                break


async def example_date_validation():
    """Example demonstrating date validation utility."""
    print("\n" + "=" * 70)
    print("Example 4: Date Validation")
    print("=" * 70)
    
    # Simulate API response data
    api_data = {
        "data": {
            "meetingsGrouped": [
                {
                    "meetings": [
                        {
                            "meetingDateLocal": "2025-02-20T00:00:00.000Z",
                            "name": "Example Meeting"
                        }
                    ]
                }
            ]
        }
    }
    
    # Validate with ISO datetime format
    print("\n🔍 Validating ISO datetime format:")
    if validate_meeting_date(api_data, "2025-02-20"):
        print("  ✅ Date validation passed (ISO format)")
    else:
        print("  ❌ Date validation failed")
    
    # Simulate __NUXT__ data
    nuxt_data = {
        "data": [
            {
                "meetings": [
                    {
                        "meetings": [
                            {
                                "meetingDateLocal": "2025-02-20",
                                "name": "Example Meeting"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    # Validate with simple date format
    print("\n🔍 Validating simple date format:")
    if validate_meeting_date(nuxt_data, "2025-02-20"):
        print("  ✅ Date validation passed (simple format)")
    else:
        print("  ❌ Date validation failed")


async def example_stealth_config():
    """Example with stealth configuration for realistic browsing."""
    print("\n" + "=" * 70)
    print("Example 5: API Capture with Stealth Configuration")
    print("=" * 70)
    
    # Configure stealth settings
    stealth = StealthConfig(
        random_delays=True,
        min_action_delay_ms=500,
        max_action_delay_ms=2000,
        human_typing=True,
        typing_speed_wpm=65,
        mouse_movement=True,
        randomize_viewport=True,
        realistic_user_agent=True
    )
    
    async with NuxtDataExtractor(
        headless=False,
        stealth_config=stealth
    ) as extractor:
        print("\n🕵️  Using stealth configuration for anti-detection")
        
        nuxt_data, api_responses = await extractor.extract_with_api_capture(
            "https://www.racenet.com.au/form-guide/harness"
        )
        
        print(f"  ✅ Captured {len(api_responses)} API responses with stealth enabled")


async def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("API Response Capture - Comprehensive Examples")
    print("=" * 70)
    print("\nThese examples demonstrate various patterns for capturing API responses")
    print("during navigation, which is essential for dynamic content extraction.")
    print("\nNote: Some examples require actual sites to run. Adjust URLs as needed.")
    print("=" * 70)
    
    # Run examples (comment out as needed)
    try:
        # Example 1: Default filter with calendar navigation
        # await example_with_default_filter()
        
        # Example 2: Custom API filter
        # await example_with_custom_filter()
        
        # Example 3: Finding specific responses
        # await example_finding_responses()
        
        # Example 4: Date validation (no network required)
        await example_date_validation()
        
        # Example 5: Stealth configuration
        # await example_stealth_config()
        
        print("\n" + "=" * 70)
        print("✅ Examples completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())


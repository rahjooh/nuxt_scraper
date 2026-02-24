"""Racenet Tomorrow's Races - Tab Navigation with API Capture

This example demonstrates:
- Clicking the "Tomorrow" tab to navigate to future races
- API response capture for tab-based navigation
- Date validation for dynamically loaded content
- Extracting race URLs from meetings data

Key Pattern: Similar to calendar navigation, clicking tabs triggers API calls
but window.__NUXT__ doesn't update. We capture API responses to get fresh data.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

from nuxt_scraper import NuxtDataExtractor, NavigationStep, validate_meeting_date
from nuxt_scraper.utils import StealthConfig


# Configuration
MEETINGS_URL = "https://www.racenet.com.au/form-guide/harness"
BASE_URL = "https://www.racenet.com.au/form-guide/harness"
OUTPUT_DIR = Path("data/racenet_tomorrow")

# Stealth configuration
stealth_config = StealthConfig(
    random_delays=True,
    min_action_delay_ms=500,
    max_action_delay_ms=2000,
    human_typing=True,
    mouse_movement=True,
    randomize_viewport=True,
    realistic_user_agent=True
)


async def extract_tomorrow_meetings() -> dict:
    """Extract tomorrow's meetings by clicking the Tomorrow tab.
    
    Returns:
        Meetings data or None if extraction fails
    """
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"\n📅 Extracting meetings for tomorrow ({tomorrow})...")
    
    async with NuxtDataExtractor(
        headless=False,
        timeout=60000,
        stealth_config=stealth_config
    ) as extractor:
        
        # Navigate to the page first
        await extractor.navigate(MEETINGS_URL)
        await asyncio.sleep(2)
        
        # Set up API capture and click Tomorrow tab
        # We need to attach the handler after initial navigation
        pages = extractor._context.pages
        page = pages[0] if pages else await extractor._context.new_page()
        
        api_responses = []
        
        async def handle_response(response):
            # Capture racing API responses
            if ("puntapi.com/racing" in response.url 
                and "meetingsIndexByStartEndDate" in response.url 
                and response.status == 200):
                try:
                    data = await response.json()
                    api_responses.append({"url": response.url, "data": data})
                    print(f"  📡 Captured API response")
                except Exception:
                    pass
        
        page.on("response", handle_response)
        
        # Click Tomorrow tab
        print("  🖱️  Clicking 'Tomorrow' tab...")
        try:
            tomorrow_link = await page.wait_for_selector(
                "a:has-text('Tomorrow')", 
                timeout=5000
            )
            await tomorrow_link.click()
            print("  ✅ Clicked Tomorrow")
            
            # Wait for content to update and API calls to complete
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"  ❌ Could not click Tomorrow: {e}")
            return None
        
        # Use the API response data (most reliable)
        if api_responses:
            print("  ✅ Using API response data")
            data = api_responses[0]["data"]
            
            # Validate date
            if validate_meeting_date(data, tomorrow):
                print(f"  ✅ Date validation passed: {tomorrow}")
                return data
            else:
                print(f"  ⚠️  Date mismatch - expected {tomorrow}")
                return data  # Return anyway, might still be useful
        else:
            print("  ⚠️  No API response captured, falling back to __NUXT__")
            try:
                return await extractor.extract_from_current_page(
                    use_combined_extraction=True,
                    deserialize_nuxt3=False
                )
            except Exception as e:
                print(f"  ❌ Error extracting data: {e}")
                return None


def extract_race_urls(meetings_data: dict, tomorrow: str) -> list:
    """Extract race URLs from meetings data.
    
    Args:
        meetings_data: Extracted meetings data
        tomorrow: Tomorrow's date in YYYY-MM-DD format
        
    Returns:
        List of race dictionaries with url, name, and num
    """
    races = []
    
    # Handle API response format
    if isinstance(meetings_data, dict) and "data" in meetings_data:
        api_data = meetings_data.get("data", {})
        
        if "meetingsGrouped" in api_data:
            # API format
            for group in api_data["meetingsGrouped"]:
                for meeting in group.get("meetings", []):
                    meeting_slug = meeting.get("slug", "")
                    meeting_name = meeting.get("name", "").lower().replace(" ", "-").replace("'", "")
                    
                    for event in meeting.get("events", []):
                        # Only get unresulted races (upcoming)
                        if not event.get("isResulted", True):
                            race_slug = event.get("slug", "")
                            race_num = event.get("eventNumber", 0)
                            
                            if race_slug:
                                races.append({
                                    "url": f"{BASE_URL}/{meeting_slug}/{race_slug}/overview",
                                    "name": meeting_name,
                                    "num": race_num
                                })
    
    return races


def save_data(data: dict, tomorrow: str):
    """Save meetings data to JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = OUTPUT_DIR / f"racenet-harness-tomorrow-{tomorrow}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Saved to: {output_file}")


async def main():
    """Main execution flow."""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print("=" * 70)
    print(f"Racenet Tomorrow's Races - Tab Navigation Example ({tomorrow})")
    print("=" * 70)
    
    # Extract tomorrow's meetings
    meetings_data = await extract_tomorrow_meetings()
    
    if not meetings_data:
        print("\n❌ Failed to extract tomorrow's meetings")
        return
    
    # Save meetings data
    save_data(meetings_data, tomorrow)
    
    # Extract race URLs
    races = extract_race_urls(meetings_data, tomorrow)
    print(f"\n🏁 Found {len(races)} upcoming races for tomorrow")
    
    # Print first few races as examples
    for i, race in enumerate(races[:5], 1):
        print(f"  {i}. {race['name']} - Race {race['num']}")
    
    if len(races) > 5:
        print(f"  ... and {len(races) - 5} more races")
    
    print("\n✅ Extraction completed successfully!")
    print(f"💡 Tip: You can now scrape individual races using the URLs in the output")


if __name__ == "__main__":
    asyncio.run(main())


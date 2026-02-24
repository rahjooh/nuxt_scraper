"""Racenet Historical Data - Calendar Navigation with API Capture

This example demonstrates:
- Calendar navigation to select a specific historical date
- API response capture for dynamic content
- Date validation to ensure correct data extraction
- Handling cases where window.__NUXT__ doesn't update after navigation

Key Pattern: When navigating calendars, the page makes API calls to fetch new data,
but window.__NUXT__ retains the original page load data. We must capture API responses
to get the correct data for the selected date.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from nuxt_scraper import NuxtDataExtractor, NavigationStep, validate_meeting_date
from nuxt_scraper.utils import StealthConfig


# Configuration
TARGET_DATE = "2025-02-20"  # Historical date to scrape
RESULTS_URL = "https://www.racenet.com.au/results/harness"
OUTPUT_DIR = Path("data/racenet_historical")

# Calendar widget selectors
CALENDAR_SELECTORS = {
    "select_date_button": "a.tab:has-text('Select Date')",
    "calendar_selector": ".vdp-datepicker__calendar",
    "month_year_display": ".vdp-datepicker__calendar header span.up",
    "prev_month": ".vdp-datepicker__calendar header .prev",
    "next_month": ".vdp-datepicker__calendar header .next",
    "date_cell": "span.cell.day",
    "view_results": "button:has-text('View Results')",
}

# Stealth configuration for realistic browsing
stealth_config = StealthConfig(
    random_delays=True,
    min_action_delay_ms=500,
    max_action_delay_ms=2000,
    human_typing=True,
    mouse_movement=True,
    randomize_viewport=True,
    realistic_user_agent=True
)


async def extract_historical_data(target_date: str) -> dict:
    """Extract historical race data by navigating calendar to target date.
    
    Args:
        target_date: Date in YYYY-MM-DD format
        
    Returns:
        Extracted meetings data or None if extraction fails
    """
    print(f"\n📅 Extracting data for {target_date}...")
    
    async with NuxtDataExtractor(
        headless=False,
        timeout=60000,
        stealth_config=stealth_config
    ) as extractor:
        
        # Use extract_with_api_capture to capture API responses during navigation
        nuxt_data, api_responses = await extractor.extract_with_api_capture(
            RESULTS_URL,
            steps=[
                # Step 1: Click "Select Date" to open calendar
                NavigationStep.click(
                    CALENDAR_SELECTORS["select_date_button"],
                    timeout=5000
                ),
                # Step 2: Navigate calendar and select target date
                NavigationStep.select_date(
                    target_date=target_date,
                    calendar_selector=CALENDAR_SELECTORS["calendar_selector"],
                    prev_month_selector=CALENDAR_SELECTORS["prev_month"],
                    next_month_selector=CALENDAR_SELECTORS["next_month"],
                    month_year_display_selector=CALENDAR_SELECTORS["month_year_display"],
                    date_cell_selector=CALENDAR_SELECTORS["date_cell"],
                    view_results_selector=CALENDAR_SELECTORS["view_results"],
                    timeout=30000
                )
            ]
        )
        
        print(f"📡 Captured {len(api_responses)} API responses")
        
        # Find the specific API response containing the updated data
        # After calendar navigation, the fresh data is in the API response, not __NUXT__
        meetings_response = extractor.find_api_response(
            api_responses,
            "meetingsGroupedByStartEndDate"  # URL pattern to search for
        )
        
        if meetings_response:
            print("✅ Found meetingsGroupedByStartEndDate API response")
            data = meetings_response["data"]
            
            # Validate the date matches what we selected
            if validate_meeting_date(data, target_date):
                print(f"✅ Date validation passed: {target_date}")
                return data
            else:
                print(f"❌ Date mismatch - expected {target_date}")
                return None
        else:
            print("⚠️  API response not found, falling back to __NUXT__")
            print("⚠️  Note: __NUXT__ may contain stale data after calendar navigation")
            return nuxt_data


def extract_race_urls(meetings_data: dict, target_date: str) -> list:
    """Extract race URLs from meetings data.
    
    Args:
        meetings_data: Extracted meetings data
        target_date: Target date in YYYY-MM-DD format
        
    Returns:
        List of race dictionaries with url, name, and num
    """
    races = []
    BASE_URL = "https://www.racenet.com.au/results/harness"
    
    # Handle API response format
    if isinstance(meetings_data, dict) and "data" in meetings_data:
        api_data = meetings_data.get("data", {})
        
        if "meetingsGrouped" in api_data:
            # API format
            for group in api_data["meetingsGrouped"]:
                for meeting in group.get("meetings", []):
                    meeting_date = meeting.get("meetingDateLocal", "")
                    # Extract just the date part if it's an ISO datetime string
                    meeting_date_only = meeting_date.split("T")[0] if "T" in meeting_date else meeting_date
                    if meeting_date_only != target_date:
                        continue
                    
                    meeting_slug = meeting.get("slug", "")
                    meeting_name = meeting.get("name", "").lower().replace(" ", "-").replace("'", "")
                    
                    for event in meeting.get("events", []):
                        # For historical data, we want resulted races
                        if event.get("isResulted", False):
                            race_slug = event.get("slug", "")
                            race_num = event.get("eventNumber", 0)
                            
                            if race_slug:
                                races.append({
                                    "url": f"{BASE_URL}/{meeting_slug}/{race_slug}",
                                    "name": meeting_name,
                                    "num": race_num
                                })
        else:
            # __NUXT__ format fallback
            data_array = meetings_data.get("data", [])
            if isinstance(data_array, list) and len(data_array) > 0:
                for group in data_array[0].get("meetings", []):
                    for meeting in group.get("meetings", []):
                        meeting_date = meeting.get("meetingDateLocal", "")
                        meeting_date_only = meeting_date.split("T")[0] if "T" in meeting_date else meeting_date
                        if meeting_date_only != target_date:
                            continue
                        
                        meeting_slug = meeting.get("slug", "")
                        meeting_name = meeting.get("name", "").lower().replace(" ", "-").replace("'", "")
                        
                        for event in meeting.get("events", []):
                            if event.get("isResulted", False):
                                race_slug = event.get("slug", "")
                                race_num = event.get("eventNumber", 0)
                                
                                if race_slug:
                                    races.append({
                                        "url": f"{BASE_URL}/{meeting_slug}/{race_slug}",
                                        "name": meeting_name,
                                        "num": race_num
                                    })
    
    return races


async def extract_with_retry(url: str, extractor: NuxtDataExtractor, max_retries: int = 3):
    """Extract data from URL with retry logic."""
    for attempt in range(max_retries):
        try:
            return await extractor.extract(
                url,
                use_combined_extraction=True,
                wait_for_nuxt=True,
                wait_for_nuxt_timeout=20000
            )
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep([5, 10, 20][attempt])
            else:
                print(f"  ❌ Failed after {max_retries} attempts: {e}")
                return None


def save_data(data: dict, target_date: str):
    """Save extracted data to JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = OUTPUT_DIR / f"racenet-harness-meetings-{target_date}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Saved meetings to: {output_file}")


async def main():
    """Main execution flow."""
    print("=" * 70)
    print("Racenet Historical Data Scraper - Calendar Navigation Example")
    print("=" * 70)
    
    # Setup directories
    races_dir = OUTPUT_DIR / "races"
    races_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Extract meetings data
    print("\n📅 Step 1: Extracting meetings data...")
    meetings_data = await extract_historical_data(TARGET_DATE)
    
    if not meetings_data:
        print("\n❌ Failed to extract meetings data")
        return
    
    # Save meetings data
    save_data(meetings_data, TARGET_DATE)
    
    # Step 2: Extract race URLs
    print(f"\n🏁 Step 2: Extracting race URLs...")
    races = extract_race_urls(meetings_data, TARGET_DATE)
    
    if not races:
        print("⚠️  No races found for this date")
        print("\n✅ Meetings data extracted successfully!")
        return
    
    print(f"Found {len(races)} historical races for {TARGET_DATE}")
    for i, race in enumerate(races[:5], 1):
        print(f"  {i}. {race['name']} - Race {race['num']}")
    if len(races) > 5:
        print(f"  ... and {len(races) - 5} more races")
    
    # Step 3: Scrape all race data
    print(f"\n📊 Step 3: Scraping race data...")
    async with NuxtDataExtractor(
        headless=False,
        timeout=60000,
        stealth_config=stealth_config
    ) as extractor:
        for i, race in enumerate(races, 1):
            print(f"\n[{i}/{len(races)}] {race['name']} Race {race['num']}")
            
            race_data = await extract_with_retry(race['url'], extractor)
            
            if race_data:
                output_file = races_dir / f"racenet-harness-{race['name']}-race-{race['num']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(race_data, f, indent=2, ensure_ascii=False, default=str)
                print(f"  ✅ Saved: {output_file.name}")
            else:
                print(f"  ❌ Failed to extract race data")
            
            # Delay between races
            if i < len(races):
                await asyncio.sleep(2)
    
    print("\n" + "=" * 70)
    print("✅ Extraction completed successfully!")
    print(f"📁 Meetings saved to: {OUTPUT_DIR}")
    print(f"📁 Races saved to: {races_dir} ({len(races)} files)")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())


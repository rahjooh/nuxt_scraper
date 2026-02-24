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


def save_data(data: dict, target_date: str):
    """Save extracted data to JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = OUTPUT_DIR / f"racenet-harness-{target_date}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Saved to: {output_file}")


async def main():
    """Main execution flow."""
    print("=" * 70)
    print("Racenet Historical Data Scraper - Calendar Navigation Example")
    print("=" * 70)
    
    # Extract data for target date
    data = await extract_historical_data(TARGET_DATE)
    
    if data:
        save_data(data, TARGET_DATE)
        print("\n✅ Extraction completed successfully!")
    else:
        print("\n❌ Extraction failed")


if __name__ == "__main__":
    asyncio.run(main())


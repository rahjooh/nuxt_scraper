"""Racenet Today's Races - Simple Direct Extraction

This example demonstrates:
- Simple extraction without navigation steps
- Using the convenience function extract_nuxt_data()
- Extracting race URLs from meetings data
- Minimal code for straightforward scraping

Key Pattern: When no navigation is needed (e.g., today's page loads with correct data),
you can use the simple extract_nuxt_data() function without API capture.
"""

import json
from datetime import datetime
from pathlib import Path

from nuxt_scraper import extract_nuxt_data
from nuxt_scraper.utils import StealthConfig


# Configuration
MEETINGS_URL = "https://www.racenet.com.au/form-guide/harness"
BASE_URL = "https://www.racenet.com.au/form-guide/harness"
OUTPUT_DIR = Path("data/racenet_today")

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


def extract_with_retry(url: str, max_retries: int = 3, deserialize: bool = False):
    """Extract data with retry logic.
    
    Args:
        url: URL to extract from
        max_retries: Maximum number of retry attempts
        deserialize: Whether to deserialize Nuxt 3 data (True for races, False for meetings)
        
    Returns:
        Extracted data or None if all retries fail
    """
    import time
    
    for attempt in range(max_retries):
        try:
            return extract_nuxt_data(
                url,
                headless=False,
                timeout=45000,
                deserialize_nuxt3=deserialize,
                stealth_config=stealth_config
            )
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = [5, 10, 20][attempt]
                print(f"  ⚠️  Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Failed after {max_retries} attempts: {e}")
                return None


def extract_race_urls(meetings_data: dict) -> list:
    """Extract race URLs from meetings data.
    
    Args:
        meetings_data: Extracted meetings data
        
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
        else:
            # __NUXT__ format (default for today's page)
            data_array = meetings_data.get("data", [])
            
            if isinstance(data_array, list) and len(data_array) > 0:
                for group in data_array[0].get("meetings", []):
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


def save_data(data: dict, filename: str):
    """Save data to JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = OUTPUT_DIR / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"  💾 Saved: {output_file}")


def main():
    """Main execution flow."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    print("=" * 70)
    print(f"Racenet Today's Races - Simple Extraction Example ({today})")
    print("=" * 70)
    
    # Setup directories
    races_dir = OUTPUT_DIR / "races"
    races_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Extract today's meetings (no navigation needed)
    print(f"\n📅 Step 1: Extracting meetings for today...")
    meetings_data = extract_with_retry(MEETINGS_URL)
    
    if not meetings_data:
        print("\n❌ Failed to extract meetings")
        return
    
    # Save meetings data
    save_data(meetings_data, f"racenet-harness-today-{today}.json")
    
    # Step 2: Extract race URLs
    print(f"\n🏁 Step 2: Extracting race URLs...")
    races = extract_race_urls(meetings_data)
    
    if not races:
        print("⚠️  No upcoming races found for today")
        print("\n✅ Meetings data extracted successfully!")
        return
    
    print(f"Found {len(races)} upcoming races for today")
    for i, race in enumerate(races[:5], 1):
        print(f"  {i}. {race['name']} - Race {race['num']}")
    if len(races) > 5:
        print(f"  ... and {len(races) - 5} more races")
    
    # Step 3: Scrape all race data
    print(f"\n📊 Step 3: Scraping race data...")
    import time
    
    for i, race in enumerate(races, 1):
        print(f"\n[{i}/{len(races)}] {race['name']} Race {race['num']}")
        
        race_data = extract_with_retry(race['url'], deserialize=True)
        
        if race_data:
            output_file = races_dir / f"racenet-harness-{race['name']}-race-{race['num']}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(race_data, f, indent=2, ensure_ascii=False, default=str)
            print(f"  ✅ Saved: {output_file.name}")
        else:
            print(f"  ❌ Failed to extract race data")
        
        # Delay between races
        if i < len(races):
            time.sleep(2)
    
    print("\n" + "=" * 70)
    print("✅ Extraction completed successfully!")
    print(f"📁 Meetings saved to: {OUTPUT_DIR}")
    print(f"📁 Races saved to: {races_dir} ({len(races)} files)")
    print("=" * 70)
    print(f"\n💡 Tip: For calendar navigation or tab clicks, use extract_with_api_capture()")
    print(f"   See: 01_historical_calendar_navigation.py or 02_tomorrow_tab_navigation.py")


if __name__ == "__main__":
    main()


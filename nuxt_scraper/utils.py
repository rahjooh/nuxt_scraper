"""Helper utilities and configuration for Nuxt Scraper.

Includes anti-detection settings.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Coroutine, Optional, TypeVar

T = TypeVar("T")


@dataclass
class StealthConfig:
    """
    Configuration options for anti-detection and human-like browser behavior.

    Attributes:
        enabled: If True, apply stealth measures (default: True).
        random_delays: Introduce random pauses between actions (default: True).
        min_action_delay_ms: Minimum delay in milliseconds (default: 100).
        max_action_delay_ms: Maximum delay in milliseconds (default: 3000).
        human_typing: Simulate realistic typing speed and typos (default: True).
        typing_speed_wpm: Words per minute for typing simulation (default: 65).
        typo_chance: Probability of a typo (0.0 to 1.0, default: 0.02).
        pause_chance: Probability of longer pause during typing (0.0-1.0, default 0.05).
        mouse_movement: Simulate realistic mouse movements before clicks (default True).
        randomize_viewport: Randomize browser viewport size (default: True).
        realistic_user_agent: Use a random realistic user agent string (default: True).
        # Add more stealth options here as needed
    """

    enabled: bool = True
    random_delays: bool = True
    min_action_delay_ms: int = 100
    max_action_delay_ms: int = 3000
    human_typing: bool = True
    typing_speed_wpm: int = 65
    typo_chance: float = 0.02
    pause_chance: float = 0.05
    mouse_movement: bool = True
    randomize_viewport: bool = True
    realistic_user_agent: bool = True

    # Internal field to hold the chosen user agent if randomized
    _resolved_user_agent: Optional[str] = field(init=False, repr=False, default=None)
    _resolved_viewport: Optional[tuple[int, int]] = field(
        init=False, repr=False, default=None
    )


def merge_stealth_configs(
    base: StealthConfig, override: Optional[StealthConfig]
) -> StealthConfig:
    """
    Merges an override StealthConfig into a base StealthConfig.

    Args:
        base: The base configuration.
        override: Optional override. Only non-None fields override base.

    Returns:
        A new StealthConfig instance with merged values.
    """
    if override is None:
        return base

    merged = StealthConfig()
    for field_name, field_value in base.__dict__.items():
        if not field_name.startswith("_"):  # Skip internal fields
            override_value = getattr(override, field_name, None)
            if override_value is not None:
                setattr(merged, field_name, override_value)
            else:
                setattr(merged, field_name, field_value)
    return merged


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run an async coroutine from synchronous code.
    Uses asyncio.run(); creates a new event loop.
    """
    return asyncio.run(coro)


def validate_meeting_date(
    data: dict,
    expected_date: str,
    date_field: str = "meetingDateLocal"
) -> bool:
    """
    Validate that extracted data matches expected date.
    
    Handles both "YYYY-MM-DD" and ISO datetime formats ("YYYY-MM-DDTHH:MM:SS.000Z").
    Supports both API response and __NUXT__ data structures.
    
    Args:
        data: Extracted data (API response or __NUXT__ format).
        expected_date: Expected date in YYYY-MM-DD format.
        date_field: Field name containing the date (default: "meetingDateLocal").
        
    Returns:
        True if date matches, False otherwise.
        
    Example:
        # With API response
        nuxt_data, api_responses = await extractor.extract_with_api_capture(url, steps)
        meetings_response = extractor.find_api_response(api_responses, "meetingsGrouped")
        if meetings_response and validate_meeting_date(meetings_response["data"], "2025-02-20"):
            print("Date validation passed!")
            
        # With __NUXT__ data
        nuxt_data = await extractor.extract(url)
        if validate_meeting_date(nuxt_data, "2025-02-20"):
            print("Date validation passed!")
    """
    try:
        # Handle API response format
        if isinstance(data, dict) and "data" in data:
            api_data = data.get("data", {})
            
            # Try API response format (meetingsGrouped)
            if "meetingsGrouped" in api_data:
                for group in api_data["meetingsGrouped"]:
                    meetings_in_group = group.get("meetings", [])
                    if meetings_in_group:
                        first_meeting = meetings_in_group[0]
                        meeting_date = first_meeting.get(date_field, "")
                        # Extract just the date part if it's an ISO datetime string
                        meeting_date_only = meeting_date.split("T")[0] if "T" in meeting_date else meeting_date
                        return meeting_date_only == expected_date
            
            # Try __NUXT__ format
            data_array = data.get("data", [])
            if isinstance(data_array, list) and len(data_array) > 0:
                first_item = data_array[0]
                if isinstance(first_item, dict) and "meetings" in first_item:
                    for group in first_item.get("meetings", []):
                        for meeting in group.get("meetings", []):
                            meeting_date = meeting.get(date_field, "")
                            # Extract just the date part if it's an ISO datetime string
                            meeting_date_only = meeting_date.split("T")[0] if "T" in meeting_date else meeting_date
                            return meeting_date_only == expected_date
        
        return False
    except Exception:
        return False

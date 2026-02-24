"""
Calendar Date Selection Example

This example demonstrates how to select dates from calendar widgets,
which is common in racing sites, booking systems, and data filtering interfaces.
"""

import asyncio
from nuxt_scraper import NuxtDataExtractor, NavigationStep


async def racing_calendar_example():
    """Select a date from a racing calendar."""
    print("🏇 Racing Calendar Example")
    
    async with NuxtDataExtractor(headless=False, timeout=60000) as extractor:
        try:
            # First, click to open the calendar
            open_calendar_step = NavigationStep.click("input[data-calendar-trigger]")
            
            # Then select a specific date
            select_date_step = NavigationStep.select_date(
                target_date="2026-03-15",  # March 15, 2026
                calendar_selector="div.calendar-widget",
                prev_month_selector="button.prev-month",
                next_month_selector="button.next-month", 
                month_year_display_selector="div.month-year-header",
                date_cell_selector="div.calendar-day",
                view_results_selector="button:has-text('View Results')",
                timeout=20000
            )
            
            steps = [open_calendar_step, select_date_step]
            
            data = await extractor.extract(
                "https://racenet.com.au/form-guide/",
                steps=steps
            )
            
            print(f"✅ Racing data extracted for March 15, 2026")
            print(f"📊 Data type: {type(data)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def booking_calendar_example():
    """Select dates from a booking system calendar."""
    print("\n📅 Booking Calendar Example")
    
    async with NuxtDataExtractor(headless=False) as extractor:
        try:
            steps = [
                # Navigate to booking page
                NavigationStep.click("a[href='/book-appointment']"),
                NavigationStep.wait(".booking-calendar"),
                
                # Select check-in date
                NavigationStep.select_date(
                    target_date="2026-04-20",
                    calendar_selector=".check-in-calendar",
                    prev_month_selector=".calendar-prev",
                    next_month_selector=".calendar-next",
                    month_year_display_selector=".calendar-month-year",
                    date_cell_selector=".calendar-date",
                    timeout=15000
                ),
                
                # Wait for check-out calendar to appear
                NavigationStep.wait(".check-out-calendar"),
                
                # Select check-out date
                NavigationStep.select_date(
                    target_date="2026-04-25",
                    calendar_selector=".check-out-calendar",
                    prev_month_selector=".calendar-prev",
                    next_month_selector=".calendar-next",
                    month_year_display_selector=".calendar-month-year",
                    date_cell_selector=".calendar-date",
                    timeout=15000
                ),
                
                # Search for availability
                NavigationStep.click("button[data-action='search-availability']"),
                NavigationStep.wait(".availability-results", timeout=20000),
            ]
            
            data = await extractor.extract(
                "https://your-booking-site.com",
                steps=steps
            )
            
            print(f"✅ Booking data extracted for April 20-25, 2026")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def data_filter_calendar_example():
    """Use calendar to filter data by date range."""
    print("\n📊 Data Filter Calendar Example")
    
    async with NuxtDataExtractor(headless=False) as extractor:
        try:
            steps = [
                # Open date range filter
                NavigationStep.click("button[data-filter='date-range']"),
                NavigationStep.wait(".date-range-picker"),
                
                # Select start date
                NavigationStep.select_date(
                    target_date="2026-02-01",
                    calendar_selector=".start-date-calendar",
                    prev_month_selector=".prev-month-btn",
                    next_month_selector=".next-month-btn",
                    month_year_display_selector=".current-month-year",
                    date_cell_selector=".date-cell",
                    timeout=15000
                ),
                
                # Select end date
                NavigationStep.select_date(
                    target_date="2026-02-28",
                    calendar_selector=".end-date-calendar", 
                    prev_month_selector=".prev-month-btn",
                    next_month_selector=".next-month-btn",
                    month_year_display_selector=".current-month-year",
                    date_cell_selector=".date-cell",
                    timeout=15000
                ),
                
                # Apply filter
                NavigationStep.click("button[data-action='apply-date-filter']"),
                NavigationStep.wait(".filtered-data-loaded", timeout=25000),
            ]
            
            data = await extractor.extract(
                "https://your-analytics-dashboard.com",
                steps=steps
            )
            
            print(f"✅ Filtered data extracted for February 2026")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def multiple_date_selections():
    """Example with multiple date selections in sequence."""
    print("\n🗓️ Multiple Date Selections Example")
    
    async with NuxtDataExtractor(headless=False, timeout=90000) as extractor:
        try:
            # Extract data for multiple dates
            dates_to_check = ["2026-03-01", "2026-03-15", "2026-03-31"]
            all_data = {}
            
            for date in dates_to_check:
                print(f"   Selecting date: {date}")
                
                steps = [
                    # Reset/clear previous selection
                    NavigationStep.click("button[data-action='clear-date']"),
                    
                    # Open calendar
                    NavigationStep.click("input.date-picker"),
                    NavigationStep.wait(".calendar-popup"),
                    
                    # Select specific date
                    NavigationStep.select_date(
                        target_date=date,
                        calendar_selector=".calendar-popup",
                        prev_month_selector=".calendar-prev",
                        next_month_selector=".calendar-next",
                        month_year_display_selector=".calendar-header",
                        date_cell_selector=".calendar-day",
                        view_results_selector="button.view-results",
                        timeout=20000
                    ),
                    
                    # Wait for data to load
                    NavigationStep.wait(".date-specific-data", timeout=15000),
                ]
                
                data = await extractor.extract_from_current_page()
                all_data[date] = data
                
                print(f"   ✅ Data extracted for {date}")
            
            print(f"📊 Total dates processed: {len(all_data)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run all calendar examples."""
    print("📅 Calendar Date Selection Examples")
    print("=" * 50)
    
    await racing_calendar_example()
    await booking_calendar_example()
    await data_filter_calendar_example()
    await multiple_date_selections()
    
    print("\n✨ All calendar examples completed!")
    print("💡 Adjust the selectors to match your target calendar widgets.")


if __name__ == "__main__":
    asyncio.run(main())
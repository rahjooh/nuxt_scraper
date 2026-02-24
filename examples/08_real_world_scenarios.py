"""
Real-World Scenarios Examples

This example demonstrates practical, real-world use cases for nuxt_scraper
including e-commerce, news sites, dashboards, and data aggregation.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from nuxt_scraper import NuxtDataExtractor, extract_nuxt_data, NavigationStep
from nuxt_scraper.utils import StealthConfig


async def ecommerce_product_scraping():
    """Scrape product data from e-commerce sites."""
    print("🛒 E-commerce Product Scraping")
    
    stealth_config = StealthConfig(
        random_delays=True,
        human_typing=True,
        mouse_movement=True,
        randomize_viewport=True
    )
    
    async with NuxtDataExtractor(
        headless=True,
        stealth_config=stealth_config,
        timeout=45000
    ) as extractor:
        try:
            # Navigate and search for products
            steps = [
                # Accept cookies
                NavigationStep.click("button[data-testid='accept-cookies']"),
                
                # Search for products
                NavigationStep.fill("input[data-testid='search-input']", "gaming laptop"),
                NavigationStep.click("button[data-testid='search-button']"),
                NavigationStep.wait(".search-results", timeout=15000),
                
                # Apply filters
                NavigationStep.click("input[data-filter='brand-asus']"),
                NavigationStep.click("input[data-filter='price-1000-2000']"),
                NavigationStep.wait(".filtered-results", timeout=10000),
                
                # Sort by price
                NavigationStep.select("select[data-sort='price']", "price-low-high"),
                NavigationStep.wait(".sorted-results", timeout=10000)
            ]
            
            data = await extractor.extract(
                "https://your-ecommerce-site.com",
                steps=steps
            )
            
            # Extract product information
            if isinstance(data, dict) and 'products' in data:
                products = data['products']
                print(f"   ✅ Found {len(products)} products")
                
                # Save product data
                output_file = Path("ecommerce_products.json")
                with open(output_file, 'w') as f:
                    json.dump({
                        "search_query": "gaming laptop",
                        "filters": ["brand-asus", "price-1000-2000"],
                        "sort": "price-low-high",
                        "scraped_at": datetime.now().isoformat(),
                        "products": products
                    }, f, indent=2, default=str)
                
                print(f"   💾 Product data saved to: {output_file}")
            else:
                print("   ⚠️ No product data found in expected format")
                
        except Exception as e:
            print(f"   ❌ E-commerce scraping failed: {e}")


async def news_aggregation():
    """Aggregate news articles from multiple sources."""
    print("\n📰 News Aggregation")
    
    news_sources = [
        {
            "name": "Tech News Site",
            "url": "https://tech-news-site.com",
            "category_selector": "a[href='/technology']",
            "wait_selector": ".tech-articles"
        },
        {
            "name": "Business News Site", 
            "url": "https://business-news-site.com",
            "category_selector": "nav a[data-category='business']",
            "wait_selector": ".business-news"
        }
    ]
    
    all_articles = []
    
    for source in news_sources:
        print(f"   Scraping {source['name']}...")
        
        try:
            steps = [
                NavigationStep.click(source["category_selector"]),
                NavigationStep.wait(source["wait_selector"], timeout=15000)
            ]
            
            data = extract_nuxt_data(
                source["url"],
                steps=steps,
                headless=True,
                timeout=30000
            )
            
            # Extract articles from the data
            if isinstance(data, dict):
                articles = data.get('articles', [])
                for article in articles:
                    article['source'] = source['name']
                    article['scraped_at'] = datetime.now().isoformat()
                
                all_articles.extend(articles)
                print(f"   ✅ {source['name']}: {len(articles)} articles")
            
        except Exception as e:
            print(f"   ❌ {source['name']}: {e}")
    
    # Save aggregated news
    if all_articles:
        output_file = Path("aggregated_news.json")
        with open(output_file, 'w') as f:
            json.dump({
                "aggregated_at": datetime.now().isoformat(),
                "total_articles": len(all_articles),
                "sources": [s['name'] for s in news_sources],
                "articles": all_articles
            }, f, indent=2, default=str)
        
        print(f"   📊 Total articles aggregated: {len(all_articles)}")
        print(f"   💾 News data saved to: {output_file}")


async def dashboard_monitoring():
    """Monitor dashboard metrics and alerts."""
    print("\n📊 Dashboard Monitoring")
    
    async with NuxtDataExtractor(headless=True, timeout=60000) as extractor:
        try:
            # Login to dashboard
            steps = [
                # Login form
                NavigationStep.fill("input[name='username']", "monitor_user"),
                NavigationStep.fill("input[name='password']", "secure_password"),
                NavigationStep.click("button[type='submit']"),
                NavigationStep.wait(".dashboard-loaded", timeout=20000),
                
                # Navigate to metrics
                NavigationStep.click("nav a[href='/metrics']"),
                NavigationStep.wait(".metrics-dashboard", timeout=15000),
                
                # Set time range to last 24 hours
                NavigationStep.select("select[name='timerange']", "24h"),
                NavigationStep.wait(".metrics-updated", timeout=10000)
            ]
            
            data = await extractor.extract(
                "https://your-monitoring-dashboard.com",
                steps=steps
            )
            
            # Extract metrics
            if isinstance(data, dict):
                metrics = data.get('metrics', {})
                alerts = data.get('alerts', [])
                
                # Check for critical alerts
                critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
                
                monitoring_report = {
                    "timestamp": datetime.now().isoformat(),
                    "metrics": metrics,
                    "total_alerts": len(alerts),
                    "critical_alerts": len(critical_alerts),
                    "alerts": alerts
                }
                
                # Save monitoring data
                output_file = Path("dashboard_monitoring.json")
                with open(output_file, 'w') as f:
                    json.dump(monitoring_report, f, indent=2, default=str)
                
                print(f"   📈 Metrics collected: {len(metrics)} data points")
                print(f"   🚨 Alerts found: {len(alerts)} ({len(critical_alerts)} critical)")
                print(f"   💾 Monitoring data saved to: {output_file}")
                
                # Alert on critical issues
                if critical_alerts:
                    print(f"   🔥 CRITICAL ALERTS DETECTED:")
                    for alert in critical_alerts:
                        print(f"     - {alert.get('message', 'Unknown alert')}")
                
        except Exception as e:
            print(f"   ❌ Dashboard monitoring failed: {e}")


async def racing_data_collection():
    """Collect racing data with date selection."""
    print("\n🏇 Racing Data Collection")
    
    # Collect data for multiple race dates
    race_dates = [
        "2026-03-15",
        "2026-03-16", 
        "2026-03-17"
    ]
    
    all_race_data = {}
    
    async with NuxtDataExtractor(
        headless=False,  # Visible for calendar interaction
        timeout=90000
    ) as extractor:
        
        for race_date in race_dates:
            print(f"   Collecting data for {race_date}...")
            
            try:
                steps = [
                    # Open calendar
                    NavigationStep.click("input[data-date-picker]"),
                    NavigationStep.wait(".calendar-popup", timeout=10000),
                    
                    # Select specific date
                    NavigationStep.select_date(
                        target_date=race_date,
                        calendar_selector=".calendar-popup",
                        prev_month_selector=".calendar-prev",
                        next_month_selector=".calendar-next",
                        month_year_display_selector=".calendar-month-year",
                        date_cell_selector=".calendar-day",
                        view_results_selector="button.view-results",
                        timeout=20000
                    ),
                    
                    # Wait for race data to load
                    NavigationStep.wait(".race-results", timeout=15000)
                ]
                
                data = await extractor.extract(
                    "https://racenet.com.au/form-guide/",
                    steps=steps
                )
                
                if isinstance(data, dict):
                    races = data.get('races', [])
                    all_race_data[race_date] = {
                        "date": race_date,
                        "races": races,
                        "total_races": len(races),
                        "collected_at": datetime.now().isoformat()
                    }
                    
                    print(f"   ✅ {race_date}: {len(races)} races collected")
                
            except Exception as e:
                print(f"   ❌ {race_date}: {e}")
    
    # Save racing data
    if all_race_data:
        output_file = Path("racing_data_collection.json")
        with open(output_file, 'w') as f:
            json.dump({
                "collection_period": f"{min(race_dates)} to {max(race_dates)}",
                "total_dates": len(race_dates),
                "successful_dates": len(all_race_data),
                "data": all_race_data
            }, f, indent=2, default=str)
        
        total_races = sum(len(d['races']) for d in all_race_data.values())
        print(f"   📊 Total races collected: {total_races}")
        print(f"   💾 Racing data saved to: {output_file}")


async def api_data_comparison():
    """Compare data from web scraping vs API endpoints."""
    print("\n🔄 API Data Comparison")
    
    base_url = "https://your-data-site.com"
    
    try:
        # Method 1: Web scraping
        print("   Extracting data via web scraping...")
        web_data = extract_nuxt_data(
            f"{base_url}/dashboard",
            headless=True,
            timeout=30000
        )
        
        # Method 2: Direct API call (if available)
        print("   Extracting data via API endpoint...")
        api_data = extract_nuxt_data(
            f"{base_url}/api/data",
            headless=True,
            timeout=15000
        )
        
        # Compare the data
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "web_scraping": {
                "data_type": type(web_data).__name__,
                "data_size": len(str(web_data)),
                "keys": list(web_data.keys()) if isinstance(web_data, dict) else None
            },
            "api_endpoint": {
                "data_type": type(api_data).__name__,
                "data_size": len(str(api_data)),
                "keys": list(api_data.keys()) if isinstance(api_data, dict) else None
            }
        }
        
        # Check data consistency
        if isinstance(web_data, dict) and isinstance(api_data, dict):
            common_keys = set(web_data.keys()) & set(api_data.keys())
            comparison["common_keys"] = list(common_keys)
            comparison["data_consistency"] = len(common_keys) / max(len(web_data), len(api_data))
        
        # Save comparison
        output_file = Path("api_comparison.json")
        with open(output_file, 'w') as f:
            json.dump(comparison, f, indent=2, default=str)
        
        print(f"   📊 Web scraping data size: {comparison['web_scraping']['data_size']:,}")
        print(f"   📊 API endpoint data size: {comparison['api_endpoint']['data_size']:,}")
        
        if 'data_consistency' in comparison:
            consistency = comparison['data_consistency'] * 100
            print(f"   🔍 Data consistency: {consistency:.1f}%")
        
        print(f"   💾 Comparison saved to: {output_file}")
        
    except Exception as e:
        print(f"   ❌ API comparison failed: {e}")


async def scheduled_data_collection():
    """Simulate scheduled data collection workflow."""
    print("\n⏰ Scheduled Data Collection Workflow")
    
    # Define collection schedule
    collection_tasks = [
        {
            "name": "Morning Market Data",
            "url": "https://market-data-site.com",
            "schedule": "09:00",
            "steps": [
                NavigationStep.click("a[href='/market-overview']"),
                NavigationStep.wait(".market-data-loaded")
            ]
        },
        {
            "name": "Afternoon News Update", 
            "url": "https://news-site.com",
            "schedule": "15:00",
            "steps": [
                NavigationStep.click("a[href='/latest-news']"),
                NavigationStep.wait(".news-loaded")
            ]
        },
        {
            "name": "Evening Analytics",
            "url": "https://analytics-dashboard.com",
            "schedule": "20:00",
            "steps": [
                NavigationStep.click("nav a[href='/daily-report']"),
                NavigationStep.wait(".report-generated")
            ]
        }
    ]
    
    # Simulate running scheduled tasks
    collected_data = {}
    
    for task in collection_tasks:
        print(f"   Running: {task['name']} (scheduled for {task['schedule']})")
        
        try:
            data = extract_nuxt_data(
                task["url"],
                steps=task["steps"],
                headless=True,
                timeout=45000
            )
            
            collected_data[task["name"]] = {
                "scheduled_time": task["schedule"],
                "collected_at": datetime.now().isoformat(),
                "data": data,
                "status": "success"
            }
            
            print(f"   ✅ {task['name']}: Success")
            
        except Exception as e:
            collected_data[task["name"]] = {
                "scheduled_time": task["schedule"],
                "collected_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "failed"
            }
            
            print(f"   ❌ {task['name']}: {e}")
    
    # Generate daily report
    successful_tasks = sum(1 for t in collected_data.values() if t["status"] == "success")
    
    daily_report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_tasks": len(collection_tasks),
        "successful_tasks": successful_tasks,
        "success_rate": successful_tasks / len(collection_tasks) * 100,
        "tasks": collected_data
    }
    
    # Save daily report
    output_file = Path(f"daily_report_{datetime.now().strftime('%Y%m%d')}.json")
    with open(output_file, 'w') as f:
        json.dump(daily_report, f, indent=2, default=str)
    
    print(f"   📊 Daily Report Summary:")
    print(f"     Tasks completed: {successful_tasks}/{len(collection_tasks)}")
    print(f"     Success rate: {daily_report['success_rate']:.1f}%")
    print(f"   💾 Daily report saved to: {output_file}")


async def main():
    """Run all real-world scenario examples."""
    print("🌍 Real-World Scenarios Examples")
    print("=" * 50)
    
    await ecommerce_product_scraping()
    await news_aggregation()
    await dashboard_monitoring()
    await racing_data_collection()
    await api_data_comparison()
    await scheduled_data_collection()
    
    print("\n✨ All real-world examples completed!")
    print("💡 These examples demonstrate:")
    print("   - E-commerce product data collection")
    print("   - Multi-source news aggregation")
    print("   - Dashboard monitoring and alerting")
    print("   - Racing data with calendar selection")
    print("   - API vs web scraping comparison")
    print("   - Scheduled data collection workflows")
    print("\n🔧 Adapt these patterns for your specific use cases!")


if __name__ == "__main__":
    asyncio.run(main())
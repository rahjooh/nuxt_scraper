"""
Parallel and Batch Extraction Examples

This example demonstrates how to extract data from multiple URLs
efficiently using parallel processing and batch operations.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from nuxt_scraper import NuxtDataExtractor, extract_nuxt_data, NavigationStep


async def sequential_extraction():
    """Extract data from multiple URLs sequentially."""
    print("📝 Sequential Extraction Example")
    
    urls = [
        "https://site1.com/data",
        "https://site2.com/data", 
        "https://site3.com/data",
        "https://site4.com/data"
    ]
    
    start_time = time.time()
    results = {}
    
    async with NuxtDataExtractor(headless=True) as extractor:
        for i, url in enumerate(urls, 1):
            print(f"   Processing {i}/{len(urls)}: {url}")
            
            try:
                data = await extractor.extract(url)
                results[url] = {
                    "status": "success",
                    "data": data,
                    "data_type": type(data).__name__
                }
                print(f"   ✅ Success: {url}")
                
            except Exception as e:
                results[url] = {
                    "status": "error", 
                    "error": str(e)
                }
                print(f"   ❌ Error: {url} - {e}")
    
    total_time = time.time() - start_time
    successful = sum(1 for r in results.values() if r["status"] == "success")
    
    print(f"\n📊 Sequential Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful: {successful}/{len(urls)}")
    print(f"   Average per URL: {total_time/len(urls):.2f}s")
    
    return results


async def parallel_extraction():
    """Extract data from multiple URLs in parallel."""
    print("\n🚀 Parallel Extraction Example")
    
    urls = [
        "https://site1.com/data",
        "https://site2.com/data",
        "https://site3.com/data", 
        "https://site4.com/data"
    ]
    
    async def extract_single_url(url):
        """Extract data from a single URL."""
        try:
            async with NuxtDataExtractor(headless=True) as extractor:
                data = await extractor.extract(url)
                return {
                    "url": url,
                    "status": "success",
                    "data": data,
                    "data_type": type(data).__name__
                }
        except Exception as e:
            return {
                "url": url,
                "status": "error",
                "error": str(e)
            }
    
    start_time = time.time()
    
    # Run extractions in parallel
    tasks = [extract_single_url(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_time = time.time() - start_time
    
    # Process results
    successful = 0
    for result in results:
        if isinstance(result, dict) and result.get("status") == "success":
            successful += 1
            print(f"   ✅ Success: {result['url']}")
        else:
            error_msg = result.get("error", str(result)) if isinstance(result, dict) else str(result)
            url = result.get("url", "Unknown") if isinstance(result, dict) else "Unknown"
            print(f"   ❌ Error: {url} - {error_msg}")
    
    print(f"\n📊 Parallel Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful: {successful}/{len(urls)}")
    print(f"   Average per URL: {total_time/len(urls):.2f}s")
    
    return results


def threaded_extraction():
    """Extract data using thread pool for synchronous operations."""
    print("\n🧵 Threaded Extraction Example")
    
    urls = [
        "https://site1.com/data",
        "https://site2.com/data",
        "https://site3.com/data",
        "https://site4.com/data"
    ]
    
    def extract_url_sync(url):
        """Synchronous extraction wrapper."""
        try:
            data = extract_nuxt_data(url, headless=True, timeout=30000)
            return {
                "url": url,
                "status": "success", 
                "data": data,
                "data_type": type(data).__name__
            }
        except Exception as e:
            return {
                "url": url,
                "status": "error",
                "error": str(e)
            }
    
    start_time = time.time()
    results = []
    
    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks
        future_to_url = {executor.submit(extract_url_sync, url): url for url in urls}
        
        # Process completed tasks
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                
                if result["status"] == "success":
                    print(f"   ✅ Success: {url}")
                else:
                    print(f"   ❌ Error: {url} - {result['error']}")
                    
            except Exception as e:
                results.append({
                    "url": url,
                    "status": "error",
                    "error": str(e)
                })
                print(f"   ❌ Exception: {url} - {e}")
    
    total_time = time.time() - start_time
    successful = sum(1 for r in results if r["status"] == "success")
    
    print(f"\n📊 Threaded Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful: {successful}/{len(urls)}")
    print(f"   Average per URL: {total_time/len(urls):.2f}s")
    
    return results


async def batch_extraction_with_navigation():
    """Extract data from multiple URLs with navigation steps."""
    print("\n📋 Batch Extraction with Navigation")
    
    # URLs with their specific navigation steps
    extraction_configs = [
        {
            "url": "https://ecommerce1.com",
            "steps": [
                NavigationStep.click("button[data-category='electronics']"),
                NavigationStep.wait(".products-loaded")
            ]
        },
        {
            "url": "https://ecommerce2.com", 
            "steps": [
                NavigationStep.fill("input[name='search']", "laptops"),
                NavigationStep.click("button[type='submit']"),
                NavigationStep.wait(".search-results")
            ]
        },
        {
            "url": "https://news-site.com",
            "steps": [
                NavigationStep.click("a[href='/technology']"),
                NavigationStep.wait(".tech-articles")
            ]
        }
    ]
    
    async def extract_with_config(config):
        """Extract data using specific configuration."""
        try:
            async with NuxtDataExtractor(headless=True, timeout=45000) as extractor:
                data = await extractor.extract(
                    config["url"],
                    steps=config["steps"]
                )
                return {
                    "url": config["url"],
                    "status": "success",
                    "data": data,
                    "steps_count": len(config["steps"])
                }
        except Exception as e:
            return {
                "url": config["url"],
                "status": "error",
                "error": str(e),
                "steps_count": len(config["steps"])
            }
    
    start_time = time.time()
    
    # Run all extractions in parallel
    tasks = [extract_with_config(config) for config in extraction_configs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_time = time.time() - start_time
    
    # Process results
    successful = 0
    for result in results:
        if isinstance(result, dict) and result.get("status") == "success":
            successful += 1
            print(f"   ✅ Success: {result['url']} ({result['steps_count']} steps)")
        else:
            error_msg = result.get("error", str(result)) if isinstance(result, dict) else str(result)
            url = result.get("url", "Unknown") if isinstance(result, dict) else "Unknown"
            print(f"   ❌ Error: {url} - {error_msg}")
    
    print(f"\n📊 Batch Navigation Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful: {successful}/{len(extraction_configs)}")
    
    return results


async def rate_limited_extraction():
    """Extract data with rate limiting to avoid overwhelming servers."""
    print("\n⏱️ Rate Limited Extraction")
    
    urls = [
        "https://api-limited-site1.com",
        "https://api-limited-site2.com",
        "https://api-limited-site3.com",
        "https://api-limited-site4.com",
        "https://api-limited-site5.com"
    ]
    
    async def extract_with_delay(url, delay_seconds=2):
        """Extract data with delay between requests."""
        try:
            # Add delay before extraction
            await asyncio.sleep(delay_seconds)
            
            async with NuxtDataExtractor(headless=True) as extractor:
                data = await extractor.extract(url)
                return {
                    "url": url,
                    "status": "success",
                    "data": data
                }
        except Exception as e:
            return {
                "url": url,
                "status": "error", 
                "error": str(e)
            }
    
    start_time = time.time()
    results = []
    
    # Process URLs with rate limiting (2 seconds between requests)
    for i, url in enumerate(urls):
        print(f"   Processing {i+1}/{len(urls)}: {url}")
        result = await extract_with_delay(url, delay_seconds=2)
        results.append(result)
        
        if result["status"] == "success":
            print(f"   ✅ Success")
        else:
            print(f"   ❌ Error: {result['error']}")
    
    total_time = time.time() - start_time
    successful = sum(1 for r in results if r["status"] == "success")
    
    print(f"\n📊 Rate Limited Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful: {successful}/{len(urls)}")
    print(f"   Rate: {len(urls)/total_time:.2f} URLs/second")
    
    return results


async def performance_comparison():
    """Compare performance of different extraction methods."""
    print("\n⚖️ Performance Comparison")
    
    # Use same URLs for fair comparison
    test_urls = [
        "https://test-site1.com",
        "https://test-site2.com", 
        "https://test-site3.com"
    ]
    
    print("   Testing sequential extraction...")
    seq_start = time.time()
    seq_results = []
    async with NuxtDataExtractor(headless=True) as extractor:
        for url in test_urls:
            try:
                await extractor.extract(url)
                seq_results.append("success")
            except:
                seq_results.append("error")
    seq_time = time.time() - seq_start
    
    print("   Testing parallel extraction...")
    par_start = time.time()
    
    async def extract_single(url):
        try:
            async with NuxtDataExtractor(headless=True) as extractor:
                await extractor.extract(url)
                return "success"
        except:
            return "error"
    
    par_results = await asyncio.gather(*[extract_single(url) for url in test_urls])
    par_time = time.time() - par_start
    
    # Results comparison
    seq_success = seq_results.count("success")
    par_success = par_results.count("success")
    
    print(f"\n📊 Performance Comparison Results:")
    print(f"   Sequential: {seq_time:.2f}s ({seq_success}/{len(test_urls)} success)")
    print(f"   Parallel:   {par_time:.2f}s ({par_success}/{len(test_urls)} success)")
    print(f"   Speedup:    {seq_time/par_time:.2f}x")
    print(f"   Efficiency: {(seq_time-par_time)/seq_time*100:.1f}% time saved")


async def main():
    """Run all parallel extraction examples."""
    print("🚀 Parallel and Batch Extraction Examples")
    print("=" * 50)
    
    await sequential_extraction()
    await parallel_extraction()
    threaded_extraction()
    await batch_extraction_with_navigation()
    await rate_limited_extraction()
    await performance_comparison()
    
    print("\n✨ All parallel extraction examples completed!")
    print("💡 Choose the method that best fits your use case:")
    print("   - Sequential: Simple, reliable, slower")
    print("   - Parallel: Fast, efficient, more complex")
    print("   - Threaded: Good for mixed sync/async code")
    print("   - Rate Limited: Respectful to target servers")


if __name__ == "__main__":
    asyncio.run(main())
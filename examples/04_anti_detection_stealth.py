"""
Anti-Detection and Stealth Configuration Examples

This example demonstrates how to configure nuxt_scraper for stealth operation
to avoid detection by anti-bot systems and WAFs.
"""

import asyncio
from nuxt_scraper import NuxtDataExtractor, extract_nuxt_data, NavigationStep
from nuxt_scraper.utils import StealthConfig


def basic_stealth_extraction():
    """Basic extraction with default stealth settings."""
    print("🥷 Basic Stealth Extraction")
    
    try:
        # Default stealth configuration is automatically applied
        data = extract_nuxt_data(
            "https://protected-site.com",
            headless=True,  # Headless mode for stealth
            timeout=45000   # Longer timeout for careful operation
        )
        
        print(f"✅ Stealth extraction successful")
        print(f"📊 Data type: {type(data)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def custom_stealth_configuration():
    """Custom stealth configuration for high-security sites."""
    print("\n🛡️ Custom Stealth Configuration")
    
    # Create custom stealth config
    paranoid_stealth = StealthConfig(
        random_delays=True,
        min_action_delay_ms=800,      # Slower, more human-like
        max_action_delay_ms=3000,
        human_typing=True,
        typing_speed_wpm=45,          # Realistic typing speed
        typo_chance=0.02,             # Occasional typos
        pause_chance=0.05,            # Occasional pauses while typing
        mouse_movement=True,          # Simulate mouse movement
        randomize_viewport=True,      # Random browser window sizes
        realistic_user_agent=True     # Rotate user agents
    )
    
    try:
        data = extract_nuxt_data(
            "https://heavily-protected-site.com",
            stealth_config=paranoid_stealth,
            headless=True,
            timeout=60000
        )
        
        print(f"✅ Paranoid stealth extraction successful")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def stealth_with_proxy():
    """Combine stealth with proxy for maximum anonymity."""
    print("\n🌐 Stealth with Proxy")
    
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
    
    # Proxy configuration (replace with your proxy details)
    proxy_config = {
        "server": "http://proxy.example.com:8080",
        "username": "your_username",  # Optional
        "password": "your_password"   # Optional
    }
    
    try:
        data = extract_nuxt_data(
            "https://geo-restricted-site.com",
            stealth_config=stealth_config,
            proxy=proxy_config,
            headless=True,
            timeout=60000
        )
        
        print(f"✅ Stealth + Proxy extraction successful")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def advanced_stealth_navigation():
    """Advanced stealth with complex navigation."""
    print("\n🎭 Advanced Stealth Navigation")
    
    # High-stealth configuration
    stealth_config = StealthConfig(
        random_delays=True,
        min_action_delay_ms=1000,
        max_action_delay_ms=4000,
        human_typing=True,
        typing_speed_wpm=40,
        typo_chance=0.03,
        pause_chance=0.08,
        mouse_movement=True,
        randomize_viewport=True,
        realistic_user_agent=True
    )
    
    async with NuxtDataExtractor(
        headless=True,
        timeout=90000,
        stealth_config=stealth_config
    ) as extractor:
        try:
            steps = [
                # Slow, human-like navigation
                NavigationStep.wait("body", timeout=3000),  # Let page fully load
                
                # Accept cookies with delay
                NavigationStep.click("button[data-accept-cookies]"),
                NavigationStep.wait(".cookies-accepted", timeout=5000),
                
                # Scroll to simulate reading
                NavigationStep.scroll(".main-content"),
                NavigationStep.wait("footer", timeout=2000),
                
                # Navigate to target section
                NavigationStep.click("nav a[href='/data']"),
                NavigationStep.wait(".data-section", timeout=10000),
                
                # Fill search form slowly and naturally
                NavigationStep.fill("input[name='query']", "search term"),
                NavigationStep.click("button[type='submit']"),
                NavigationStep.wait(".search-results", timeout=15000),
            ]
            
            data = await extractor.extract(
                "https://advanced-protection-site.com",
                steps=steps
            )
            
            print(f"✅ Advanced stealth navigation successful")
            
        except Exception as e:
            print(f"❌ Error: {e}")


async def stealth_configuration_comparison():
    """Compare different stealth levels."""
    print("\n⚖️ Stealth Configuration Comparison")
    
    configs = {
        "minimal": StealthConfig(
            random_delays=True,
            human_typing=False,
            mouse_movement=False,
            randomize_viewport=False,
            realistic_user_agent=False
        ),
        "moderate": StealthConfig(
            random_delays=True,
            human_typing=True,
            mouse_movement=False,
            randomize_viewport=True,
            realistic_user_agent=True
        ),
        "maximum": StealthConfig(
            random_delays=True,
            min_action_delay_ms=1500,
            max_action_delay_ms=4000,
            human_typing=True,
            typing_speed_wpm=35,
            typo_chance=0.04,
            pause_chance=0.10,
            mouse_movement=True,
            randomize_viewport=True,
            realistic_user_agent=True
        )
    }
    
    url = "https://test-site.com"
    
    for level, config in configs.items():
        print(f"   Testing {level} stealth...")
        
        try:
            async with NuxtDataExtractor(
                headless=True,
                stealth_config=config,
                timeout=45000
            ) as extractor:
                data = await extractor.extract(url)
                print(f"   ✅ {level.capitalize()} stealth: Success")
                
        except Exception as e:
            print(f"   ❌ {level.capitalize()} stealth: {e}")


def performance_vs_stealth_tradeoff():
    """Demonstrate performance vs stealth tradeoffs."""
    print("\n⚡ Performance vs Stealth Tradeoff")
    
    import time
    
    configs = [
        ("Fast (No Stealth)", StealthConfig(
            random_delays=False,
            human_typing=False,
            mouse_movement=False,
            randomize_viewport=False,
            realistic_user_agent=False
        )),
        ("Balanced", StealthConfig(
            random_delays=True,
            min_action_delay_ms=200,
            max_action_delay_ms=800,
            human_typing=True,
            typing_speed_wpm=80,
            mouse_movement=False,
            randomize_viewport=True,
            realistic_user_agent=True
        )),
        ("Maximum Stealth", StealthConfig(
            random_delays=True,
            min_action_delay_ms=2000,
            max_action_delay_ms=5000,
            human_typing=True,
            typing_speed_wpm=30,
            typo_chance=0.05,
            pause_chance=0.12,
            mouse_movement=True,
            randomize_viewport=True,
            realistic_user_agent=True
        ))
    ]
    
    for name, config in configs:
        start_time = time.time()
        
        try:
            data = extract_nuxt_data(
                "https://simple-test-site.com",
                stealth_config=config,
                timeout=30000
            )
            
            duration = time.time() - start_time
            print(f"   {name}: {duration:.2f}s ✅")
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"   {name}: {duration:.2f}s ❌ ({e})")


async def main():
    """Run all stealth examples."""
    print("🥷 Anti-Detection and Stealth Examples")
    print("=" * 50)
    
    basic_stealth_extraction()
    custom_stealth_configuration()
    stealth_with_proxy()
    await advanced_stealth_navigation()
    await stealth_configuration_comparison()
    performance_vs_stealth_tradeoff()
    
    print("\n✨ All stealth examples completed!")
    print("💡 Adjust stealth levels based on target site protection.")
    print("🔒 Remember: Higher stealth = Slower but more reliable.")


if __name__ == "__main__":
    asyncio.run(main())
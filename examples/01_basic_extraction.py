"""
Basic Nuxt Data Extraction Examples

This example demonstrates the simplest ways to extract Nuxt data from websites.
Perfect for getting started with nuxt_scraper.
"""

from nuxt_scraper import extract_nuxt_data


def simple_extraction():
    """Extract data from a Nuxt site with minimal configuration."""
    print("🚀 Simple Extraction Example")
    
    url = "https://your-nuxt-app.com"
    
    try:
        # Most basic usage - extract with defaults
        data = extract_nuxt_data(url)
        print(f"✅ Extracted data type: {type(data)}")
        print(f"📊 Data preview: {str(data)[:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def extraction_with_options():
    """Extract data with common configuration options."""
    print("\n🔧 Extraction with Options Example")
    
    url = "https://your-nuxt-app.com"
    
    try:
        # Extract with custom options
        data = extract_nuxt_data(
            url,
            headless=False,           # Show browser window
            timeout=60000,            # 60 second timeout
            deserialize_nuxt3=True    # Enable deserialization (default)
        )
        
        print(f"✅ Extracted with custom options")
        print(f"📊 Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def compare_serialization():
    """Compare raw vs deserialized data."""
    print("\n📊 Serialization Comparison Example")
    
    url = "https://your-nuxt-app.com"
    
    try:
        # Get raw serialized data
        raw_data = extract_nuxt_data(
            url,
            deserialize_nuxt3=False  # Get raw format
        )
        
        # Get deserialized data
        deserialized_data = extract_nuxt_data(
            url,
            deserialize_nuxt3=True   # Get hydrated format (default)
        )
        
        print(f"📦 Raw data type: {type(raw_data)}")
        print(f"🔧 Deserialized data type: {type(deserialized_data)}")
        
        if isinstance(raw_data, list):
            print(f"📏 Raw array length: {len(raw_data):,}")
        
        # Compare sizes (rough estimation)
        raw_size = len(str(raw_data))
        deserialized_size = len(str(deserialized_data))
        
        print(f"📈 Size comparison:")
        print(f"   Raw: {raw_size:,} characters")
        print(f"   Deserialized: {deserialized_size:,} characters")
        print(f"   Ratio: {deserialized_size / raw_size:.2f}x")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🏗️ Basic Nuxt Data Extraction Examples")
    print("=" * 50)
    
    # Run examples
    simple_extraction()
    extraction_with_options()
    compare_serialization()
    
    print("\n✨ Examples completed!")
    print("💡 Try changing the URL to your target Nuxt application.")
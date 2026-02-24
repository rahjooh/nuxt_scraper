"""
Advanced Deserialization Examples

This example demonstrates the new Nuxt 3 deserialization engine,
including handling of special types, performance monitoring, and troubleshooting.
"""

import json
import time
import logging
from pathlib import Path
from nuxt_scraper import extract_nuxt_data, deserialize_nuxt3_data


def setup_logging():
    """Enable detailed logging for deserialization debugging."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('nuxt_scraper.parser')
    logger.setLevel(logging.DEBUG)
    return logger


def basic_deserialization_comparison():
    """Compare raw vs deserialized data."""
    print("🔄 Basic Deserialization Comparison")
    
    url = "https://your-nuxt3-app.com"
    
    try:
        # Extract raw serialized data
        print("   Extracting raw data...")
        raw_data = extract_nuxt_data(url, deserialize_nuxt3=False)
        
        # Extract deserialized data
        print("   Extracting deserialized data...")
        deserialized_data = extract_nuxt_data(url, deserialize_nuxt3=True)
        
        # Compare structures
        print(f"📊 Comparison Results:")
        print(f"   Raw data type: {type(raw_data)}")
        print(f"   Deserialized data type: {type(deserialized_data)}")
        
        if isinstance(raw_data, list):
            print(f"   Raw array length: {len(raw_data):,}")
        
        # Estimate sizes
        raw_size = len(json.dumps(raw_data, default=str))
        deserialized_size = len(json.dumps(deserialized_data, default=str))
        
        print(f"   Raw size: {raw_size:,} characters")
        print(f"   Deserialized size: {deserialized_size:,} characters")
        print(f"   Expansion ratio: {deserialized_size / raw_size:.2f}x")
        
        # Check if expansion is reasonable
        if deserialized_size / raw_size > 10:
            print("   ⚠️ High expansion ratio detected")
        else:
            print("   ✅ Reasonable expansion ratio")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def manual_deserialization_example():
    """Manually deserialize data with custom processing."""
    print("\n🔧 Manual Deserialization Example")
    
    try:
        # Get raw data first
        url = "https://your-nuxt3-app.com"
        raw_data = extract_nuxt_data(url, deserialize_nuxt3=False)
        
        if not isinstance(raw_data, list):
            print("   ⚠️ Data is not in Nuxt 3 serialized format")
            return
        
        print(f"   Raw data array length: {len(raw_data):,}")
        
        # Manual deserialization with timing
        start_time = time.time()
        deserialized_data = deserialize_nuxt3_data(raw_data, is_json_string=False)
        deserialization_time = time.time() - start_time
        
        print(f"   ✅ Manual deserialization completed")
        print(f"   ⏱️ Processing time: {deserialization_time:.2f} seconds")
        print(f"   📊 Result type: {type(deserialized_data)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def special_types_demonstration():
    """Demonstrate handling of special devalue types."""
    print("\n🎯 Special Types Demonstration")
    
    # Example of Nuxt 3 data with special types
    sample_data = [
        {"state": 1},  # Metadata
        {
            "user": 2,
            "settings": 3,
            "timestamps": 4
        },  # Root object
        {
            "name": "Alice",
            "created": {"$d": 1672531200000},  # Date
            "tags": {"$s": [5, 6]},           # Set
            "metadata": {"$m": [[7, 8], [9, 10]]},  # Map
            "bigNumber": {"$b": "123456789012345"},  # BigInt
            "pattern": {"$r": "/test/gi"}     # RegExp
        },
        {
            "theme": "dark",
            "notifications": True
        },
        [
            {"$d": 1672617600000},  # Another date
            {"$d": 1672704000000}   # Another date
        ],
        "admin",      # Index 5
        "user",       # Index 6
        "version",    # Index 7
        "1.0.0",      # Index 8
        "author",     # Index 9
        "John Doe"    # Index 10
    ]
    
    try:
        print("   Sample data with special types:")
        print("   - Date objects ($d)")
        print("   - Set objects ($s)")
        print("   - Map objects ($m)")
        print("   - BigInt objects ($b)")
        print("   - RegExp objects ($r)")
        
        # Deserialize the sample
        result = deserialize_nuxt3_data(sample_data, is_json_string=False)
        
        print(f"\n   ✅ Deserialization successful")
        print(f"   📊 Result structure:")
        
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"     {key}: {type(value).__name__}")
                
                # Show special type conversions
                if hasattr(value, '__dict__'):
                    for sub_key, sub_value in value.__dict__.items():
                        print(f"       {sub_key}: {type(sub_value).__name__}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def performance_monitoring():
    """Monitor deserialization performance."""
    print("\n📈 Performance Monitoring")
    
    logger = setup_logging()
    
    try:
        url = "https://data-heavy-nuxt3-app.com"
        
        # Test with different data sizes
        print("   Testing performance with real data...")
        
        # Raw extraction timing
        start_time = time.time()
        raw_data = extract_nuxt_data(url, deserialize_nuxt3=False)
        raw_time = time.time() - start_time
        
        # Deserialized extraction timing
        start_time = time.time()
        deserialized_data = extract_nuxt_data(url, deserialize_nuxt3=True)
        deserialized_time = time.time() - start_time
        
        print(f"   📊 Performance Results:")
        print(f"     Raw extraction: {raw_time:.2f}s")
        print(f"     Deserialized extraction: {deserialized_time:.2f}s")
        print(f"     Deserialization overhead: {deserialized_time - raw_time:.2f}s")
        
        # Memory usage estimation
        if isinstance(raw_data, list):
            print(f"     Raw array elements: {len(raw_data):,}")
        
        # Check logs for cache size information
        print("   💡 Check logs for cache size and processing details")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def troubleshooting_large_datasets():
    """Troubleshoot issues with large datasets."""
    print("\n🔍 Troubleshooting Large Datasets")
    
    try:
        url = "https://potentially-problematic-site.com"
        
        # Extract with monitoring
        print("   Extracting data with size monitoring...")
        
        raw_data = extract_nuxt_data(url, deserialize_nuxt3=False)
        
        # Analyze raw data structure
        if isinstance(raw_data, list):
            print(f"   📊 Raw Data Analysis:")
            print(f"     Array length: {len(raw_data):,}")
            
            # Count different types
            type_counts = {}
            reference_count = 0
            
            for i, item in enumerate(raw_data[:1000]):  # Sample first 1000
                item_type = type(item).__name__
                type_counts[item_type] = type_counts.get(item_type, 0) + 1
                
                # Count potential references
                if isinstance(item, int) and 0 <= item < len(raw_data):
                    reference_count += 1
            
            print(f"     Type distribution (first 1000): {type_counts}")
            print(f"     Potential references: {reference_count}")
            
            # Estimate deserialization impact
            if reference_count > len(raw_data) * 0.1:
                print("   ⚠️ High reference density - may cause expansion")
            else:
                print("   ✅ Reference density looks reasonable")
        
        # Try deserialization with monitoring
        print("   Attempting deserialization...")
        start_time = time.time()
        
        try:
            deserialized_data = deserialize_nuxt3_data(raw_data, is_json_string=False)
            deserialization_time = time.time() - start_time
            
            # Check result size
            result_size = len(json.dumps(deserialized_data, default=str))
            print(f"   ✅ Deserialization successful")
            print(f"   ⏱️ Time: {deserialization_time:.2f}s")
            print(f"   📏 Result size: {result_size:,} characters")
            
            if result_size > 10_000_000:  # > 10MB
                print("   ⚠️ Large result detected - consider data filtering")
            
        except Exception as deser_error:
            print(f"   ❌ Deserialization failed: {deser_error}")
            print("   💡 Try using raw data or implement custom filtering")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def save_and_analyze_data():
    """Save data to files for analysis."""
    print("\n💾 Save and Analyze Data")
    
    try:
        url = "https://your-target-site.com"
        output_dir = Path("deserialization_analysis")
        output_dir.mkdir(exist_ok=True)
        
        # Extract both formats
        print("   Extracting both data formats...")
        raw_data = extract_nuxt_data(url, deserialize_nuxt3=False)
        deserialized_data = extract_nuxt_data(url, deserialize_nuxt3=True)
        
        # Save to files
        raw_file = output_dir / "raw_data.json"
        deserialized_file = output_dir / "deserialized_data.json"
        
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2, default=str)
        
        with open(deserialized_file, 'w', encoding='utf-8') as f:
            json.dump(deserialized_data, f, indent=2, default=str)
        
        # File size analysis
        raw_size = raw_file.stat().st_size
        deserialized_size = deserialized_file.stat().st_size
        
        print(f"   📁 Files saved to: {output_dir}")
        print(f"   📊 File sizes:")
        print(f"     Raw: {raw_size / 1024 / 1024:.2f} MB")
        print(f"     Deserialized: {deserialized_size / 1024 / 1024:.2f} MB")
        print(f"     Ratio: {deserialized_size / raw_size:.2f}x")
        
        # Generate analysis report
        report_file = output_dir / "analysis_report.txt"
        with open(report_file, 'w') as f:
            f.write("Nuxt 3 Deserialization Analysis Report\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"URL: {url}\n")
            f.write(f"Raw data type: {type(raw_data)}\n")
            f.write(f"Deserialized data type: {type(deserialized_data)}\n")
            f.write(f"Raw file size: {raw_size:,} bytes\n")
            f.write(f"Deserialized file size: {deserialized_size:,} bytes\n")
            f.write(f"Expansion ratio: {deserialized_size / raw_size:.2f}x\n")
            
            if isinstance(raw_data, list):
                f.write(f"Raw array length: {len(raw_data):,}\n")
        
        print(f"   📋 Analysis report: {report_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all deserialization examples."""
    print("🔧 Advanced Deserialization Examples")
    print("=" * 50)
    
    basic_deserialization_comparison()
    manual_deserialization_example()
    special_types_demonstration()
    performance_monitoring()
    troubleshooting_large_datasets()
    save_and_analyze_data()
    
    print("\n✨ All deserialization examples completed!")
    print("💡 Use these techniques to optimize data extraction for your use case.")
    print("🔍 Enable logging for detailed deserialization insights.")


if __name__ == "__main__":
    main()
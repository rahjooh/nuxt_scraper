"""Performance and edge case tests for Nuxt 3 deserialization."""

from __future__ import annotations

import json
import time
from typing import Any, List

import pytest

from nuxt_scraper.parser import deserialize_nuxt3_data, _hydrate_nuxt3_value


class TestDeserializationPerformance:
    """Test performance characteristics of the new deserialization engine."""
    
    def test_large_array_performance(self) -> None:
        """Test performance with large data arrays."""
        # Create a large array with many references
        size = 1000
        raw_data = [{"state": 1}]  # metadata
        
        # Add root object with many references
        root = {"items": list(range(2, size + 2))}
        raw_data.append(root)
        
        # Add many items
        for i in range(size):
            raw_data.append({"id": i, "name": f"item_{i}", "value": i * 10})
        
        start_time = time.time()
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        end_time = time.time()
        
        # Should complete in reasonable time (less than 1 second for 1000 items)
        processing_time = end_time - start_time
        assert processing_time < 1.0, f"Processing took {processing_time:.2f}s, expected < 1.0s"
        
        # Verify correctness
        assert len(result["items"]) == size
        assert result["items"][0]["id"] == 0
        assert result["items"][-1]["id"] == size - 1
    
    def test_deep_nesting_performance(self) -> None:
        """Test performance with deeply nested structures."""
        depth = 100
        raw_data = [{"state": 1}]  # metadata
        
        # Create deeply nested structure
        current_index = 1
        for i in range(depth):
            if i == 0:
                # Root object
                raw_data.append({"level": i, "next": current_index + 1})
            elif i == depth - 1:
                # Last level
                raw_data.append({"level": i, "value": "deep_value"})
            else:
                # Intermediate levels
                raw_data.append({"level": i, "next": current_index + 1})
            current_index += 1
        
        start_time = time.time()
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        end_time = time.time()
        
        # Should complete in reasonable time
        processing_time = end_time - start_time
        assert processing_time < 0.5, f"Deep nesting took {processing_time:.2f}s, expected < 0.5s"
        
        # Verify structure
        current = result
        for i in range(depth - 1):
            assert current["level"] == i
            current = current["next"]
        assert current["level"] == depth - 1
        assert current["value"] == "deep_value"
    
    def test_many_circular_references_performance(self) -> None:
        """Test performance with many circular references."""
        num_objects = 50
        raw_data = [{"state": 1}]  # metadata
        
        # Create root with references to all objects
        root = {"objects": list(range(2, num_objects + 2))}
        raw_data.append(root)
        
        # Create objects that reference each other
        for i in range(num_objects):
            obj = {
                "id": i,
                "name": f"obj_{i}",
                "next": ((i + 1) % num_objects) + 2,  # Circular reference
                "prev": ((i - 1) % num_objects) + 2   # Circular reference
            }
            raw_data.append(obj)
        
        start_time = time.time()
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        end_time = time.time()
        
        # Should complete without infinite loops
        processing_time = end_time - start_time
        assert processing_time < 1.0, f"Circular refs took {processing_time:.2f}s, expected < 1.0s"
        
        # Verify structure (basic check to ensure no infinite loops)
        assert len(result["objects"]) == num_objects
        assert result["objects"][0]["id"] == 0
        assert result["objects"][0]["next"]["id"] == 1
        assert result["objects"][0]["prev"]["id"] == num_objects - 1
    
    def test_memory_efficiency_with_caching(self) -> None:
        """Test that caching prevents memory explosion."""
        # Create data where many objects reference the same large object
        shared_object = {"data": list(range(1000)), "metadata": "large_shared_object"}
        
        raw_data = [
            {"state": 1},  # metadata
            {"references": [2, 2, 2, 2, 2]},  # Many refs to same object
            shared_object
        ]
        
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        
        # All references should point to the same object (memory efficient)
        refs = result["references"]
        assert len(refs) == 5
        assert all(ref is refs[0] for ref in refs), "References should share the same object"
        assert refs[0]["metadata"] == "large_shared_object"
    
    def test_special_types_performance(self) -> None:
        """Test performance with many special type objects."""
        num_items = 100
        raw_data = [{"state": 1}]  # metadata
        
        # Create root with references to special type objects
        root = {"items": list(range(2, num_items + 2))}
        raw_data.append(root)
        
        # Add many special type objects
        for i in range(num_items):
            item = {
                "id": i,
                "date": {"$d": 1672531200000 + i * 86400000},  # Different dates
                "tags": {"$s": [num_items + 2 + i * 2, num_items + 2 + i * 2 + 1]},  # Sets
                "bignum": {"$b": str(123456789012345 + i)},  # BigInts
                "pattern": {"$r": f"/pattern_{i}/g"}  # RegExps
            }
            raw_data.append(item)
        
        # Add tag strings
        for i in range(num_items * 2):
            raw_data.append(f"tag_{i}")
        
        start_time = time.time()
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        end_time = time.time()
        
        # Should complete in reasonable time
        processing_time = end_time - start_time
        assert processing_time < 2.0, f"Special types took {processing_time:.2f}s, expected < 2.0s"
        
        # Verify some special types were processed correctly
        first_item = result["items"][0]
        assert hasattr(first_item["date"], "year")  # datetime object
        assert isinstance(first_item["tags"], set)  # set object
        assert isinstance(first_item["bignum"], int)  # int object
        assert hasattr(first_item["pattern"], "pattern")  # regex object


class TestDeserializationEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_self_referencing_object(self) -> None:
        """Test object that references itself."""
        raw_data = [
            {"state": 1},
            {"name": "self", "self_ref": 1}  # References itself
        ]
        
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        
        # Should handle self-reference without infinite recursion
        assert result["name"] == "self"
        assert result["self_ref"]["name"] == "self"
        # The self_ref should be the same object (cached)
        assert result["self_ref"] is result
    
    def test_complex_circular_chain(self) -> None:
        """Test complex circular reference chain."""
        raw_data = [
            {"state": 1},
            {"name": "A", "next": 2},  # A -> B
            {"name": "B", "next": 3},  # B -> C  
            {"name": "C", "next": 1}   # C -> A (circular)
        ]
        
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        
        # Should resolve circular chain
        assert result["name"] == "A"
        assert result["next"]["name"] == "B"
        assert result["next"]["next"]["name"] == "C"
        assert result["next"]["next"]["next"]["name"] == "A"
        # Should be the same object (cached)
        assert result["next"]["next"]["next"] is result
    
    def test_mixed_reference_types(self) -> None:
        """Test mixing integer references with special types."""
        raw_data = [
            {"state": 1},
            {
                "user": 2,
                "settings": {"$m": [[3, 4]]},
                "timestamps": [{"$d": 1672531200000}, 5]
            },
            {"name": "Alice", "created": {"$d": 1672617600000}},
            "theme",
            "dark",
            {"last_login": {"$d": 1672704000000}}
        ]
        
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        
        # Check mixed types resolved correctly
        assert result["user"]["name"] == "Alice"
        assert hasattr(result["user"]["created"], "year")
        assert isinstance(result["settings"], dict)
        assert result["settings"]["theme"] == "dark"
        assert len(result["timestamps"]) == 2
        assert hasattr(result["timestamps"][0], "year")
        assert hasattr(result["timestamps"][1]["last_login"], "year")
    
    def test_malformed_special_type_fallback(self) -> None:
        """Test fallback behavior for malformed special types."""
        raw_data = [
            {"state": 1},
            {
                "bad_date": {"$d": "not_a_timestamp"},
                "bad_set": {"$s": "not_an_array"},
                "bad_map": {"$m": "not_an_array"},
                "bad_bigint": {"$b": None},
                "bad_regexp": {"$r": None},
                "good_field": "works"
            }
        ]
        
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        
        # Should fallback gracefully for malformed types
        assert result["bad_date"] == {"$d": "not_a_timestamp"}
        assert result["bad_set"] == {"$s": "not_an_array"}
        assert result["bad_map"] == {"$m": "not_an_array"}
        assert result["bad_bigint"] == {"$b": None}
        assert result["bad_regexp"] is None  # Special case for None
        assert result["good_field"] == "works"
    
    def test_empty_special_types(self) -> None:
        """Test handling of empty special types."""
        raw_data = [
            {"state": 1},
            {
                "empty_set": {"$s": []},
                "empty_map": {"$m": []},
                "empty_bigint": {"$b": ""},
                "empty_regexp": {"$r": "//"}
            }
        ]
        
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        
        # Should handle empty cases
        assert isinstance(result["empty_set"], set)
        assert len(result["empty_set"]) == 0
        assert isinstance(result["empty_map"], dict)
        assert len(result["empty_map"]) == 0
        # Empty string BigInt should fallback
        assert result["empty_bigint"] == {"$b": ""}
        # Empty regex should work
        assert hasattr(result["empty_regexp"], "pattern")
    
    def test_nested_special_types(self) -> None:
        """Test special types containing references to other special types."""
        raw_data = [
            {"state": 1},
            {
                "complex": {"$m": [[2, 3], [4, 5]]}
            },
            "dates",
            {"$s": [6, 7]},  # Set containing dates
            "users",
            [{"$d": 1672531200000}, {"$d": 1672617600000}],  # Array of dates
            {"$d": 1672531200000},  # Date 1
            {"$d": 1672617600000}   # Date 2
        ]
        
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        
        # Check nested special types
        assert isinstance(result["complex"], dict)
        assert "dates" in result["complex"]
        assert "users" in result["complex"]
        
        # The set should contain dates
        date_set = result["complex"]["dates"]
        assert isinstance(date_set, set)
        assert len(date_set) == 2
        assert all(hasattr(d, "year") for d in date_set)
        
        # The array should contain dates
        date_array = result["complex"]["users"]
        assert isinstance(date_array, list)
        assert len(date_array) == 2
        assert all(hasattr(d, "year") for d in date_array)
    
    def test_very_large_json_string(self) -> None:
        """Test handling of very large JSON strings."""
        # Create a moderately large structure
        size = 500
        large_data = [{"state": 1}]
        
        # Add root with many items
        root = {"items": list(range(2, size + 2))}
        large_data.append(root)
        
        # Add items with nested data
        for i in range(size):
            item = {
                "id": i,
                "name": f"item_{i}",
                "data": list(range(10)),  # Some nested data
                "metadata": {
                    "created": {"$d": 1672531200000 + i * 1000},
                    "tags": {"$s": [size + 2 + i * 2, size + 2 + i * 2 + 1]}
                }
            }
            large_data.append(item)
        
        # Add tag strings
        for i in range(size * 2):
            large_data.append(f"tag_{i}")
        
        # Convert to JSON string
        json_string = json.dumps(large_data)
        
        # Should handle large JSON string
        start_time = time.time()
        result = deserialize_nuxt3_data(json_string, is_json_string=True)
        end_time = time.time()
        
        processing_time = end_time - start_time
        assert processing_time < 3.0, f"Large JSON took {processing_time:.2f}s, expected < 3.0s"
        
        # Verify structure
        assert len(result["items"]) == size
        assert hasattr(result["items"][0]["metadata"]["created"], "year")
        assert isinstance(result["items"][0]["metadata"]["tags"], set)


class TestCachingBehavior:
    """Test caching behavior in detail."""
    
    def test_cache_prevents_duplicate_processing(self) -> None:
        """Test that cache prevents duplicate processing of same objects."""
        raw_data = [
            {"state": 1},
            {"refs": [2, 2, 2]},  # Multiple refs to same object
            {"expensive": "object", "data": list(range(100))}
        ]
        
        cache = {}
        result = _hydrate_nuxt3_value(raw_data, 1, cache)
        
        # Should have cached the expensive object
        assert 2 in cache
        
        # All references should be the same object
        refs = result["refs"]
        assert all(ref is refs[0] for ref in refs)
    
    def test_cache_handles_primitive_values(self) -> None:
        """Test that cache properly handles primitive values."""
        raw_data = ["string", 42, True, None]
        cache = {}
        
        # Process primitive values
        for i in range(len(raw_data)):
            result = _hydrate_nuxt3_value(raw_data, i, cache)
            assert result == raw_data[i]
            assert i in cache
            assert cache[i] == raw_data[i]
    
    def test_cache_early_insertion_prevents_infinite_recursion(self) -> None:
        """Test that early cache insertion prevents infinite recursion."""
        raw_data = [
            {"state": 1},
            {"name": "A", "ref": 1}  # Self-reference
        ]
        
        cache = {}
        result = _hydrate_nuxt3_value(raw_data, 1, cache)
        
        # Should have cached early to prevent infinite recursion
        assert 1 in cache
        assert result is cache[1]
        assert result["ref"] is result
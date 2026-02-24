"""Tests for Nuxt Scraper parser module."""

from __future__ import annotations

import json
from datetime import datetime
import re

import pytest

from nuxt_scraper.exceptions import DataParsingError, NuxtDataNotFound
from nuxt_scraper.parser import (
    NUXT_DATA_ELEMENT_ID,
    parse_nuxt_json,
    parse_nuxt_result,
    validate_extracted_result,
    deserialize_nuxt3_data,
    _hydrate_nuxt3_value,
)


class TestParseNuxtJson:
    def test_parses_valid_json_object(self) -> None:
        raw = '{"key": "value", "nested": {"a": 1}}'
        result = parse_nuxt_json(raw)
        assert result == {"key": "value", "nested": {"a": 1}}

    def test_parses_valid_json_array(self) -> None:
        raw = '[1, 2, {"x": 3}]'
        result = parse_nuxt_json(raw)
        assert result == [1, 2, {"x": 3}]

    def test_raises_on_empty_string(self) -> None:
        with pytest.raises(DataParsingError) as exc_info:
            parse_nuxt_json("")
        assert "empty" in str(exc_info.value).lower()

    def test_raises_on_whitespace_only(self) -> None:
        with pytest.raises(DataParsingError):
            parse_nuxt_json("   \n\t  ")

    def test_raises_on_invalid_json(self) -> None:
        with pytest.raises(DataParsingError) as exc_info:
            parse_nuxt_json("not valid json {")
        assert exc_info.value.raw_content == "not valid json {"


class TestValidateExtractedResult:
    def test_accepts_dict(self) -> None:
        value = {"a": 1}
        assert validate_extracted_result(value) is value

    def test_accepts_list(self) -> None:
        value = [1, 2, 3]
        assert validate_extracted_result(value) is value

    def test_raises_on_none(self) -> None:
        with pytest.raises(NuxtDataNotFound):
            validate_extracted_result(None)


class TestConstants:
    def test_nuxt_data_element_id(self) -> None:
        assert NUXT_DATA_ELEMENT_ID == "__NUXT_DATA__"


class TestDeserializeNuxt3Data:
    """Test the new hydration-based Nuxt 3 deserialization engine."""
    
    def test_deserialize_simple_array(self) -> None:
        """Test basic array deserialization."""
        raw_data = [
            {"state": 1},  # metadata
            {"name": "test", "value": 42}  # actual data
        ]
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        assert result == {"name": "test", "value": 42}
    
    def test_deserialize_with_references(self) -> None:
        """Test deserialization with integer references."""
        raw_data = [
            {"state": 1},  # metadata
            {"users": [2, 3]},  # root with references
            {"id": 1, "name": "Alice"},  # index 2
            {"id": 2, "name": "Bob"}     # index 3
        ]
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        expected = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ]
        }
        assert result == expected
    
    def test_deserialize_date_objects(self) -> None:
        """Test deserialization of Date objects ($d)."""
        raw_data = [
            {"state": 1},
            {"created": {"$d": 1672531200000}}  # 2023-01-01 00:00:00 UTC
        ]
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        assert isinstance(result["created"], datetime)
        assert result["created"].year == 2023
        assert result["created"].month == 1
        assert result["created"].day == 1
    
    def test_deserialize_set_objects(self) -> None:
        """Test deserialization of Set objects ($s)."""
        raw_data = [
            {"state": 1},
            {"tags": {"$s": [2, 3]}},
            "admin",
            "user"
        ]
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        assert isinstance(result["tags"], set)
        assert result["tags"] == {"admin", "user"}
    
    def test_deserialize_map_objects(self) -> None:
        """Test deserialization of Map objects ($m)."""
        raw_data = [
            {"state": 1},
            {"metadata": {"$m": [[2, 3], [4, 5]]}},
            "version",
            "1.0.0",
            "author", 
            "John Doe"
        ]
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        assert isinstance(result["metadata"], dict)
        assert result["metadata"] == {"version": "1.0.0", "author": "John Doe"}
    
    def test_deserialize_bigint_objects(self) -> None:
        """Test deserialization of BigInt objects ($b)."""
        raw_data = [
            {"state": 1},
            {"bigNumber": {"$b": "123456789012345"}}
        ]
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        assert isinstance(result["bigNumber"], int)
        assert result["bigNumber"] == 123456789012345
    
    def test_deserialize_regexp_objects(self) -> None:
        """Test deserialization of RegExp objects ($r)."""
        raw_data = [
            {"state": 1},
            {"pattern": {"$r": "/test/gi"}}
        ]
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        assert isinstance(result["pattern"], re.Pattern)
        assert result["pattern"].pattern == "test"
        assert result["pattern"].flags & re.IGNORECASE
        assert result["pattern"].flags & re.MULTILINE
    
    def test_deserialize_circular_references(self) -> None:
        """Test handling of circular references through caching."""
        raw_data = [
            {"state": 1},
            {"parent": 2, "child": 3},
            {"name": "parent", "child": 3},
            {"name": "child", "parent": 2}
        ]
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        
        # Should resolve without infinite recursion
        assert result["parent"]["name"] == "parent"
        assert result["child"]["name"] == "child"
        # Circular references should be handled gracefully
        assert result["parent"]["child"]["name"] == "child"
        assert result["child"]["parent"]["name"] == "parent"
    
    def test_deserialize_complex_nested_structure(self) -> None:
        """Test complex nested structure with multiple reference types."""
        raw_data = [
            {"state": 1},
            {
                "user": 2,
                "settings": 3,
                "timestamps": 4
            },
            {
                "name": "Alice",
                "created": {"$d": 1672531200000},
                "tags": {"$s": [5, 6]},
                "metadata": {"$m": [[7, 8]]}
            },
            {
                "theme": "dark",
                "notifications": True
            },
            [
                {"$d": 1672617600000},
                {"$d": 1672704000000}
            ],
            "admin",
            "user",
            "version",
            "1.0.0"
        ]
        
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        
        # Check structure
        assert result["user"]["name"] == "Alice"
        assert isinstance(result["user"]["created"], datetime)
        assert isinstance(result["user"]["tags"], set)
        assert result["user"]["tags"] == {"admin", "user"}
        assert isinstance(result["user"]["metadata"], dict)
        assert result["user"]["metadata"] == {"version": "1.0.0"}
        assert result["settings"]["theme"] == "dark"
        assert isinstance(result["timestamps"], list)
        assert len(result["timestamps"]) == 2
        assert all(isinstance(ts, datetime) for ts in result["timestamps"])
    
    def test_deserialize_json_string(self) -> None:
        """Test deserialization from JSON string."""
        raw_data = [
            {"state": 1},
            {"name": "test", "value": 42}
        ]
        json_string = json.dumps(raw_data)
        
        result = deserialize_nuxt3_data(json_string, is_json_string=True)
        assert result == {"name": "test", "value": 42}
    
    def test_deserialize_non_list_data(self) -> None:
        """Test handling of non-list data (not Nuxt 3 format)."""
        raw_data = {"simple": "object"}
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        assert result == raw_data  # Should return as-is
    
    def test_deserialize_empty_array(self) -> None:
        """Test handling of empty array."""
        raw_data = []
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        assert result == raw_data  # Should return as-is
    
    def test_deserialize_malformed_special_types(self) -> None:
        """Test graceful handling of malformed special types."""
        raw_data = [
            {"state": 1},
            {
                "bad_date": {"$d": "invalid"},
                "bad_bigint": {"$b": "not_a_number"},
                "bad_regexp": {"$r": "invalid_regex"},
                "normal_field": "works"
            }
        ]
        
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        
        # Should fallback gracefully for malformed types
        assert result["bad_date"] == {"$d": "invalid"}
        assert result["bad_bigint"] == {"$b": "not_a_number"}
        assert result["bad_regexp"] == "invalid_regex"  # Fallback to string
        assert result["normal_field"] == "works"
    
    def test_deserialize_invalid_json_string(self) -> None:
        """Test error handling for invalid JSON string."""
        with pytest.raises(DataParsingError) as exc_info:
            deserialize_nuxt3_data("invalid json {", is_json_string=True)
        assert "Failed to parse Nuxt data JSON" in str(exc_info.value)
    
    def test_deserialize_out_of_bounds_reference(self) -> None:
        """Test handling of out-of-bounds references."""
        raw_data = [
            {"state": 1},
            {"ref": 999}  # Out of bounds reference
        ]
        
        result = deserialize_nuxt3_data(raw_data, is_json_string=False)
        assert result["ref"] is None  # Should handle gracefully


class TestHydrateNuxt3Value:
    """Test the core hydration function."""
    
    def test_hydrate_primitive_values(self) -> None:
        """Test hydration of primitive values."""
        data_array = ["test", 42, True, None]
        cache = {}
        
        assert _hydrate_nuxt3_value(data_array, "direct_string", cache) == "direct_string"
        assert _hydrate_nuxt3_value(data_array, 42, cache) == 42
        assert _hydrate_nuxt3_value(data_array, True, cache) == True
        assert _hydrate_nuxt3_value(data_array, None, cache) is None
    
    def test_hydrate_index_references(self) -> None:
        """Test hydration of index references."""
        data_array = ["zero", "one", {"key": "value"}]
        cache = {}
        
        result = _hydrate_nuxt3_value(data_array, 0, cache)
        assert result == "zero"
        
        result = _hydrate_nuxt3_value(data_array, 2, cache)
        assert result == {"key": "value"}
        
        # Check caching
        assert 0 in cache
        assert 2 in cache
    
    def test_hydrate_out_of_bounds_index(self) -> None:
        """Test handling of out-of-bounds index."""
        data_array = ["zero", "one"]
        cache = {}
        
        result = _hydrate_nuxt3_value(data_array, 999, cache)
        assert result is None
    
    def test_hydrate_caching_prevents_reprocessing(self) -> None:
        """Test that caching prevents duplicate processing."""
        data_array = ["test", {"complex": "object"}]
        cache = {}
        
        # First call should process and cache
        result1 = _hydrate_nuxt3_value(data_array, 1, cache)
        assert 1 in cache
        
        # Second call should use cache
        result2 = _hydrate_nuxt3_value(data_array, 1, cache)
        assert result1 is result2  # Same object reference


class TestParseNuxtResult:
    """Test the parse_nuxt_result function."""
    
    def test_parse_element_method_with_deserialization(self) -> None:
        """Test parsing from element method with deserialization enabled."""
        extraction_result = {
            "data": json.dumps([{"state": 1}, {"name": "test"}]),
            "method": "element",
            "raw": "raw_data"
        }
        
        result, method = parse_nuxt_result(extraction_result, deserialize_nuxt3=True)
        assert method == "element"
        assert result == {"name": "test"}
    
    def test_parse_element_method_without_deserialization(self) -> None:
        """Test parsing from element method with deserialization disabled."""
        test_data = {"simple": "object"}
        extraction_result = {
            "data": json.dumps(test_data),
            "method": "element", 
            "raw": "raw_data"
        }
        
        result, method = parse_nuxt_result(extraction_result, deserialize_nuxt3=False)
        assert method == "element"
        assert result == test_data
    
    def test_parse_window_method_with_deserialization(self) -> None:
        """Test parsing from window method with deserialization enabled."""
        raw_data = [{"state": 1}, {"name": "test"}]
        extraction_result = {
            "data": raw_data,
            "method": "window",
            "raw": "raw_data"
        }
        
        result, method = parse_nuxt_result(extraction_result, deserialize_nuxt3=True)
        assert method == "window"
        assert result == {"name": "test"}
    
    def test_parse_window_method_without_deserialization(self) -> None:
        """Test parsing from window method with deserialization disabled."""
        test_data = {"simple": "object"}
        extraction_result = {
            "data": test_data,
            "method": "window",
            "raw": "raw_data"
        }
        
        result, method = parse_nuxt_result(extraction_result, deserialize_nuxt3=False)
        assert method == "window"
        assert result == test_data
    
    def test_parse_unknown_method_raises_error(self) -> None:
        """Test that unknown method raises DataParsingError."""
        extraction_result = {
            "data": "test",
            "method": "unknown",
            "raw": "raw_data"
        }
        
        with pytest.raises(DataParsingError) as exc_info:
            parse_nuxt_result(extraction_result)
        assert "Unknown extraction method: unknown" in str(exc_info.value)
    
    def test_parse_missing_data_raises_error(self) -> None:
        """Test that missing data raises NuxtDataNotFound."""
        extraction_result = {
            "data": None,
            "method": "element",
            "raw": "raw_data"
        }
        
        with pytest.raises(NuxtDataNotFound):
            parse_nuxt_result(extraction_result)
    
    def test_parse_invalid_extraction_result(self) -> None:
        """Test handling of invalid extraction result."""
        with pytest.raises(NuxtDataNotFound):
            parse_nuxt_result(None)
        
        with pytest.raises(NuxtDataNotFound):
            parse_nuxt_result({})
        
        with pytest.raises(NuxtDataNotFound):
            parse_nuxt_result({"data": None, "method": None})

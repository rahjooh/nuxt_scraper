"""Data extraction and JSON parsing utilities for Nuxt __NUXT_DATA__ and window.__NUXT__."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, Tuple, Set, Union, List
from datetime import datetime
import re

from nuxt_scraper.exceptions import DataParsingError, NuxtDataNotFound

logger = logging.getLogger(__name__)

NUXT_DATA_ELEMENT_ID = "__NUXT_DATA__"

# JavaScript snippet to extract __NUXT_DATA__ content (runs in browser context)
EXTRACT_NUXT_DATA_SCRIPT = """
() => {
    const element = document.getElementById('__NUXT_DATA__');
    if (!element) return null;
    const text = element.textContent;
    if (!text || !text.trim()) return null;
    return text;
}
"""

# JavaScript snippet to extract window.__NUXT__ content (runs in browser context)
EXTRACT_WINDOW_NUXT_SCRIPT = """
() => {
    if (typeof window !== 'undefined' && window.__NUXT__) {
        return window.__NUXT__;
    }
    return null;
}
"""

# Combined JavaScript snippet that tries both methods with priority and metadata
EXTRACT_NUXT_COMBINED_SCRIPT = """
() => {
    const result = {
        data: null,
        method: null,
        raw: null
    };
    
    // Method 1: Try #__NUXT_DATA__ element (Nuxt 3 style)
    const element = document.getElementById('__NUXT_DATA__');
    if (element) {
        const text = element.textContent;
        if (text && text.trim()) {
            result.data = text;
            result.method = 'element';
            result.raw = text;
            return result;
        }
    }
    
    // Method 2: Try window.__NUXT__ (Nuxt 2 style and some Nuxt 3 configs)
    if (typeof window !== 'undefined' && window.__NUXT__) {
        result.data = window.__NUXT__;
        result.method = 'window';
        result.raw = JSON.stringify(window.__NUXT__);
        return result;
    }
    
    return result;
}
"""

# Note: The old NUXT3_REACTIVE_TYPES approach has been replaced with proper hydration
# that follows Nuxt 3's actual serialization format using the devalue library


def _hydrate_nuxt3_value(data_array: List[Any], index_or_value: Any, cache: Dict[int, Any]) -> Any:
    """
    Hydrate a Nuxt 3 serialized value using proper caching to handle circular references.
    
    This implements the proper Nuxt 3 deserialization logic based on the devalue library
    that Nuxt uses internally for serialization.
    
    Args:
        data_array: The full Nuxt data array
        index_or_value: Either an index (int) pointing to data_array or a direct value
        cache: Cache to store already hydrated values and prevent circular references
        
    Returns:
        Hydrated value with all references resolved
    """
    # If it's not an integer, return as-is (primitive value)
    if not isinstance(index_or_value, int):
        return index_or_value
    
    # Check bounds
    if index_or_value < 0 or index_or_value >= len(data_array):
        logger.warning(f"Index {index_or_value} out of bounds for data array of length {len(data_array)}")
        return None
    
    # Check cache to prevent circular references and avoid re-processing
    if index_or_value in cache:
        return cache[index_or_value]
    
    value = data_array[index_or_value]
    
    # Handle primitives (None, str, bool, float, int)
    if value is None or isinstance(value, (str, bool, float, int)):
        cache[index_or_value] = value
        return value
    
    # Handle objects (dictionaries)
    if isinstance(value, dict):
        # Check for special Nuxt/devalue types
        if "$d" in value:
            # Date object: {"$d": timestamp_in_milliseconds}
            try:
                timestamp = value["$d"] / 1000  # Convert from milliseconds to seconds
                result = datetime.fromtimestamp(timestamp)
                cache[index_or_value] = result
                return result
            except (ValueError, TypeError, OverflowError) as e:
                logger.warning(f"Failed to parse date from {value}: {e}")
                cache[index_or_value] = value
                return value
        
        elif "$s" in value:
            # Set object: {"$s": [index1, index2, ...]}
            result = set()
            cache[index_or_value] = result  # Cache early to handle circular refs
            for item_index in value["$s"]:
                hydrated_item = _hydrate_nuxt3_value(data_array, item_index, cache)
                result.add(hydrated_item)
            return result
        
        elif "$m" in value:
            # Map object: {"$m": [[key_index, value_index], ...]}
            result = {}
            cache[index_or_value] = result  # Cache early to handle circular refs
            for key_index, value_index in value["$m"]:
                hydrated_key = _hydrate_nuxt3_value(data_array, key_index, cache)
                hydrated_value = _hydrate_nuxt3_value(data_array, value_index, cache)
                result[hydrated_key] = hydrated_value
            return result
        
        elif "$b" in value:
            # BigInt object: {"$b": "123456789..."}
            try:
                result = int(value["$b"])
                cache[index_or_value] = result
                return result
            except ValueError as e:
                logger.warning(f"Failed to parse BigInt from {value}: {e}")
                cache[index_or_value] = value
                return value
        
        elif "$r" in value:
            # RegExp object: {"$r": "/pattern/flags"}
            try:
                pattern_str = value["$r"]
                if pattern_str.startswith('/') and '/' in pattern_str[1:]:
                    last_slash = pattern_str.rfind('/')
                    pattern = pattern_str[1:last_slash]
                    flags_str = pattern_str[last_slash + 1:]
                    
                    # Convert JS regex flags to Python flags
                    flags = 0
                    if 'i' in flags_str:
                        flags |= re.IGNORECASE
                    if 'm' in flags_str:
                        flags |= re.MULTILINE
                    if 's' in flags_str:
                        flags |= re.DOTALL
                    
                    result = re.compile(pattern, flags)
                    cache[index_or_value] = result
                    return result
                else:
                    # Fallback: just return the pattern string
                    cache[index_or_value] = pattern_str
                    return pattern_str
            except Exception as e:
                logger.warning(f"Failed to parse RegExp from {value}: {e}")
                cache[index_or_value] = value
                return value
        
        else:
            # Regular object - hydrate all key-value pairs
            result = {}
            cache[index_or_value] = result  # Cache early to handle circular refs
            for k, v in value.items():
                result[k] = _hydrate_nuxt3_value(data_array, v, cache)
            return result
    
    # Handle arrays
    if isinstance(value, list):
        result = []
        cache[index_or_value] = result  # Cache early to handle circular refs
        for item in value:
            result.append(_hydrate_nuxt3_value(data_array, item, cache))
        return result
    
    # Fallback for unknown types
    cache[index_or_value] = value
    return value


def deserialize_nuxt3_data(raw_data: Union[str, List[Any]], is_json_string: bool = True) -> Any:
    """
    Deserialize Nuxt 3 serialized data format using proper hydration.
    
    This implements the correct Nuxt 3 deserialization logic that handles:
    - Circular references through caching
    - Special types (Date, Set, Map, BigInt, RegExp)
    - Proper reference resolution without exponential expansion
    
    Args:
        raw_data: Raw Nuxt data (JSON string or already parsed list)
        is_json_string: Whether raw_data is a JSON string that needs parsing
        
    Returns:
        Deserialized data with resolved references
        
    Raises:
        DataParsingError: When deserialization fails
    """
    try:
        # Parse JSON string if needed
        if is_json_string:
            if isinstance(raw_data, str):
                parsed_data = json.loads(raw_data)
            else:
                raise DataParsingError("Expected JSON string but got non-string type")
        else:
            parsed_data = raw_data
        
        # Validate it's a list (Nuxt 3 serialized format)
        if not isinstance(parsed_data, list):
            logger.debug("Data is not in Nuxt 3 serialized format (not a list)")
            return parsed_data
        
        # Check if it has the expected structure
        if len(parsed_data) == 0:
            logger.debug("Empty data array")
            return parsed_data
        
        # Initialize cache for circular reference handling
        cache = {}
        
        logger.info("Deserializing Nuxt 3 data format using hydration")
        
        # For Nuxt 3, the actual data is usually at index 1, with index 0 being metadata
        # But we should check the structure first
        if len(parsed_data) >= 2:
            # Try to hydrate from index 1 (common Nuxt 3 pattern)
            result = _hydrate_nuxt3_value(parsed_data, 1, cache)
        else:
            # Fallback: hydrate from index 0
            result = _hydrate_nuxt3_value(parsed_data, 0, cache)
        
        logger.info(f"Successfully deserialized Nuxt 3 data. Cache size: {len(cache)}")
        return result
        
    except json.JSONDecodeError as e:
        raise DataParsingError(f"Failed to parse Nuxt data JSON: {e}") from e
    except Exception as e:
        logger.warning(f"Nuxt 3 deserialization failed, returning raw data: {e}")
        # Return raw data if deserialization fails
        if is_json_string:
            try:
                return json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            except:
                return raw_data
        return raw_data


def parse_nuxt_json(raw: str, deserialize_nuxt3: bool = True) -> Any:
    """
    Parse raw string content from __NUXT_DATA__ as JSON.

    Args:
        raw: Raw text content from the __NUXT_DATA__ element.
        deserialize_nuxt3: Whether to deserialize Nuxt 3 reactive references.

    Returns:
        Parsed Python object (dict, list, etc.).

    Raises:
        DataParsingError: When the content is not valid JSON.
    """
    if not raw or not raw.strip():
        raise DataParsingError("Nuxt data content is empty", raw_content=raw)

    try:
        parsed_data = json.loads(raw)
        
        # Apply Nuxt 3 deserialization if requested
        if deserialize_nuxt3:
            return deserialize_nuxt3_data(parsed_data, is_json_string=False)
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        logger.debug("JSON decode error: %s", e)
        raise DataParsingError(
            message=f"Failed to parse Nuxt data as JSON: {e!s}",
            raw_content=raw,
        ) from e


def parse_nuxt_result(extraction_result: Dict[str, Any], deserialize_nuxt3: bool = True) -> Tuple[Any, str]:
    """
    Parse the result from the combined Nuxt extraction script.
    
    Args:
        extraction_result: Result dictionary from EXTRACT_NUXT_COMBINED_SCRIPT
        deserialize_nuxt3: Whether to deserialize Nuxt 3 reactive references
        
    Returns:
        Tuple of (parsed_data, extraction_method)
        
    Raises:
        DataParsingError: When the content cannot be parsed
        NuxtDataNotFound: When no Nuxt data is found
    """
    if not extraction_result or not isinstance(extraction_result, dict):
        raise NuxtDataNotFound("No extraction result received")
    
    data = extraction_result.get('data')
    method = extraction_result.get('method')
    raw = extraction_result.get('raw')
    
    if not data or not method:
        raise NuxtDataNotFound("No Nuxt data found via element or window methods")
    
    logger.info(f"Nuxt data found via {method} method")
    
    try:
        if method == 'element':
            # Data from #__NUXT_DATA__ element is a JSON string
            return parse_nuxt_json(data, deserialize_nuxt3=deserialize_nuxt3), method
        elif method == 'window':
            # Data from window.__NUXT__ is already a JavaScript object
            # Apply deserialization if it's in Nuxt 3 format and requested
            if deserialize_nuxt3 and isinstance(data, list):
                return deserialize_nuxt3_data(data, is_json_string=False), method
            return data, method
        else:
            raise DataParsingError(f"Unknown extraction method: {method}")
            
    except (json.JSONDecodeError, TypeError) as e:
        logger.debug("Parse error for method %s: %s", method, e)
        raise DataParsingError(
            message=f"Failed to parse Nuxt data from {method}: {e!s}",
            raw_content=str(raw),
        ) from e


def validate_extracted_result(value: Any) -> Any:
    """
    Validate that the extracted value is usable (non-null, typically dict).

    Args:
        value: Value returned from browser evaluation.

    Returns:
        The same value if valid.

    Raises:
        NuxtDataNotFound: When value is None or indicates missing data.
    """
    if value is None:
        raise NuxtDataNotFound("__NUXT_DATA__ element not found or empty")
    return value


def validate_combined_result(extraction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the result from combined Nuxt extraction.
    
    Args:
        extraction_result: Result from EXTRACT_NUXT_COMBINED_SCRIPT
        
    Returns:
        The same result if valid
        
    Raises:
        NuxtDataNotFound: When no valid Nuxt data is found
    """
    if not extraction_result or not isinstance(extraction_result, dict):
        raise NuxtDataNotFound("No valid extraction result received")
    
    if not extraction_result.get('data') or not extraction_result.get('method'):
        raise NuxtDataNotFound("No Nuxt data found via #__NUXT_DATA__ element or window.__NUXT__")
    
    return extraction_result

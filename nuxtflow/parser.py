"""Data extraction and JSON parsing utilities for Nuxt __NUXT_DATA__."""

from __future__ import annotations

import json
import logging
from typing import Any

from nuxtflow.exceptions import DataParsingError, NuxtDataNotFound

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


def parse_nuxt_json(raw: str) -> Any:
    """
    Parse raw string content from __NUXT_DATA__ as JSON.

    Args:
        raw: Raw text content from the __NUXT_DATA__ element.

    Returns:
        Parsed Python object (dict, list, etc.).

    Raises:
        DataParsingError: When the content is not valid JSON.
    """
    if not raw or not raw.strip():
        raise DataParsingError("Nuxt data content is empty", raw_content=raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.debug("JSON decode error: %s", e)
        raise DataParsingError(
            message=f"Failed to parse Nuxt data as JSON: {e!s}",
            raw_content=raw,
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

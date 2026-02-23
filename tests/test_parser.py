"""Tests for NuxtFlow parser module."""

from __future__ import annotations

import pytest

from nuxtflow.exceptions import DataParsingError, NuxtDataNotFound
from nuxtflow.parser import (
    NUXT_DATA_ELEMENT_ID,
    parse_nuxt_json,
    validate_extracted_result,
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

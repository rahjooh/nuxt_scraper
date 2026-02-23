"""Custom exception classes for NuxtFlow."""

from __future__ import annotations

from typing import Any


class NuxtFlowException(Exception):
    """Base exception for all NuxtFlow errors."""

    pass


class NuxtDataNotFound(NuxtFlowException):
    """Raised when the __NUXT_DATA__ element is missing or empty."""

    def __init__(self, message: str = "__NUXT_DATA__ element not found") -> None:
        self.message = message
        super().__init__(self.message)


class NavigationStepFailed(NuxtFlowException):
    """Raised when a navigation step fails during execution."""

    def __init__(
        self,
        step: Any,
        original_error: Exception,
        message: str | None = None,
    ) -> None:
        self.step = step
        self.original_error = original_error
        msg = message or f"Step failed: {original_error!s}"
        super().__init__(msg)


class ExtractionTimeout(NuxtFlowException):
    """Raised when an operation exceeds the configured timeout."""

    def __init__(self, message: str = "Extraction timed out") -> None:
        self.message = message
        super().__init__(self.message)


class DataParsingError(NuxtFlowException):
    """Raised when Nuxt data cannot be parsed as valid JSON."""

    def __init__(
        self,
        message: str = "Failed to parse Nuxt data as JSON",
        raw_content: str | None = None,
    ) -> None:
        self.message = message
        self.raw_content = raw_content
        super().__init__(self.message)


class BrowserError(NuxtFlowException):
    """Raised when Playwright browser operations fail."""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        self.original_error = original_error
        super().__init__(message)

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.3] - 2026-02-23

### Changed

-   Revamped `README.md` to provide a more robust and comprehensive "Usage" guide.
-   Restructured "Usage" section with detailed subsections for `extract_nuxt_data`, `NuxtDataExtractor`, `NavigationStep` (with individual examples for each factory method), and `StealthConfig`.
-   Moved calendar date selection example into the main "Navigation Steps" section.
-   Updated `pyproject.toml` and `nuxt_scraper/__init__.py` to version `0.2.3`.

## [0.2.2] - 2026-02-23

### Added

-   `NavigationStep.select_date` for interacting with calendar pop-ups.
-   `StepType.SELECT_DATE` enum value.
-   `DateNotFoundInCalendarError` exception.
-   New example in `examples/advanced_navigation.py` for calendar date selection.

### Changed

-   Updated `pyproject.toml` and `nuxt_scraper/__init__.py` to version `0.2.2`.

## [0.2.1] - 2026-02-23

### Changed

-   Renamed package from `nuxtflow` to `nuxt_scraper`.
-   Updated all file paths, module imports, and references to `nuxtflow` to `nuxt_scraper`.
-   Updated `pyproject.toml` with new package name, repository URLs, and `per-file-ignores` for `ruff`.
-   Updated `README.md` to reflect the new package name and usage.
-   Updated `CHANGELOG.md` with package rename entry.
-   Updated GitHub Actions CI workflow (`.github/workflows/ci.yml`) to use new package name.
-   Updated all test files (`tests/`) to use `nuxt_scraper` imports and match new project structure.
-   Updated `NuxtFlowException` in `nuxt_scraper/exceptions.py` to be compatible with `N818` linting rule via `per-file-ignore`.

### Fixed

-   Resolved GitHub CI errors related to `black` formatting and `ruff` linting by:
    -   Running `black` to reformat code.
    -   Running `ruff --fix` to auto-correct linting issues.
    -   Configuring `pyproject.toml` to ignore `E501` (line too long) for specific files (`user_agents.py`, `stealth_scripts.py`) where long strings are unavoidable.
    -   Manually refactoring long docstrings and comments in various Python files to comply with line limits.

## [0.2.0] - 2026-02-22

### Added

-   **Anti-Detection Strategies** to emulate human-like browsing behavior:
    -   `StealthConfig` dataclass for granular control over anti-detection features.
    -   `human_delay` (randomized pauses between actions).
    -   `simulate_mouse_movement` (realistic curved mouse paths).
    -   `human_type` (variable typing speed, typos, and corrections).
    -   `get_realistic_user_agent` (random user agent rotation).
    -   `get_random_viewport` (randomized browser viewport sizes).
    -   `STEALTH_SCRIPTS` (Playwright `context.add_init_script` for masking automation).
-   **Proxy Support** for `NuxtDataExtractor` to integrate with external proxy services.
-   New `ProxyError` exception for proxy-related issues.
-   Detailed documentation in `README.md` on anti-detection and considerations for WAFs, IP reputation, and CAPTCHA.
-   New `anti_detection` module with sub-modules for each strategy.

### Changed

-   Refactored `NuxtDataExtractor` to accept `StealthConfig` and `proxy` parameters.
-   Updated `execute_step` to optionally apply anti-detection measures.
-   Updated `pyproject.toml` with new dependencies (`playwright`, `pyyaml`).
-   Updated `nuxtflow/__init__.py` to expose new anti-detection components.

### Fixed

-   Corrected async mocking in `tests/conftest.py` for Playwright page methods.
-   Resolved redundant assignments and synchronous calls to async functions in `tests/test_extractor.py`.
-   Removed `self` parameter from module-level async functions in `tests/test_steps.py`.
-   Fixed `simulate_mouse_movement` test by correctly mocking awaited `bounding_box()` method.

## [0.1.0] - 2026-02-21

### Added

-   Initial project structure for `nuxt_scraper`.
-   `NuxtDataExtractor` class for core extraction logic.
-   `extract_nuxt_data` convenience function.
-   `NavigationStep` dataclass and `execute_step`, `execute_steps` functions for browser automation.
-   `parse_nuxt_json` for robust Nuxt data parsing.
-   Custom exception classes: `NuxtFlowException`, `NuxtDataNotFound`, `NavigationStepFailed`, `ExtractionTimeout`, `DataParsingError`, `BrowserError`.
-   Basic `pyproject.toml` for package metadata and dependencies.
-   `README.md`, `LICENSE`, `.gitignore`.
-   Basic unit tests for core functionality.
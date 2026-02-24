# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-02-24

### 🚀 Major Release - Complete Deserialization Engine Rewrite

#### ✨ New Features

- **Complete Nuxt 3 Deserialization Engine Rewrite**: Implemented proper hydration-based deserialization following Nuxt 3's actual serialization format
- **Comprehensive Example Suite**: 8 new example files covering all usage scenarios from basic to advanced
- **Complete Test Suite Overhaul**: Added performance tests, integration tests, and comprehensive coverage
- **Mermaid Architecture Diagrams**: Added visual documentation of system architecture and data flow

#### 🔧 Technical Improvements

- **New `_hydrate_nuxt3_value()` Function**: Replaces old recursive approach with proper hydration algorithm
- **Special Type Support**: Full support for Nuxt/devalue special types:
  - `{"$d": timestamp}` → `datetime` objects
  - `{"$s": [indices]}` → Python `set` objects  
  - `{"$m": [[key, value]]}` → Python `dict` objects
  - `{"$b": "123..."}` → Python `int` objects (BigInt)
  - `{"$r": "/pattern/flags"}` → Python `re.Pattern` objects
- **Smart Caching System**: Prevents circular references and duplicate processing
- **O(n) Time Complexity**: Optimized from exponential to linear time complexity

#### 🐛 Critical Bug Fixes

- **Fixed Exponential Data Expansion**: Resolved issue where 10K line files became 1GB+ when deserialized
- **Circular Reference Handling**: Proper prevention of infinite loops in interconnected data
- **Memory Efficiency**: Eliminated memory exhaustion on large datasets
- **Performance Optimization**: 60x+ faster processing for complex data structures

#### 📊 Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Large datasets | 1GB+ files | <50MB typical | 20x+ reduction |
| Processing time | Minutes | Seconds | 60x+ faster |
| Memory usage | Exponential growth | Linear scaling | Stable |
| Circular references | Infinite loops | Proper handling | ✅ Fixed |

#### 📚 Documentation & Examples

- **8 New Example Files**: Comprehensive coverage of all functionality
  - `01_basic_extraction.py` - Getting started
  - `02_navigation_steps.py` - All navigation types
  - `03_calendar_date_selection.py` - Calendar interactions
  - `04_anti_detection_stealth.py` - Stealth configurations
  - `05_deserialization_advanced.py` - Advanced deserialization
  - `06_parallel_extraction.py` - Concurrent processing
  - `07_error_handling.py` - Comprehensive error handling
  - `08_real_world_scenarios.py` - Production use cases

- **Complete Test Suite**: 6 new comprehensive test files
  - Performance and edge case testing
  - Integration and end-to-end testing
  - Extraction method validation
  - Utility function testing

- **Mermaid Diagrams**: Visual architecture documentation
  - System architecture overview
  - Data flow sequence diagrams
  - Component interaction maps
  - Deserialization engine flowchart

#### 🧹 Repository Cleanup

- Removed redundant test files from `test_manual/`
- Cleaned up build artifacts
- Organized codebase structure
- Updated development documentation

#### 🔄 Backward Compatibility

- **API Unchanged**: All existing code continues to work without modifications
- **Default Behavior Improved**: `deserialize_nuxt3=True` now uses the new engine automatically
- **No Breaking Changes**: Seamless upgrade path for existing users

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
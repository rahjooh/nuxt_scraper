# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-23

### Added
-   **Anti-Detection Module (`nuxtflow/anti_detection`)**:
    -   `delays.py`: Human-like random pauses (`human_delay`).
    -   `mouse_movement.py`: Realistic mouse movement simulation (`simulate_mouse_movement`).
    -   `typing.py`: Human-like typing with variable speed and optional typos (`human_type`).
    -   `user_agents.py`: Rotation of realistic user agent strings (`get_realistic_user_agent`).
    -   `viewports.py`: Randomization of browser viewport sizes (`get_random_viewport`).
    -   `stealth_scripts.py`: Collection of JavaScript snippets for Playwright `add_init_script` to mask automation.
-   **`StealthConfig` (`nuxtflow/utils.py`)**: Centralized dataclass for anti-detection parameters.
-   **`ProxyError` (`nuxtflow/exceptions.py`)**: New exception for proxy-related issues.

### Changed
-   **`NuxtDataExtractor` (`nuxtflow/extractor.py`)**:
    -   Constructor now accepts `stealth_config` and `proxy` parameters.
    -   `_start()` method enhanced to apply dynamic user agents, randomized viewports, browser launch arguments, and inject stealth JavaScripts based on `StealthConfig`.
    -   `_start()` now handles `proxy` configuration for `browser.new_context()`.
    -   `extract()` and `extract_sync()` methods pass `stealth_config` to `execute_steps`.
    -   `extract_nuxt_data()` convenience function updated to accept `stealth_config` and `proxy`.
-   **`execute_step` (`nuxtflow/steps.py`)**: Modified to use `StealthConfig` for human-like delays, typing, and mouse movements.
-   **`README.md`**: Updated with new sections on Anti-Detection Strategies and WAF/Advanced Detection Considerations, including examples.

### Fixed
-   Improved handling of browser launch failures with specific `BrowserError` and `ProxyError` exceptions.

## [0.1.0] - 2026-02-23

### Added
- Initial release of NuxtFlow
- NuxtDataExtractor class for browser automation
- NavigationStep system for multi-step interactions
- Support for click, fill, select, wait, scroll, hover actions
- Cross-platform compatibility (Linux, macOS, Windows)
- Comprehensive test suite with pytest
- Examples and documentation

### Features
- Async/await support with context manager
- Configurable browser types (Chromium, Firefox, WebKit)
- Error handling with custom exceptions
- JSON parsing and validation
- Playwright integration for reliable browser automation

### Documentation
- Comprehensive README with usage examples
- API reference documentation
- Example scripts for basic and advanced usage
- Cross-platform installation instructions
# Nuxt Scraper

Extract `__NUXT_DATA__` from Nuxt.js applications using [Playwright](https://playwright.dev/python/). Navigate to a URL, optionally run steps (click, fill, wait, scroll, etc.), then get the page's Nuxt data as JSON.

## Installation

### From PyPI (when published):
```bash
pip install nuxt_scraper
playwright install chromium
```

### From GitHub:
```bash
pip install git+https://github.com/rahjooh/nuxt_scraper.git
playwright install chromium
```

### For development:
```bash
git clone https://github.com/rahjooh/nuxt_scraper.git
cd nuxt_scraper
pip install -e ".[dev]"
playwright install chromium
```

## Usage

Nuxt Scraper provides flexible ways to extract data, from simple one-liners to complex, multi-step navigation with advanced anti-detection. Below are examples covering common scenarios.

### Basic Extraction

For straightforward cases where you just need to navigate to a URL and extract the `__NUXT_DATA__` without complex interactions, use the `extract_nuxt_data` convenience function.

```python
import asyncio
from nuxt_scraper import extract_nuxt_data
from nuxt_scraper.utils import StealthConfig

async def basic_extraction_example():
    # Simple extraction
    data = await extract_nuxt_data("https://your-nuxt-app.com")
    print("Simple Extraction Data:", data)

    # Extraction with anti-detection and proxy
    stealth_config = StealthConfig(random_delays=True, human_typing=True)
    proxy_config = {"server": "http://user:password@proxy.example.com:8080"}

    data_with_stealth_proxy = await extract_nuxt_data(
        "https://your-advanced-nuxt-app.com",
        stealth_config=stealth_config,
        proxy=proxy_config
    )
    print("Stealthy Extraction Data:", data_with_stealth_proxy)

if __name__ == "__main__":
    asyncio.run(basic_extraction_example())
```

### Advanced Extraction with `NuxtDataExtractor`

For more control over the browser session, including persistent sessions, custom browser arguments, and advanced debugging, use the `NuxtDataExtractor` class as an asynchronous context manager.

```python
import asyncio
from nuxt_scraper import NuxtDataExtractor, NavigationStep
from nuxt_scraper.utils import StealthConfig

async def advanced_extraction_example():
    custom_stealth = StealthConfig(
        random_delays=True, min_action_delay_ms=200, max_action_delay_ms=2000,
        human_typing=True, typing_speed_wpm=60,
        mouse_movement=True, randomize_viewport=True,
    )
    custom_proxy = {"server": "http://proxy.example.com:8080"}

    async with NuxtDataExtractor(
        headless=False, # Run browser in headful mode for debugging
        timeout=60000, # Longer timeout for complex pages
        browser_type="chromium",
        ignore_https_errors=True,
        stealth_config=custom_stealth,
        proxy=custom_proxy,
    ) as extractor:
        steps = [
            NavigationStep.click("button[data-accept-cookies]"),
            NavigationStep.wait(".main-content-loaded", timeout=10000),
        ]
        data = await extractor.extract(
            "https://your-complex-site.com",
            steps=steps,
            wait_for_nuxt=True,
            wait_for_nuxt_timeout=20000,
        )
    print("Advanced Extraction Data:", data)

if __name__ == "__main__":
    asyncio.run(advanced_extraction_example())
```

### Navigation Steps

`NavigationStep` objects define interactions with the web page before data extraction. They are chained in a list and executed sequentially. Each step can have an optional `wait_after_selector` to pause execution until a specific element appears after the step's action.

```python
from nuxt_scraper import NavigationStep
```

#### `NavigationStep.click(selector, timeout=5000, wait_after_selector=None)`

Clicks an element matching the given CSS `selector`.

```python
click_button = NavigationStep.click("button#submit-form", wait_after_selector=".form-submitted-message")
```

#### `NavigationStep.fill(selector, value, timeout=5000, wait_after_selector=None)`

Fills an input or textarea field with the specified `value`.

```python
fill_input = NavigationStep.fill("input[name='username']", "myusername", wait_after_selector="#username-validation-ok")
```

#### `NavigationStep.select(selector, value, timeout=5000, wait_after_selector=None)`

Selects an option in a dropdown (`<select>`) element by its `value`.

```python
select_dropdown = NavigationStep.select("select#country", "US", wait_after_selector="#state-dropdown-loaded")
```

#### `NavigationStep.wait(selector, timeout=10000, wait_after_selector=None)`

Waits for an element matching the `selector` to become visible on the page. Useful for ensuring dynamic content has loaded.

```python
wait_for_element = NavigationStep.wait("div.loading-spinner-hidden", timeout=15000)
```

#### `NavigationStep.scroll(selector, timeout=5000, wait_after_selector=None)`

Scrolls the element matching the `selector` into the viewport. Useful for triggering lazy-loaded content.

```python
scroll_to_footer = NavigationStep.scroll("footer#main-footer", wait_after_selector="#lazy-loaded-ads")
```

#### `NavigationStep.hover(selector, timeout=5000, wait_after_selector=None)`

Hover over an element matching the `selector`.

```python
hover_menu_item = NavigationStep.hover("li.menu-item-with-submenu", wait_after_selector=".submenu-visible")
```

#### `NavigationStep.select_date(target_date, calendar_selector, prev_month_selector, next_month_selector, month_year_display_selector, date_cell_selector, view_results_selector=None, timeout=15000, wait_after_selector=None)`

Selects a specific date from a calendar pop-up. This step intelligently navigates months until the `target_date` (format: YYYY-MM-DD) is found and clicked. You must provide specific selectors for the calendar components.

```python
import asyncio
from nuxt_scraper import NuxtDataExtractor, NavigationStep
from nuxt_scraper.utils import StealthConfig

async def select_date_example():
    # First, click the input that opens the calendar (if necessary)
    open_calendar_step = NavigationStep.click("input#date-picker-input")

    # Then, define the date selection step
    select_specific_date = NavigationStep.select_date(
        target_date="2026-03-15", # Example: March 15, 2026
        calendar_selector="div.calendar-popup", # Main calendar container
        prev_month_selector="button.prev-month", # Button to go to previous month
        next_month_selector="button.next-month", # Button to go to next month
        month_year_display_selector="div.month-year-display", # Element showing current month/year (e.g., "Feb 2026")
        date_cell_selector="div.day-cell", # General selector for individual date cells
        view_results_selector="button:has-text('View Results')", # Optional: button to click after date is selected
        timeout=20000, # Max timeout for this entire step
    )

    async with NuxtDataExtractor(headless=False, stealth_config=StealthConfig()) as extractor:
        data = await extractor.extract(
            "https://your-site-with-calendar.com",
            steps=[open_calendar_step, select_specific_date]
        )
    print("Data after date selection:", data)

if __name__ == "__main__":
    asyncio.run(select_date_example())
```

### Anti-Detection Configuration (`StealthConfig`)

To make your scraping activities less detectable, `nuxt_scraper` offers a `StealthConfig` dataclass to fine-tune human-like behaviors. By default, anti-detection is enabled with sensible defaults. You can customize it as needed.

```python
from nuxt_scraper.utils import StealthConfig

# Enable only random delays and human typing
moderate_stealth = StealthConfig(
    random_delays=True,
    human_typing=True,
    mouse_movement=False, # Disable mouse movement for faster execution
    randomize_viewport=False,
    realistic_user_agent=False,
)

# Or a more aggressive configuration
paranoid_config = StealthConfig(
    random_delays=True,
    min_action_delay_ms=500,
    max_action_delay_ms=4000,
    human_typing=True,
    typing_speed_wpm=45,
    typo_chance=0.03,
    pause_chance=0.08,
    mouse_movement=True,
    randomize_viewport=True,
    realistic_user_agent=True,
)

# Pass to extractor:
# extractor = NuxtDataExtractor(stealth_config=paranoid_config)
# or
# data = extract_nuxt_data(url, stealth_config=moderate_stealth)
```

### Error Handling

`nuxt_scraper` defines a suite of custom exceptions, all inheriting from `NuxtFlowException`, to help you gracefully handle various failure scenarios. Key exceptions include `NuxtDataNotFound`, `NavigationStepFailed`, `ExtractionTimeout`, `DataParsingError`, `BrowserError`, `ProxyError`, and `DateNotFoundInCalendarError`.

## API Reference

### `extract_nuxt_data(url, steps=None, headless=True, timeout=30000, wait_for_nuxt=True, wait_for_nuxt_timeout=None, stealth_config=None, proxy=None)`

Convenience function: creates an extractor, opens the URL, and returns the parsed `__NUXT_DATA__`.

- **`url`** (`str`) – Target page URL.
- **`steps`** (`Optional[List[NavigationStep]]`) – List of `NavigationStep` instances to execute.
- **`headless`** (`bool`) – Run browser in headless mode (default `True`).
- **`timeout`** (`int`) – Default timeout for Playwright operations in milliseconds (default `30000`).
- **`wait_for_nuxt`** (`bool`) – If `True`, waits for the `#__NUXT_DATA__` element to be present (default `True`).
- **`wait_for_nuxt_timeout`** (`Optional[int]`) – Specific timeout for waiting for `#__NUXT_DATA__`. Defaults to `timeout`.
- **`stealth_config`** (`Optional[StealthConfig]`) – Configuration for anti-detection features. Defaults to `StealthConfig()`.
- **`proxy`** (`Optional[Dict[str, str]]`) – Dictionary for proxy settings (e.g., `{"server": "http://ip:port", "username": "user", "password": "pass"}`).

### `NuxtDataExtractor`

Main class for controlled extraction and reuse of a browser session. Use as an `async with` context manager.

**Constructor:**

- **`headless`** (`bool`) – Run browser headless (default `True`).
- **`timeout`** (`int`) – Default timeout for Playwright operations in milliseconds (default `30000`).
- **`browser_type`** (`str`) – `"chromium"`, `"firefox"`, or `"webkit"` (default `"chromium"`).
- **`ignore_https_errors`** (`bool`) – Ignore HTTPS certificate errors (default `False`).
- **`viewport_width`** (`Optional[int]`) / **`viewport_height`** (`Optional[int]`) – Fixed viewport size in pixels. Ignored when `StealthConfig.randomize_viewport` is `True`.
- **`user_agent`** (`Optional[str]`) – Custom user agent string. Ignored when `StealthConfig.realistic_user_agent` is `True`.
- **`stealth_config`** (`Optional[StealthConfig]`) – Configuration for anti-detection features. Defaults to `StealthConfig()`.
- **`proxy`** (`Optional[Dict[str, str]]`) – Dictionary for proxy settings.

**Methods:**

- **`extract(url, steps=None, wait_for_nuxt=True, wait_for_nuxt_timeout=None)`**  
  Asynchronous method: navigates to `url`, runs `steps` (if any), then extracts and returns parsed Nuxt data.
- **`extract_sync(url, steps=None, wait_for_nuxt=True, wait_for_nuxt_timeout=None)`**  
  Synchronous wrapper that executes the `extract()` method in an event loop.

### `NavigationStep`

Dataclass representing a single browser interaction step. Steps are executed in order before data extraction.

| Factory method | Description | Parameters |
|----------------|-------------|------------|
| `NavigationStep.click` | Clicks an element. | `selector`, `timeout`, `wait_after_selector` |
| `NavigationStep.fill` | Fills an input/textarea. | `selector`, `value`, `timeout`, `wait_after_selector` |
| `NavigationStep.select` | Selects a dropdown option. | `selector`, `value`, `timeout`, `wait_after_selector` |
| `NavigationStep.wait` | Waits for a selector. | `selector`, `timeout`, `wait_after_selector` |
| `NavigationStep.scroll` | Scrolls element into view. | `selector`, `timeout`, `wait_after_selector` |
| `NavigationStep.hover` | Hovers over an element. | `selector`, `timeout`, `wait_after_selector` |
| `NavigationStep.select_date` | Selects a date from a calendar. | `target_date`, `calendar_selector`, `prev_month_selector`, `next_month_selector`, `month_year_display_selector`, `date_cell_selector`, `view_results_selector`, `timeout`, `wait_after_selector` |

## Anti-Detection Strategies

Nuxt Scraper incorporates several measures to make automation less detectable:

-   **Human-like Delays**: Random pauses between actions and during typing.
-   **Realistic Mouse Movements**: Simulated curved mouse paths before clicks.
-   **Human-like Typing**: Varied typing speeds, occasional typos, and corrections.
-   **User Agent Rotation**: Uses a random, realistic browser user agent for each new browser context.
-   **Randomized Viewports**: Cycles through common desktop resolutions to avoid a consistent browser footprint.
-   **Stealth Scripts**: Injects JavaScript to mask `webdriver` property, mock `chrome.runtime`, spoof permissions API, mimic browser plugins, and reduce WebGL fingerprinting.

These features are controlled via the `StealthConfig` object, allowing you to fine-tune the level of stealth needed.

## WAF & Advanced Detection Considerations

While Nuxt Scraper provides robust browser-level anti-detection, certain advanced measures like AWS WAF, sophisticated IP reputation systems, and CAPTCHAs require additional considerations:

-   **TLS-based Rules**: Playwright uses real browser engines, so its TLS fingerprint is generally good. However, highly advanced WAFs might analyze the full TLS handshake for bot patterns. For such cases, consider using *external proxy services* that specialize in TLS fingerprinting obfuscation. Nuxt Scraper's proxy support allows integration with these services.

-   **IP Reputation**: Repeated requests from a single IP address will quickly flag you. For effective evasion:
    -   **Proxy Rotation**: Utilize a pool of high-quality, frequently rotating residential or mobile proxies. Nuxt Scraper allows you to configure a proxy for each extractor instance.
    -   **Proxy Provider**: Choose reputable proxy providers (e.g., Bright Data, Oxylabs, Smartproxy) that manage IP rotation and quality.

-   **CAPTCHA**: Nuxt Scraper does not automatically solve CAPTCHAs, as this is a complex and evolving challenge. If you encounter CAPTCHAs:
    -   **Manual Intervention**: For low-volume tasks, you might configure the extractor to pause and wait for manual CAPTCHA solving.
    -   **Third-Party CAPTCHA Solving Services**: Integrate with services like 2Captcha, Anti-Captcha, or CapMonster. Your script can detect the CAPTCHA, send it to the service, and then input the solved token.

-   **Behavioral CAPTCHAs**: These monitor mouse movements, typing speed, and other interactions. Nuxt Scraper's human-like behaviors (mouse movement, typing, delays) significantly improve your chances against these, but are not foolproof.

Effective evasion against advanced WAFs often requires a layered approach combining Nuxt Scraper's browser stealth with high-quality external proxy infrastructure and, if necessary, CAPTCHA solving services.

## Examples (Deprecated - see Usage section)

-   **examples/basic_usage.py** – Simple extraction and context manager usage.
-   **examples/advanced_navigation.py** – Multiple steps: tabs, fill, scroll, select.
-   **examples/async_parallel.py** – Sequential and parallel extraction from multiple URLs.

## Development

```bash
pip install -e ".[dev]"
pytest
black nuxt_scraper tests
ruff check nuxt_scraper tests
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Run linting (`black . && ruff check .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Development

```bash
git clone https://github.com/rahjooh/nuxt_scraper.git
cd nuxt_scraper
pip install -e ".[dev]"
playwright install chromium

# Run tests
pytest

# Run linting
black nuxt_scraper tests examples
ruff check nuxt_scraper tests examples

# Build package
python -m build
```

## License

MIT License. See [LICENSE](LICENSE) for details.

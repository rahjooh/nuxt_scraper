# NuxtFlow

Extract `__NUXT_DATA__` from Nuxt.js applications using [Playwright](https://playwright.dev/python/). Navigate to a URL, optionally run steps (click, fill, wait, scroll, etc.), then get the page's Nuxt data as JSON.

## Installation

### From PyPI (when published):
```bash
pip install nuxtflow
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

## Quick start

**Simple extraction (no steps):**

```python
from nuxtflow import extract_nuxt_data

data = extract_nuxt_data("https://your-nuxt-app.com")
print(data)  # dict (or list) from __NUXT_DATA__
```

**With navigation steps (click tab, wait, then extract):**

```python
import asyncio
from nuxtflow import NuxtDataExtractor, NavigationStep

async def main():
    steps = [
        NavigationStep.click("button[data-tab='products']"),
        NavigationStep.wait("div.products-loaded", timeout=10000),
    ]
    async with NuxtDataExtractor(headless=True, timeout=30000) as extractor:
        data = await extractor.extract("https://shop.example.com", steps=steps)
    return data

data = asyncio.run(main())
```

## API

### `extract_nuxt_data(url, ...)`

Convenience function: creates an extractor, opens the URL, and returns the parsed `__NUXT_DATA__`.

- **url** – Target page URL.
- **steps** – Optional list of `NavigationStep` instances.
- **headless** – Run browser headless (default `True`).
- **timeout** – Timeout in milliseconds (default `30000`).
- **wait_for_nuxt** – Wait for `#__NUXT_DATA__` to be present (default `True`).
- **stealth_config** – `StealthConfig` object for anti-detection settings.
- **proxy** – Dictionary for proxy settings (`{"server": "http://ip:port", ...}`).

### `NuxtDataExtractor`

Main class for controlled extraction and reuse of a browser session.

**Constructor:**

- **headless** – Run browser headless (default `True`).
- **timeout** – Default timeout in ms (default `30000`).
- **browser_type** – `"chromium"`, `"firefox"`, or `"webkit"` (default `"chromium"`).
- **ignore_https_errors** – Ignore HTTPS certificate errors (default `False`).
- **viewport_width** / **viewport_height** – Viewport size in pixels. Overridden if `stealth_config.randomize_viewport` is `True`.
- **user_agent** – Optional custom user agent. Overridden if `stealth_config.realistic_user_agent` is `True`.
- **stealth_config** – `StealthConfig` object for anti-detection settings. Defaults to `StealthConfig()`.
- **proxy** – Dictionary for proxy settings (`{"server": "http://ip:port", ...}`).

**Methods:**

- **`extract(url, steps=None, wait_for_nuxt=True, wait_for_nuxt_timeout=None)`**  
  Async: navigate to `url`, run `steps` (if any), then extract and return parsed Nuxt data.
- **`extract_sync(url, steps=None, ...)`**  
  Sync wrapper that runs `extract()` in an event loop.

Use as an async context manager to manage browser lifecycle:

```python
async with NuxtDataExtractor() as extractor:
    data = await extractor.extract(url, steps=steps)
```

### `NavigationStep`

Steps are executed in order before extraction.

| Factory method | Description |
|----------------|-------------|
| `NavigationStep.click(selector, timeout=5000, wait_after_selector=None)` | Click an element |
| `NavigationStep.fill(selector, value, ...)` | Fill input/textarea |
| `NavigationStep.select(selector, value, ...)` | Select dropdown option |
| `NavigationStep.wait(selector, timeout=10000, ...)` | Wait for selector to be visible |
| `NavigationStep.scroll(selector, ...)` | Scroll element into view |
| `NavigationStep.hover(selector, ...)` | Hover over element |

All accept optional **wait_after_selector** to wait for another element after the action.

### `StealthConfig`

Dataclass for configuring anti-detection behaviors. Use `StealthConfig()` for defaults or customize:

```python
from nuxtflow.utils import StealthConfig

paranoid_config = StealthConfig(
    random_delays=True,
    min_action_delay_ms=500,
    max_action_delay_ms=4000,
    human_typing=True,
    typing_speed_wpm=45,
    mouse_movement=True,
    randomize_viewport=True,
    realistic_user_agent=True,
    typo_chance=0.03,
    pause_chance=0.08,
)

# Then pass to extractor:
# extractor = NuxtDataExtractor(stealth_config=paranoid_config)
```

### Exceptions

- **NuxtFlowException** – Base for all NuxtFlow errors.
- **NuxtDataNotFound** – `__NUXT_DATA__` element missing or empty.
- **NavigationStepFailed** – A navigation step failed (includes step and original error).
- **ExtractionTimeout** – Timeout waiting for Nuxt data.
- **DataParsingError** – Content is not valid JSON (includes `raw_content`).
- **BrowserError** – Playwright/browser error.
- **ProxyError** – Issue with proxy configuration or connection.

## Anti-Detection Strategies

NuxtFlow incorporates several measures to make automation less detectable:

-   **Human-like Delays**: Random pauses between actions and during typing.
-   **Realistic Mouse Movements**: Simulated curved mouse paths before clicks.
-   **Human-like Typing**: Varied typing speeds, occasional typos, and corrections.
-   **User Agent Rotation**: Uses a random, realistic browser user agent for each new browser context.
-   **Randomized Viewports**: Cycles through common desktop resolutions to avoid a consistent browser footprint.
-   **Stealth Scripts**: Injects JavaScript to mask `webdriver` property, mock `chrome.runtime`, spoof permissions API, mimic browser plugins, and reduce WebGL fingerprinting.

These features are controlled via the `StealthConfig` object, allowing you to fine-tune the level of stealth needed.

## WAF & Advanced Detection Considerations

While NuxtFlow provides robust browser-level anti-detection, certain advanced measures like AWS WAF, sophisticated IP reputation systems, and CAPTCHAs require additional considerations:

-   **TLS-based Rules**: Playwright uses real browser engines, so its TLS fingerprint is generally good. However, highly advanced WAFs might analyze the full TLS handshake for bot patterns. For such cases, consider using *external proxy services* that specialize in TLS fingerprinting obfuscation. NuxtFlow's proxy support allows integration with these services.

-   **IP Reputation**: Repeated requests from a single IP address will quickly flag you. For effective evasion:
    -   **Proxy Rotation**: Utilize a pool of high-quality, frequently rotating residential or mobile proxies. NuxtFlow allows you to configure a proxy for each extractor instance.
    -   **Proxy Provider**: Choose reputable proxy providers (e.g., Bright Data, Oxylabs, Smartproxy) that manage IP rotation and quality.

-   **CAPTCHA**: NuxtFlow does not automatically solve CAPTCHAs, as this is a complex and evolving challenge. If you encounter CAPTCHAs:
    -   **Manual Intervention**: For low-volume tasks, you might configure the extractor to pause and wait for manual CAPTCHA solving.
    -   **Third-Party CAPTCHA Solving Services**: Integrate with services like 2Captcha, Anti-Captcha, or CapMonster. Your script can detect the CAPTCHA, send it to the service, and then input the solved token.

-   **Behavioral CAPTCHAs**: These monitor mouse movements, typing speed, and other interactions. NuxtFlow's human-like behaviors (mouse movement, typing, delays) significantly improve your chances against these, but are not foolproof.

Effective evasion against advanced WAFs often requires a layered approach combining NuxtFlow's browser stealth with high-quality external proxy infrastructure and, if necessary, CAPTCHA solving services.

## Examples

-   **examples/basic_usage.py** – Simple extraction and context manager usage.
-   **examples/advanced_navigation.py** – Multiple steps: tabs, fill, scroll, select.
-   **examples/async_parallel.py** – Sequential and parallel extraction from multiple URLs.

## Development

```bash
pip install -e ".[dev]"
pytest
black nuxtflow tests
ruff check nuxtflow tests
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
black nuxtflow tests examples
ruff check nuxtflow tests examples

# Build package
python -m build
```

## License

MIT License. See [LICENSE](LICENSE) for details.
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

### `NuxtDataExtractor`

Main class for controlled extraction and reuse of a browser session.

**Constructor:**

- **headless** – Run browser headless (default `True`).
- **timeout** – Default timeout in ms (default `30000`).
- **browser_type** – `"chromium"`, `"firefox"`, or `"webkit"` (default `"chromium"`).
- **ignore_https_errors** – Ignore HTTPS certificate errors (default `False`).
- **viewport_width** / **viewport_height** – Viewport size in pixels.
- **user_agent** – Optional custom user agent.

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

### Exceptions

- **NuxtFlowException** – Base for all NuxtFlow errors.
- **NuxtDataNotFound** – `__NUXT_DATA__` element missing or empty.
- **NavigationStepFailed** – A navigation step failed (includes step and original error).
- **ExtractionTimeout** – Timeout waiting for Nuxt data.
- **DataParsingError** – Content is not valid JSON (includes `raw_content`).
- **BrowserError** – Playwright/browser error.

## Examples

- **examples/basic_usage.py** – Simple extraction and context manager usage.
- **examples/advanced_navigation.py** – Multiple steps: tabs, fill, scroll, select.
- **examples/async_parallel.py** – Sequential and parallel extraction from multiple URLs.

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

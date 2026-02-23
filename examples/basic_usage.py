"""
Basic usage examples for NuxtFlow.

Run with: python -m examples.basic_usage
Ensure nuxtflow is installed or PYTHONPATH includes the project root.
"""

from __future__ import annotations

# Use local package when run as python -m examples.basic_usage
try:
    from nuxtflow import extract_nuxt_data
except ImportError:
    extract_nuxt_data = None  # type: ignore[misc, assignment]


def simple_extract() -> None:
    """Extract Nuxt data from a URL with no navigation steps."""
    if extract_nuxt_data is None:
        raise ImportError("Install nuxtflow to run this example")

    url = "https://your-nuxt-app.example.com"
    data = extract_nuxt_data(url)
    print("Extracted keys:", list(data.keys()) if isinstance(data, dict) else type(data))
    return data


def extract_with_context_manager() -> None:
    """Use the extractor as an async context manager (recommended)."""
    import asyncio
    from nuxtflow import NuxtDataExtractor

    async def run() -> None:
        async with NuxtDataExtractor(headless=True, timeout=15000) as extractor:
            data = await extractor.extract("https://your-nuxt-app.example.com")
            print("Data received:", type(data))

    asyncio.run(run())


def extract_sync_wrapper() -> None:
    """Use the extractor's synchronous wrapper for one-off extraction."""
    import asyncio
    from nuxtflow import NuxtDataExtractor

    extractor = NuxtDataExtractor(headless=True)
    # Start the browser (in real use you'd use async with or call _start())
    # For sync-only usage, use extract_nuxt_data() instead:
    if extract_nuxt_data is None:
        raise ImportError("Install nuxtflow to run this example")
    data = extract_nuxt_data(
        "https://your-nuxt-app.example.com",
        headless=True,
        timeout=20000,
    )
    print("Sync extraction done:", type(data))


if __name__ == "__main__":
    print("Basic usage examples (replace URL with a real Nuxt app to run)")
    if extract_nuxt_data:
        print("Simple extract:", extract_nuxt_data.__doc__)
    # Uncomment to run against a real URL:
    # simple_extract()
    # extract_with_context_manager()

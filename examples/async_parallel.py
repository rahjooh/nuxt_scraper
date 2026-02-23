"""
Async and parallel extraction patterns with NuxtFlow.

Run with: python -m examples.async_parallel
"""

from __future__ import annotations

import asyncio
from nuxtflow import NuxtDataExtractor


async def extract_one(extractor: NuxtDataExtractor, url: str) -> dict | list:
    """Extract from a single URL using an existing extractor (shared browser)."""
    return await extractor.extract(url)


async def extract_multiple_sequential(urls: list[str]) -> list:
    """Extract from multiple URLs one after another (one browser session)."""
    results = []
    async with NuxtDataExtractor(timeout=20000) as extractor:
        for url in urls:
            data = await extractor.extract(url)
            results.append(data)
    return results


async def extract_multiple_parallel(urls: list[str]) -> list:
    """Extract from multiple URLs in parallel (one browser, multiple pages)."""
    async with NuxtDataExtractor(timeout=20000) as extractor:
        tasks = [extractor.extract(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    # Optionally re-raise exceptions instead of returning them
    out = []
    for r in results:
        if isinstance(r, Exception):
            raise r
        out.append(r)
    return out


async def main() -> None:
    urls = [
        "https://nuxt-app-1.example.com",
        "https://nuxt-app-2.example.com",
    ]
    print("Sequential:", len(urls), "URLs")
    # results = await extract_multiple_sequential(urls)
    print("Parallel: use extract_multiple_parallel(urls) for concurrent extraction")


if __name__ == "__main__":
    asyncio.run(main())
